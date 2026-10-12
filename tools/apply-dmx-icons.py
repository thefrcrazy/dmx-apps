#!/usr/bin/env python3
"""Installe les icônes de la bibliothèque DMX-Icons dans chaque application DMX.

    python3 tools/apply-dmx-icons.py <DMX-Icons> <app> <dépôt>

<app> : utilities, money, server-manager, dart, board ou catalog. Relancer après
chaque régénération de la bibliothèque ; le script ne fait que copier ou
redimensionner des fichiers, les apps se chargent de les compiler.

Conventions :
- macOS : le document Icon Composer (.icon) quand l'app cible macOS 26, pour les
  apparences claire, sombre et teintée ; sinon le catalogue AppIcon. Le rendu
  macos/default-1024.png de la bibliothèque remplit tout le carré : on lui
  rend la marge de la grille Apple (tuile de 824 px sur 1024) pour qu'il ait
  la taille des autres apps dans le Dock.
- iOS : catalogue universel 1024 Any + Dark (ios/AppIcon-modern.appiconset).
- Web : favicons ICO, PNG et SVG, apple-touch-icon opaque, icônes PWA « any »
  (symbole) et « maskable » (fond plein) séparées.
- Barres de menus et de notification : silhouettes template, noires et
  blanches de tray/.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

LIBRARY = Path(sys.argv[1]).expanduser()
APP = sys.argv[2]
REPO = Path(sys.argv[3]).expanduser()
CODES = {"utilities": "UTL", "money": "MON", "server-manager": "SRV", "dart": "DRT", "board": "BRD", "catalog": "APP"}
EXPORTS = LIBRARY / "exports"
written: list[Path] = []


def export(code: str) -> Path:
    return EXPORTS / f"DMX-{code}-01"


def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    written.append(destination)


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store"))
    written.append(destination)


def resized(source: Path, destination: Path, size: int | None = None) -> None:
    image = Image.open(source).convert("RGBA")
    size = size or Image.open(destination).size[0]
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.resize((size, size), Image.LANCZOS).save(destination, optimize=True)
    written.append(destination)


def macos_icon(code: str, destination: Path) -> None:
    """macos/default-1024.png with the Apple grid margin put back."""
    tile = Image.open(export(code) / "macos/default-1024.png").convert("RGBA").resize((824, 824), Image.LANCZOS)
    canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    canvas.paste(tile, (100, 100), tile)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, optimize=True)
    written.append(destination)


def macos_iconset(code: str, appiconset: Path) -> None:
    """Every file of an existing macOS AppIcon catalog, resized from macos_icon()."""
    master = appiconset / ".master-1024.png"
    macos_icon(code, master)
    for png in appiconset.glob("*.png"):
        if png != master:
            resized(master, png)
    master.unlink()
    written.remove(master)


def icns(code: str, destination: Path) -> None:
    work = destination.parent / ".dmx.iconset"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    master = work / "master.png"
    macos_icon(code, master)
    written.remove(master)
    for size in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            name = f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"
            Image.open(master).resize((size * scale,) * 2, Image.LANCZOS).save(work / name)
    master.unlink()
    subprocess.run(["iconutil", "-c", "icns", str(work), "-o", str(destination)], check=True)
    shutil.rmtree(work)
    written.append(destination)


def web(code: str, public: Path, *, logo: Path | None = None, favicon_png: str | None = None) -> None:
    w = export(code) / "web"
    for name in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "icon-maskable-192.png", "icon-maskable-512.png"):
        copy(w / name, public / name)
    if favicon_png:
        size = Image.open(public / favicon_png).size[0] if (public / favicon_png).exists() else 32
        copy(w / f"favicon-{size}.png", public / favicon_png)
    if logo:
        resized(w / "icon-512.png", logo)


def utilities() -> None:
    e, app = export("UTL"), REPO / "DmxUtilities"
    copy_tree(LIBRARY / "icon-composer/DMX-UTL-01.icon", app / "DmxUtilities.icon")
    macos_iconset("UTL", app / "Assets.xcassets/AppIcon.appiconset")
    copy(e / "tray/menuTemplate.png", app / "Assets.xcassets/MenuBarIcon.imageset/icon_18x18.png")
    copy(e / "tray/menuTemplate@2x.png", app / "Assets.xcassets/MenuBarIcon.imageset/icon_18x18@2x.png")
    copy(export("APP") / "logo-1024.png", app / "Assets.xcassets/DmxFolderLogo.imageset/DmxFolderLogo.png")
    for name in ("icon_source.png", "source.png"):
        copy(e / "logo-1024.png", app / "Assets.xcassets" / name)
    # Safari toolbar item: 18 pt template PDF (rsvg-convert counts 96 px per inch).
    pdf = REPO / "SafariAuthenticator/ToolbarIcon.pdf"
    subprocess.run(["rsvg-convert", "-f", "pdf", "-w", "24", "-h", "24", str(e / "logo-mono.svg"), "-o", str(pdf)], check=True)
    written.append(pdf)


def money() -> None:
    e = export("MON")
    brand = REPO / "shared/brand"
    icons = brand / "icons"
    symbol = e / "web/icon-512.png"
    # Apple
    copy_tree(LIBRARY / "icon-composer/DMX-MON-01.icon", REPO / "apple/DmxMoney-macOS-Modern/DmxMoney.icon")
    macos_icon("MON", icons / "macos-1024.png")
    copy_tree(e / "ios/AppIcon-modern.appiconset", icons / "ios/AppIcon-modern.appiconset")
    for png in (icons / "ios").glob("*.png"):
        resized(e / "ios/app-store-1024.png", png)
    for d in (REPO / "apple/DmxMoney-macOS/Assets.xcassets/MenuBarIcon.imageset",
              REPO / "apple/Packages/DmxKit/Sources/DmxKit/Resources/Icons.xcassets/MenuBarIcon.imageset"):
        copy(e / "tray/menuTemplate.png", d / "MenuBarIcon.png")
        copy(e / "tray/menuTemplate@2x.png", d / "MenuBarIcon@2x.png")
    # Marque partagée
    resized(symbol, brand / "logo.png")
    for name in ["32x32.png", "64x64.png", "128x128.png", "128x128@2x.png", "icon.png", "StoreLogo.png"] + \
            [p.name for p in icons.glob("Square*Logo.png")]:
        resized(symbol, icons / name)
    icns("MON", icons / "icon.icns")
    copy(e / "windows/DMX-MON-01.ico", icons / "icon.ico")
    for png in (icons / "android").glob("mipmap-*/*.png"):
        density = png.parent.name
        source = e / "android/res" / (density.replace("mipmap", "drawable") if "foreground" in png.name else density) / png.name
        resized(source if source.exists() else symbol, png)
    for size in (16, 24, 32, 48, 64, 128, 256, 512):
        copy(e / f"linux/hicolor/{size}x{size}/apps/dmx-money-tricolor-arrow.png",
             icons / f"hicolor/{size}x{size}/apps/com.dmxmoney.app.png")
    copy(e / "linux/hicolor/scalable/apps/dmx-money-tricolor-arrow.svg", icons / "hicolor/scalable/apps/com.dmxmoney.app.svg")
    # Windows : application, et zone de notification en couleur.
    copy(e / "windows/DMX-MON-01.ico", REPO / "windows/src/DmxMoney.App/Assets/dmxmoney.ico")
    copy(e / "tray/color.ico", REPO / "windows/src/DmxMoney.App/Assets/dmxmoney-tray.ico")
    # Compagnon PWA
    pwa = REPO / "pwa/public"
    web("MON", pwa, logo=pwa / "logo.png")
    copy(e / "web/icon-192.png", pwa / "pwa-192.png")
    copy(e / "web/icon-512.png", pwa / "pwa-512.png")
    for size in (192, 512):
        copy(e / f"web/icon-maskable-{size}.png", pwa / f"pwa-maskable-{size}.png")
        (pwa / f"icon-maskable-{size}.png").unlink()
        written.remove(pwa / f"icon-maskable-{size}.png")
    copy(e / "web/favicon-32.png", pwa / "favicon-32.png")


def server_manager() -> None:
    e, public = export("SRV"), REPO / "frontend/public"
    web("SRV", public, favicon_png="favicon.png")
    # No web app manifest: the PWA icons have no use here.
    for size in (192, 512):
        (public / f"icon-maskable-{size}.png").unlink()
        written.remove(public / f"icon-maskable-{size}.png")
    resized(e / "web/icon-512.png", public / "dmx-server-manager-logo.png", 256)


def dart() -> None:
    e, public = export("DRT"), REPO / "web/public"
    web("DRT", public, favicon_png="favicon.png")
    copy(e / "web/icon-192.png", public / "icon-192.png")
    copy(e / "web/icon-512.png", public / "icon-512.png")
    # Android notification badge: white silhouette on transparent, 96 px.
    copy(e / "android/res/drawable-xxxhdpi/ic_stat_app.png", public / "badge-96.png")


def board() -> None:
    e, public = export("BRD"), REPO / "apps/web/public"
    web("BRD", public)
    copy(e / "web/favicon.svg", public / "icon.svg")
    (public / "favicon.svg").unlink()
    written.remove(public / "favicon.svg")
    copy(e / "web/favicon-32.png", public / "favicon-32.png")
    copy(e / "web/icon-192.png", public / "icon-192.png")
    copy(e / "web/icon-512.png", public / "icon-512.png")
    copy(e / "windows/DMX-BRD-01.ico", REPO / "apps/windows/Assets/dmx-board.ico")


def catalog() -> None:
    icons = REPO / "icons"
    for app, code in [("dmx-utilities", "UTL"), ("dmx-money", "MON"), ("dmx-server-manager", "SRV"),
                      ("dmx-dart", "DRT"), ("dmx-board", "BRD"), ("dmx-apps", "APP")]:
        resized(export(code) / "web/icon-maskable-512.png", icons / f"{app}.png", 256)
    w = export("APP") / "web"
    copy(w / "favicon.svg", icons / "favicon.svg")
    copy(w / "favicon-32.png", icons / "favicon-32.png")
    copy(w / "apple-touch-icon.png", icons / "apple-touch-icon.png")


{"utilities": utilities, "money": money, "server-manager": server_manager,
 "dart": dart, "board": board, "catalog": catalog}[APP]()
print(f"{len(written)} fichiers écrits dans {REPO} depuis DMX-{CODES[APP]}-01")
