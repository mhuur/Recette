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
