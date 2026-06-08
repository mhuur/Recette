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
- `index - <timestamp>.html` — titre « 🍳 Mes Recettes », ~7 600 lignes = **l'app Recettes** (le fichier qu'on modifie). Nom horodaté car re-téléchargé ; c'est toujours le plus volumineux / titre Recettes.
- `index - <autre timestamp>.html` — titre « Devis Photo » = **autre outil**, gardé comme **référence de design** (sidebar, menu « Signaler un bug »). Ne pas le modifier ni le confondre.

## Commandes
- **Aucun build / install / lint / test.** On édite le `.html` directement.
- Test local : `py -m http.server 8000` dans le dossier → `http://localhost:8000/<fichier>.html`.
- Le **login Google exige `http://localhost`** (échoue en `file://`).

## Architecture (fichier Recettes)
- Ordre interne : `<head>` CDN → `<style>` (~1900 lignes : thème + responsive `@media (max-width:768px)`) → `<body>` (sidebar + onglets + modals) → `<script>`.
- **État unique** `state` : `recipes`, `ingredients`, `units`, `ingredientTypes`, `ingredientFamilies`, `mealTypes`, `filters`, `notes`, `bugs`, sélection… IDs via `uid()`.
- **Persistance** : `save()` = localStorage + push Firestore débouncé (5 s) ; `saveLocal()` = local seul (filtres/UI).
- **Sync** : `fbDocRef` → `users/{uid}/app/data` (perso) ou `sharedData/{espace}` (partagé) ; `onSnapshot` temps réel ; `applyCloudData()` applique le cloud.
- **Onglets** : Recettes, Courses, Saison, Données, Réglages, **Debug**. Bascule via `switchTab(id)` ; chaque onglet a son `render*()`.
- **Onglet Debug** = « Notes & Remarques » (bugs/idées à transmettre à Claude) : `state.bugs.items`, rendu par `renderDebug()`, copie presse-papier.
- **Accès** : Google perso, mode partagé (`getSharedMode()`), mode invité lecture seule (`#invite=` dans l'URL).

## Conventions
- Échappement HTML : **`escapeHtml()`** — il n'existe **pas** de `esc()` (piège fréquent en portant du code de « Devis Photo »).
- Composants réutilisables : `createAutocomplete()`, `createChipsInput()`. Modals in-app `showConfirm()`, `openMergeModal()` au lieu de `confirm()`/`prompt()` natifs.
- Inputs texte : `autocomplete/autocorrect/autocapitalize=off`, `spellcheck=false` (anti AutoFill iOS).
- Sidebar : desktop = onglets primaires (Recettes/Courses/Saison) visibles, secondaires (Données/Réglages/Debug) dans le menu « Mon compte » ; mobile = tous dans la barre du bas.
- Hauteurs en `dvh` (gère le clavier iOS).

## Workflows
- **Feature / fix** : éditer le `.html` → tester via serveur local → vérifier à la main les onglets touchés + un cycle save/sync.
- **Debug headless (pas de console accessible facilement)** : copier le fichier, injecter une sonde qui écrit le résultat dans `document.title`, lancer `chrome --headless=new --dump-dom`, lire le `<title>`. (Méthode utilisée pour traquer le bug `esc`/`escapeHtml`.)
- Pas de CI ni de tests auto.

## Pièges connus
- `fbSaveTimer` : remettre à `null` **avant** `fbDocRef.set()` dans le timer, sinon les snapshots cloud entrants restent bloqués.
- `authStateResolved` : flag anti-flash de l'overlay de login au boot — ne pas retirer.
- `fbDocRef` doit être assigné **avant** `renderFirebaseUI()`.
- `.autocomplete-dropdown` est appendé à `document.body` : le listener `click` global de fermeture doit l'ignorer.
- `applyCloudData()` : appeler `renderSeasonTab()` inconditionnellement (sinon vide sur mobile après sync).
- **Code mort Notes** : `#notes-editor`, `initNotesTab()`, `notesUndo/Redo` subsistent mais l'onglet Notes a été **remplacé par Debug** ; ne pas s'y fier.

## Hors-périmètre (ne PAS modifier sans demander)
- `DEFAULT_FIREBASE_CONFIG` (projet Firebase de prod).
- `STORAGE_KEY = 'mhuur_recipes_app_v1'` (changer efface les données locales des utilisateurs).
- `migrateRecipes()` (migration one-shot appelée au `load()`).
- `state.notes` (conservé pour compat même si son UI a disparu).
