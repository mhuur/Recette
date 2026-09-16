# -*- coding: utf-8 -*-
"""Sources web relevées le 2026-09-16 pour les produits sans calendrier dans FL / IF / GP / BNA.

Chaque entrée : liste de (code source, mois, mois de pleine saison, libellé). Codes et URL dans data/saisons/SOURCES.md.
Une entrée sous forme ("replace", [...]) remplace les sources déjà câblées dans saisons_fill.py ; une liste simple s'y ajoute.
« via résumé » : la page n'a pas été lue, la valeur vient du résumé du moteur de recherche.
"""
from saisons_fill import R, fiche, rng

ALL = set(range(1, 13))

WEB = {
    # ---- lot A : légumes, herbes, fruits sans source
    "Poireau primeur": [rng("LPF", R(4, 7), label="primeur semé : fin avr.-20 mai ; primeur planté : 20 mai-fin juil."), rng("JM", R(4, 5), label="récolte avr.-mai")],
    "Asperge sauvage": [rng("AJ", R(4, 5), label="« souvent au mois d'avril » ; mai via résumé ; espèce protégée dans plusieurs régions")],
    "Chou de Pontoise": [rng("AGS", R(10, 3), label="récolte mi-oct.-mi-mars (Deadon F1)")],
    "Chou-fleur coloré (vert, violet, orange)": [rng("POU", R(5, 11), label="vert mai-oct./nov. ; violet et orange juil.-oct.")],
    "Brocoli à jets violet": [rng("JDJ", R(1, 5), pic={3, 4}, label="têtes centrales dès janv., jets fév.-avr./mai ; Semailles : mars-avr.")],
    "Fleur de courgette": [rng("JM", R(4, 10), label="avr.-oct. selon climat")],
    "Cornichon": [rng("TV", R(8, 10), label="août-oct. selon la date de semis ; juin/juil.-sept. via résumé (Kokopelli)")],
    "Tomate verte (à confire)": [rng("IRI", R(9, 10), label="fruits restés verts avant les gelées")],
    "Pomme de terre grenaille": [rng("GB", R(5, 7), label="jeune tubercule = primeur, mai-31 juil."), rng("BMS", R(4, 7))],
    "Ratte (du Touquet)": [rng("RDT", R(9, 6), label="sur les étals de sept. à juin")],
    "Mogette de Vendée (fraîche / demi-sèche)": [rng("MDV", R(8, 9), label="fraîche dès août ; récolte août-sept. ; fin de saison fraîche non précisée")],
    "Radis daikon (blanc japonais)": [rng("GB", R(9, 11), label="semis juil.-sept., récolte 7-8 semaines après")],
    "Cerfeuil tubéreux": [rng("GB", R(7, 10), label="arrachage juil.-oct. ; consommation après 1-2 mois de maturation (via résumé)")],
    "Persil tubéreux (racine)": [rng("GB", R(9, 11), label="dès sept. jusqu'aux premières gelées")],
    "Raifort": [rng("ALE", R(10, 3), pic=R(11, 1), label="fin automne-début printemps ; ICI Alsace : récolte nov.-janv.")],
    "Chicorée pain de sucre": [rng("GBQ", R(9, 12), label="mi-sept.-gelées ; sous abri tout l'hiver")],
    "Mizuna / moutardes asiatiques": [rng("GSM", R(4, 11), label="plein champ"), rng("ADP", R(10, 2), label="semis d'août-sept., salade d'hiver")],
    "Salicorne": [rng("ML", R(5, 8), label="mi-mai-fin août ; arrêté Pas-de-Calais 2025 : 2 juin-31 août")],
    "Oronge (amanite des Césars)": [rng("CLC", R(8, 11), pic=R(9, 10), label="mi-sept.-mi-nov., dès mi-août dans le Sud-Ouest ; SDC : fortes cueillettes fin août-mi-oct.")],
    "Verveine citronnelle": [rng("PJ", R(6, 9), label="2 cueillettes : juin, puis août-sept.")],
    "Livèche": [rng("PJ", R(4, 10), pic={5, 6}, label="toute la végétation ; JM : printemps-automne ; mai-juin avant floraison")],
    "Ortie (jeunes pousses)": [rng("TPM", R(3, 5), label="début mars-mi-mai (régions alpines), plants < 20 cm")],
    "Pêche plate": [rng("BMS", R(7, 9))],
    "Prune Président": [rng("GRO", {9}, label="tardive : ~20 sept., étalée sur 15 jours")],
    "Nèfle du Japon (bibace)": [rng("JM", R(5, 6), label="mai-juin selon régions")],
    "Olive verte fraîche (à confire)": [rng("JM", R(9, 10), label="récoltées vertes sept.-oct., puis saumure")],
    "Oignon doux des Cévennes (AOP)": ("replace", [rng("ODC", R(8, 3), label="sur les étals de mi-août à mars ; récolte août-sept.")]),
    "Oignon rosé de Roscoff (AOP)": ("replace", [rng("OTR", R(8, 4), label="d'août à avril ; vente lancée à la fête de l'oignon (3e w-e d'août)")]),
    # ---- lot B : variétés de fruits, herbes, légumineuses
    "Pomme Elstar": ("replace", [rng("PPF", R(8, 3), label="vente août-mars"), rng("PJ", R(8, 9), label="récolte fin août-mi-sept.")]),
    "Pomme Granny Smith / Pink Lady / Fuji (tardives)": [
        rng("PPF", R(10, 5), label="Granny Smith : vente oct.-mai"),
        rng("PPF", R(11, 5), label="Pink Lady : vente nov.-mai ; cueillette fin oct.-début nov. (PL)"),
        rng("PPF", R(9, 6), label="Fuji : vente sept.-juin"),
    ],
    "Poire Williams": ("replace", [rng("PPF", R(8, 11), label="vente août-nov. (Williams et Williams rouge)"), rng("IF fiche poire", R(7, 11), label="sur les étals dès début juil. (fin non précisée, alignée sur PPF)")]),
    "Poire Louise-Bonne d'Avranches": [rng("PPF", R(10, 3), label="vente oct.-mars"), rng("WK", R(9, 10), label="maturité mi-sept.-mi-oct.")],
    "Poire Alexandrine Douillard": [rng("WK", R(9, 12), label="maturité sept.-oct., conservation 3 mois")],
    "Poire Passe-Crassane": ("replace", [rng("PPF", R(12, 5), label="vente déc.-mai")]),
    "Poire Angélys": ("replace", [rng("PPF", R(11, 4), label="vente nov.-avr. (« Angys »)"), rng("WK", R(12, 6), label="poire d'hiver, déc.-juin")]),
    "Poire Abate Fetel": [rng("PJ", R(9, 1), label="récolte mi-sept.-fin sept. ; conservation jusqu'en janv.")],
    "Poire Beurré Hardy": ("replace", [rng("JM", R(9, 10), label="récolte mi-sept.-oct., conservation 1-2 semaines"), rng("DBB", {9}, label="poires d'automne")]),
    "Fraise remontante (Charlotte, Mara des bois, Seascape…)": [rng("IF fiche fraise", R(5, 11), label="Charlotte mai-nov., Mara des bois mi-mai-oct."), rng("FDF", R(6, 10), label="Mara des bois juin-oct.")],
    "Figue violette de Solliès (AOP)": ("replace", [rng("FDS", R(8, 11), pic=R(9, 10), label="mi-août-mi-nov. ; pic de production 1er sept.-30 oct. (FreshPlaza)")]),
    "Figue Dauphine / Boule d'or (bifère)": [rng("PDB", R(6, 10), label="figues-fleurs fin juin-début août, figues d'automne mi-août-mi-oct.")],
    "Figue noire de Caromb": [rng("LAF", {6, 8, 9}, label="juin ; août-sept."), rng("COC", {7}, label="1re récolte en juillet")],
    "Figue fleur (1re récolte)": [rng("LAF", R(6, 7), label="juin (Marseille, Grise St-Jean, Caromb) ; juil. (Dalmatie, Longue d'Août, Dorée)")],
    "Arbouse": [rng("TLJ", R(10, 12)), rng("MV", {12}, label="« en hiver, autour de décembre »")],
    "Cédrat": [rng("WK", R(10, 11), label="cédrat de Corse : récolte 15 oct.-15 nov."), rng("CAN", R(9, 11))],
    "Bergamote": [rng("GB", R(12, 1), label="culture en France anecdotique")],
    "Yuzu": [rng("AAA", {9, 11, 12}, label="vert en sept., jaune nov.-mi-déc. (Armagnac)")],
    "Raisin Chasselas (de Moissac AOP)": ("replace", [fiche("Raisin", R(8, 10), label="fin août-fin oct."), rng("LN", R(8, 11), label="mi-août-nov.")]),
    "Raisin Muscat de Hambourg / du Ventoux": ("replace", [fiche("Raisin", R(8, 10), label="début août-mi-oct."), rng("LN", R(8, 11), label="fin août-début nov.")]),
    "Raisin Italia": ("replace", [rng("LN", R(9, 12))]),
    "Raisin Alphonse Lavallée": ("replace", [fiche("Raisin", R(8, 10), label="mi-août-mi-oct."), rng("LN", R(8, 10), label="fin août-oct.")]),
    "Raisin Danlas": ("replace", [rng("LN", R(8, 9), label="mi-août-sept.")]),
    "Raisin Cardinal": ("replace", [rng("LN", R(7, 8), label="fin juil.-août")]),
    "Coriandre": ("replace", [rng("JM", R(5, 10), label="récolte mai-oct."), rng("ML", {3, 4, 5, 7, 8}, label="Coriandre")]),
    "Basilic": ("replace", [rng("IF fiche herbes", ALL, pic={7, 8}, label="feuilles toute l'année, pleine saison juil.-août"), rng("ML", R(5, 8), label="Basilic"), rng("JM", R(6, 8), label="récolte : été")]),
    "Ciboulette": ("replace", [rng("PJ", R(4, 10), label="fin avr.-premières gelées"), rng("ML", R(3, 5), label="Ciboulette (hors pots d'intérieur)")]),
    "Tomates anciennes (noire de Crimée, ananas, green zebra…)": ("replace", [rng("ADP", R(6, 10), label="Green Zebra juil.-oct., Noire de Crimée juin-sept. ; Ananas sans mois lu"), rng("GF", {9}, "SEPT")]),
    "Haricot tarbais frais": ("replace", [rng("WK", R(8, 9), label="grain frais en gousses fin août-début sept.")]),
    "Flageolet frais": ("replace", [rng("BAK", R(7, 9), label="stade demi-sec"), rng("PRO", {9}, label="campagne du flageolet en sept.")]),
    "Prune japonaise (Angeleno, Friar, Black Amber)": ("replace", [fiche("Prune", R(7, 9), label="Black Amber ~20 juil., Friar un mois plus tard, Angeleno mi-sept.")]),
    "Noix sèche (nouvelle récolte)": ("replace", [rng("IF fiche noix", R(10, 12), label="en rayon début oct. ; PNA : ramassage début oct. ; TD : Grenoble ~10 j après le 26 sept."), rng("BNA", {11, 12, 1}, label="noix")]),
    "Pêche de vigne": [rng("JM", R(9, 10), label="maturité sept.-oct. selon régions")],
}

NOTES = {
    "Bergamote": "Culture en France anecdotique (GB).",
    "Cornichon": "Terre Vivante seule lue ; Kokopelli (juin/juil.-sept.) via résumé.",
    "Asperge sauvage": "Espèce protégée dans plusieurs régions (AJ).",
    "Pomme Elstar": "Vente août-mars (PPF), récolte fin août-mi-sept. (PJ) : la source FM (mi-août-sept.) est remplacée.",
    "Noix sèche (nouvelle récolte)": "Le calendrier IF « Noix » (noix sèche disponible toute l'année) n'est pas compté pour ce produit.",
    "Chou de Pontoise": "Une seule source (semencier).",
    "Prune Président": "Une seule source (pépiniériste).",
    "Poire Alexandrine Douillard": "Absente du tableau PPF ; Wikipédia seule.",
    "Fraise remontante (Charlotte, Mara des bois, Seascape…)": "Le cœur de saison IF « Fraise » (mars-juin) vaut pour les non remontantes.",
}
