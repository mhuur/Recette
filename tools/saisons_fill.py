# -*- coding: utf-8 -*-
"""Remplit les 12 colonnes mois de data/saisons/saisons.csv à partir des sources.

Sources 12 mois (copies dans data/saisons/sources/) :
  FL  fruits-legumes-org.json      (de saison / pleine saison)
  IF  interfel-12mois.json         (month-* = de saison, coeur = cœur de saison, dispo = simple disponibilité, non comptée)
  GP  greenpeace-12mois.json       (guide PDF 2022, pages 2-3)
  BNA bna-12mois.json              (calendrier PDF Bio Nouvelle-Aquitaine)
Sources à période (relevées à la main sur les pages, cf. SOURCES.md) : SM, ML, MC, FM, PDT, LN, DNC, VD, CJ, IF fiche, WEB…
Sources « septembre seulement » (listes d'un mois) : GF, DBB, CV, BM, PG, CDC.

Règle par mois : chaque source à couverture annuelle vote « oui » (mois listé) ou « non ».
  ● pleine saison (2) : mois listé par une majorité (égalité = oui) ET « pleine saison » chez FL, cœur chez IF (si le cœur
    ne couvre pas les 12 mois) ou source explicite.
  ● de saison (1)     : mois listé par une majorité (égalité = oui).
  vide                : aucune source ne le donne (ou minorité).
  ?                   : aucune source pour ce produit.
La colonne SEPTEMBRE suit la même règle ; les écarts avec la relecture manuelle du 2026-09-16 sont affichés.

Usage : py tools/saisons_fill.py [--check]   (--check : n'écrit rien, affiche seulement les écarts septembre)
"""
import csv
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "data", "saisons")
CSV_PATH = os.path.join(DIR, "saisons.csv")
SRC = os.path.join(DIR, "sources")

