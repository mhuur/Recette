# Sources du calendrier de saison

Relevé le 2026-09-16 pour la colonne **septembre** de `saisons.csv`. Périmètre : France métropolitaine, sauf catégorie « Exotique (import) ».

| Code | Source | Ce qu'elle apporte | Copie locale |
| --- | --- | --- | --- |
| FL | fruits-legumes.org — <https://fruits-legumes.org/calendrier-fruits-legumes/septembre/>, `/liste-fruits/`, `/liste-legumes/`, fiches produits | 155 produits × 12 mois avec distinction **de saison / pleine saison** (attributs `data-mois` + classe `est-pic` des cartes). Inclut exotiques et importés. | `sources/fruits-legumes-org.json` |
| IF | Interfel — <https://www.lesfruitsetlegumesfrais.com/calendrier-fruits-legumes> (page filtrée sur le mois courant) + fiches produits (oignon, oignon primeur, échalote, ail, la-salade, poire, raisin, prune, pêche-nectarine, figue, melon, haricot-vert, champignons) | 47 produits en septembre (classes `month-septembre`). Fiches : variétés nommées et calendrier cœur de saison / saison / disponibilité. Le PDF `calendrier-de-saison-fruits-legumes.pdf` (2025-09) est graphique : mois illisibles par extraction de texte. | `sources/interfel-septembre.json` |
| GP | Greenpeace — <https://www.greenpeace.fr/guetteur/calendrier/> et guide PDF 2022 | 31 légumes + 18 fruits en septembre, 12 mois. Base de l'ancien `data/saisons.md`. | `sources/greenpeace-guide-2022.pdf` |
| BNA | Bio Nouvelle-Aquitaine — <https://www.bionouvelleaquitaine.com/wp-content/uploads/2020/04/calendrier-saisons-fruits-legumes.pdf> | 12 mois, distingue oignon blanc / oignon sec, aillet, haricot à écosser, haricots plats, poire Guyot, pomme d'été, pêche de vigne. | `sources/bio-nouvelle-aquitaine.pdf` |
| GF | Green Fudge — <https://www.greenfudge.org/guide/les-legumes-de-septembre-liste-complete-par-famille/4625/> | Légumes de septembre par famille avec variétés (Créances, Pardailhan, Charlotte, Bintje, Vitelotte, tomates anciennes, kale, poireau primeur). | — |
| DBB | DocteurBonneBouffe — <https://docteurbonnebouffe.com/fruits-legumes-saison-septembre/> | Variétés de septembre : pommes (Gala, Royal Gala, Golden, Reine des reinettes), poires d'automne (Beurré Hardy, Louise-Bonne, Alexandrine Douillard), fraises remontantes (Charlotte, Seascape, Mara des bois), chou-fleur coloré. | — |
| CV | Cerise et Vinaigrette — <https://ceriseetvinaigrette.fr/alimentation/la-liste-des-fruits-et-legumes-de-saison-en-septembre/> | Liste de septembre (premiers coings, premières châtaignes, poireau début). | — |
| BM | BienManger — <https://www.bienmanger.com/1C600_Saison_Fruits_Legumes_Calendrier.html> | Liste de septembre. | — |
| PG | Les Producteurs Gâtinais — <https://lesproducteursgatinais.com/consommer-local/calendrier-des-legumes-et-fruits-de-saison/> | Liste automne (mogette, crosne, salsifis, topinambour, échalote) ; signale les produits « en conservation ». | — |
| FM | La Ferme de Margaux — <https://lafermedemargaux.fr/calendrier-de-maturite-des-pommes/> | 30 variétés de pommes avec mois de récolte et de disponibilité. | — |
| ML | Mangeons local .bzh — <https://www.mangeons-local.bzh/saison-courge/>, <https://www.mangeons-local.bzh/aromatiques-calendrier/> | Courges par variété (8) ; aromatiques par mois (20). | — |
| MC | Mycocarta — <https://mycocarta.fr/guides/saisons> | 12 champignons avec mois de cueillette. | — |
| CDC | Chasseurs de champignons — <https://www.chasseursdechampignons.com/blog/comment-trouver-des-champignons/champignons-dautomne-septembre-octobre-novembre/> (via résumé de recherche) | Espèces de septembre (oronge, coulemelle, lactaire, rosé des prés). | — |
| SM | Swissmilk — <https://www.swissmilk.ch/fr/recettes-idees/calendrier-des-saisons/choux-de-saison/> | 15 choux avec mois (Suisse, climat comparable). | — |
| PDT | lespommesdeterre.com — <https://www.lespommesdeterre.com/les-pommes-de-terre-de-primeurs-et-de-conservation/> | Primeur : avril → 15 août ; variétés primeur. | — |
| LN | LaNutrition.fr — <https://www.lanutrition.fr/bien-dans-son-assiette/aliments/fruits/raisin/les-varietes-de-raisins> (via résumé de recherche) | Raisins de table par variété : Chasselas, Cardinal, Muscat de Hambourg, Italia, Alphonse Lavallée, Danlas. | — |
| DNC | Drive de nos campagnes — <https://www.drive-de-nos-campagnes.fr/saison-de-la-noix/> (via résumé de recherche) | Noix fraîche : mi-septembre → fin octobre. | — |
| VD | Vedura — <http://www.vedura.fr/guide/legumes/crosne> (via résumé de recherche) | Crosne : septembre → mars. | — |
| CJ | Culture Jardin / Aroma-Zone — <https://www.culturejardin.fr/cebette> (via résumé de recherche) | Cébette : bottes dès mi-mars (Sud) / avril. | — |
| PPF | Pommes et poires de France — <https://pommesetpoiresdefrance.fr/varietes/calendrier> | Liste de variétés ; le calendrier mois par mois est chargé en JavaScript et le PDF `tableau-varietal-pommes.pdf` est une image : **non exploitable** par extraction. | — |

