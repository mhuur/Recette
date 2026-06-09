# CLAUDE.md

Guide pour Claude Code sur ce projet.

## Projet
- App de gestion de **recettes** (usage perso/familial) : recettes, liste de courses, ingrédients de saison.
- Multi-comptes via partage Firestore + mode invité lecture seule.
- État : **en prod**, utilisée au quotidien sur mobile et desktop.

## Stack & versions
- **Single-file** : tout (HTML + CSS + JS) dans un seul `.html`. Pas de build, bundler, ni npm.
- Vanilla JS ; CSS dark « néon » (variables `--bg`, `--primary`…) ; polices Google Inter + Tilt Neon.
- CDN dans `<head>` : Firebase compat **10.12.5** (app/auth/firestore), SheetJS **xlsx 0.18.5** (import Excel).
- Données : `localStorage` + sync temps réel Firestore.

## Fichiers du dossier
- `index.html` — **l'app Recettes** (titre « 🍳 Mes Recettes », ~7 600 lignes), suivi par git.
- `index - <timestamp>.html` (titre « Devis Photo ») — **autre outil**, gardé en local comme **référence de design** (sidebar, menu « Signaler un bug ») ; **gitignored** (hors repo). Ne pas le confondre avec l'app.

## Commandes
- **Aucun build / install / lint / test.** On édite `index.html` directement.
- **Dépôt git lié** : ce dossier est un clone de `github.com/mhuur/Recette` (branche `main`). Workflow : éditer `index.html` → `git add/commit/push` direct (le dossier vit dans OneDrive, comme le projet todolist).
- Test local : `py -m http.server 8000` dans le dossier → `http://localhost:8000/index.html`.
- Le **login Google exige `http://localhost`** (échoue en `file://`).

