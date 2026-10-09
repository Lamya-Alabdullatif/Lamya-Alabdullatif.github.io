#!/usr/bin/env python3
"""Reorganises the Work section of index.html (run from the repo root, next to index.html).
Keeps ALL existing projects, adds Nova + Hospital, converts tool lines to badges.
Makes index.backup.html first. Aborts without writing if the structure is not as expected."""
import re, shutil, os, urllib.request

SRC = "index.html"
html = open(SRC, encoding="utf-8").read()
ARROW = '<svg viewBox="0 0 20 20" fill="none"><path d="M5 15L15 5M15 5H7M15 5V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ---------- locate the work section ----------
a = html.index("<!-- ===== Graduation Project ===== -->")
sk = html.index("<!-- ================= SKILLS")
sec_end = html.rindex("</section>", 0, sk)
wrap_end = html.rindex("</div>", 0, sec_end)
body, tail = html[a:wrap_end], html[wrap_end:]

cards = {}
for m in re.finditer(r'<article class="card reveal.*?</article>', body, re.S):
    t = re.search(r'card-tag">(P-\d+)<', m.group(0))
    if t: cards[t.group(1)] = m.group(0)
need = ["P-%02d" % i for i in range(2, 14)]
assert all(k in cards for k in need), "Unexpected structure: missing " + str([k for k in need if k not in cards])
fm = re.search(r'<div class="feature-project reveal">.*?(?=<!-- ===== University Projects)', body, re.S)
assert fm, "Graduation block not found"
feature = fm.group(0).rstrip()

# ---------- tool badges ----------
def cls(t):
    l = t.lower()
    if "excel" in l: return "excel"
    if "power bi" in l: return "pbi"
    if any(k in l for k in ("python", "pandas", "seaborn")): return "py"
    if "sql" in l: return "sql"
    return ""
def badges(s):
    items = [x.strip() for x in s.split("·") if x.strip()]
    return '<div class="tool-badges">' + "".join(
        '<span class="tool-badge %s">%s</span>' % (cls(i), i) for i in items) + "</div>"
def conv(card):
    return re.sub(r'<p class="card-tech">(.*?)</p>', lambda m: badges(m.group(1)), card, flags=re.S)