« via résumé de recherche » : la page n'a pas été lue directement, la valeur vient du résumé renvoyé par le moteur de recherche. À relire avant de s'y fier pour un autre mois.

## Pages tentées sans résultat

- `lesfruitsetlegumesfrais.com/calendrier-fruits-legumes/septembre` et `/fruits-legumes/asperge` : 404 (les fiches sont sous `/fruits-legumes/<famille>/<produit>`).
- `mangerbouger.fr` calendrier : 404.
- `fruits-legumes.org/guide-tomates/` et `/guide-fraises/` : guides payants, variétés non listées en clair.
- `ailmacocotte.com`, `kimiyo.fr` : pages sans contenu textuel exploitable.

## Relevé du 2026-09-16 (soir) — les 12 mois

Remplissage par `tools/saisons_fill.py` (règle de vote en tête du script) à partir de tables 12 mois normalisées :

| Fichier | Contenu | Origine |
| --- | --- | --- |
| `sources/interfel-12mois.json` | 102 produits : mois de saison (`month-*`), cœur de saison (`product_seasons-coeur-de-saison-MM`), simple disponibilité (`-disponibilite-MM`, non comptée), texte « Pleine saison » de la fiche | API REST WordPress `https://www.lesfruitsetlegumesfrais.com/wp-json/wp/v2/interfel-products?per_page=100&page=1..5` (493 billets, 102 fiches principales `parent = 0`). Le calendrier en ligne ne montre que le mois courant ; l'API rend tout. |
| `sources/greenpeace-12mois.json` | 77 produits × mois | pages 2-3 de `greenpeace-guide-2022.pdf` (texte extrait avec `pypdf`) |
| `sources/bna-12mois.json` | 84 produits × mois | `bio-nouvelle-aquitaine.pdf` (ligatures « ﬂ », « ﬁ » recollées) |

Relevés à la main dans `tools/saisons_fill.py` : Swissmilk (15 choux), Mangeons local (8 courges, 19 aromatiques mois par mois), Mycocarta (12 champignons), La Ferme de Margaux (tableau de disponibilité sept.→mai, `<table>` de la page).

### Sources web des produits sans calendrier (`tools/saisons_web.py`)

Une page lue par produit (WebFetch), sauf mention « via résumé ».

