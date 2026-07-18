# Handoff : Écran principal Recettes — direction 2a

## Overview
Refonte de l'écran principal de l'app **Recettes** (repo `mhuur/Recette`) : la liste des recettes et le panneau de détail. Objectif de la refonte : garder des **lignes compactes** (voir beaucoup de recettes d'un coup), **récupérer l'espace perdu**, **densifier l'information** et **repenser la navigation**. La direction retenue (« 2a ») réunit trois zones sur un seul écran, sans quitter la page :

1. Une **barre de commande horizontale** en haut (marque + recherche + trier + panier + ajouter).
2. Un **panneau de filtres toujours visible** à gauche.
3. La **liste dense** au centre.
4. Une **carte de détail permanente** à droite.

## About the Design Files
Les fichiers de ce bundle sont des **références de design réalisées en HTML/CSS** — des prototypes qui montrent l'apparence et le comportement voulus, **pas du code de production à copier tel quel**. La tâche est de **recréer ce design dans l'environnement du codebase existant** (`mhuur/Recette` : HTML/CSS/JS vanilla, un seul `index.html`, `styles.css`, thème « Sylva »), en réutilisant ses patterns et ses tokens CSS déjà en place. Ne pas introduire de framework : l'app est en JS vanilla avec un état persisté dans `localStorage` (`STORAGE_KEY = 'mhuur_recipes_app_v1'`) et des fonctions `renderRecipes()` / rendu du détail.

## Fidelity
**High-fidelity (hifi).** Couleurs, typographie, espacements et rayons sont définitifs et alignés sur le design system **Sylva** déjà présent dans le codebase. Recréer l'UI fidèlement en réutilisant les variables CSS et les composants existants (`.glass`, boutons pilule, chips, etc.). Les données affichées dans la maquette sont des exemples.

## Screens / Views

### Écran : Recettes (liste + détail)
- **Purpose** : parcourir/filtrer/rechercher les recettes, cocher celles à ajouter au panier de courses, et consulter le détail d'une recette sélectionnée sans changer d'écran.
- **Layout global** : conteneur pleine hauteur sur fond dégradé forêt clair. À l'intérieur, un **cadre arrondi** (radius 24px, `box-shadow` vert diffus) qui contient, en colonne :
  1. La **barre de commande** (pleine largeur).
  2. Une **rangée à 3 colonnes** en flex, `gap: 16px`, `align-items: stretch` :
     - Colonne filtres : `width: 224px`, `flex-shrink: 0`.
     - Colonne liste : `flex: 1; min-width: 0`.
     - Colonne détail : `width: 392px`, `flex-shrink: 0`.
- **Fond** : `assets/forest-bg.jpg` recouvert d'un voile clair — dégradés `radial-gradient(90% 70% at 12% -5%, rgba(244,239,201,.4), transparent 45%)` + `linear-gradient(165deg, rgba(236,246,238,.5), rgba(158,199,172,.42))`, `background-size: cover; background-position: center 40%`.

#### Composant : Barre de commande (haut)
- Surface verre : `background: rgba(255,255,255,.74)`, `backdrop-filter: blur(16px)`, bordure `1px rgba(255,255,255,.65)`, radius 18px, `box-shadow: 0 8px 24px rgba(20,48,32,.12)`, padding `11px 16px`. Flex, `align-items: center`, `gap: 14px`, `margin-bottom: 16px`.
- De gauche à droite :
  - **Marque** : carré vert 30×30, radius 9px, `background: var(--green-600)`, icône chef-hat blanche (Lucide `chef-hat`) ; mot « Recettes » en `--font-display` 16px/700 ; compteur « 8 » en `--mist-500` 12.5px/600.
  - **Recherche** (élément extensible, `flex: 1; min-width: 200px`) : pilule `background: var(--mist-100)`, bordure `--mist-200`, radius 999px, padding `9px 16px`, icône loupe + placeholder « Rechercher une recette, un ingrédient… » 13.5px `--mist-500`.
  - **Trier** : bouton texte + icône (Lucide `arrow-up-down`), 13px/600 `--mist-800`.
  - **Séparateur** : trait vertical 1×22px `--mist-200`.
  - **Panier** : pilule blanche translucide bordée `--mist-200`, icône caddie (Lucide `shopping-cart`), libellé « Panier » + **badge** vert (`--green-600`, texte blanc, radius 999px, min 18px) indiquant le nombre d'articles.
  - **Ajouter** : bouton plein `background: var(--green-600)`, texte blanc 13.5px/700, radius 999px, padding `9px 16px`, icône `plus`.

#### Composant : Panneau Filtres (gauche)
- Surface verre `rgba(255,255,255,.76)`, blur 16px, bordure `rgba(255,255,255,.65)`, radius 20px, `box-shadow: 0 12px 40px rgba(20,48,32,.14)`, padding 18px. Flex colonne, `gap: 18px`.
- **Titre** : icône entonnoir (Lucide `filter`, trait `--green-600`) + « Filtres » en `--font-display` 15px/700.
- Chaque groupe a un **libellé eyebrow** : `--font-mono` 10px/600, `letter-spacing: .1em`, `text-transform: uppercase`, `--mist-500`, `margin-bottom: 9px`.
  - **Type de plat** : chips pilule qui s'enroulent (`flex-wrap; gap: 6px`). Chip **actif** = plein `--green-600` texte blanc ; **inactif** = `rgba(255,255,255,.7)`, bordure `--mist-200`, texte `--mist-700`. Chips : Plat principal (actif), Entrée, Dessert, Salade, Sauce. 12px/600, padding `4px 11px`, `white-space: nowrap`.
  - **Note minimum** : boutons carrés-arrondis (radius 9px) « 6+ 7+ 8+ 9+ », 12px/700. Actif « 7+ » = `background: #faf6e0`, bordure `#eee6a4`, texte `--sun-600`.
  - **Temps total** : chips pilule « ≤ 30 min », « ≤ 1 h » (mêmes styles inactifs).
- **Pied** (`margin-top: auto`, bordure haute `--mist-200`, `padding-top: 12px`) : « 1 filtre actif · **Tout effacer** » (lien `--green-600` 600).

#### Composant : Liste dense (centre)
- Surface verre `rgba(255,255,255,.78)`, blur 16px, bordure `rgba(255,255,255,.65)`, radius 18px, `box-shadow: 0 12px 40px rgba(20,48,32,.16), inset 0 1px 0 rgba(255,255,255,.55)`, `overflow: hidden`, `align-self: flex-start`.
- **En-tête de colonnes** (clé de la densification) : `display: grid; grid-template-columns: 24px 1fr 92px 56px 128px; gap: 14px; padding: 9px 18px`, bordure basse `--mist-200`. Libellés eyebrow mono 10px : (case) · RECETTE · NOTE · PERS. · TEMPS.
- **Lignes** : même grille, `padding: 7px 18px`, bordure basse `--mist-100`.
  - **Case à cocher** : 16×16, `accent-color: var(--green-600)`. Cochée = recette dans le panier.
  - **Nom** : 14px/700 `--text-strong`, `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`.
  - **Note** : 5 étoiles ★ sur 5, à partir d'une note /10 (voir Design Tokens → Étoiles). Pleines `#b7a63a`, vides `#ccd6cf`, demi-étoile en dégradé 50/50.
  - **Pers.** : icône `user` + nombre, 12.5px `--mist-600`.
  - **Temps** : icône `clock` + texte « prépa + cuisson » (ex. « 20 min + 45 min »).
- **Interaction** : cliquer une ligne charge la recette dans la carte de détail à droite (ligne active mise en évidence — voir États).

#### Composant : Carte de détail permanente (droite)
- Surface verre plus opaque `rgba(255,255,255,.82)`, blur 20px, bordure `rgba(255,255,255,.7)`, radius 20px, `box-shadow: 0 12px 40px rgba(20,48,32,.18), inset 0 1px 0 rgba(255,255,255,.55)`, padding 22px. Flex colonne, `gap: 12px`, `align-self: flex-start`.
- **En-tête** : titre recette en `--font-display` 24px/700, `letter-spacing: -.02em`, `line-height: 1.1`, `--text-strong` ; à droite bouton **Modifier** plein `--green-600` blanc, radius 999px, 13px/700, icône crayon.
- **Note** : étoiles 16px + « 8/10 » 13px/700 `--mist-600`.
- **Chips type de plat** : `--green-100` fond, texte `--green-800`, 11px/600, radius 999px, `padding: 3px 10px`.
- **Méta** : rangée bordée haut+bas `--mist-200`, `padding: 12px 0`, 12.5px/600 `--mist-700`, séparateurs middot `--mist-300` : « 4 pers. · Prépa 20 min · Cuisson 45 min ».
- **Corps en 2 colonnes** (`grid-template-columns: 1fr 1fr; gap: 18px`) :
  - **Ingrédients** (eyebrow mono) : liste, quantité en gras `--green-700` + nom `--mist-800`, 13px.
  - **Préparation** (eyebrow mono) : liste ordonnée sans puce, numéro d'étape en `--font-mono` 11px/700 `--green-600` positionné à gauche, texte 12.5px `--mist-800`.
- **Note (encadré)** : `background: var(--green-50)`, bordure `--green-100`, radius 12px, `padding: 11px 14px`, 12.5px `--green-800` : « **Note** · <texte> ». À masquer si la recette n'a pas de note.

## Interactions & Behavior
- **Clic sur une ligne** → charge la recette dans la carte de détail (état `selectedRecipeId` ou équivalent). La ligne active reçoit un fond `var(--green-50)` et/ou une barre gauche `--green-600`.
- **Case à cocher** → ajoute/retire la recette du panier de courses (`selectedRecipeIds` dans le state existant) ; le **badge du panier** se met à jour en temps réel.
- **Chips filtres** → toggle ; filtrage combiné (type de plat + note mini + temps) appliqué à la liste. « Tout effacer » réinitialise. Compteur « N filtre(s) actif(s) » recalculé.
- **Recherche** → filtre la liste par nom de recette et par ingrédient (déjà supporté côté données).
- **Trier** → ouvre les options de tri existantes (A→Z, note, temps).
- **Ajouter** → ouvre la modale de création de recette existante.
- **Panier** → ouvre le tiroir de liste de courses existant.
- **Modifier** → ouvre la modale d'édition de la recette affichée.
- **Hover** : boutons pleins `filter: brightness(1.05)` ; lignes de liste fond `--mist-50` ; chips inactifs bordure `--mist-300`. Transitions douces 140–240ms, `ease-out` (tokens Sylva).
- **Responsive** : sur largeur réduite (mobile/tablette), passer en une seule colonne — la liste occupe la largeur, les **filtres** basculent dans un panneau/tiroir déclenché par un bouton dans la barre, et le **détail** s'ouvre en plein écran (overlay) au clic sur une ligne, avec un bouton retour. La barre de commande reste en haut ; recherche à pleine largeur, actions condensées en icônes.

## State Management
Réutiliser l'état existant (`state` persisté en `localStorage`, clé `mhuur_recipes_app_v1`) :
- `recipes[]`, `ingredients[]`, `units[]`, `ingredientTypes[]`, `mealTypes[]` — données.
- `selectedRecipeIds[]` — recettes cochées pour le panier (pilote le badge et les cases).
- **Nouveau/à confirmer** : `activeRecipeId` — recette affichée dans la carte de détail (par défaut la première de la liste filtrée).
- `filters` — `{ mealType, minRating, maxTime, search, sort }` pour piloter le panneau de filtres toujours visible.
- Transitions : cocher → maj `selectedRecipeIds` ; cliquer ligne → maj `activeRecipeId` ; toggler un chip → maj `filters` puis re-rendu de la liste filtrée.

## Design Tokens
Tous alignés sur le thème Sylva du codebase (`styles.css`). Valeurs utilisées ici :

**Couleurs**
- Verts : `--green-900 #143020` · `--green-800 #1c4530` · `--green-700 #235a3d` · `--green-600 #2f7d55` (accent/action) · `--green-500 #3f9a6a` · `--green-100 #e0f1e6` · `--green-50 #f0f8f3`
- Neutres « mist » (verts désaturés) : `--mist-900 #1f2d26` · `--mist-800 #37453d` · `--mist-700 #4f5f55` · `--mist-600 #6b7b71` · `--mist-500 #8b9a90` · `--mist-300 #ccd6cf` · `--mist-200 #e2eae4` · `--mist-100 #eef4f0` · `--mist-50 #f6faf7`
- Soleil (emphase positive) : `--sun-600 #b7a63a`
- Texte fort : `--text-strong #0f2418`

**Verre (glass)** : fond `rgba(255,255,255,.74–.82)` selon la profondeur, `backdrop-filter: blur(16–20px)`, bordure `rgba(255,255,255,.65–.7)`, highlight interne `inset 0 1px 0 rgba(255,255,255,.55)`.

**Ombres** (vertes diffuses, rgba de #143020) : `0 8px 24px rgba(20,48,32,.12)` · `0 12px 40px rgba(20,48,32,.14–.18)` · cadre externe `0 18px 48px rgba(20,48,32,.14)`.

**Typographie**
- Display/titres : **Bricolage Grotesque** 600/700, `letter-spacing: -.02em`.
- Corps/UI : **Manrope** 400–700.
- Mono (eyebrows, quantités, numéros d'étape) : **JetBrains Mono** 400/500.
- Tailles clés : titre détail 24px · nom recette 14px · corps liste 12.5–13.5px · eyebrow 10px `letter-spacing: .1em` uppercase.

**Rayons** : cadre 24px · panneaux 18–20px · chips/boutons pilule 999px · boutons note 9px · encadré note 12px.

**Espacements** (grille 4px) : padding surfaces 18–22px · gap colonnes 16px · gap barre 14px · padding lignes `7px 18px`.

**Étoiles (note /10 → 5 étoiles)** : `v = note/10*5`. Pour i de 1 à 5 : plein `#b7a63a` si `v ≥ i` ; demi si `v ≥ i-0.5` (dégradé `linear-gradient(90deg,#b7a63a 50%,#ccd6cf 50%)` + `background-clip: text; color: transparent`) ; sinon vide `#ccd6cf`.

## Assets
- `assets/forest-bg.jpg` — photo de forêt en fond (déjà dans le codebase). **Attention licence** : image tierce (filigrane « Ruby-Art / deviantart »), usage personnel non publié uniquement. Pour toute diffusion publique, la remplacer par une image sous licence.
- **Icônes** : [Lucide](https://lucide.dev) (outline, trait 2px, `currentColor`), déjà utilisées dans le codebase via `icons.js`. Icônes de cet écran : `chef-hat`, `search`, `arrow-up-down`, `shopping-cart`, `plus`, `filter`, `user`, `clock`, `pencil`/`edit`.

## Files
- `mock_2a_liste_detail.html` — maquette hi-fi autoportante de la direction 2a (ouvrir dans un navigateur). Styles inline, variables CSS = tokens Sylva.
- `assets/forest-bg.jpg` — image de fond référencée par la maquette.
- Référence codebase : `index.html` (markup + `renderRecipes()` + rendu détail + modales), `styles.css` (thème Sylva, classes `.recipe-row`, `.recipe-detail`, `.toolbar`, `.topbar`…), `icons.js`.
