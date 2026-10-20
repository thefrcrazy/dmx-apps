# DMX Apps

Toutes les applications DMX distribuées gratuitement : téléchargements, flux de
mise à jour automatique et liens vers les web apps.

**Catalogue : <https://apps.develop-max.com>**

Le site du catalogue vit dans le dépôt privé `thefrcrazy/dmx-apps-web` et lit les
GitHub Releases de ce dépôt. Les flux de mise à jour restent servis ici, par GitHub
Pages (`https://thefrcrazy.github.io/dmx-apps/<app>/…`).

Le code source de chaque application vit dans son propre dépôt, qui peut être
privé. Ce dépôt public ne contient que ce dont les utilisateurs et les apps
installées ont besoin : le catalogue, les flux de mise à jour et, dans les
GitHub Releases, les binaires.

## Organisation

```
dmx-apps/
├── index.html            catalogue (GitHub Pages)
├── apps.json             liste des apps lue par le catalogue
├── icons/
└── <app>/                un dossier par app : ses flux de mise à jour
    └── appcast.xml       (Sparkle, manifeste JSON… selon l'app)
```

| App | Dossier | Tags de release |
| --- | --- | --- |
| DmxUtilities | `dmx-utilities/` | `dmx-utilities-v1.9.4` |
| DmxMoney 2 | `dmx-money/` | `dmx-money-v2.1.1` |
| DmxServerManager | `dmx-server-manager/` | `dmx-server-manager-v1.2.8` |
| DmxDart | `dmx-dart/` | `dmx-dart-v1.0.1` |
| DMX Board | `dmx-board/` | `dmx-board-v1.0.0` |

## Règles pour publier

- **Tags préfixés par l'app** (`<app>-v<version>`) : plusieurs apps partagent
  ce dépôt, un tag `v1.0.0` nu serait ambigu. Pas de `/` dans les tags, pour
  garder des URLs de téléchargement simples.
- **Ne jamais s'appuyer sur `releases/latest`** : la « dernière release » de ce
  dépôt peut être celle de n'importe quelle app. Chaque app lit son propre flux,
  servi par GitHub Pages depuis son dossier :
  `https://thefrcrazy.github.io/dmx-apps/<app>/…`
- Les liens de téléchargement des flux pointent vers des releases taguées
  (`releases/download/<tag>/<fichier>`), jamais vers `latest`.
- Une release ne touche que les fichiers de son app : jamais de suppression ou
  de réécriture dans le dossier d'une autre.

## Publication depuis les dépôts sources

Chaque application publie directement ses releases, ses flux et ses assets dans ce dépôt via sa propre chaîne de publication (CI/CD ou scripts locaux).

`DMX_APPS_TOKEN` est un token *fine-grained* limité à ce dépôt, permissions **Contents** en lecture et écriture, enregistré comme secret Actions dans les dépôts sources (`dmx_utils`, `DmxServerManager`, `dmx-money-2`…).

## Icônes

Les icônes des apps viennent de la bibliothèque DMX-Icons. Après chaque
régénération de la bibliothèque :

```bash
python3 tools/apply-dmx-icons.py "~/Developer/personal/Icons App/DMX-Icons" money ~/Developer/work/apps/dmx-money-2
```

(`utilities`, `money`, `server-manager`, `dart`, `board`, `streamhub` ou `catalog`.) Le script
écrit les fichiers aux emplacements que chaque app attend ; ses conventions
(marge de la grille Apple, catalogue iOS Any + Dark, favicons…) sont décrites en
tête du fichier.

Les documents et exports utilisent le contour intérieur **Inset White** de DMX-Icons
(4 px à 1024 px, blanc à 32 %, fond clair `#FAFAFA`). L'import Money synchronise
aussi l'icône PWA iOS dédiée et son premier plan reproductible. Board inclut
ses ressources macOS et Linux ; StreamHub conserve les chemins de ses assets Tauri.
Les imports copient les ressources source ; les binaires et sites des autres apps
ne sont pas reconstruits ou publiés automatiquement.

Pour garder une copie préalable des fichiers remplacés, définir
`DMX_ICON_BACKUP_ROOT`. `DMX_ICON_REPORT` désigne un fichier JSON contenant
les chemins écrits et leurs empreintes SHA-256.
