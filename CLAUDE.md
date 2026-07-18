# CLAUDE.md

Guide pour Claude Code sur ce projet.

## Projet
- App de gestion de **recettes** (usage perso/familial) : recettes, liste de courses, ingrédients de saison.
- Multi-comptes via partage Firestore + mode invité lecture seule.
- État : **en prod**, utilisée au quotidien sur mobile et desktop.

## Stack & versions
- **Pas de build/bundler/npm.** 3 fichiers de code, chargés dans cet ordre : `styles.css` → `icons.js` → le `<script>` inline d'`index.html`.
- Vanilla JS ; CSS clair **« Sylva »** (forêt, verre dépoli) : tokens `--green-*`/`--mist-*`/`--sun-*` + **alias hérités** (`--bg`, `--primary`, `--surface`…) pointés vers Sylva — les styles inline du JS s'adaptent via ces alias. Polices Google Bricolage Grotesque (titres) + Manrope (texte) + JetBrains Mono. Fond photo `assets/forest-bg.jpg` (cache immutable : **renommer** le fichier si on change l'image). Maquette source : `Recette Sylva - autonome.html` (bundle artifact, gitignoré + ignoré au deploy).
- CDN dans `<head>` : Firebase compat **10.12.5** (app/auth/firestore), SheetJS **xlsx 0.18.5** (import Excel).
- Données : `localStorage` + sync temps réel Firestore.

## Fichiers du dossier
- `index.html` — balisage + **tout le JS applicatif** (~6 300 lignes).
- `styles.css` — toute la CSS (~2 160 lignes). Thème + responsive `@media (max-width:768px)`.
- `icons.js` — `_ICO`/`ICONS`/`injectIcons`, **script classique** (pas un module : les `const` top-level restent visibles depuis `index.html`). Chargé **avant** le script principal.
- `tools/smoke.py` — test de fumée (cf. Commandes). Non déployé (`firebase.json` → `ignore: tools/**`).
- `manifest.webmanifest`, `sw.js`, `icons/` — **PWA** (installable + offline). `sw.js` : stale-while-revalidate shell/CDN, **bypass total Firestore/Auth** ; bumper `CACHE_VERSION` à chaque déploiement, et **ajouter tout nouveau fichier servi à `PRECACHE_URLS`**. Icônes = `chef-hat` Lucide crème sur vert forêt ; source vectorielle = `icons/icon.svg`, PNG régénérables par capture Chrome headless (`--screenshot --window-size=NxN` vers `C:/Temp`).
- `index - <timestamp>.html` (titre « Devis Photo ») — **autre outil**, gardé en local comme **référence de design** (sidebar, menu « Signaler un bug ») ; **gitignored** (hors repo). Ne pas le confondre avec l'app.

## Commandes
- **Aucun build / install / lint.** Un seul test : `py tools/smoke.py` (Chrome headless, sert le dossier en HTTP local). Code 0 = OK. Vérifie : 0 erreur JS, `ICONS` chargé, aucun `[data-icon]` vide, `styles.css` appliquée, les 4 `render*` définies. **À lancer avant chaque `firebase deploy`** (`py tools/smoke.py && firebase deploy --only hosting`).
- **Dépôt git lié** : ce dossier est un clone de `github.com/mhuur/Recette` (branche `main`). Workflow : éditer → `git add/commit/push` direct (le dossier vit dans OneDrive, comme le projet todolist).
- **Déploiement prod ≠ git push** : `git push` ne met RIEN en ligne. Le site est servi par **Firebase Hosting** : `firebase deploy --only hosting` (et `,firestore:rules` si les règles changent). CLI déjà authentifiée (`saintilan.romain@gmail.com`, projet `mes-recettes-ff138`). Toujours **bumper `CACHE_VERSION` dans `sw.js`** sinon la PWA installée garde l'ancien code.
- **Nouveau fichier servi** = 3 endroits : `PRECACHE_URLS` (`sw.js`), en-tête `Cache-Control: no-cache` (`firebase.json`, **avant** la règle `/icons/**`), et la balise dans `index.html`.
- **OneDrive crée des copies de conflit** « `nom (2).ext` » — ignorées via `.gitignore` (`* (2).*`). Ne pas les committer.
- Test local : `py -m http.server 8000` dans le dossier → `http://localhost:8000/index.html`.
- Le **login Google exige `http://localhost`** (échoue en `file://`).

