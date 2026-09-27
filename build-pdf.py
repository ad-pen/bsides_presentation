#!/usr/bin/env python3
"""Lay the deck out as one slide per page and render it to PDF via headless Chrome."""
import io, os, re, subprocess, sys, tempfile

SRC = sys.argv[1] if len(sys.argv) > 1 else "Live Prompt Injection.dc.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(SRC)[0].replace(".dc", "") + ".pdf"

s = io.open(SRC, encoding="utf-8").read()
s = s.replace('<script src="./support.js"></script>', '')
s = re.sub(r'<script type="text/x-dc".*?</script>', '', s, flags=re.S)
# the in-body sheet pins body to one viewport, which collapses every slide onto page 1
s = s.replace('height:100%; overflow:hidden; }', '}', 1)

n = 0
def fix(m):
    global n; n += 1
    st = m.group(1).replace(
        'position:absolute;inset:0;',
        'position:relative;inset:auto;width:100vw;height:56.25vw;container-type:size;')
    return '<section data-slide="" style="%s">' % re.sub(r'opacity:[01]$', 'opacity:1', st)
s = re.sub(r'<section data-slide="" data-screen-label="\d+" style="([^"]*)">', fix, s)

s = s.replace('width:100vw;height:100vh;display:flex;align-items:center;justify-content:center;background:#0B0C0E',
              'width:100vw;background:#0B0C0E')
s = s.replace('position:relative;width:100vw;max-width:177.7vh;aspect-ratio:16/9;max-height:100vh;container-type:size;overflow:hidden;background:#0B0C0E',
              'position:relative;width:100vw;background:#0B0C0E')
s = s.replace("</head>", """<style>
@page { size: 297mm 167.06mm; margin: 0; }
html, body { margin:0 !important; padding:0 !important; height:auto !important; overflow:visible !important; background:#0B0C0E !important; }
x-dc { display:block; }
helmet { display:none; }
[data-slide] { break-after:page; page-break-after:always; }
[data-slide]:last-of-type { break-after:auto; page-break-after:auto; }
#dc-counter, #dc-notes, template { display:none !important; }
#dc-logo { position:fixed !important; right:7mm !important; bottom:6mm !important; left:auto !important; height:11mm !important; width:auto !important; opacity:0.9; }
</style>
</head>""")

tmp = os.path.join(tempfile.mkdtemp(), "print.html")
io.open(tmp, "w", encoding="utf-8").write(s)
subprocess.run(["google-chrome-stable", "--headless", "--disable-gpu", "--no-sandbox",
                "--hide-scrollbars", "--virtual-time-budget=20000", "--no-pdf-header-footer",
                "--print-to-pdf=" + OUT, "file://" + tmp],
               check=True, capture_output=True)
print("%d slides -> %s" % (n, OUT))
