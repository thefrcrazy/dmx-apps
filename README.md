<p align="center">
  <img src="icons/dmx-apps.png" alt="" width="96" height="96">
</p>

<h1 align="center">DMX Apps</h1>

<p align="center">
  Les applications gratuites de Develop Max : binaires signés, flux de mise à jour et historique des versions.
  <br>
  <a href="https://apps.develop-max.com"><strong>apps.develop-max.com</strong></a>
</p>

---

## Télécharger

Le plus simple est de passer par **[apps.develop-max.com](https://apps.develop-max.com)** : le site détecte
votre système, propose la bonne version et donne accès aux bêtas et aux anciennes versions. Les fichiers
eux-mêmes sont hébergés dans les [releases de ce dépôt](https://github.com/thefrcrazy/dmx-apps/releases).

| Application | Pour | Plateformes |
| --- | --- | --- |
| [**DmxUtilities**](https://apps.develop-max.com/utilities) | Une quinzaine d'outils dans la barre de menus : presse-papiers, captures, OCR, Authenticator… | macOS 26+ (Apple Silicon) |
| [**DmxMoney 2**](https://apps.develop-max.com/money) | Finances personnelles locales et privées | macOS, Windows, Linux |
| [**DmxServerManager**](https://apps.develop-max.com/server-manager) | Panneau auto-hébergé pour serveurs de jeux | Docker, Linux, Windows |
| [**DmxDart**](https://apps.develop-max.com/dart) | Fléchettes multijoueur, même à distance | Web (PWA) |
| [**DmxBoard**](https://apps.develop-max.com/board) | Documents, tâches, tableurs et canvas | En développement |

Une fois installées, les applications se mettent à jour d'elles-mêmes à partir des flux publiés ici.

## Rôle de ce dépôt

Le code de chaque application vit dans son propre dépôt, souvent privé. Ce dépôt public ne contient que ce
dont les utilisateurs et les apps installées ont besoin :

- **les binaires**, attachés aux GitHub Releases ;
- **les flux de mise à jour**, relayés par apps.develop-max.com (et encore servis par GitHub Pages) ;
- **les icônes** du catalogue et l'outil qui les installe dans chaque app.

Le site [apps.develop-max.com](https://apps.develop-max.com) (dépôt privé `thefrcrazy/dmx-apps-web`) lit ces
releases et les présente. L'ancienne adresse `thefrcrazy.github.io/dmx-apps/` redirige vers lui.

```text
dmx-apps/
├── dmx-utilities/        appcast Sparkle, archives et deltas
├── dmx-money/            manifestes de mise à jour stable et bêta (macOS, Windows)
├── dmx-server-manager/   manifeste signé et fichiers d'installation « latest »
├── icons/                icônes du catalogue (DMX-Icons)
├── tools/                apply-dmx-icons.py
└── index.html            redirection vers apps.develop-max.com
```

### Flux de mise à jour

**apps.develop-max.com/feeds** relaie les flux de ce dépôt (cache d'une minute, contenu
identique ; les archives redirigent vers `raw.githubusercontent.com`). Les prochaines versions
des apps le lisent en premier ; les versions déjà installées lisent encore GitHub Pages, qui sert
les mêmes fichiers.

| Application | Nouvelle adresse | Adresse GitHub Pages |
| --- | --- | --- |
| DmxUtilities | `https://apps.develop-max.com/feeds/dmx-utilities/appcast.xml` | `https://thefrcrazy.github.io/dmx-apps/dmx-utilities/appcast.xml` |
| DmxMoney 2 | `…/feeds/dmx-money/updates.json`, `updates-rc.json` ; Windows : `…/feeds/dmx-money/win/`, `win-rc/` | mêmes chemins sous `thefrcrazy.github.io/dmx-apps/` |
| DmxServerManager | `…/feeds/dmx-server-manager/release-manifest.json` (signé, relayé tel quel) | `thefrcrazy.github.io/dmx-apps/dmx-server-manager/release-manifest.json` |

### Bascule hors de GitHub Pages

Pages ne peut pas être coupé tant que des versions installées lisent ses adresses : elles
ne recevraient plus aucune mise à jour.

1. **Fait** : apps.develop-max.com relaie les flux sous `/feeds` (dépôt `dmx-apps-web`).
2. **Prêt sur les branches `feeds/apps-develop-max`** de `dmx_utils`, `dmx-money-2` et
   `DmxServerManager` : chaque app lit d'abord apps.develop-max.com. DmxMoney garde Pages
   puis l'ancien dépôt en secours ; DmxServerManager garde son propre dépôt en secours ;
   DmxUtilities (Sparkle n'accepte qu'un flux) lit uniquement le site.
3. Publier une version de chaque app depuis ces branches. Les versions précédentes
   continuent de lire Pages et y trouvent la nouvelle version, qui lira ensuite le site.
4. Laisser le temps aux installations de se mettre à jour (quelques mois), puis
   désactiver Pages. La page d'accueil redirige aujourd'hui les anciens liens
   (`…/dmx-apps/#dmx-money`) : ils ne fonctionneront plus.
5. Retirer ensuite les secours Pages du code de DmxMoney.

## Publier une version

Chaque application publie ses releases, ses flux et ses fichiers depuis sa propre chaîne de publication (CI ou
scripts locaux), avec une deploy key ou le token *fine-grained* `DMX_APPS_TOKEN` limité à ce dépôt
(permission **Contents** en lecture et écriture).

- **Tags préfixés par l'app** : `<app>-v<version>`, par exemple `dmx-money-v2.1.10`. Plusieurs apps partagent
  ce dépôt, un tag `v1.0.0` nu serait ambigu. Pas de `/` dans les tags.
- **Bêtas** : une version avec suffixe (`1.10.0-rc.1`) est publiée en pre-release et ne devient jamais
  « Latest ».
- **Jamais `releases/latest`** : la dernière release du dépôt peut appartenir à n'importe quelle app. Les flux
  pointent vers des releases taguées (`releases/download/<tag>/<fichier>`).
- **Chacun chez soi** : une release ne modifie que le dossier de son app.
- **Notes de version** : le corps de la release est affiché tel quel sur le site ; la première ligne d'un tag
  annoté sert de titre (workflow `Release DmxUtilities`).

Le site repère seul les nouvelles releases (cache de 5 minutes). Pour l'actualiser immédiatement :
`POST https://apps.develop-max.com/api/refresh` avec `Authorization: Bearer <REFRESH_TOKEN>`.

## Icônes

Les icônes viennent de la bibliothèque DMX-Icons. Après une régénération de la bibliothèque :

```bash
python3 tools/apply-dmx-icons.py <DMX-Icons> <app> <dépôt de l'app>
```

`<app>` vaut `utilities`, `money`, `server-manager`, `dart`, `board`, `streamhub` ou `catalog`. Le script écrit
les fichiers aux emplacements que chaque app attend ; ses conventions (marge de la grille Apple, catalogue iOS
Any + Dark, favicons, contour intérieur Inset White sur fond `#FAFAFA`) sont décrites en tête du fichier.
`DMX_ICON_BACKUP_ROOT` garde une copie des fichiers remplacés ; `DMX_ICON_REPORT` produit un rapport JSON des
chemins écrits et de leurs empreintes SHA-256.
