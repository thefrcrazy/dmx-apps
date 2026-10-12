#!/usr/bin/env python3
"""Recopie dans dmx-apps les releases des dépôts sources listés dans mirror.json.

Pour chaque app :

1. chaque release publiée du dépôt source à partir de `since` qui manque ici est
   recopiée sous le tag `<id>-<tag>` (assets, notes, statut de préversion) ;
2. les fichiers servis par GitHub Pages (`pages`) sont réécrits depuis la
   release miroir stable la plus récente, puis, si elle est plus récente, la
   dernière préversion ;
3. le bouton « Télécharger » du catalogue (apps.json) suit la dernière stable.

Idempotent : relancé sans nouvelle release, il ne change rien. Une release
recopiée à moitié reste un brouillon et est refaite au passage suivant.

Les assets de `rewrite_assets` sont des flux non signés dont les liens de
téléchargement sont réécrits vers dmx-apps. Les flux signés (manifeste
DmxServerManager) sont produits par la CI source pour les deux emplacements :
le miroir ne fait que les renommer (`rename_assets`).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = os.environ.get("MIRROR_TARGET_REPO", "thefrcrazy/dmx-apps")


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, text=True, capture_output=True).stdout


def releases(repo: str) -> list[dict]:
    pages = json.loads(gh("api", "--paginate", "--slurp", f"repos/{repo}/releases?per_page=100"))
    return [release for page in pages for release in page]


def published(releases_: list[dict]) -> list[dict]:
    """Releases publiées, de la plus ancienne à la plus récente."""
    return sorted((r for r in releases_ if not r["draft"]), key=lambda r: r["published_at"])


def mirror_release(app: dict, release: dict, tag: str) -> None:
    source_tag = release["tag_name"]
    print(f"==> {app['id']}: {app['source']}@{source_tag} -> {TARGET}@{tag}")
    with tempfile.TemporaryDirectory(prefix="dmx-mirror-") as directory:
        folder = Path(directory)
        if release["assets"]:
            gh("release", "download", source_tag, "--repo", app["source"], "--dir", str(folder))
        for name in app["skip_assets"]:
            (folder / name).unlink(missing_ok=True)
        for old, new in app["rename_assets"].items():
            if (folder / old).exists():
                (folder / old).replace(folder / new)
        old_base = f"https://github.com/{app['source']}/releases/download/{source_tag}/"
        new_base = f"https://github.com/{TARGET}/releases/download/{tag}/"
        for name in app["rewrite_assets"]:
            path = folder / name
            if path.exists():
                path.write_text(path.read_text(encoding="utf-8").replace(old_base, new_base), encoding="utf-8")
                if old_base in path.read_text(encoding="utf-8"):
                    sys.exit(f"error: {name} still names {old_base}")

        notes = folder.parent / f"{folder.name}-notes.md"
        notes.write_text(release["body"] or "", encoding="utf-8")
        try:
            # Brouillon d'abord : une copie interrompue n'apparaît jamais comme publiée.
            flags = ["--draft", "--latest=false"] + (["--prerelease"] if release["prerelease"] else [])
            files = sorted(str(path) for path in folder.iterdir())
            gh("release", "create", tag, "--repo", TARGET, "--target", "main",
               "--title", release["name"] or f"{app['id']} {source_tag}",
               "--notes-file", str(notes), *flags, *files)
            gh("release", "edit", tag, "--repo", TARGET, "--draft=false", "--latest=false")
        finally:
            notes.unlink(missing_ok=True)


def write_pages(mapping: dict, release: dict) -> None:
    if not mapping:
        return
    names = set(mapping.values())
    available = {asset["name"] for asset in release["assets"]}
    with tempfile.TemporaryDirectory(prefix="dmx-pages-") as directory:
        folder = Path(directory)
        for name in sorted(names & available):
            gh("release", "download", release["tag_name"], "--repo", TARGET, "--pattern", name, "--dir", str(folder))
        for destination, name in mapping.items():
            if name not in available:
                print(f"    warning: {release['tag_name']} has no {name}, {destination} left as is")
                continue
            path = ROOT / destination
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(folder / name, path)


def update_catalog(app_id: str, url: str) -> None:
    path = ROOT / "apps.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    app = next((a for a in catalog["apps"] if a["id"] == app_id), None)
    if app is None:
        return
    primary = next((link for link in app["links"] if link.get("primary")), None)
    if primary is None or primary["url"] == url:
        return
    primary["url"] = url
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    config = json.loads((ROOT / "mirror.json").read_text(encoding="utf-8"))
    for app in config["apps"]:
        prefix = app["id"] + "-"
        source = published(releases(app["source"]))
        since = next((r for r in source if r["tag_name"] == app["since"]), None)
        if since is None:
            print(f"==> {app['id']}: {app['source']}@{app['since']} is not published yet, nothing to mirror")
            continue

        existing = {r["tag_name"]: r for r in releases(TARGET) if r["tag_name"].startswith(prefix)}
        for release in source:
            if release["published_at"] < since["published_at"]:
                continue
            tag = prefix + release["tag_name"]
            if tag in existing and not existing[tag]["draft"]:
                continue
            if tag in existing:
                gh("release", "delete", tag, "--repo", TARGET, "--yes")
            mirror_release(app, release, tag)

        mirrored = published(r for r in releases(TARGET) if r["tag_name"].startswith(prefix))
        stable = next((r for r in reversed(mirrored) if not r["prerelease"]), None)
        prerelease = next((r for r in reversed(mirrored) if r["prerelease"]), None)
        if stable:
            write_pages(app["pages"]["stable"], stable)
            update_catalog(app["id"], stable["html_url"])
        if prerelease and (stable is None or prerelease["published_at"] > stable["published_at"]):
            write_pages(app["pages"]["prerelease"], prerelease)


if __name__ == "__main__":
    main()
