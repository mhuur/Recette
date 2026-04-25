# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack & structure

Single-file app: **tout le code est dans `index.html`** (~6 200 lignes). Pas de build, pas de bundler, pas de dépendances npm. On modifie `index.html` directement.

Dépendances CDN (dans le `<head>`) :
- Firebase compat SDK v10.12.5 (`firebase-app-compat`, `firebase-auth-compat`, `firebase-firestore-compat`)
- SheetJS `xlsx@0.18.5` pour l'import Excel

Structure interne de `index.html` :
1. `<head>` — CDN scripts
2. `<style>` — CSS complet (~1 100 lignes), thème dark avec variables CSS `--bg`, `--primary`, etc.
3. `<body>` — HTML des onglets + modals
4. `<script>` — toute la logique JS (~4 700 lignes)

## Architecture JS

**État global unique** (`state`, ~ligne 2 104) — objet mutable avec `recipes`, `ingredients`, `units`, `ingredientTypes`, `ingredientFamilies`, `mealTypes`, `filters`, `notes`, `selectedRecipeIds`, `checkedShoppingItems`.

**Persistance à deux niveaux** :
- `save()` → `localStorage` + planifie un push Firestore (debounce 5 s)
- `saveLocal()` → `localStorage` uniquement (pour les filtres/préférences)
- `fbSchedulePush()` → `fbDocRef.set({...state, lastModified})` après debounce

**Sync Firestore** :
- `fbDocRef` pointe sur `users/{uid}/app/data` (mode perso) ou `sharedData/{spaceName}` (mode partagé)
- `onSnapshot` écoute en temps réel ; ignoré si `fbSkipNextSnapshot` ou si `fbSaveTimer` est actif (écriture locale en cours)
- `visibilitychange` force un `get()` à la reprise de session
- `applyCloudData(data)` applique les données cloud, appelle toujours `renderSeasonTab()` et met à jour l'éditeur de notes (même si l'onglet n'est pas actif)

**Modes d'accès** :
- Authentifié perso (Google Sign-In)
- Mode partagé (`sharedMode`) — espace nommé dans Firestore, UIDs autorisés
- Mode invité (`guestMode`) — lecture seule, accès via hash URL `#invite=...`

**Rendus par onglet** :
- `renderRecipes()` — filtre via `getFilteredRecipes()`, construit les cartes DOM
- `renderSeasonTab()` — grille mois × ingrédients
- `renderShopping()` — liste de courses groupée par famille
- `renderDataTab()` — gestion ingrédients / unités / types / familles
- `rerenderAll()` — appelé après sync cloud, re-rend tous les onglets actifs

**Composants réutilisables** :
- `createAutocomplete(wrapper, options)` — input avec dropdown simple (retourne `{ setValue, getValue }`)
- `createChipsInput(wrapper, options)` — input multi-valeurs avec chips (retourne `{ getValues, setValues }`). Le dropdown est appendé à `document.body` en `position:fixed`.
- `showConfirm(title, msg, okLabel, onOk)` — modal de confirmation in-app (remplace `confirm()`)
- `openMergeModal(...)` — modal de fusion en 2 étapes (remplace `prompt()`)

## Conventions

**Branches Git** : développement sur `claude/fix-mobile-login-visibility-sSNoW`, merge vers `main` via PR. Nommage : `claude/<description>`.

**IDs** : générés par `uid()` = `Date.now().toString(36) + random`. Jamais d'index tableau comme identifiant.

**Lookup helpers** : `getIngredientName(id)`, `getUnitName(id)`, `getTypeName(id)`, `getFamilyName(id)` — retournent `''` si non trouvé. `findOrCreate*()` pour créer à la volée.

**CSS** : variables `--bg`, `--bg-2`, `--surface`, `--primary`, `--accent`, `--danger`, `--text`, `--text-muted`. Breakpoint mobile : `@media (max-width: 768px)`. Unité de hauteur : `dvh` (dynamic viewport height, gère le clavier iOS).

**Formulaires** : tous les inputs texte ont `autocomplete="off" autocorrect="off" autocapitalize="none" spellcheck="false"` pour éviter la barre AutoFill iOS.

## Pièges spécifiques

**`fbSaveTimer`** : doit être reset à `null` **avant** d'appeler `fbDocRef.set()` dans le timer, sinon les snapshots cloud entrants sont bloqués indéfiniment.

**`authStateResolved`** : flag qui empêche le flash de l'overlay de login au chargement. Ne pas supprimer la logique qui le set dans `onAuthStateChanged`.

**`fbDocRef` doit être assigné AVANT `renderFirebaseUI()`** dans `onAuthStateChanged` — sinon le chemin de synchro affiché dans les réglages est vide.

**Dropdown `.autocomplete-dropdown`** : appendé à `document.body`, donc **en dehors** de `.recipe-card`. Le listener `click` global qui ferme les cartes doit ignorer les clics sur `.autocomplete-dropdown` (déjà géré — ne pas retirer ce guard).

**`applyCloudData`** : toujours appeler `renderSeasonTab()` et mettre à jour `#notes-editor` inconditionnellement (pas seulement si l'onglet est actif), sinon les données ne s'affichent pas sur mobile après un sync.

**`setValues([])` sur `mealCtrl`** : ne déclenche pas `onChange` — sûr à appeler pour vider le widget sans effet de bord.

## Ne pas toucher

- La config Firebase hardcodée (`DEFAULT_FIREBASE_CONFIG`) — elle pointe sur le projet Firebase de prod.
- `STORAGE_KEY = 'mhuur_recipes_app_v1'` — changer la clé efface toutes les données locales des utilisateurs.
- `migrateRecipes()` — migration one-shot des anciens formats de données, appelée au `load()`.
