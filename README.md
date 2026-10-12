# DMX Apps

Toutes les applications DMX distribuées gratuitement : téléchargements, flux de
mise à jour automatique et liens vers les web apps.

**Catalogue : <https://thefrcrazy.github.io/dmx-apps/>**

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
