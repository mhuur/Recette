# -*- coding: utf-8 -*-
"""Génère saisons.js (servi par l'app) à partir de :
  - data/saisons/saisons.csv          : calendrier (289 produits × 12 mois)
  - data/saisons/correspondance.csv   : nom d'ingrédient de l'app → produit du calendrier
                                        (produit vide = explicitement toute l'année)

Un mois compte « de saison » pour 1, 2 ou ? (non vérifié : on n'exclut pas sur un doute) ;
vide = hors saison. Les clés de SEASON_ALIASES sont normalisées comme normalizeText()
d'index.html (minuscules, accents retirés, espaces bornés).

Usage : py tools/saisons_js.py
"""
import csv
import io
import json
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "saisons", "saisons.csv")
MAP_PATH = os.path.join(ROOT, "data", "saisons", "correspondance.csv")
OUT_PATH = os.path.join(ROOT, "saisons.js")


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def main():
    with io.open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))
    body = rows[1:]
    calendar = {}
    for r in body:
        name = r[1].strip()
        months = [i + 1 for i, v in enumerate(r[2:14]) if v.strip() in ("1", "2", "?")]
        if name in calendar:
            print("doublon calendrier :", name)
            return 1
        calendar[name] = months

    with io.open(MAP_PATH, encoding="utf-8-sig", newline="") as f:
        maps = list(csv.reader(f, delimiter=";"))[1:]
    aliases = {}
    bad = []
    for r in maps:
        if not r or not r[0].strip():
            continue
        ing, prod = r[0].strip(), (r[1].strip() if len(r) > 1 else "")
        if prod and prod not in calendar:
            bad.append(f"{ing} → {prod}")
        key = norm(ing)
        if key in aliases and aliases[key] != prod:
            bad.append(f"clé en double : {ing}")
        aliases[key] = prod
    if bad:
        print("correspondance.csv : produits inconnus ou doublons")
        for b in bad:
            print("  - " + b)
        return 1

    def js_obj(d, indent="  "):
        lines = []
        for k, v in d.items():
            lines.append(f"{indent}{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}")
        return "{\n" + ",\n".join(lines) + "\n}"

    out = (
        "/* Généré par tools/saisons_js.py à partir de data/saisons/saisons.csv et\n"
        "   data/saisons/correspondance.csv — ne pas éditer à la main.\n"
        "   Script classique (pas un module) : SEASON_CALENDAR et SEASON_ALIASES sont\n"
        "   visibles depuis le script inline d'index.html, comme ICONS dans icons.js. */\n"
        "// Produit du calendrier → mois de saison (1-12). 12 mois = non spécifique à une saison.\n"
        f"const SEASON_CALENDAR = {js_obj(calendar)};\n"
        "// Nom d'ingrédient de l'app (normalisé : minuscules, sans accents) → produit du\n"
        "// calendrier. Chaîne vide = explicitement toute l'année (produit de garde, import).\n"
        f"const SEASON_ALIASES = {js_obj(aliases)};\n"
    )
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    n12 = sum(1 for m in calendar.values() if len(m) == 12)
    print(f"OK {OUT_PATH} — {len(calendar)} produits ({n12} toute l'année), {len(aliases)} alias")
    return 0


if __name__ == "__main__":
    sys.exit(main())