ABBR = ["jan.", "fév.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
FR = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
ALL = set(range(1, 13))


def strip(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower().strip()


def R(a, b=None):
    """Plage de mois, bouclante : R(11, 2) = {11, 12, 1, 2}."""
    if b is None:
        b = a
    out, m = set(), a
    while True:
        out.add(m)
        if m == b:
            return out
        m = m % 12 + 1


# ---------------------------------------------------------------- sources 12 mois
with open(os.path.join(SRC, "fruits-legumes-org.json"), encoding="utf-8") as f:
    _fl = json.load(f)
FL = {}
for v in _fl.values():
    FL[strip(v["name"])] = (set(FR.index(m) + 1 for m in v["mois"]), set(FR.index(m) + 1 for m in v["pic"]))

with open(os.path.join(SRC, "interfel-12mois.json"), encoding="utf-8") as f:
    _if = json.load(f)
IF = {}
for name, v in _if.items():
    months = set(v["months"]) | set(v["coeur"]) | set(v["saison"])
    coeur = set(v["coeur"])
    if len(coeur) == 12:  # cœur toute l'année = information vide
        coeur = set()
    IF[strip(name)] = (months, coeur)

with open(os.path.join(SRC, "greenpeace-12mois.json"), encoding="utf-8") as f:
    _gp = json.load(f)
GP = {}
for name, v in _gp.items():
    k = strip(name).replace("ppamplemousse", "pamplemousse")
    GP.setdefault(k, set()).update(v)

with open(os.path.join(SRC, "bna-12mois.json"), encoding="utf-8") as f:
    _bna = json.load(f)
BNA = {}
for name, v in _bna.items():
    k = strip(name).replace("choux-de-bruxelles", "choux de bruxelles")
    BNA.setdefault(k, set()).update(v)

FULL = {"FL": FL, "IF": IF, "GP": GP, "BNA": BNA}


def src(code, name):
    """Référence à une source 12 mois : (code, mois, pleine, libellé)."""
    table = FULL[code]
    k = strip(name)
    if k not in table:
        raise KeyError(f"{code}: « {name} » absent ({k})")
    v = table[k]
    months, pic = (v, set()) if isinstance(v, set) else v
    return (code, months, pic, name)


def rng(code, months, pic=None, label=""):
    """Source à période relevée à la main (couverture annuelle supposée)."""
    return (code, set(months), set(pic or ()), label)


def fiche(species, months, label=""):
    """Variété lue sur une fiche Interfel : sa fenêtre, en pleine saison là où la fiche de l'espèce est en cœur de saison."""
    _, coeur = IF[strip(species)]
    return (f"IF fiche {species.lower()}", set(months), set(months) & coeur, label)


def sept(*codes):
    """Sources dont on ne connaît que la liste de septembre."""
    return [(c, {9}, set(), "SEPT") for c in codes]


# ---------------------------------------------------------------- sources à période (relevé manuel)
SM = {  # Swissmilk, choux-de-saison (lu le 2026-09-16)
    "Brocoli": R(5, 11), "Chou blanc": ALL, "Chou chinois": R(5, 3), "Chou frisé": ALL, "Chou kale": R(10, 3),
    "Chou pointu": R(6, 2), "Chou romanesco": R(5, 11), "Chou rouge": ALL, "Chou-fleur": R(5, 11),
    "Choux de Bruxelles": R(9, 1), "Cima di rapa": R(4, 10), "Colrave": R(4, 11), "Kalettes": R(11, 3),
    "Pak choï": R(4, 11), "Rutabaga": R(7, 4),
}
MLC = {  # Mangeons local .bzh, saison-courge
    "Potiron": R(10, 1), "Citrouille": R(10, 1), "Pâtisson": R(8, 10), "Potimarron": R(9, 12), "Butternut": R(9, 3),
    "Courge de Nice": R(9, 11), "Courge musquée de Provence": R(7, 11), "Courge spaghetti": R(9, 11),
}
MLA = {  # Mangeons local .bzh, aromatiques-calendrier (mois par mois)
    "Ciboulette": R(3, 5) | {10, 11, 12, 1, 2}, "Persil": {1, 2, 3, 4, 6, 9, 10, 11}, "Laurier": {1, 2, 10, 11, 12},
    "Thym": {1, 2, 6, 7, 8, 9, 10, 11, 12}, "Romarin": {1, 2, 6, 7, 8, 9, 10, 11, 12}, "Estragon": R(3, 9),
    "Menthe": R(3, 9), "Cerfeuil": {3, 4, 9}, "Ail des ours": {3, 4}, "Coriandre": {3, 4, 5, 7, 8}, "Origan": R(3, 8),
    "Basilic": R(5, 8), "Aneth": R(5, 8), "Sauge": {5, 6, 9}, "Mélisse": R(5, 11), "Sarriette": R(6, 9),
    "Bourrache": {7, 8}, "Fenouil": {7, 8}, "Lavande": {7, 8},
}
MC = {  # Mycocarta, guides/saisons (relevé du 2026-09-16)
    "Morille": R(3, 5), "Mousseron": R(4, 5), "Girolle": R(6, 11), "Cèpe": R(8, 11), "Pied de mouton": R(8, 11),
    "Trompette de la mort": R(9, 12), "Coulemelle": R(9, 10), "Rosé des prés": R(7, 10), "Lactaire délicieux": R(9, 11),
    "Pied bleu": R(9, 2), "Truffe noire": R(11, 2), "Pleurote": R(10, 2),
}
FM = {  # La Ferme de Margaux, tableau de disponibilité (sept. → mai) + tableau récapitulatif
    "Vergheat": {9}, "Akane": R(9, 11), "Reine des reinettes": R(9, 12), "Golden": R(10, 3), "Reinette grise du Canada": R(10, 3),
    "Belle de Boskoop": R(11, 3), "Chantecler": R(11, 3), "Elstar": R(8, 9), "Transparente de Croncels": R(7, 8),
}


def sm(n): return rng("SM", SM[n], label=n)
def mlc(n): return rng("ML", MLC[n], label=n)
def mla(n): return rng("ML", MLA[n], label=n)
def mc(n): return rng("MC", MC[n], label=n)
def fm(n): return rng("FM", FM[n], label=n)


# ---------------------------------------------------------------- mappage produit → sources
# « = X » : valeurs et sources reprises du produit X (variété non distinguée par les sources).
P = {}
def m(name, *refs):
    P[name] = list(refs)

# Alliacées
m("Ail sec (de garde)", src("FL", "Ail"), src("GP", "Ail"), src("IF", "Ail"), src("BNA", "ail"), *sept("CV", "BM"))
m("Ail frais / ail nouveau", fiche("Ail", R(6, 7)), rng("FL fiche ail", R(5, 7)))
m("Ail rose de Lautrec (Label rouge)", "= Ail sec (de garde)")
m("Ail violet de Cadours (AOP)", "= Ail sec (de garde)")
m("Ail fumé d'Arleux", "= Ail sec (de garde)")
m("Aillet (ail vert)", src("BNA", "aillet"))
m("Ail des ours", mla("Ail des ours"))
m("Oignon jaune (de garde)", src("FL", "Oignon"), src("IF", "Oignon"), src("GP", "Oignon"), src("BNA", "oignon"), src("BNA", "oignon sec"), *sept("CV", "BM", "PG"))
m("Oignon rouge", src("FL", "Oignon rouge"), src("IF", "Oignon"))
m("Oignon doux des Cévennes (AOP)", "= Oignon jaune (de garde)")
m("Oignon rosé de Roscoff (AOP)", "= Oignon jaune (de garde)")
m("Oignon blanc / oignon nouveau (botte)", src("FL", "Petit oignon blanc"), src("IF", "Oignon Primeur"), src("BNA", "oignon blanc"))
m("Cébette / ciboule", src("IF", "Oignon Primeur"), src("FL", "Petit oignon blanc"))
m("Échalote", src("IF", "Échalote"), src("BNA", "échalote"), src("GP", "Échalote"), *sept("PG"))
m("Échalote grise", "= Échalote")
m("Poireau", src("FL", "Poireau"), src("GP", "Poireau"), src("IF", "Poireau"), src("BNA", "poireau"), *sept("CV", "PG"))
m("Poireau primeur", *sept("GF"))
m("Asperge blanche", src("FL", "Asperge blanche"), src("IF", "Asperge"), src("GP", "Asperge"), src("BNA", "asperge"))
m("Asperge verte", src("FL", "Asperge verte"), src("IF", "Asperge"), src("GP", "Asperge"), src("BNA", "asperge"))
m("Asperge violette", "= Asperge blanche")
m("Asperge sauvage")
# Choux
m("Chou blanc (cabus)", src("FL", "Chou blanc"), src("GP", "Chou"), src("IF", "Chou pommé"), src("BNA", "choux"), sm("Chou blanc"), *sept("BM"))
m("Chou rouge", src("FL", "Chou rouge"), src("GP", "Chou"), src("IF", "Chou rouge"), sm("Chou rouge"), *sept("GF"))
m("Chou vert (cabus lisse)", src("FL", "Chou vert"), src("GP", "Chou"), src("IF", "Chou pommé"), src("BNA", "choux"))
m("Chou vert frisé / chou de Milan", src("FL", "Chou frisé"), src("GP", "Chou"), sm("Chou frisé"))
m("Chou kale", src("IF", "Chou kale"), sm("Chou kale"), *sept("GF"))
m("Chou pointu", sm("Chou pointu"))
m("Chou de Bruxelles", src("FL", "Chou de Bruxelles"), src("GP", "Chou"), src("IF", "Choux de Bruxelles"), src("BNA", "choux de bruxelles"), sm("Choux de Bruxelles"))
m("Chou de Pontoise")
m("Chou-fleur", src("FL", "Chou-fleur"), src("GP", "Chou-fleur"), src("IF", "Chou-fleur"), src("BNA", "chou-fleur"), sm("Chou-fleur"), *sept("DBB", "CV", "BM"))
m("Chou-fleur coloré (vert, violet, orange)", *sept("DBB"))
m("Chou romanesco", src("FL", "Chou Romanesco"), src("GP", "Chou romanesco"), sm("Chou romanesco"), *sept("DBB"))
m("Brocoli", src("FL", "Brocoli"), src("GP", "Brocoli"), src("IF", "Brocoli"), src("BNA", "brocoli"), sm("Brocoli"), *sept("GF", "DBB", "CV", "BM", "PG"))
m("Brocoli à jets violet")
m("Chou-rave", src("FL", "Chou-rave"), sm("Colrave"))
m("Chou chinois (pé-tsaï)", src("FL", "Chou-chinois"), sm("Chou chinois"))
m("Pak choï", src("FL", "Pak choï"), sm("Pak choï"))
m("Cima di rapa (brocoli-rave)", src("FL", "Cima di Rapa"), sm("Cima di rapa"))
m("Kalettes (chou-fleur de Bruxelles)", sm("Kalettes"))
# Courges
m("Courgette", src("FL", "Courgette"), src("GP", "Courgette"), src("IF", "Courgette"), src("BNA", "courgette"), *sept("GF", "DBB", "CV", "BM"))
m("Courgette ronde / jaune", "= Courgette")
m("Fleur de courgette")
m("Pâtisson", src("FL", "Pâtisson"), mlc("Pâtisson"))
m("Potimarron", src("FL", "Potimarron"), mlc("Potimarron"), src("BNA", "potimarron"), *sept("GF", "BM"))
m("Potiron", src("FL", "Potiron"), src("IF", "Potiron"), src("GP", "Potiron"), src("GP", "Courge"), src("BNA", "potiron"), mlc("Potiron"), *sept("GF", "BM", "PG", "CV"))
m("Citrouille", src("FL", "Citrouille"), mlc("Citrouille"))
m("Butternut (doubeurre)", src("FL", "Butternut"), mlc("Butternut"))
m("Courge spaghetti", src("FL", "Courge spaghetti"), mlc("Courge spaghetti"))
m("Courge musquée de Provence", src("FL", "Courge musquée"), mlc("Courge musquée de Provence"))
m("Courge longue de Nice", mlc("Courge de Nice"))
m("Sucrine du Berry", src("FL", "Sucrine du Berry"))
m("Courge (autres : Jack be little, Delicata, Bleue de Hongrie, Hokkaido…)", src("FL", "Courge"), src("GP", "Courge"), src("IF", "Courges et potirons"), src("BNA", "courge"))
m("Chayotte (christophine)", src("FL", "Chayote"))
m("Concombre", src("FL", "Concombre"), src("GP", "Concombre"), src("IF", "Concombre"), src("BNA", "concombre"), *sept("DBB", "CV", "BM"))
m("Cornichon")
# Solanacées
m("Tomate ronde / grappe", src("FL", "Tomate"), src("GP", "Tomate"), src("IF", "Tomate"), src("BNA", "tomate"), *sept("GF", "DBB", "CV", "BM"))
m("Tomate cerise / cocktail", "= Tomate ronde / grappe")
m("Tomate cœur de bœuf", src("FL", "Tomate charnue"), *sept("GF"))
m("Tomates anciennes (noire de Crimée, ananas, green zebra…)", rng("recherche", R(8, 10)), *sept("GF"))
m("Tomate allongée (Roma, San Marzano, Peretti)", src("FL", "Tomate Peretti"))
m("Tomate verte (à confire)")
m("Aubergine", src("FL", "Aubergine"), src("GP", "Aubergine"), src("IF", "Aubergine"), src("BNA", "aubergine"), *sept("GF", "DBB", "CV"))
m("Poivron", src("FL", "Poivron"), src("GP", "Poivron"), src("IF", "Poivron"), src("BNA", "poivron"), *sept("GF", "DBB", "CV", "BM"))
m("Piment (doux des Landes, d'Espelette…)", src("FL", "Piment"))
m("Pomme de terre de conservation", src("FL", "Pomme de terre"), src("BNA", "pomme de terre"), rng("PDT", R(8, 4), label="conservation : de la récolte (15 août) au printemps"), *sept("GP", "GF", "CV", "BM", "PG"))
m("Pomme de terre primeur / nouvelle", rng("PDT", R(4, 8), label="avr. → 15 août"), src("BNA", "pomme de terre primeur"), rng("GP", R(4, 8), label="site guetteur"))
m("Pomme de terre grenaille")
m("Vitelotte", "= Pomme de terre de conservation")
m("Ratte (du Touquet)")
# Légumineuses
m("Haricot vert", src("IF", "Haricot vert"), src("FL", "Haricot"), src("GP", "Haricot vert"), src("BNA", "haricot vert"), *sept("DBB", "CV", "BM"))
m("Haricot beurre", "= Haricot vert")
m("Haricot plat / mange-tout", src("IF", "Haricot vert"), src("BNA", "haricots plats"))
m("Coco de Paimpol (AOP) / cocos frais", src("FL", "Haricot coco"), src("BNA", "haricot à écosser"))
m("Mogette de Vendée (fraîche / demi-sèche)", *sept("PG"))
m("Haricot tarbais frais", rng("recherche", R(7, 9)))
m("Flageolet frais", rng("recherche", R(7, 9)))
m("Petit pois", src("FL", "Petit pois"), src("GP", "Petit pois"), src("IF", "Petit pois"), src("BNA", "petit pois"))
m("Pois gourmand / mange-tout", src("FL", "Pois mange-tout"))
m("Fève", src("BNA", "fève"), src("IF", "Fève"))
m("Maïs doux (épi)", src("FL", "Maïs"), src("BNA", "maïs doux"), *sept("GP", "CV"))
m("Germe de haricot mungo (soja vert)", src("IF", "Germe de haricot mungo Soja vert"))
# Racines
m("Carotte", src("FL", "Carotte"), src("GP", "Carotte"), src("IF", "Carotte"), src("BNA", "carotte"), *sept("GF", "CV", "BM", "PG"))
m("Carotte nouvelle (botte)", src("IF", "Carotte primeur"))
m("Betterave rouge", src("FL", "Betterave rouge"), src("GP", "Betterave"), src("IF", "Betterave"), src("BNA", "betterave"), *sept("GF", "CV"))
m("Betterave Chioggia / jaune", "= Betterave rouge")
m("Navet", src("FL", "Navet"), src("GP", "Navet"), src("IF", "Navet"), src("BNA", "navet"), *sept("GF", "PG"))
m("Navet boule d'or", "= Navet")
m("Radis rose (botte)", src("FL", "Radis"), src("GP", "Radis"), src("IF", "Radis"), src("BNA", "radis rose"), src("BNA", "radis"), *sept("CV", "BM"))
m("Radis noir", src("FL", "Radis noir"), src("BNA", "radis noir"))
m("Radis long / demi-long", src("FL", "Radis long"))
m("Radis daikon (blanc japonais)")
m("Panais", src("FL", "Panais"), src("GP", "Panais"), src("IF", "Panais"), src("BNA", "panais"), *sept("GF", "PG"))
m("Céleri-rave", src("FL", "Céleri rave"), src("IF", "Céleri-rave"), src("GP", "Céleri-rave"), src("GP", "Céleri"), src("BNA", "céleri"), *sept("PG", "CV"))
m("Céleri-branche", src("FL", "Céleri branche"), src("IF", "Céleri-branche"), src("GP", "Céleri-branche"), src("BNA", "céleri branche"), *sept("GF", "DBB", "PG"))
m("Rutabaga", sm("Rutabaga"), src("GP", "Rutabaga"), src("IF", "Rutabaga"), src("BNA", "rutabaga"))
m("Topinambour", src("FL", "Topinambour"), src("GP", "Topinambour"), src("IF", "Topinambour"), src("BNA", "topinambour"))
m("Crosne", src("GP", "Crosne"), src("BNA", "crosne"), rng("VD", R(9, 3), label="via résumé"), *sept("PG"))
m("Salsifis / scorsonère", src("FL", "Salsifis"), src("GP", "Salsifi"), src("BNA", "salsifis"))
m("Patate douce", src("FL", "Patate douce"), src("GP", "Patate douce"), src("IF", "Patate douce"), *sept("BM"))
m("Cerfeuil tubéreux")
m("Persil tubéreux (racine)")
m("Raifort")
# Feuilles & salades
m("Laitue pommée (beurre)", src("IF", "Laitue"), src("GP", "Laitue"), src("BNA", "salade"), *sept("CV", "BM"))
m("Batavia", "= Laitue pommée (beurre)")
m("Feuille de chêne", src("FL", "Feuille de chêne"), src("IF", "Salade"))
m("Romaine", src("FL", "Laitue romaine"))
m("Sucrine", "= Laitue pommée (beurre)")
m("Iceberg", "= Laitue pommée (beurre)")
m("Rougette", "= Laitue pommée (beurre)")
m("Frisée", src("FL", "Frisée"), src("GP", "Frisée"), src("IF", "Chicorée"), src("BNA", "frisée"))
m("Scarole", src("IF", "Chicorée"))
m("Trévise / radicchio", src("IF", "Chicorée"))
m("Chicorée pain de sucre", src("IF", "Chicorée"))
m("Catalogne / puntarelle", src("FL", "Catalonia"))
m("Endive", src("FL", "Endive"), src("GP", "Endive"), src("IF", "Endive"), src("BNA", "endive"))
m("Mâche", src("FL", "Mâche"), src("GP", "Mâche"), src("IF", "Mâche"), src("BNA", "mâche"))
m("Roquette", src("FL", "Roquette"), *sept("DBB", "GP"))
m("Cresson", src("FL", "Cresson"), src("IF", "Cresson"), *sept("CV"))
m("Pourpier", src("IF", "Pourpier"), *sept("GP"))
m("Pissenlit", rng("IF fiche salade", ALL, label="toute l'année"))
m("Pousses d'épinard / mesclun", src("IF", "Salade"))
m("Épinard", src("FL", "Epinard"), src("GP", "Épinard"), src("IF", "Épinard"), src("BNA", "épinard"), *sept("DBB"))
m("Blette / bette à carde", src("FL", "Bette"), src("GP", "Blette"), src("IF", "Blette"), src("BNA", "blette"), *sept("GF", "DBB", "CV"))
m("Oseille", src("IF", "Oseille"))
m("Tétragone", src("FL", "Tétragone"))
m("Mizuna / moutardes asiatiques")
m("Cardon", src("GP", "Cardon"), src("BNA", "cardon"))
# Tiges & fleurs
m("Fenouil", src("FL", "Fenouil"), src("GP", "Fenouil"), src("IF", "Fenouil"), src("BNA", "fenouil"), *sept("DBB", "CV"))
m("Artichaut (camus, gros)", src("FL", "Artichaut"), src("GP", "Artichaut"), src("IF", "Artichaut"), src("BNA", "artichaut"), *sept("DBB", "CV"))
m("Artichaut violet / poivrade", "= Artichaut (camus, gros)")
m("Rhubarbe", src("IF", "Rhubarbe"), src("FL", "Rhubarbe"), src("GP", "Rhubarbe"), src("BNA", "rhubarbe"))
m("Salicorne")
# Champignons
m("Champignon de Paris", src("FL", "Champignon de Paris"), src("IF", "Champignon de Paris"), *sept("GF"))
m("Pleurote", src("IF", "Champignons cultivés"), mc("Pleurote"))
m("Shiitaké", src("FL", "Shiitaké"), src("IF", "Champignons cultivés"))
m("Cèpe / bolets", src("FL", "Cèpe"), src("IF", "Cèpe"), mc("Cèpe"), *sept("GP", "GF", "DBB", "CDC"))
m("Girolle / chanterelle", src("FL", "Girolle"), mc("Girolle"), *sept("GF", "CDC"))
m("Chanterelle en tube / grise", "= Girolle / chanterelle")
m("Trompette de la mort", src("FL", "Trompette de la mort"), mc("Trompette de la mort"), *sept("GF"))
m("Pied de mouton", src("FL", "Pied de mouton"), mc("Pied de mouton"), *sept("CDC"))
m("Coulemelle", mc("Coulemelle"), *sept("CDC"))
m("Rosé des prés", src("FL", "Rosé des prés"), mc("Rosé des prés"), *sept("CDC"))
m("Lactaire délicieux (sanguin)", mc("Lactaire délicieux"), *sept("CDC"))
m("Pied bleu", mc("Pied bleu"))
m("Oronge (amanite des Césars)", *sept("CDC"))
m("Morille", mc("Morille"), src("IF", "Morille"))
m("Mousseron (tricholome de la Saint-Georges)", mc("Mousseron"))
m("Truffe de Bourgogne / truffe d'été", src("IF", "Truffe"))
m("Truffe noire du Périgord", mc("Truffe noire"))
# Herbes
m("Persil", src("IF", "Persil"), mla("Persil"), *sept("GF"))
m("Basilic", mla("Basilic"), rng("recherche", R(5, 9), label="pleine saison juil.-août, via résumé"))
m("Ciboulette", mla("Ciboulette"), rng("recherche", R(4, 9), label="via résumé"))
m("Coriandre", mla("Coriandre"), rng("recherche", R(8, 10), label="via résumé"))
m("Estragon", mla("Estragon"))
m("Menthe", mla("Menthe"), rng("recherche", R(6, 9)))
m("Aneth", mla("Aneth"), rng("recherche", R(6, 9)), *sept("GF"))
m("Cerfeuil", mla("Cerfeuil"), rng("recherche", R(6, 9)))
m("Sauge", mla("Sauge"))
m("Thym", mla("Thym"))
m("Romarin", mla("Romarin"))
m("Laurier", src("FL", "Laurier"), mla("Laurier"))
m("Origan / marjolaine", mla("Origan"))
m("Sarriette", mla("Sarriette"))
m("Mélisse", mla("Mélisse"))
m("Bourrache", mla("Bourrache"))
m("Verveine citronnelle")
m("Livèche")
m("Ortie (jeunes pousses)")
# Fruits à noyau
m("Pêche jaune", src("FL", "Pêche"), src("GP", "Pêche"), src("IF", "Pêche, Nectarine"), src("BNA", "pêche"), *sept("DBB", "CV", "BM"))
m("Pêche blanche", "= Pêche jaune")
m("Pêche plate")
m("Pêche de vigne", fiche("Pêche, Nectarine", R(9, 10), label="variété tardive"), src("BNA", "pêche de vigne"))
m("Nectarine", src("FL", "Nectarine"), src("IF", "Pêche, Nectarine"), src("GP", "Nectarine"), *sept("BM"))
m("Brugnon", fiche("Pêche, Nectarine", R(7, 9)), src("GP", "Brugnon"), src("BNA", "brugnon"))
m("Abricot", src("FL", "Abricot"), src("GP", "Abricot"), src("IF", "Abricot"), src("BNA", "abricot"))
m("Cerise", src("FL", "Cerise"), src("GP", "Cerise"), src("IF", "Cerise"), src("BNA", "cerise"))
m("Reine-claude (dorée, de Bavay)", src("FL", "Reine-claude"), fiche("Prune", R(8, 9), label="Bavay mi-sept."))
m("Mirabelle", src("FL", "Mirabelle"), src("GP", "Mirabelle"), src("IF", "Mirabelle"), src("BNA", "mirabelle"), *sept("DBB", "CV", "BM"))
m("Quetsche", src("FL", "Quetsche"), src("IF", "Prune"), *sept("CV"))
m("Prune d'Ente (pruneau frais)", src("GP", "Pruneau"), src("BNA", "pruneau"), *sept("BM"))
m("Prune Président")
m("Prune japonaise (Angeleno, Friar, Black Amber)", fiche("Prune", R(8, 9), label="Friar ~20 août, Angeleno mi-sept."))
m("Prune (toutes variétés)", src("FL", "Prune"), src("GP", "Prune"), src("IF", "Prune"), src("BNA", "prune"), *sept("DBB", "CV", "BM"))
m("Jujube", src("FL", "Jujube"))
m("Nèfle du Japon (bibace)")
m("Olive verte fraîche (à confire)")
# Pépins
m("Pomme (toutes variétés)", src("FL", "Pomme"), src("GP", "Pomme"), src("IF", "Pomme"), src("BNA", "pomme"), *sept("DBB", "CV", "BM", "PG"))
m("Pomme d'été précoce (Delbard Estivale, Vergheat, Akane…)", fm("Vergheat"), fm("Akane"), fm("Transparente de Croncels"), src("BNA", "pomme d'été"))
m("Pomme Reine des reinettes", rng("FM", R(8, 12), pic={8, 9}, label="tableau sept.-déc. ; texte : « pleine saison » mi-août-sept."), rng("recherche", R(8, 9), label="récolte fin août-sept."), *sept("DBB"))
m("Pomme Gala / Royal Gala", rng("recherche", R(8, 9), label="récolte fin août-début sept., via résumé"), *sept("DBB"))
m("Pomme Golden", fm("Golden"), *sept("DBB"))
m("Pomme Elstar", fm("Elstar"))
m("Pomme Reinette grise du Canada", fm("Reinette grise du Canada"))
m("Pomme Belle de Boskoop", fm("Belle de Boskoop"))
m("Pomme Chantecler", fm("Chantecler"))
m("Pomme Granny Smith / Pink Lady / Fuji (tardives)")
m("Poire (toutes variétés)", src("FL", "Poire"), src("GP", "Poire"), src("IF", "Poire"), src("BNA", "poire"), *sept("CV", "BM", "PG"))
m("Poire Williams", fiche("Poire", R(7, 9), label="dès juillet"))
m("Poire Guyot", fiche("Poire", R(7, 8)), src("BNA", "poire guyot"))
m("Poire Conférence", fiche("Poire", R(9, 4)))
m("Poire Comice", fiche("Poire", R(9, 12)))
m("Poire Beurré Hardy", fiche("Poire", R(9, 11), label="automne"), *sept("DBB"))
m("Poire Louise-Bonne d'Avranches", *sept("DBB"))
m("Poire Alexandrine Douillard", *sept("DBB"))
m("Poire Passe-Crassane", fiche("Poire", R(12, 3), label="hiver"))
m("Poire Angélys", rng("FL fiche poire", R(1, 3), label="après Conférence et Comice"))
m("Poire Abate Fetel")
m("Nashi", src("FL", "Nashi"))
m("Coing", src("FL", "Coing"), src("GP", "Coing"), src("IF", "Coing"), src("BNA", "coing"), *sept("DBB", "CV", "PG"))
# Petits fruits
m("Fraise remontante (Charlotte, Mara des bois, Seascape…)", src("BNA", "fraise"), *sept("DBB"))
m("Fraise Gariguette / Ciflorette (non remontantes)", src("FL", "Fraise"), src("GP", "Fraise"), src("IF", "Fraise"))
m("Fraise des bois", src("FL", "Fraise des bois"))
m("Framboise (remontante)", src("FL", "Framboise"), src("IF", "Framboise"), src("GP", "Framboise"), src("BNA", "framboise"), *sept("DBB"))
m("Mûre", src("FL", "Mûre"), src("GP", "Mûre"), src("IF", "Mûre"), src("BNA", "mûre"), *sept("DBB", "CV", "BM"))
m("Myrtille", src("FL", "Myrtille"), src("GP", "Myrtille"), src("IF", "Myrtille"), src("BNA", "myrtille"), *sept("DBB", "CV", "BM"))
m("Groseille", src("FL", "Groseille"), src("IF", "Groseille"), src("GP", "Groseille"), src("BNA", "groseille"))
m("Groseille à maquereau", src("FL", "Groseille à maquereau"))
m("Cassis", src("FL", "Cassis"), src("IF", "Cassis"), src("GP", "Cassis"), src("BNA", "cassis"), *sept("DBB"))
m("Airelle rouge", src("FL", "Airelle"))
m("Cranberry (canneberge)", src("FL", "Cranberry"))
m("Sureau (baies)", src("FL", "Sureau"))
m("Argousier", src("FL", "Argousier"))
m("Aronia", src("FL", "Aronia"))
m("Cornouille", src("FL", "Cornouille"))
m("Baie de goji", src("FL", "Baie de goji"), src("GP", "Baie de goji"))
m("Kiwaï", src("FL", "Kiwaï"))
m("Physalis (coqueret du Pérou)", src("FL", "Physalis"), src("GP", "Physalis"), src("IF", "Physalis"))
m("Arbouse")
# Raisin & figue
m("Raisin (toutes variétés)", src("FL", "Raisin"), src("GP", "Raisin"), src("IF", "Raisin"), src("BNA", "raisin"), *sept("DBB", "CV", "BM", "PG"))
m("Raisin Chasselas (de Moissac AOP)", fiche("Raisin", R(8, 10), label="fin août-fin oct."), rng("LN", R(8, 11), label="via résumé"))
m("Raisin Muscat de Hambourg / du Ventoux", fiche("Raisin", R(8, 10), label="début août-mi-oct."), rng("LN", R(8, 10), label="via résumé"))
m("Raisin Italia", rng("LN", R(9, 12), label="via résumé"))
m("Raisin Alphonse Lavallée", fiche("Raisin", R(8, 10), label="mi-août-mi-oct."), rng("LN", R(8, 10), label="via résumé"))
m("Raisin Danlas", rng("LN", R(8, 9), label="via résumé"))
m("Raisin Cardinal", rng("LN", R(7, 8), label="via résumé"))
m("Raisin sans pépins (Centennial, Sultanine…)", src("IF", "Raisin"))
m("Figue (toutes variétés)", src("FL", "Figue fraîche"), src("GP", "Figue"), src("IF", "Figue"), src("BNA", "figue"), *sept("DBB", "CV", "BM", "PG"))
m("Figue violette de Solliès (AOP)", "= Figue (toutes variétés)")
m("Figue Dauphine / Boule d'or (bifère)", *sept("IF"))
m("Figue noire de Caromb", *sept("IF"))
m("Figue noire de Bursa (import Turquie)", fiche("Figue", R(7, 10), label="mi-juil.-oct."))
m("Figue fleur (1re récolte)")
# Melon
m("Melon charentais (jaune, vert)", src("FL", "Melon"), src("GP", "Melon"), src("IF", "Melon"), src("BNA", "melon"), *sept("DBB", "CV", "BM"))
m("Melon Galia / canari / brodé / piel de sapo", src("IF", "Melon"))
m("Pastèque", src("FL", "Pastèque"), src("GP", "Pastèque"), src("IF", "Pastèque"), src("BNA", "pastèque"), *sept("CV", "BM", "PG"))
# Agrumes
m("Citron", src("FL", "Citron"), src("GP", "Citron"), src("IF", "Citron, Citron vert"), src("BNA", "citron"))
m("Clémentine", src("FL", "Clémentine"), src("GP", "Clémentine"), src("IF", "Clémentine, Mandarine"), src("BNA", "clémentine"))
m("Mandarine", src("FL", "Mandarine"), src("GP", "Mandarine"), src("IF", "Clémentine, Mandarine"))
m("Orange", src("FL", "Orange"), src("GP", "Orange"), src("IF", "Orange"))
m("Orange sanguine", src("FL", "Orange sanguine"))
m("Pamplemousse / pomelo", src("FL", "Pamplemousse"), src("GP", "Pamplemousse"), src("IF", "Pomelo"), src("BNA", "pomelos"))
m("Kumquat", src("FL", "Kumquat"))
m("Cédrat")
m("Bergamote")
m("Yuzu")
# À coque
m("Noix fraîche", src("FL", "Noix"), src("GP", "Noix"), src("BNA", "noix fraîche"), rng("DNC", R(9, 10), label="mi-sept.-oct., via résumé"), *sept("BM", "PG"))
m("Noix sèche (nouvelle récolte)", src("IF", "Noix"), src("BNA", "noix"))
m("Noisette", src("FL", "Noisette"), src("GP", "Noisette"), src("IF", "Noisette"), *sept("PG"))
m("Amande fraîche", src("GP", "Amande fraiche"))
m("Amande sèche (nouvelle récolte)", src("FL", "Amande"), src("GP", "Amande sèche"), src("IF", "Amande"))
m("Châtaigne", src("FL", "Châtaigne"), src("GP", "Châtaigne"), src("IF", "Châtaigne"), src("BNA", "châtaigne"), *sept("CV", "PG"))
m("Marron", src("FL", "Marron"))
m("Pignon de pin", src("IF", "Pignon de pin"))
m("Kiwi", src("FL", "Kiwi"), src("GP", "Kiwi"), src("IF", "Kiwi"), src("BNA", "kiwi"))
m("Kaki", src("FL", "Kaki"), src("GP", "Kaki"), src("IF", "Kaki"), src("BNA", "kaki"))
m("Grenade", src("FL", "Grenade"), src("IF", "Grenade"))
# Exotique
m("Avocat", src("FL", "Avocat"), src("IF", "Avocat"))
m("Banane", src("FL", "Banane"))
m("Banane plantain", src("FL", "Banane plantain"))
m("Ananas", src("FL", "Ananas"), src("IF", "Ananas"))
m("Mangue", src("FL", "Mangue"), src("IF", "Mangue"))
m("Papaye", src("FL", "Papaye"), src("IF", "Papaye"))
m("Litchi", src("FL", "Litchi"), src("IF", "Litchi"))
m("Fruit de la passion", src("FL", "Fruit de la passion"), src("IF", "Fruit de la passion"))
m("Datte", src("FL", "Datte"), src("IF", "Datte"))
m("Figue de Barbarie", src("FL", "Figue de Barbarie"), src("IF", "Figue de Barbarie"))
m("Carambole", src("IF", "Carambole"))
m("Mangoustan", src("IF", "Mangoustan"))
m("Pitaya", src("IF", "Pitaya"))
m("Sapotille", src("IF", "Sapotille"))
m("Longane", src("FL", "Longane"))
m("Manioc", src("FL", "Manioc"))
m("Taro", src("FL", "Taro"))
m("Canne à sucre", src("FL", "Canne à sucre"))
m("Pistache", src("FL", "Pistache"))
m("Noix de pécan", src("FL", "Noix de pécan"))
m("Cacahuète", src("FL", "Cacahuète"))
m("Combava", src("FL", "Combava"))
m("Calamansi", src("FL", "Calamansi"))

# Sources trouvées sur le web pour les produits sans calendrier (voir WEB dans saisons_web.py, généré à part)
def apply_web():
    """Sources web (tools/saisons_web.py) : ajoutées aux sources câblées, ou les remplacent (« replace »)."""
    from saisons_web import WEB, NOTES
    for name, refs in WEB.items():
        if name not in P:
            raise KeyError(f"WEB : produit inconnu « {name} »")
        if isinstance(refs, tuple) and refs[0] == "replace":
            P[name] = list(refs[1])
        else:
            P[name] = [r for r in P[name] if not isinstance(r, str)] + list(refs)
    return NOTES


# ---------------------------------------------------------------- calcul
def compute(refs):
    """→ (valeurs[12], texte sources)."""
    full = [r for r in refs if r[3] != "SEPT"]
    only9 = [r for r in refs if r[3] == "SEPT"]
    vals = []
    for mo in range(1, 13):
        yes = sum(1 for r in full if mo in r[1])
        no = sum(1 for r in full if mo not in r[1])
        yes += sum(1 for r in full if mo in r[2])  # une « pleine saison » déclarée pèse double
        if mo == 9:
            yes += len(only9)
        if yes + no == 0:
            vals.append("?")
            continue
        if yes >= 1 and yes >= no:
            vals.append("2" if any(mo in r[2] for r in full) else "1")
        else:
            vals.append("")
    return vals


def period(months, pic=()):
    """{9,10,11,12,1} → « sept.-jan. » ; pleine saison entre parenthèses."""
    if not months:
        return "aucun mois"
    if len(months) == 12:
        txt = "toute l'année"
    else:
        ms = set(months)
        prev = lambda k: (k - 2) % 12 + 1
        nxt = lambda k: k % 12 + 1
        runs = []
        for a in range(1, 13):  # début de plage = mois présent dont le précédent est absent (bouclant)
            if a in ms and prev(a) not in ms:
                b = a
                while nxt(b) in ms:
                    b = nxt(b)
                runs.append((a, b))
        txt = ", ".join(ABBR[a-1] if a == b else f"{ABBR[a-1]}-{ABBR[b-1]}" for a, b in runs)
    if pic:
        txt += f" (pleine {period(set(pic))})"
    return txt


def sources_text(refs):
    parts, sept_codes = [], []
    for code, months, pic, label in refs:
        if label == "SEPT":
            sept_codes.append(code)
            continue
        if code in FULL and label:
            head = f"{code} « {label} »" if strip(label) not in (code.lower(),) else code
        elif label:
            head = f"{code} ({label})"
        else:
            head = code
        parts.append(f"{head} : {period(months, pic)}")
    if sept_codes:
        parts.append("sept. seul : " + ", ".join(sept_codes))
    return " · ".join(parts)


def main():
    check = "--check" in sys.argv
    NOTES = apply_web()
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))
    head, body = rows[0], rows[1:]
    names = [r[1] for r in body]
    missing = [n for n in names if n not in P]
    extra = [n for n in P if n not in names]
    assert not missing and not extra, (missing, extra)

    results = {}
    for r in body:
        name = r[1]
        refs = P[name]
        if refs and isinstance(refs[0], str):
            base = refs[0][2:]
            vals = results[base][0] if base in results else compute(P[base])
            results[name] = (vals, f"= {base} (assimilé)", True)
        else:
            results[name] = (compute(refs), sources_text(refs) if refs else "—", False)

    diffs, resolved = [], 0
    out = []
    for r in body:
        name = r[1]
        vals, stxt, assim = results[name]
        old9 = r[10]
        new = list(vals)
        if old9 == "?" and new[8] != "?":
            resolved += 1
        elif new[8] != old9:
            diffs.append((name, old9, new[8]))  # septembre : la règle unique remplace la relecture du 2026-09-16
        note = r[15] if len(r) > 15 else ""
        if note.strip() == "Hors saison en septembre":
            note = ""
        if name in NOTES:
            note = (note + " ; " if note else "") + NOTES[name]
        out.append(r[:2] + new + [stxt, note])

    print(f"{len(out)} produits · septembre : {len(diffs)} écarts avec la relecture (relu > règle), {resolved} « ? » résolus")
    for name, o, n in diffs:
        print(f"  sept. {name}: {o or "vide"} > {n or "vide"}")
    from collections import Counter
    for i, mo in enumerate(ABBR):
        c = Counter(r[2 + i] for r in out)
        print(f"  {mo:<6} pleine={c['2']:>3} saison={c['1']:>3} ?={c['?']:>3} vide={c['']:>3}")
    if check:
        return 0
    head = head[:14] + ["Sources (période par source)", "Notes"]
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(head)
        w.writerows(out)
    print(f"OK {CSV_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
