# CLAUDE.md

Guide pour Claude Code sur ce projet.

## Projet
- App de gestion de **recettes** (usage perso/familial) : recettes, liste de courses.
- Multi-comptes via partage Firestore + mode invité lecture seule.
- État : **en prod**, utilisée au quotidien sur mobile et desktop.

## Stack & fichiers
- **Pas de build/bundler/npm.** 3 fichiers de code, chargés dans cet ordre : `styles.css` → `icons.js` → le `<script>` inline d'`index.html`.
- `index.html` (~6 300 l.) = balisage + tout le JS. `styles.css` (~2 160 l.) = toute la CSS, responsive `@media (max-width:768px)`. `icons.js` = `_ICO`/`ICONS`/`injectIcons`, **script classique** (pas un module : les `const` top-level restent visibles depuis `index.html`).
- Vanilla JS ; CSS claire **« Sylva »** (forêt, verre dépoli) : tokens `--green-*`/`--mist-*`/`--sun-*` + **alias hérités** (`--bg`, `--primary`, `--surface`…) pointés vers Sylva — les styles inline du JS s'adaptent via ces alias. Polices Bricolage Grotesque (titres) + Manrope (texte) + JetBrains Mono. Fond `assets/forest-bg.jpg` (cache immutable : **renommer** le fichier si on change l'image).
- CDN dans `<head>` : Firebase compat **10.12.5** (app/auth/firestore), SheetJS **xlsx 0.18.5** (import Excel).
- Données : `localStorage` + sync temps réel Firestore.
- **PWA** (`manifest.webmanifest`, `sw.js`, `icons/`) : stale-while-revalidate shell/CDN, **bypass total Firestore/Auth**. Bumper `CACHE_VERSION` à chaque déploiement et **ajouter tout nouveau fichier servi à `PRECACHE_URLS`**. Icônes = flamme façon Calcifer sur bûches (fan art maison, usage perso) ; source `icons/icon-v3.svg`, déclinaisons `icon-v3-{192,512,apple,maskable-512}.png`.
  - **Fond transparent** pour le SVG et les PNG `any` (viewBox resserré sur le dessin, faute de carré coloré pour le porter). ⚠️ Mais **`apple-touch-icon` et le `maskable` gardent un fond plein** (`#f6faf7`) : iOS remplit la transparence en **noir** et Android rend mal un maskable non plein. Capture transparente = `--default-background-color=00000000` ; côté redimensionnement, créer le `Bitmap` en `Format32bppArgb` sinon l'alpha est perdu.
  - ⚠️ **`/icons/**` est en `immutable` 1 an** (`firebase.json`) : changer une icône = **renommer le fichier** (suffixe `-v3`…) et mettre à jour les 3 points (`manifest.webmanifest`, balises d'`index.html`, `PRECACHE_URLS`), sinon les appareils gardent l'ancienne indéfiniment.
  - ⚠️ **Ne jamais capturer un PNG < 500px en headless** : Chrome impose une largeur mini et rend une image tronquée (c'est ainsi qu'`icon-192`/`apple-touch-icon` étaient devenus des rectangles blancs, d'où l'icône générique du navigateur sur mobile). Capturer en **512** puis réduire — `System.Drawing` en PowerShell (`Add-Type -AssemblyName System.Drawing`, `InterpolationMode HighQualityBicubic`) fait ça sans dépendance.
  - Le PNG `maskable` doit garder ~20% de marge (Android rogne) : le SVG est régénéré avec le dessin à `scale(0.74)` sur un fond plein cadre.
- Non déployés : `tools/smoke.py` (`ignore: tools/**`), `data/saisons.md` (calendrier de saison conservé, `data/**`).
- Références locales gitignorées : `Recette Sylva - autonome.html` (maquette source Sylva) et `index - <timestamp>.html` (titre « Devis Photo », **autre outil**, gardé pour son design — ne pas le confondre avec l'app).

## Commandes
- **Aucun build / install / lint.** Un seul test : `py tools/smoke.py` (Chrome headless, sert le dossier en HTTP local). Code 0 = OK. Vérifie : 0 erreur JS, `ICONS` chargé, aucun `[data-icon]` vide, `styles.css` appliquée, les 4 `render*` définies. **À lancer avant chaque `firebase deploy`.**
- **Dépôt git lié** : clone de `github.com/mhuur/Recette` (branche `main`). Éditer → `git add/commit/push` direct.
- **Déploiement prod ≠ git push** : `git push` ne met RIEN en ligne. Le site est servi par **Firebase Hosting** : `firebase deploy --only hosting` (`,firestore:rules` si les règles changent). CLI déjà authentifiée (`saintilan.romain@gmail.com`, projet `mes-recettes-ff138`). Toujours **bumper `CACHE_VERSION`** sinon la PWA installée garde l'ancien code.
- **Nouveau fichier servi** = 3 endroits : `PRECACHE_URLS` (`sw.js`), en-tête `Cache-Control: no-cache` (`firebase.json`, **avant** la règle `/icons/**`), balise dans `index.html`.
- **OneDrive crée des copies de conflit** « `nom (2).ext` » — ignorées via `.gitignore`. Ne pas les committer.
- Test local : `py -m http.server 8000` → `http://localhost:8000/index.html`. Le **login Google exige `http://localhost`** (échoue en `file://`).

## Architecture

### Noyau
- Ordre interne : `<head>` CDN + `<link styles.css>` → `<body>` (sidebar + onglets + modals) → `<script src="icons.js">` → `<script>` principal (~5 600 l., une seule portée globale : ~160 fonctions, ~60 globales).
- **État unique** `state` : `recipes`, `ingredients`, `units`, `ingredientTypes`, `ingredientFamilies`, `mealTypes`, `filters`, `notes`, `bugs`, sélection… IDs via `uid()`.
- **Persistance** : `save()` = localStorage + push Firestore débouncé (5 s) ; `saveLocal()` = local seul (filtres/UI).
- **Sync** : `fbDocRef` → `users/{uid}/app/data` ; `onSnapshot` temps réel via `attachSnapshotListener()` (**une seule** implémentation, partagée propriétaire / co-éditeur) ; `applyCloudData()` applique le cloud.
  - ⚠️ **Un snapshot ignoré est perdu** : Firestore ne redélivre pas un document inchangé. D'où `fbPendingSnapshot` — pendant la fenêtre de push (`FB_PUSH_DELAY`, 1,5 s) on met la version distante **de côté**, on ne la jette pas ; elle est rejouée si le push n'a finalement rien écrit (`pushToCloud()` renvoie un booléen).
  - Seul `snap.metadata.hasPendingWrites` doit filtrer l'écho de nos propres écritures. Un drapeau « ignorer le prochain snapshot » avalait indifféremment celui d'un autre appareil → co-éditeur invisible jusqu'au `visibilitychange`.
  - ⚠️ **Reste en last-write-wins** : `pushToCloud()` réécrit le document **entier**. Deux appareils qui modifient en même temps = le dernier écrase l'autre (typiquement `selectedRecipeIds`). Une fusion champ par champ n'a pas été faite.
- Onglets : `tab-recipes`, `tab-data`, `tab-settings` (Debug fusionné dans Réglages).
- **Réglages = sous-onglets** (`.settings-subnav` / `.settings-pane`, `setSettingsPane()`, choix persisté par appareil `sylva_settings_pane_v1`) : Apparence (défaut) · Partage · Remarques. « Partage » n'est monté que connecté (`syncSettingsShareTab()`, appelée des deux branches de `renderFirebaseUI()`) ; une nouvelle rubrique = un bouton + un `.settings-pane` de même `data-pane`.
- **Pas de carte « Mon compte »** : identité, statut de synchro et déconnexion vivent **uniquement** dans le menu de l'avatar (`#user-menu`, `sidebar-user-avatar`, `sidebar-sync-status`, `menu-sign-out`). Push/pull manuels, sauvegarde `.json` et « modifier la config Firebase » retirés en juillet 2026 (jamais utilisés ; le vrai export ré-importable est Données › Export JSON). `openFirebaseModal()` n'a plus qu'un appelant : `mobile-login-btn` quand aucune config n'est stockée.

### Écran Recettes (direction 2a — handoff `design_handoff_recettes_2a/`, référence)
- **Une seule barre de commande** `.topbar` (verre, radius 18) : marque + compteur, recherche, Filtres, séparateur, Courses, Claude, Ajouter, avatar. Trier et « sélection uniquement » y sont **masqués ≥769px** (ils vivent dans l'en-tête de colonnes). Les contrôles propres aux recettes portent `.cmd-recipes-only`. Plus de `.toolbar`.
- **Cadre arrondi** = `.app-layout` (radius 24, padding 22, max-width 1800) ; le **fond forêt est peint DANS le cadre** (`.app-layout::before` photo + `::after` voile, réglés par Apparence) ; hors cadre = dégradé clair.
  - ⚠️ Les pseudos sont en **`position:fixed`** calés sur le viewport. En `absolute`, `cover` se calcule sur la hauteur du CONTENU → ultrazoom dès que la liste est longue (invisible avec un jeu de test court, criant avec 382 recettes).
  - ⚠️ Pas d'`overflow:hidden` sur `.app-layout` (casserait les sticky) : le radius est porté par les pseudos. `smoke.py` cherche la photo sur `.app-layout::before`.
- **3 colonnes** `.recipes-layout` (gap 16) : filtres 224 · liste `flex:1` · détail 392.
- **Défilement ≥1280px** : la page ne scrolle pas (`html,body{overflow:hidden}`). Seul `#recipes-container` défile. ⚠️ Les autres onglets scrollent via `main` (`overflow-y:auto`, coupé **uniquement** quand `#tab-recipes` est actif) — remettre `overflow:hidden` sur `main` sans cette condition rend Données/Réglages inaccessibles.
- **Liste dense** : `.recipe-list-head` + `.recipe-row` partagent la grille `24px 1fr 92px 56px 128px` (gap 14). ⚠️ Toute nouvelle cellule va dans les DEUX ou est masquée (`.recipe-row-tags` est en `display:none`, sinon 6e colonne fantôme). L'en-tête porte les contrôles : `.rlh-sort` sur Recette/Note/Pers./Temps (1er clic croissant, 2e décroissant — `SORT_COLUMNS` + `syncSortHead()`), `.rlh-sel` au-dessus des cases. L'en-tête étant **masqué ≤768px**, les équivalents restent dans la barre du haut → classe partagée `.js-selection-only` (câbler toutes les occurrences, pas un id).
- **Détail** : actions = **Modifier** + corbeille rouge (`#detail-delete-btn` → `deleteRecipeFromMenu`, confirmation `showConfirm`). Pas de menu ⋮ ; ajout aux courses = case à cocher de la liste. `duplicateRecipe()` subsiste sans appelant.
- **Détail permanent ≥1280px** : `isDetailPermanent()`, `ensureDetailSelection()` (fin de `renderRecipes()`) sélectionne la 1re recette filtrée ; `closeRecipeDetail()` est inopérant. Corps **empilé** (`.recipe-detail-cols` en flex column) : les 2 colonnes du handoff coupaient les libellés dans 392px — choix utilisateur, prioritaire sur la maquette.
- **Courses = tiroir latéral** (`body.cart-open`, `openCartDrawer()`) ; **≥1100px = carte centrée de 880px** en fondu (ni 440px, ni pleine largeur — choix utilisateur). Corps en grille `400px | 1fr` : outils collants à gauche (`.cart-side`), liste au centre (`.cart-main`) sur une seule colonne — les outils sont plus larges car les noms de recettes sont longs. `.serving-name` **passe à la ligne** (aucune largeur ne suffisait). Sous 1100px, tiroir de droite inchangé.
- **Suggestions = 2e tiroir** (`body.sugg-open`, `openSuggestDrawer()`, bouton « Idées » de la barre) : même ossature CSS que Courses (scrim transparent, UI derrière en `visibility:hidden`, carte centrée de 620px ≥1100px), inscrit dans `BACK_LAYERS`.
  - Tirage **pondéré sans remise** (`suggestionWeight()` / `pickSuggestions()`), jamais uniforme : note (9+ → ×5, sous 6 → ×0.5, non notée → 3 « à tester »), ×1.5 si jamais retenue, décote de récence `SUGG_RECENCY`, et pénalité de variété si un type de plat ou une famille viande/poisson est déjà tiré. Poids planchonné à 0.02 — avec un carnet étroit tout doit rester tirable.
  - Puise dans `suggPool()` = `suggRailFiltered()` (rail seul), ou tout le carnet si `suggIgnoreFilters` : **les filtres du rail s'appliquent par défaut**. ⚠️ **Pas `getFilteredRecipes()`** : `recipeMatches()` y applique aussi la **recherche** de la barre du haut et `selectedOnly`, que le rail ne compte pas dans « filtres actifs » et que la barre masquée rend invisibles tiroir ouvert → une recherche oubliée restreignait le tirage sans que rien ne l'indique (d'où `{ search: true, selected: true }` en `skip`).
  - Le tiroir **ne se ferme pas au clic extérieur** (contrairement à Courses) : le tirage en cours n'est pas récupérable. Croix, Échap, bouton retour uniquement.
  - **Le rail reste manipulable tiroir ouvert** : `.sugg-scrim` est en **`pointer-events:none`** (il ne ferme plus rien, il ne sert qu'à couvrir le fond). ⚠️ Un `z-index` sur le rail **ne suffit pas** — il est enfermé dans le contexte d'empilement du cadre, donc sous un voile en `position:fixed`, quel que soit son z-index. `suggSyncWithFilters()`, appelée en fin de `renderRecipes()`, rejoue le tirage **seulement** si l'empreinte des filtres a changé.
  - Desktop : carte de 760px à **hauteur réglée sur le contenu** (`height:auto; max-height:min(80vh,820px)`, centrée par `translateY(-50%)`), corps en grille **`300px | 1fr`** avec `grid-template-areas` — outils et bouton d'ajout à gauche, liste au centre, comme le tiroir Courses. ⚠️ `.sugg-foot` suit `.sugg-main` **dans le DOM** (ordre voulu en mobile : outils, liste, bouton) ; c'est la grille qui le remonte à gauche en desktop.
  - Badge **« à tester »** réservé aux recettes **sans note ET sans `lastPickedAt`**. L'ancien « jamais faite » sur toute recette sans `lastPickedAt` était faux : ce champ ne remonte qu'à l'arrivée des suggestions, alors qu'une note prouve que la recette a déjà été cuisinée. Le sous-titre les chiffre (« 7 recettes où piocher sur 382 · filtres du rail appliqués ») et un bouton bascule les ignore — un filtre ingrédient oublié réduisait le tirage à 7 recettes toutes identiques sans que la cause soit lisible. `suggIgnoreFilters` retombe à `false` à chaque ouverture : le rail reste la référence.
  - **Clic sur une carte = aperçu dans le tiroir** (`body.sugg-preview-open`, `suggPreviewHtml()`, lecture seule), pas un renvoi vers l'onglet Recettes qui ferait perdre le tirage en cours. Couche inscrite dans `BACK_LAYERS` **après** celle du tiroir (le retour ferme l'aperçu d'abord). Le HTML réutilise les classes du panneau détail (`recipe-section`, `ingredients-list`, `recipe-steps`) pour hériter du style.
  - ⚠️ Le remplacement d'une carte doit **exclure la recette refusée** du tirage, sinon elle peut être resservie aussitôt et le clic paraît sans effet.
- **`lastPickedAt`** (champ de recette, horodatage) : posé par `markRecipePicked()` quand une recette entre dans la sélection — **deux appelants** : la case de la liste et le bouton « Ajouter à ma sélection ». C'est la seule mémoire de l'anti-répétition ; synchronisé (donc partagé avec le co-éditeur, contrairement à un historique local). Absent = « jamais faite ».
- **Coches de courses** : `state.checkedShoppingItems` stocke des clés **stables** (`ingId|unitId`, `ingId|measure|famille`, `manual|id`) sans lien avec la recette d'origine → `pruneCheckedShoppingItems()` (appelée par `renderShopping()`) retire celles absentes de la liste courante, sinon vider la sélection puis cocher d'autres recettes ressort les mêmes ingrédients pré-cochés. ⚠️ L'appel doit rester **avant** le retour anticipé « liste vide » de `renderShopping()` — c'est précisément le cas à purger. Garde-fou : sélection non vide + 0 article = données pas encore chargées, on ne purge pas.

### Surfaces & superpositions
- **Deux familles** : les **encadrés de fond** (barre, rail, liste, détail, cartes) sont translucides → `--glass-fill(-strong)`. Les **menus flottants** (`.user-menu`, `.sort-popup`, `.recipe-context-menu`, `.autocomplete-dropdown`, filter-sheet en popover) doivent masquer ce qu'ils recouvrent → `--menu-fill` (blanc 98 %), **jamais** `--glass-fill*` : à faible opacité en style « Contour » (flou 0), le contenu dessous reste lisible au travers.
- ⚠️ **Toujours des tokens, jamais de `rgba()` en dur** : `--glass-fill(-strong)`, `--glass-border(-soft)`, `blur(var(--blur-md|lg))`. Recopier une valeur littérale de maquette **débranche silencieusement les réglages Apparence** sur l'écran concerné (symptôme : les curseurs n'agissent que sur certains onglets).
- **Apparence** (Réglages) : fond forêt + style/opacité des encadrés → `localStorage sylva_appearance_v1` ; `applyAppearance()` surcharge `--glass-*`, `--blur-*`, `--sylva-bg-*`. Préférence par appareil, non synchronisée.
- **Cartes en surimpression = fond forêt visible, pas le texte de l'app.** Scrim **transparent** + UI derrière masquée en `visibility:hidden` :
  - Modale → `body:has(.modal-overlay.active)` masque `.app-layout > *` (le **contenu** du cadre, pas le cadre : il porte le fond) + `.cart-drawer` + `.cart-scrim`.
  - Détail (mode superposé **≤1100px** seulement ; en desktop c'est une colonne, ne pas masquer) → `body.detail-open` masque `.topbar` + `.recipes-main`.
  - Tiroir courses → `body.cart-open` masque `.topbar` + `.recipes-main` + `.recipe-detail` + `.detail-scrim`.
  - ⚠️ Ne pas remettre un scrim opaque sur détail/modale/tiroir : ça re-cache le fond forêt. `--scrim-veil` ne sert plus **que** pour `.filter-sheet-overlay` (mobile).

### Filtres
- **Ordre du rail** : Ingrédients · Type de plat · Note · Chaud/froid · Régime · Temps. Plus de section « Avancé » ; `createFacetSelect()` n'a plus d'appelant.
- **Sections à hauteur constante** : une section qui grandit selon la sélection décale tout ce qui est en dessous (plainte utilisateur). Ingrédients et Type de plat sont donc des **boutons d'une ligne** (libellé ellipsé) + **menus flottants** (enfants directs de `body`, `position:fixed`, `--menu-fill`), pas des nuages de chips.
  - Un seul composant : `createFilterMenu(cfg)`, instances dans `FILTER_MENUS` (un seul menu ouvert à la fois). `cfg.stateOf()` renvoie `''｜'on'｜'exc'` → 2 états pour les types, **3 pour les ingrédients** (requis + → interdit − → retiré).
  - Les menus listent **tout**, options inatteignables grisées (`.off`) plutôt que retirées : la liste ne saute pas sous le doigt.
  - ⚠️ Menus appendus à `body` → les exclure du clic-extérieur du popover de filtres **et** les inscrire dans `BACK_LAYERS` + l'observer (sélecteur `.filter-menu`, pas un id).
  - **Menu ouvert = fond figé** comme un `<select>` natif : `wheel`/`touchmove` hors du menu sont `preventDefault()`. Sa liste garde `overscroll-behavior:contain`. Deux alternatives déjà rejetées par l'utilisateur : suivre son ancre (se colle en haut quand le bouton sort du champ) et fermer au scroll (disparaît sous la molette).
- **Sélection multiple** : dans un groupe les valeurs s'**unissent** (OU), les groupes se croisent (ET). `ratingSel[]` (`'unrated'` + seuils 6/7/8/9 ; plusieurs seuils → le plus permissif) et `temperatures[]`. Temps (`prepMax`/`cookMax`) reste **exclusif** (un OU de « ≤ X » revient au plus grand).
- **Ingrédients requis** : `ingredientsMode` (`'any'` défaut = au moins un · `'all'` = tous), basculeur dans l'en-tête du menu. L'ancien ET systématique rendait « n'importe quelle tomate » impossible (13 entrées tomate → cocher 3 variantes = 0 recette). Les **interdits** restent un ET-NON.
- ⚠️ **Nouveau champ de filtre = 4 endroits** : état initial, secours de `load()`, migration, `resetAllFilters()`.
- **Chaud/froid** : `temperature` est un **champ de recette** (`'chaud'|'froid'|null`) → à maintenir dans l'objet reconstruit par `saveRecipe()`.
- **Végétarien / pescarien** : **calculés** depuis les familles (`recipeHasFamilies`) — végétarien = ni `MEAT_FAMILIES` ni `FISH_FAMILIES` ; pescarien = pas de `MEAT_FAMILIES`. UI = **bulles exclusives** (`#filter-diet .chip-toggle`) : végétarien ⊂ pescarien, donc les deux ensemble = Végétarien seul → `buildFilterBar()` normalise un état persisté qui aurait les deux. Le lien ingrédient→famille est `ing.familyIds` (**tableau**), pas `familyId`. Un ingrédient **sans famille** passe pour compatible avec les deux → la justesse dépend du classement. Le filtre **Familles est retiré de l'UI** (les familles restent en données) ; un filtre persisté est purgé au `load()`.

### Données & modales
- **Types de plat** : simples chaînes, référencées **par nom** (`r.mealTypes`) → tout renommage doit propager aux recettes + au filtre actif. `'Aucun'` est **dérivé** (réinjecté par `load()`/`migrateRecipes()`) : exclusif d'un vrai type, ni renommable ni attribuable à la main.
- **Affectation en masse** : modale `#meal-recipes-modal` pilotée par `openCheckAssignDialog(cfg)` — **générique**, 3 usages : types de plat (`openMealRecipesDialog`), familles d'ingrédients (`openFamilyIngredientsDialog`, bouton `listChecks` dans Données), chaud/froid (`openTemperatureRecipesDialog`, valeur **exclusive**). `cfg.sub(item)` = tableau de libellés rendus en chips ; `cfg.meta(item)` = 2e ligne (branchée sur `recipeOriginInfo` pour les dialogues à base de recettes, absente pour les familles qui listent des ingrédients). ⚠️ La ligne est un `<label>` : tout élément interactif ajouté doit `stopPropagation()`. Toute modif touche les trois usages — les tester tous.
- **Saisons** : mode saison **retiré le 2026-07-18** (trop de cas particuliers : conserves, formes sèches, produits de garde). Le champ `seasonMonths` (tableau 1-12) reste sur l'ingrédient, éditable dans sa modale et affiché dans Données. Code récupérable au commit `1af9fd0` ; calendrier dans `data/saisons.md`. Si on y revient : c'est le *type déclaré* de l'ingrédient qui écarte conserves et formes sèches, aucun rapprochement par nom n'y arrive.
- **Ajout via Claude** : bouton « Avec Claude » → `#claude-modal`. `buildClaudePrompt()` embarque types de plat + unités ; ouverture de `claude.ai/new?q=` (fallback « copier le prompt » au-delà de 7500 car.). ⚠️ Le retour est du **JSON parsé et validé** (`extractJsonObject` + `validateClaudeRecipe`), **jamais `eval()`** : le texte vient de l'extérieur. Champs hors schéma ignorés, `origin` `javascript:` rejetée, `rating` forcé à `null`.
- **Debug** = « Notes & Remarques » (`state.bugs.items`, `renderDebug()`, copie presse-papier).

### Navigation & accès
- **Bouton retour Android** : `BACK_LAYERS` + `initBackGuard()` (fin du script, avant l'init). Chaque couche ouverte (onglet ≠ Recettes, détail, tiroir, filtres, modale, menu) pousse une entrée d'historique fictive ; `popstate` ferme la couche du dessus, une fermeture par l'UI rend l'entrée (`history.go(-n)`). Synchro par listener `click` (bubble) **+** MutationObserver → une nouvelle couche se branche en ajoutant une entrée à `BACK_LAYERS`, jamais en modifiant les `open`/`close`.
  - ⚠️ Chrome Android ignore au retour les entrées poussées hors geste utilisateur : le `pushState` doit rester **synchrone dans le clic** (l'observer seul, en microtask, ne suffit pas ; tout handler qui coupe la propagation doit appeler `syncBackGuard()`).
- **Accès** : Google perso ; **invité via lien** `#guestAccess=` (collection `accessRequests/{uid}`, champ `guestRole` `viewer`/`editor`) approuvé en lecture (`body.guest-mode`) ou modification (`body.coeditor-mode` : le co-éditeur écrit le carnet du proprio `users/{owner}/app/data`, sync deux-sens). Règle Firestore `isApprovedEditor` (`firestore.rules`, déployé via CLI). L'ancien « mode partagé »/`sharedData` est retiré de l'UI ; `getSharedMode`/`getFirebaseDocRef` conservés (routent vers le perso).
  - ⚠️ Le **contexte invité est persisté** (`GUEST_CTX_KEY`, `persistGuestContext`/`restoreGuestContext`) : sans ça, rouvrir l'app sans le hash (favori, PWA) renvoie l'invité sur SON carnet vide.
  - ⚠️ Une PWA iOS « sur l'écran d'accueil » a un localStorage **isolé** de Safari → l'invité doit cliquer le lien _dans le contexte qui sert l'app_.

## Conventions
- Échappement HTML : **`escapeHtml()`** ; `esc()` est un simple alias (code porté de « Devis Photo »).
- Composants réutilisables : `createAutocomplete()`, `createChipsInput()`. Modals in-app `showConfirm()`, `openMergeModal()` au lieu de `confirm()`/`prompt()` natifs.
- Inputs texte : `autocomplete/autocorrect/autocapitalize=off`, `spellcheck=false` (anti AutoFill iOS).
- Sidebar : desktop = onglets primaires (Recettes/Courses) visibles, secondaires (Données/Réglages/Debug) dans le menu « Mon compte » ; mobile = tous dans la barre du bas.
- Hauteurs en `dvh` (gère le clavier iOS).
- **Icônes : zéro emoji dans l'UI** — que du Lucide SVG inline via `ICONS{}` + `injectIcons()` (rempli au boot, après `detectGuestMode()`). Ajouter `data-icon="clé"` sur un élément vide ; sur du HTML rendu **après** le boot, interpoler `${ICONS.clé}` ou rappeler `injectIcons(container)`. Taille = CSS sur le `svg` enfant (`_ICO` pose `width=18` en dur) ; `.tb-ico` donne un défaut en `em`.
  - Là où un SVG est **impossible** (`<option>`, `placeholder`, `content:` CSS, `confirm()`, `toast()`, texte copié) → texte nu, pas d'emoji. Exception : `::before` peut porter un `mask` CSS.
  - Un bouton qui sauve/restaure son libellé doit utiliser `innerHTML`, pas `textContent` (sinon le SVG est détruit).
  - Les `★` de `parseRating()` sont de la **donnée** (cellules Excel), pas de la déco : ne pas les toucher.

## Workflows
- **Livraison automatique (demandé par l'utilisateur, 2026-07-09)** : à la fin de chaque tâche qui modifie l'app, enchaîner **sans redemander** : bumper `CACHE_VERSION` → `git commit` + `push` → `py tools/smoke.py && firebase deploy --only hosting`. Le smoke test est le **dernier verrou avant la prod** : s'il sort ≠ 0, ne pas déployer. Retour arrière = `git revert <sha>` puis redéployer.
- **Feature / fix** : éditer → tester via serveur local → vérifier à la main les onglets touchés + un cycle save/sync.
- **Vérification — adapter l'effort au risque** :
  - *Visuel / CSS / icônes* → l'utilisateur regarde sur `localhost:8000`. **Pas** de screenshot headless de ma part.
  - *Logique JS* → une seule sonde `dump-dom`/`document.title` ; s'arrêter **dès qu'elle répond**.
  - *Sync / données* → cycle save/reload manuel.
- **Debug headless** : copier le fichier, injecter une sonde qui écrit dans `document.title`, `chrome --headless=new --dump-dom`, lire le `<title>`.
  - ⚠️ Injecter la sonde avant le **dernier** `</body>` (`rpartition`), pas un `replace` global — `</body>` apparaît dans des chaînes JS de l'app, et le remplacer partout casse le script principal.
  - **Screenshot** : `chrome --headless=new --no-sandbox --screenshot=C:/Temp/x.png` (échoue silencieusement vers un chemin OneDrive avec espaces → écrire dans `C:/Temp`). Hors connexion, injecter `#login-overlay{display:none}` + `.active` sur `#sidebar-user` pour voir la sidebar.
- Pas de CI ni de tests auto.

## Pièges connus
- **Ne jamais réécrire un fichier du repo avec `Get-Content`/`Set-Content`** : PS 5.1 lit en ANSI et réécrit en UTF-8 **avec BOM et CRLF** → accents en mojibake et diff sur tout le fichier. Utiliser Edit/Write, ou Python en `rb`/`wb`. Réparation : décoder l'UTF-8, ré-encoder en cp1252 en mappant à la main `0x81/8D/8F/90/9D` (Python refuse ces 5 octets, .NET les accepte), réécrire en octets, BOM retiré et CRLF→LF.
- `saveRecipe()` **reconstruit** l'objet recette et l'écrase dans `state.recipes`. Il commence par `...previous` : tout nouveau champ doit être ajouté à cet objet, sinon il est effacé à chaque modification.
- Recette : `instructions` (1 étape par ligne, numérotées à l'affichage) et `notes` sont **hors recherche** (choix utilisateur). Ne pas confondre `recipe.notes` avec `state.notes` (legacy).
- `fbSaveTimer` : remettre à `null` **avant** `fbDocRef.set()` dans le timer, sinon les snapshots cloud entrants restent bloqués (ils sont désormais mis de côté dans `fbPendingSnapshot`, mais un timer jamais libéré fige quand même la réception).
- `fbDocRef` doit être assigné **avant** `renderFirebaseUI()`.
- **`*/` dans un commentaire de bloc** (ex. écrire `open*/close*`) ferme le commentaire → SyntaxError qui tue **tout** le script inline. Symptôme : `ICONS` OK mais toutes les fonctions `undefined`, et `window.onerror` ne l'attrape pas. `py tools/smoke.py` le détecte.
- `authStateResolved` : flag anti-flash de l'overlay de login au boot — ne pas retirer.
- `.autocomplete-dropdown` est appendé à `document.body` : le listener `click` global de fermeture doit l'ignorer.
- **Code mort Notes** : `#notes-editor`, `initNotesTab()`, `notesUndo/Redo` subsistent mais l'onglet Notes a été remplacé par Debug ; ne pas s'y fier.
- **Headless + `--virtual-time-budget` fige les transitions CSS** (le tiroir reste hors écran, `visibility` héritée reste hidden) → injecter `transition:none !important` pour capturer un état ouvert. Chrome headless impose une **largeur mini ~500px** et recadre un `--window-size` plus petit (mobile : capturer à 504px, le media ≤768 s'applique).
- Pas de `transition: all` sur `button` : ça anime `visibility` héritée du tiroir Courses (boutons invisibles).

## Hors-périmètre (ne PAS modifier sans demander)
- `DEFAULT_FIREBASE_CONFIG` (projet Firebase de prod).
- `STORAGE_KEY = 'mhuur_recipes_app_v1'` (changer efface les données locales des utilisateurs).
- `migrateRecipes()` (migration one-shot appelée au `load()`).
- `state.notes` (conservé pour compat même si son UI a disparu).

## Auto-maintenance
- **Auto-alimentation** : en fin de tâche, si une convention non documentée, un piège ou une commande non triviale a été découvert → l'ajouter ici en 1-2 lignes max.
- **Critère d'ajout strict** : (a) non déductible du code en < 30 s **et** (b) utile dans une future session. Sinon ne rien écrire. Documenter le piège, pas son historique.
- **Diagnostic** : tous les ~10 commits, ou au-delà de ~4000 tokens, proposer un nettoyage (obsolète, redondant, trivial). Court et juste > long et flou.
- **Format** : phrases courtes, listes à puces.

## Efficacité
- **Lecture ciblée** : `index.html` fait ~7 600 lignes — ne jamais le lire en entier. `grep`/`glob` pour repérer la zone, puis lire ~50 lignes autour.
- **Veille MCP & skills** : ~1×/semaine en usage actif, signaler un MCP server ou une skill qui réduirait le coût ou améliorerait la qualité sur les tâches récurrentes ici.
- **Audit trimestriel** : ~tous les 3 mois, proposer une revue — quelles règles de ce fichier ralentissent, quels nouveaux outils existent côté Claude Code.