## Architecture (fichier Recettes)
- Ordre interne : `<head>` CDN + `<link styles.css>` → `<body>` (sidebar + onglets + modals) → `<script src="icons.js">` → `<script>` principal (~5 600 lignes, une seule portée globale : ~160 fonctions, ~60 globales).
- **État unique** `state` : `recipes`, `ingredients`, `units`, `ingredientTypes`, `ingredientFamilies`, `mealTypes`, `filters`, `notes`, `bugs`, sélection… IDs via `uid()`.
- **Persistance** : `save()` = localStorage + push Firestore débouncé (5 s) ; `saveLocal()` = local seul (filtres/UI).
- **Sync** : `fbDocRef` → `users/{uid}/app/data` (perso) ou `sharedData/{espace}` (partagé) ; `onSnapshot` temps réel ; `applyCloudData()` applique le cloud.
- **Écran Recettes = direction 2a** (handoff `design_handoff_recettes_2a/`, 2026-07-18 ; README + maquette hi-fi = référence). **Une seule barre de commande** (`.topbar`, verre radius 18) : marque + compteur, recherche, Filtres, Trier, sélection, séparateur, Panier, Claude, Ajouter, avatar. Les contrôles propres aux recettes portent `.cmd-recipes-only` (masqués hors onglet Recettes via `body:not(:has(#tab-recipes.active))`). Plus de `.toolbar`. **Cadre arrondi** = `.app-layout` (radius 24, padding 22, max-width 1800) ; le **fond forêt est peint DANS le cadre** (`.app-layout::before` photo + `::after` voile, opacité/cadrage via Apparence) ; hors cadre = dégradé clair. Les pseudos sont en **`position:fixed`** calés sur le viewport (géométrie = marges du cadre) : en `absolute`, `cover` se calcule sur la hauteur du CONTENU et l'image part en ultrazoom dès que la liste est longue — invisible avec un jeu de test court, criant avec 382 recettes. Pas d'`overflow:hidden` sur `.app-layout` (casserait les sticky) : le radius est porté par les pseudos. `smoke.py` cherche la photo sur `.app-layout::before'. **3 colonnes** `.recipes-layout` (gap 16) : filtres 224 · liste `flex:1` · détail 392. **Courses = tiroir latéral** (`body.cart-open`, `openCartDrawer()`). **Debug fusionné dans Réglages**. Onglets : `tab-recipes`, `tab-data`, `tab-settings`.
- **Défilement (≥1280px)** : la page ne scrolle pas (`html,body{overflow:hidden}`, cadre = hauteur de fenêtre). Seul `#recipes-container` défile ; barre, rail, `.recipe-list-head` et détail sont figés. Les autres onglets scrollent via `main` (`overflow-y:auto`, coupé seulement quand `#tab-recipes` est actif) — ne pas remettre `overflow:hidden` sur `main` sans cette condition, sinon Données/Réglages deviennent inaccessibles.
- **Liste dense** : `.recipe-list-head` + `.recipe-row` partagent la grille `24px 1fr 92px 56px 128px` (gap 14). Toute nouvelle cellule doit être ajoutée aux DEUX ou masquée (`.recipe-row-tags` est en `display:none`, sinon 6e colonne fantôme).
- **Actions du détail** : **Modifier** + **corbeille rouge** (`#detail-delete-btn` → `deleteRecipeFromMenu`, confirmation `showConfirm`). Le menu ⋮ (`openRecipeMenu`) a été **supprimé** avec sa CSS et sa couche back-guard : ajout aux courses = case à cocher de la liste, duplication retirée de l'UI (`duplicateRecipe()` subsiste sans appelant).
- **Détail permanent** ≥1280px : `isDetailPermanent()`, `ensureDetailSelection()` (appelée en fin de `renderRecipes()`) sélectionne la 1re recette filtrée ; `closeRecipeDetail()` est inopérant dans ce mode. Corps **empilé** (`.recipe-detail-cols` en flex column) : les 2 colonnes du handoff coupaient les libellés dans 392px — choix utilisateur, prioritaire sur la maquette.
- **Bouton retour Android** : `BACK_LAYERS` + `initBackGuard()` (fin du script, avant l'init). Chaque couche ouverte (onglet ≠ Recettes, détail, tiroir, filtres, modale, menu) pousse une entrée d'historique fictive ; `popstate` ferme la couche du dessus, une fermeture par l'UI rend l'entrée (`history.go(-n)`). Synchro par un listener `click` (bubble) **+** MutationObserver → une nouvelle couche se branche en ajoutant une entrée à `BACK_LAYERS` (+ l'élément observé si sa classe n'est pas sur `body`), jamais en modifiant les `open*`/`close*`. **Piège** : Chrome Android ignore au retour les entrées poussées hors geste utilisateur — le `pushState` doit rester **synchrone dans le clic** (l'observer seul, en microtask, ne suffit pas ; tout handler qui coupe la propagation doit appeler `syncBackGuard()` lui-même).
- **Deux familles de surfaces** : les **encadrés de fond** (barre, rail, liste, détail, cartes) sont translucides et suivent `--glass-fill(-strong)` ; les **menus flottants** (`.user-menu`, `.sort-popup`, `.recipe-context-menu`, `.autocomplete-dropdown`, filter-sheet en popover) doivent masquer ce qu'ils recouvrent → `--menu-fill` (blanc 98%), **jamais** `--glass-fill*` : à faible opacité et en style « Contour » (flou 0), le contenu dessous reste lisible au travers.
- **Surfaces = tokens, jamais de `rgba()` en dur** : toute carte/barre/panneau doit utiliser `--glass-fill` (ou `-strong`), `--glass-border(-soft)`, `blur(var(--blur-md|lg))`. Reprendre les valeurs littérales d'une maquette (ex. `rgba(255,255,255,.78)`) **débranche silencieusement les réglages Apparence** sur l'écran concerné — symptôme : les curseurs n'ont d'effet que sur certains onglets.
- **Apparence** (Réglages) : fond forêt + style/opacité des encadrés → `localStorage sylva_appearance_v1`, `applyAppearance()` surcharge `--glass-*`, `--blur-*`, `--sylva-bg-*` (préférence par appareil, non synchronisée).
- **Cartes en surimpression = fond forêt visible, pas le texte de l'app** : les encadrés sont translucides. Pour voir le **vrai fond forêt** derrière une carte (et non un aplat) sans que le texte de la liste transparaisse, on garde le scrim **transparent** ET on **masque l'UI derrière** en `visibility:hidden` :
  - Modale (`.modal-overlay`, tous formats) → `body:has(.modal-overlay.active)` masque `.app-layout > *` (le **contenu** du cadre, pas le cadre : il porte le fond forêt) + `.cart-drawer` + `.cart-scrim`.
  - Panneau détail (mode superposé **≤1100px** seulement ; en desktop c'est une colonne, ne pas masquer) → `body.detail-open` masque `.topbar` + `.recipes-main` (siblings du `.recipe-detail`, pas le détail lui-même).
  - Tiroir courses (`body.cart-open`) → masque `.topbar` + `.recipes-main` + `.recipe-detail` + `.detail-scrim`.
  - Le fond forêt (`body::before/after`, fixe) reste peint derrière tout. `--scrim-veil` (dégradé forêt opaque) ne sert plus **que** pour `.filter-sheet-overlay` (mobile). Ne pas remettre un scrim opaque sur détail/modale/tiroir : ça re-cache le fond forêt.
- (Onglet **Saison** + filtre Saison retirés ; les ingrédients gardent `seasonMonths` éditable dans la modale ingrédient, données préservées.)
- **Filtres Chaud/froid et Végétarien** : `temperature` est un **champ de recette** (`'chaud'|'froid'|null`, chips dans la modale) → à maintenir dans l'objet reconstruit par l'enregistrement. `vegetarianOnly` est **calculé** par `isVegetarianRecipe()` : aucun ingrédient rattaché à une famille « Viande »/« Poisson » (`NON_VEG_FAMILIES`) — un ingrédient sans famille passe pour végétarien. Le filtre **Familles est retiré de l'UI** (les familles restent en données, elles alimentent ce calcul) et un filtre persisté est purgé au `load()`.
- **Types de plat** : simples chaînes ; les recettes les référencent **par nom** (`r.mealTypes`) → tout renommage doit propager aux recettes + au filtre actif. `'Aucun'` est **dérivé** (réinjecté par `load()`/`migrateRecipes()`) : exclusif d'un vrai type, ni renommable ni attribuable à la main. Affectation en masse : modale `#meal-recipes-modal`, pilotée par `openCheckAssignDialog(cfg)` — **générique**, partagée par les types de plat (`openMealRecipesDialog`) et les familles d'ingrédients (`openFamilyIngredientsDialog`, bouton `listChecks` sur chaque famille dans Données). Toute modif de cette modale touche les deux : tester les deux.
- **Ajout via Claude** : bouton « Avec Claude » (barre d'outils Recettes) → `#claude-modal`. `buildClaudePrompt()` embarque types de plat + unités existants ; ouverture de `claude.ai/new?q=` (fallback « copier le prompt » au-delà de 7500 car.). Le retour est du **JSON parsé et validé** (`extractJsonObject` + `validateClaudeRecipe`), **jamais `eval()`** : le texte vient de l'extérieur. Champs hors schéma ignorés, `origin` `javascript:` rejetée, `rating` forcé à `null`.
- **Onglet Debug** = « Notes & Remarques » (bugs/idées à transmettre à Claude) : `state.bugs.items`, rendu par `renderDebug()`, copie presse-papier.
- **Accès** : Google perso ; **invité via lien** `#guestAccess=` (collection `accessRequests/{uid}`, champ `guestRole` `viewer`/`editor`) approuvé en **lecture** (CSS `body.guest-mode`) ou **modification** (`body.coeditor-mode` : co-éditeur écrit le carnet du proprio `users/{owner}/app/data`, sync deux-sens). Règle Firestore `isApprovedEditor` (fichier `firestore.rules`, déployé via CLI). L'ancien « mode partagé »/`sharedData` est **retiré de l'UI** ; helpers `getSharedMode`/`getFirebaseDocRef` conservés (routent vers le perso). Le **contexte invité est persisté** (`GUEST_CTX_KEY` localStorage, `persistGuestContext`/`restoreGuestContext`) : sans ça, rouvrir l'app sans le hash `#guestAccess=` (favori, PWA installée) renvoie l'invité sur SON propre carnet vide. **Piège** : une PWA iOS « sur l'écran d'accueil » a un localStorage **isolé** de Safari → l'invité doit cliquer le lien _dans le contexte qui sert l'app_ (au pire, utiliser le lien/favori navigateur plutôt que l'icône installée).

## Conventions
- Échappement HTML : **`escapeHtml()`** ; `esc()` existe comme simple alias (ajouté pour le code porté de « Devis Photo »).
- Composants réutilisables : `createAutocomplete()`, `createChipsInput()`. Modals in-app `showConfirm()`, `openMergeModal()` au lieu de `confirm()`/`prompt()` natifs.
- Inputs texte : `autocomplete/autocorrect/autocapitalize=off`, `spellcheck=false` (anti AutoFill iOS).
- Sidebar : desktop = onglets primaires (Recettes/Courses) visibles, secondaires (Données/Réglages/Debug) dans le menu « Mon compte » ; mobile = tous dans la barre du bas.
- **Icônes** : **zéro emoji dans l'UI** — que du Lucide SVG inline via `ICONS{}` + `injectIcons()` (rempli au boot, après `detectGuestMode()`). Ajouter une icône avec `data-icon="clé"` sur un élément vide ; sur du HTML rendu **après** le boot, soit interpoler `${ICONS.clé}` directement, soit rappeler `injectIcons(container)`. Taille = CSS sur le `svg` enfant (`_ICO` pose `width=18` en dur) ; `.tb-ico` donne un défaut en `em`.
  - Là où un SVG est **impossible** (`<option>`, `placeholder`, `content:` CSS, `confirm()`, `toast()`, texte copié) → texte nu, pas d'emoji. Exception : `::before` peut porter un `mask` CSS (cf. `.autocomplete-item.selected`).
  - Un bouton qui sauve/restaure son libellé doit utiliser `innerHTML`, pas `textContent` (sinon le SVG est détruit).
  - `ICONS` vit dans `icons.js`, chargé avant : plus de zone morte temporelle, utilisable partout.
  - Les `★` de `parseRating()` sont de la **donnée** (cellules Excel), pas de la déco : ne pas les toucher.
- Hauteurs en `dvh` (gère le clavier iOS).

## Workflows
- **Livraison automatique (demandé par l'utilisateur, 2026-07-09)** : à la fin de chaque tâche qui modifie l'app, enchaîner **sans redemander** : bumper `CACHE_VERSION` (`sw.js`) → `git commit` + `push` → `py tools/smoke.py && firebase deploy --only hosting`. Le smoke test est le **dernier verrou avant la prod** : s'il sort ≠ 0, ne pas déployer. Retour arrière = `git revert <sha>` puis redéployer.
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
- `saveRecipe()` **reconstruit** l'objet recette et l'écrase dans `state.recipes`. Il commence par `...previous` : tout nouveau champ doit être ajouté à cet objet, sinon il est effacé à chaque modification (c'était le cas de `createdAt`/`importedFromExcel` avant 2026-07-09).
- Recette : `instructions` (texte, 1 étape par ligne, numérotées à l'affichage) et `notes` (texte libre) sont **hors recherche** (choix utilisateur). Ne pas confondre `recipe.notes` avec `state.notes` (legacy).
- `fbSaveTimer` : remettre à `null` **avant** `fbDocRef.set()` dans le timer, sinon les snapshots cloud entrants restent bloqués.
- **`*/` dans un commentaire de bloc** (ex. écrire `open*/close*`) ferme le commentaire → SyntaxError qui tue **tout** le script inline. Symptôme identique au piège `</body>` : `ICONS` OK mais toutes les fonctions de l'app `undefined`, et `window.onerror` ne l'attrape pas (l'erreur précède la sonde). `py tools/smoke.py` le détecte.
- `authStateResolved` : flag anti-flash de l'overlay de login au boot — ne pas retirer.
- `fbDocRef` doit être assigné **avant** `renderFirebaseUI()`.
- `.autocomplete-dropdown` est appendé à `document.body` : le listener `click` global de fermeture doit l'ignorer.
- **Code mort Notes** : `#notes-editor`, `initNotesTab()`, `notesUndo/Redo` subsistent mais l'onglet Notes a été **remplacé par Debug** (lui-même fusionné dans Réglages) ; ne pas s'y fier.
- **Headless + `--virtual-time-budget` fige les transitions CSS** (le tiroir reste hors écran, `visibility` héritée reste hidden) → pour un screenshot d'état ouvert, injecter `transition:none !important` dans la page de test. Chrome headless impose aussi une **largeur mini ~500px** et **recadre** un `--window-size` plus petit (mobile : capturer à 504px, le media ≤768 s'applique).
- Pas de `transition: all` sur `button` : ça anime `visibility` héritée du tiroir Courses (boutons invisibles).

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
