"""Test de fumee — Mes Recettes.

Boote l'app dans Chrome headless et verifie qu'elle demarre vraiment :
aucune erreur JS, les fichiers extraits sont charges, l'app a rendu.
Sert le dossier en HTTP local (file:// fausse le comportement du SW et du login).

Usage :   py tools/smoke.py
Sortie :  code 0 = OK, code 1 = echec (bloque le deploiement dans une chaine &&)
"""

import http.server
import json
import os
import pathlib
import re
import shutil
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

# Erreurs attendues hors ligne / hors domaine autorise : elles ne disent rien du code.
IGNORE_ERRORS = re.compile(
    r"auth/|firebase|firestore|gstatic|googleapis|ERR_|Failed to fetch|NetworkError"
    r"|net::|Manifest|service ?worker",
    re.I,
)

# La sonde s'insere avant le DERNIER </body> : le tag apparait aussi dans des
# chaines JS de l'app (feuille d'impression), un replace global casserait le script.
PROBE = """
<script>
window.__smoke = { errors: [] };
window.addEventListener('error', function (e) {
  window.__smoke.errors.push(String((e.error && e.error.stack) || e.message));
});
window.addEventListener('unhandledrejection', function (e) {
  window.__smoke.errors.push('unhandledrejection: ' + String(e.reason));
});
</script>
"""

REPORT = """
<script>
setTimeout(function () {
  var out = { errors: window.__smoke.errors, checks: {} };
  try {
    var c = out.checks;
    c.icons        = (typeof ICONS === 'object') && Object.keys(ICONS).length;
    c.injectIcons  = typeof injectIcons === 'function';
    c.unfilledIcon = [].slice.call(document.querySelectorAll('[data-icon]'))
                       .filter(function (el) { return !el.querySelector('svg'); }).length;
    // Theme Sylva : la photo foret est sur body::before, la police est Manrope —
    // deux marqueurs propres a styles.css.
    var bs = getComputedStyle(document.body);
    var bb = getComputedStyle(document.body, '::before');
    c.cssLoaded = /forest-bg/.test(bb.backgroundImage) && /Manrope/.test(bs.fontFamily);
    c.appRendered  = !!document.querySelector('#recipes-container');
    c.starPicker   = typeof createStarPicker === 'function';
    c.ratingStars  = (ratingStars(10).match(/<svg/g) || []).length;
    c.renderTabs   = ['renderRecipes','renderDataTab','renderDebug','renderShopping']
                       .filter(function (f) { return typeof window[f] === 'function'; }).length;
  } catch (e) {
    out.errors.push('probe: ' + e.message);
  }
  document.title = 'SMOKE' + JSON.stringify(out);
}, 1200);
</script>
"""


def find_chrome():
    for c in ("chrome", "google-chrome", "chromium"):
        if shutil.which(c):
            return shutil.which(c)
    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ):
        if os.path.exists(p):
            return p
    return None


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(port):
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(ROOT), **k
    )
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    httpd.log_message = lambda *a: None
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def fail(msg):
    print(f"SMOKE ECHEC : {msg}")
    sys.exit(1)


def main():
    chrome = find_chrome()
    if not chrome:
        fail("Chrome introuvable")

    src = INDEX.read_text(encoding="utf-8")
    head, sep, tail = src.rpartition("</body>")
    if not sep:
        fail("</body> introuvable dans index.html")
    probed = src.replace("<head>", "<head>" + PROBE, 1)
    head, sep, tail = probed.rpartition("</body>")
    probed = head + REPORT + sep + tail

    smoke_file = ROOT / "__smoke.html"  # gitignore : __*
    smoke_file.write_text(probed, encoding="utf-8")

    port = free_port()
    httpd = serve(port)
    profile = tempfile.mkdtemp(prefix="smoke-profile-")
    try:
        out = subprocess.run(
            [
                chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                f"--user-data-dir={profile}", "--virtual-time-budget=6000",
                "--dump-dom", f"http://127.0.0.1:{port}/__smoke.html",
            ],
            capture_output=True, text=True, timeout=90, encoding="utf-8", errors="replace",
        ).stdout
    except subprocess.TimeoutExpired:
        fail("Chrome n'a pas repondu (timeout)")
    finally:
        httpd.shutdown()
        smoke_file.unlink(missing_ok=True)
        shutil.rmtree(profile, ignore_errors=True)

    m = re.search(r"<title>SMOKE(.*?)</title>", out, re.S)
    if not m:
        fail("l'app n'a pas atteint la sonde — erreur de syntaxe JS probable "
             "(le script principal n'a pas tourne)")

    data = json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))
    c, errors = data["checks"], [e for e in data["errors"] if not IGNORE_ERRORS.search(e)]

    problems = []
    if errors:
        problems.append("erreurs JS : " + " | ".join(errors[:3]))
    if not c.get("icons"):
        problems.append("ICONS absent (icons.js non charge ?)")
    if c.get("unfilledIcon"):
        problems.append(f"{c['unfilledIcon']} [data-icon] sans SVG")
    if not c.get("cssLoaded"):
        problems.append("styles.css non appliquee (photo foret ou police Manrope absentes sur body)")
    if not c.get("appRendered"):
        problems.append("l'app n'a pas rendu")
    if c.get("ratingStars") != 5:
        problems.append(f"ratingStars(10) = {c.get('ratingStars')} etoiles, attendu 5")
    if c.get("renderTabs") != 4:
        problems.append(f"{c.get('renderTabs')}/4 fonctions render* definies")
    if not c.get("starPicker"):
        problems.append("createStarPicker absent")

    if problems:
        for p in problems:
            print("  - " + p)
        fail(f"{len(problems)} probleme(s)")

    print(f"SMOKE OK — {c['icons']} icones, styles.css appliquee, "
          f"{c['renderTabs']}/4 onglets, 0 erreur JS")


if __name__ == "__main__":
    main()
