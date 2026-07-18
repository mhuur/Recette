"""Régénère data/saisons.md à partir de SEASON_REFERENCE (index.html).

La table JS est la source de vérité : ce script la relit et produit le document
dans les deux sens (par produit, puis par mois). Ne pas éditer le .md à la main.

    py tools/seasons_doc.py

Non déployé (firebase.json ignore tools/**).
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MONTHS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
          'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
ALL_YEAR = list(range(1, 13))


def extract_table():
    """Lit le bloc SEASON_REFERENCE = { ... }; et le convertit en dict Python."""
    src = (ROOT / 'index.html').read_text(encoding='utf-8')
    start = src.index('const SEASON_REFERENCE = {')
    start = src.index('{', start)
    depth, i = 0, start
    while True:                       # équilibrage d'accolades : pas de parseur JS ici
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = src[start:i + 1]
    block = re.sub(r'/\*.*?\*/', '', block, flags=re.S)  # commentaires de bloc
    block = re.sub(r'//[^\n]*', '', block)          # commentaires de fin de ligne
    block = block.replace('ALL_YEAR', json.dumps(ALL_YEAR))
    block = re.sub(r"'([^']*)'", lambda m: json.dumps(m.group(1)), block)  # quotes JS → JSON
    block = re.sub(r'(\w+):', lambda m: '"%s":' % m.group(1), block)       # clés nues
    block = re.sub(r',\s*([}\]])', r'\1', block)    # virgules traînantes
    return json.loads(block)


def months_label(months):
    if sorted(months) == ALL_YEAR:
        return 'toute l\'année'
    return ', '.join(MONTHS[m - 1] for m in sorted(months))


def main():
    table = extract_table()
    flat = []                                        # (nom, catégorie, mois)
    for cat, label in (('legume', 'Légume'), ('fruit', 'Fruit'), ('complement', 'Complément')):
        for name, months in table.get(cat, {}).items():
            flat.append((name, label, months))
    flat.sort(key=lambda x: x[0].lower())

    out = []
    out.append('# Fruits et légumes de saison')
    out.append('')
    out.append('Source : <https://www.greenpeace.fr/guetteur/calendrier/> (France métropolitaine), '
               'relevé le 2026-07-18.')
    out.append('')
    out.append('**Fichier généré — ne pas éditer à la main.** La source de vérité est la table '
               '`SEASON_REFERENCE` dans `index.html` ; ce document est reconstruit par '
               '`py tools/seasons_doc.py`.')
    out.append('')
    out.append('Céréales et légumineuses (blé, riz, lentille, quinoa…) figurent sur le site mais '
               'sont volontairement exclues : elles se conservent toute l\'année, les dater '
               'restreindrait des recettes sans raison.')
    out.append('')
    out.append('## Par produit')
    out.append('')
    out.append('| Produit | Type | Mois de saison |')
    out.append('| --- | --- | --- |')
    for name, cat, months in flat:
        out.append('| %s | %s | %s |' % (name, cat, months_label(months)))
    out.append('')
    out.append('## Par mois')
    out.append('')
    for idx, month in enumerate(MONTHS, start=1):
        legumes = sorted(n for n, c, m in flat if c == 'Légume' and idx in m)
        fruits = sorted(n for n, c, m in flat if c == 'Fruit' and idx in m)
        extra = sorted(n for n, c, m in flat if c == 'Complément' and idx in m)
        out.append('### %s' % month)
        out.append('')
        out.append('- **Légumes (%d)** : %s' % (len(legumes), ', '.join(legumes) or '—'))
        out.append('- **Fruits (%d)** : %s' % (len(fruits), ', '.join(fruits) or '—'))
        out.append('- **Compléments (%d)** : %s' % (len(extra), ', '.join(extra) or '—'))
        out.append('')

    dest = ROOT / 'data' / 'saisons.md'
    dest.parent.mkdir(exist_ok=True)
    dest.write_text('\n'.join(out), encoding='utf-8')
    print('data/saisons.md ecrit : %d produits (%d legumes, %d fruits)' % (
        len(flat),
        sum(1 for _, c, _ in flat if c == 'Légume'),
        sum(1 for _, c, _ in flat if c == 'Fruit')))


if __name__ == '__main__':
    main()