| Code | Source | Produits | URL |
| --- | --- | --- | --- |
| LPF | Le Poireau de France | poireau primeur | <https://www.lepoireau.fr/la-production-francaise/> |
| AJ | Au Jardin | asperge sauvage | <https://www.aujardin.info/plantes/ornithogalum-pyrenaicum.php> |
| AGS | Agrosemens | chou de Pontoise | <https://www.agrosemens.com/249-chou-d-hiver-et-de-pontoise> |
| POU | Pouliquen (producteur) | chou-fleur coloré | <https://www.pouliquen.fr/en/produit/coloured-cauliflowers-orange-purple-green/> |
| JDJ | Le Jardin de Jenny | brocoli à jets | <https://www.le-jardin-de-jenny.fr/la-culture-du-chou-brocoli-a-jets.html> |
| JM | Jardiner-malin | fleur de courgette, nèfle du Japon, olive, poire Beurré Hardy, coriandre, basilic, pêche de vigne, poireau primeur | <https://www.jardiner-malin.fr/> (fiches `fleur-de-courgette-comestible-utilisation`, `neflier-du-japon`, `recolte-olives`, `poirier-beurre-hardy`, `coriandre`, `basilic`, `peche-de-vigne-sanguine`) |
| TV | Terre Vivante | cornichon | <https://www.terrevivante.org/contenu/culture-cornichon-semis-entretien-recolte/> |
| IRI | Iriso | tomate verte | <https://iriso.fr/blog/que-faire-des-tomates-vertes-a-la-fin-de-l-ete-au-jardin-astuce-anti-gaspi> |
| GB | Gerbeaud | grenaille, daikon, cerfeuil tubéreux, persil tubéreux, bergamote | <https://www.gerbeaud.com/> (`fruit-legume-de-saison/pomme-de-terre.php`, `jardin/fiches/radis-blanc-japonais-daikon,2404`, `cerfeuil-tubereux-semis-culture,1625`, `persil-tubereux,1126`, `bergamotier-citrus-bergamia,2663`) |
| BMS | Bien manger selon les saisons | grenaille, pêche plate | <https://www.bien-manger-selon-les-saisons.com/> |
| RDT | La Ratte du Touquet (ancien site producteur) | ratte | <https://p6006.phpnet.org/larattedutouquetold/conseils-pratiques-ratte-du-touquet/peut-on-trouver-la-rdt-toute-lannee-au-supermarche/> |
| MDV | Mogette de Vendée (filière) | mogette | <https://www.mogettedevendee.fr/la-saison-de-la-mogette-en-vendee/> |
| ALE | Alélor + ICI Alsace | raifort | <https://www.alelor.fr/actualites/le-raifort-gout-sauce-accords-et-histoire-dun-embleme-alsacien/39> ; <https://www.ici.fr/infos/agriculture-peche/la-recolte-du-raifort-a-commence-dans-le-bas-rhin-1509551251> |
| GBQ | Graines Bocquet | pain de sucre | <https://www.graines-bocquet.fr/33-chicoree-a-large-feuille-amelioree-pain-de-sucre.html> |
| GSM / ADP | Graines-semences.com / Autour du potager | mizuna ; tomates anciennes | <https://www.graines-semences.com/legumes/2705-mizuna-vert-pourpre-chou-japonais-legume-ancien-jardin-potager-terrasse-balcon-5420000001329.html> ; <https://www.autourdupotager.com/tomates-couleur/> |
| ML | Mangeons local .bzh | salicorne | <https://www.mangeons-local.bzh/salicorne/> |
| CLC | Cultiver-les-champignons.com (+ Secrets des champignons) | oronge | <https://cultiver-les-champignons.com/oronge/> |
| PJ | PagesJaunes jardinage / potager | verveine, livèche, ciboulette, pomme Elstar, poire Abate Fetel | <https://potager.pagesjaunes.fr/fiche/voir/741811/tailler-et-recolter-la-verveine-citronnelle> ; <https://jardinage.pagesjaunes.fr/plante/voir/480/liveche> ; <https://potager.pagesjaunes.fr/fiche/voir/733685/cueillir-et-couper-la-ciboulette> ; <https://jardinage.pagesjaunes.fr/astuce/voir/597049/pomme-elstar> ; <https://jardinage.pagesjaunes.fr/astuce/voir/621219/poire-abate> |
| TPM | Tisanes et potions des montagnes | ortie | <https://www.tisanesetpotionsdesmontagnes.com/reconnaitre-preparer-jeunes-pousses-ortie.html> |
| GRO | Pépinières Gromolard | prune Président | <https://www.pepinieres-gromolard.com/fruitiers/prunier-pr%C3%A9sident.html> |
| ODC | AOP Oignon doux des Cévennes | oignon des Cévennes | <https://oignon-doux-des-cevennes.fr/l-oignon-doux-des-cevennes/> |
| OTR | Office de tourisme de Roscoff | oignon de Roscoff | <https://www.roscoff-tourisme.com/fr/restauration/les-produits-et-plats-du-leon/oignon-de-roscoff/> |
| PPF | Pommes et poires de France / ANPP — **tableaux variétaux PDF lisibles** (périodes de vente) | Elstar, Granny Smith, Pink Lady, Fuji, Williams, Louise-Bonne, Passe-Crassane, Angélys | <https://pommesetpoiresdefrance.fr/wp-content/uploads/2026/02/tableau-varietal-pommes.pdf> ; <https://pommesetpoiresdefrance.fr/wp-content/uploads/2026/02/tableau-varietal-poires.pdf> |
| PL | pomme-pinklady.com | Pink Lady (cueillette) | <https://www.pomme-pinklady.com/wwp-parcours-scene/la-cueillette/> |
| WK | Wikipédia | Louise-Bonne, Alexandrine Douillard, Angélys, cédrat de Corse, haricot tarbais | <https://fr.wikipedia.org/wiki/Louise-Bonne_d'Avranches> ; `Alexandrine_Douillard` ; `Ang%C3%A9lys` ; `C%C3%A9drat_de_Corse` ; `Haricot_tarbais` |
| FDF | Fraisiers de France | fraise remontante | <https://fraisiersdefrance.fr/fraisiers-remontants/32-mara-des-bois.html> |
| FDS | Syndicat AOP Figue de Solliès + FreshPlaza | figue de Solliès | <https://www.figue.org/> ; <https://www.freshplaza.fr/article/9760322/nous-sommes-deja-en-plein-pic-de-production-pour-la-figue-de-sollies-aop/> |
| PDB | Pépinière du Bosc | figue Dauphine | <https://pepinieredubosc.fr/nos-arbres-fruitiers/dauphine/> |
| LAF / COC | L'Arbre aux fruits (pépinière Watson) / Pépinière Cochet | figue de Caromb, figue fleur | <https://www.larbreauxfruits.fr/catalogue-des-fruitiers/figuier/les-figues-bif%C3%A8res/> ; <https://www.cochet-pepiniere-fruitier.com/Figuiers/64-FIGUIER-Noire-de-caromb.html> |
| TLJ / MV | Tom le jardinier / Monde Végétal | arbouse | <https://www.tomlejardinier.com/cultiver-son-potager/arbousier> ; <https://monde-vegetal.fr/blogs/blog/arbousier> |
| CAN | Canaghja | cédrat | <https://www.canaghja.com/LE-CEDRAT-un-fruit-symbolique-de-la-Corse_a161.html> |
| AAA | Les Agrumes de l'Armagnac | yuzu | <https://agrumes-armagnac.fr/citrons-yuzu/> |
| BAK / PRO | Bakker / Prosem | flageolet frais | <https://fr-fr.bakker.com/products/haricot-nain-flageolet-chevrier-vert-flagrano> ; <https://www.prosem.fr/fscmsDocument/show/id/12077> |
| PNA / TD | Produits de Nouvelle-Aquitaine / Terre Dauphinoise | noix sèche nouvelle récolte | <https://www.produits-de-nouvelle-aquitaine.fr/les-produits-de-nouvelle-aquitaine/fruits/noix-du-perigord/> ; <https://www.terredauphinoise.fr/articles/la-recolte-de-noix-de-grenoble-aop-est-lancee-95381/> |
| IF fiche | Fiches Interfel relues : poire (Williams dès début juillet), fraise (Charlotte mai-nov., Mara mi-mai-oct.), herbes (basilic pleine saison juil.-août), prune (Black Amber, Friar, Angeleno), pêche (pêche de vigne sept.-oct.), noix (noix sèche en rayon début oct.), raisin (Chasselas, Muscat, Lavallée) | — | `https://www.lesfruitsetlegumesfrais.com/fruits-legumes/<famille>/<produit>` |

LaNutrition (LN, variétés de raisin) a été **lue** cette fois (plus « via résumé »).