# ---------- images (download locally, fall back to hotlink) ----------
os.makedirs("assets/projects", exist_ok=True)
N = "https://github.com/Lamya-Alabdullatif/nova/raw/main/"
H = "https://github.com/Lamya-Alabdullatif/Hospital-analysis/raw/main/images/"
def img(url, name):
    dest = "assets/projects/" + name
    if not os.path.exists(dest):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            open(dest, "wb").write(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            print("! download failed, hotlinking:", name, e); return url
    return dest
nova1 = img(N + "%D9%84%D9%82%D8%B7%D8%A9_%D9%84%D9%88%D8%AD%D8%A9_%D8%A7%D9%84%D8%AA%D8%AD%D9%83%D9%85.png", "nova-dashboard.png")
nova2 = img(N + "%D9%84%D9%82%D8%B7%D8%A9_%D8%B4%D9%8A%D8%AA_%D8%A7%D9%84%D9%85%D8%AE%D8%B7%D8%B7%D8%A7%D8%AA.png", "nova-charts.png")
hos1 = img(H + "dashboard.png", "hospital-dashboard.png")
hos2 = img(H + "cover.png", "hospital-cover.png")

def new_card(tag, title, stat, desc, tech, i1, alt, i2, lbl2, gh, extra="", delay=""):
    d = ' data-delay="%s"' % delay if delay else ""
    return f'''<article class="card reveal"{d}>
<div class="card-media js-lightbox" data-full="{i1}"><span class="card-tag">{tag}</span><img src="{i1}" alt="{alt}"></div>
<div class="card-body">
<h3 class="card-title">{title}</h3>
<p class="card-stat">{stat}</p>
<p class="card-desc">{desc}</p>
{badges(tech)}
<div class="card-actions">
<a class="card-action primary js-lightbox" data-full="{i1}" href="javascript:void(0)">View Dashboard {ARROW}</a>
<a class="card-action js-lightbox" data-full="{i2}" href="javascript:void(0)">{lbl2} {ARROW}</a>
<a class="card-action" href="{gh}" target="_blank" rel="noopener">GitHub {ARROW}</a>{extra}
</div>
</div>
</article>'''

nova = new_card("P-14", "Nova Electronics Sales Analysis",
  "→ ≈3.7M SAR sales · 1,120 cleaned orders · 5 branches",
  "End-to-end Excel analysis of 2024 retail sales: documented data cleaning, formula-driven summary tables, an interactive dashboard with region and category filters, and actionable recommendations.",
  "Excel · Data Cleaning · Dashboard · SUMIFS / INDEX-MATCH", nova1,
  "Nova Electronics Excel sales dashboard", nova2, "View Charts", "https://github.com/Lamya-Alabdullatif/nova",
  extra=f'\n<a class="card-action" href="https://github.com/Lamya-Alabdullatif/2024" target="_blank" rel="noopener">Workbook {ARROW}</a>', delay="0")
hosp = new_card("P-15", "Hospital Data Analytics",
  "→ 20.6M SAR revenue · 2,100 cleaned records · 8 charts",
  "Excel analysis of 2024 hospital operations (synthetic data): documented cleaning (2,142 to 2,100 records), eight formula-driven tables, and a department-filtered interactive dashboard.",
  "Excel · Data Cleaning · Dashboard · SUMIFS / COUNTIFS", hos1,
  "Hospital analytics Excel dashboard", hos2, "View Cover", "https://github.com/Lamya-Alabdullatif/Hospital-analysis", delay="1")
nova = nova.replace(' data-delay="0"', "")

def head(n, title, count):
    return f'''<div class="track-header reveal">
<h3 class="track-title"><span class="track-n">{n}</span>{title}</h3>
<span class="track-count">{count}</span>
</div>
'''
grid = lambda cs, g="grid": f'<div class="{g}">\n' + "\n".join(conv(c) for c in cs) + "\n</div>\n"

de = '''<div class="grid grid-2">
<article class="card reveal" style="border-style:dashed;">
<div class="card-body">
<h3 class="card-title">Data Engineering — coming soon</h3>
<p class="card-desc">SQL, ETL and database projects will be added here.</p>
<div class="tool-badges"><span class="tool-badge sql">SQL</span><span class="tool-badge">ETL</span><span class="tool-badge">Databases</span></div>
</div>
</article>
</div>
'''
new = (
 head("01", "AI &amp; Machine Learning Projects", "5 projects") + grid([cards["P-%02d" % i] for i in range(5, 10)]) +
 head("02", "Data Analysis &amp; Business Intelligence", "6 projects") +
   grid([cards["P-%02d" % i] for i in range(10, 14)] + [nova, hosp], "grid grid-2") +
 head("03", "Data Engineering Projects", "Coming soon") + de +
 head("04", "Graduation Project", "Most important project") + feature + "\n" +
 head("05", "Other Projects &amp; Future Projects", "3 projects · more coming") +
   grid([cards["P-%02d" % i] for i in range(2, 5)]) + "<!-- ADD NEW PROJECT CARDS INSIDE THE MATCHING .grid ABOVE -->\n")

out = html[:a] + new + tail
out = out.replace("Thirteen projects", "Fifteen projects")
out = re.sub(r"Grouped by track:[^<]*", "Grouped by track: AI &amp; machine learning, data analysis &amp; BI, data engineering, the graduation project, and other work.", out, count=1)
css = """.tool-badges{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 16px;}
.tool-badge{font-family:var(--mono);font-size:10.5px;font-weight:600;padding:4px 9px;border-radius:6px;border:1px solid var(--line);background:var(--surface-2);color:var(--muted);letter-spacing:.02em;}
.tool-badge.excel{color:#5fd08a;border-color:rgba(95,208,138,.45);background:rgba(95,208,138,.08);}
.tool-badge.pbi{color:#f2c94c;border-color:rgba(242,201,76,.45);background:rgba(242,201,76,.08);}
.tool-badge.py{color:#6ea8ff;border-color:rgba(110,168,255,.45);background:rgba(110,168,255,.08);}
.tool-badge.sql{color:#ff9f6b;border-color:rgba(255,159,107,.45);background:rgba(255,159,107,.08);}
"""
assert "/* ---------- skills ---------- */" in out
out = out.replace("/* ---------- skills ---------- */", css + "/* ---------- skills ---------- */", 1)

shutil.copy(SRC, "index.backup.html")
open(SRC, "w", encoding="utf-8").write(out)
print("Done. Cards now:", len(re.findall(r'class="card-tag">P-', out)), "(expected 14 + 1 graduation poster).")
print("Backup: index.backup.html")