## Architecture (fichier Recettes)
- Ordre interne : `<head>` CDN → `<style>` (~1900 lignes : thème + responsive `@media (max-width:768px)`) → `<body>` (sidebar + onglets + modals) → `<script>`.
- **État unique** `state` : `recipes`, `ingredients`, `units`, `ingredientTypes`, `ingredientFamilies`, `mealTypes`, `filters`, `notes`, `bugs`, sélection… IDs via `uid()`.
- **Persistance** : `save()` = localStorage + push Firestore débouncé (5 s) ; `saveLocal()` = local seul (filtres/UI).
- **Sync** : `fbDocRef` → `users/{uid}/app/data` (perso) ou `sharedData/{espace}` (partagé) ; `onSnapshot` temps réel ; `applyCloudData()` applique le cloud.
- **Onglets** : Recettes, Courses, Données, Réglages, **Debug**. Bascule via `switchTab(id)` ; chaque onglet a son `render*()`. (Onglet **Saison** + filtre Saison retirés ; les ingrédients gardent `seasonMonths` éditable dans la modale ingrédient, données préservées.)
- **Onglet Debug** = « Notes & Remarques » (bugs/idées à transmettre à Claude) : `state.bugs.items`, rendu par `renderDebug()`, copie presse-papier.
- **Accès** : Google perso, mode partagé (`getSharedMode()`), mode invité lecture seule (`#invite=` dans l'URL).

## Conventions
- Échappement HTML : **`escapeHtml()`** — il n'existe **pas** de `esc()` (piège fréquent en portant du code de « Devis Photo »).
- Composants réutilisables : `createAutocomplete()`, `createChipsInput()`. Modals in-app `showConfirm()`, `openMergeModal()` au lieu de `confirm()`/`prompt()` natifs.
- Inputs texte : `autocomplete/autocorrect/autocapitalize=off`, `spellcheck=false` (anti AutoFill iOS).
- Sidebar : desktop = onglets primaires (Recettes/Courses) visibles, secondaires (Données/Réglages/Debug) dans le menu « Mon compte » ; mobile = tous dans la barre du bas.
- **Icônes** : Lucide SVG inline via `ICONS{}` + `injectIcons()` (rempli au boot, après `detectGuestMode()`). Ajouter une icône avec `data-icon="clé"` sur un élément vide. Pas d'emoji dans la sidebar.
- Hauteurs en `dvh` (gère le clavier iOS).

## Workflows
- **Feature / fix** : éditer le `.html` → tester via serveur local → vérifier à la main les onglets touchés + un cycle save/sync.
- **Vérification — adapter l'effort au risque (3 niveaux)** :
  - *Visuel / CSS / icônes* → l'utilisateur regarde `__preview.html` (cf. ci-dessous). **Pas** de screenshot headless de ma part.
  - *Logique JS* → une seule sonde `dump-dom`/`document.title` ; s'arrêter **dès qu'elle répond** (ne pas escalader vers des screenshots).
  - *Sync / données* → cycle save/reload manuel.
- **Preview local sans login** : `__preview.html` (gitignoré) — iframe sur `index.html?_=<ts>` (cache-buster, fini le « stale »), masque `#login-overlay` → app en mode local. Lancer `py -m http.server 8000`, ouvrir `http://localhost:8000/__preview.html`, **rafraîchir** après chaque modif.
- **Debug headless (pas de console accessible facilement)** : copier le fichier, injecter une sonde qui écrit le résultat dans `document.title`, lancer `chrome --headless=new --dump-dom`, lire le `<title>`. (Méthode utilisée pour traquer le bug `esc`/`escapeHtml`.)
  - **Piège** : injecter la sonde avant le **dernier** `</body>` (`rpartition`), pas un `replace` global — `</body>` apparaît dans des chaînes JS de l'app, et le remplacer partout casse le script principal (symptôme : tout `ICONS`/fonctions deviennent `undefined`, l'app n'affiche plus que le HTML statique).
  - **Screenshot** : `chrome --headless=new --no-sandbox --screenshot=C:/Temp/x.png` (échoue silencieusement vers un chemin OneDrive avec espaces → écrire dans `C:/Temp`). Sidebar masquée par `#login-overlay` hors connexion : injecter `#login-overlay{display:none}` + `.active` sur `#sidebar-user` pour la voir.
- Pas de CI ni de tests auto.

## Pièges connus
- `fbSaveTimer` : remettre à `null` **avant** `fbDocRef.set()` dans le timer, sinon les snapshots cloud entrants restent bloqués.
- `authStateResolved` : flag anti-flash de l'overlay de login au boot — ne pas retirer.
- `fbDocRef` doit être assigné **avant** `renderFirebaseUI()`.
- `.autocomplete-dropdown` est appendé à `document.body` : le listener `click` global de fermeture doit l'ignorer.
- **Code mort Notes** : `#notes-editor`, `initNotesTab()`, `notesUndo/Redo` subsistent mais l'onglet Notes a été **remplacé par Debug** ; ne pas s'y fier.

## Hors-périmètre (ne PAS modifier sans demander)
- `DEFAULT_FIREBASE_CONFIG` (projet Firebase de prod).
- `STORAGE_KEY = 'mhuur_recipes_app_v1'` (changer efface les données locales des utilisateurs).
- `migrateRecipes()` (migration one-shot appelée au `load()`).
- `state.notes` (conservé pour compat même si son UI a disparu).

## Auto-maintenance
Règles que je suis à chaque session sur ce fichier.

- **Auto-alimentation** : en fin de tâche, si une convention non documentée, un piège ou une commande non triviale a été découvert → l'ajouter ici en 1-2 lignes max.
- **Critère d'ajout strict** : une info entre dans ce fichier seulement si (a) non déductible du code en < 30 s, **et** (b) utile dans une future session. Sinon, ne rien écrire.
- **Diagnostic périodique** : tous les ~10 commits, ou si le fichier dépasse 300 lignes / ~4000 tokens, relancer un diagnostic (sections obsolètes/redondantes/triviales) et proposer un nettoyage.
- **Nettoyage** : supprimer sans hésiter l'obsolète, le redondant, le trivial. Court et juste > long et flou.
- **Format** : phrases courtes, listes à puces. Pas de « il est important de noter que ».

## Efficacité
Méthodes pour aller vite et juste sur ce projet.

- **Lecture ciblée** : `grep`/`glob` avant `read`. Sur ce fichier unique de ~7600 lignes, ne jamais lire en entier — repérer la zone puis lire ~50 lignes autour.
- **Outils projet** : pas de linter/formatter/test auto. Avant de déclarer une tâche finie → vérif manuelle (onglets touchés + un cycle save/sync) ; pour un doute JS, sonde headless (cf. Workflows).
- **Économie de tokens** : résumer plutôt que citer ; ne pas réafficher de gros blocs sans nécessité ; grouper les modifs liées en un seul tour.
- **Veille MCP & skills** : ~1×/semaine en usage actif, vérifier si un nouveau MCP server ou une skill Anthropic réduirait le coût/la qualité sur les tâches récurrentes ici. Si oui, le proposer.
- **Audit trimestriel** : ~tous les 3 mois, proposer une revue — quelles règles de ce fichier ralentissent, quels nouveaux outils existent côté Claude Code.
