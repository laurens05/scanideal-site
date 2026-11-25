#!/usr/bin/env python3
"""Génère les pages statiques /marques/<slug>/ (SEO) à partir des données du site.
Usage : python3 tools/gen-marques.py   (depuis la racine du dépôt)
Relancer après toute modification des marques ou des produits dans « Scanideal v2.dc.html »."""
import json, os, re, subprocess, html, tempfile, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://scanideal.com"
tmp = tempfile.mktemp(suffix=".json")
subprocess.check_call(["node", os.path.join(ROOT, "tools/extract-data.js"), os.path.join(ROOT, "Scanideal v2.dc.html"), tmp], stdout=subprocess.DEVNULL)
data = json.load(open(tmp, encoding="utf-8")); os.remove(tmp)
brands, products = data["brands"], data["products"]
SLUG = {"fredericia":"fredericia","naver":"naver-collection","loca":"loca","cph":"cph-lighting","rye":"rye-sleep","viacph":"via-copenhagen","savir":"savir-design"}
e = lambda t: html.escape(t, quote=False)
ea = lambda t: html.escape(t, quote=True)
def url(p): return p if p.startswith("http") else "/" + p.lstrip("/")
def og_image(b):
    if b["img"].startswith("http") and b.get("gallery"): return absu(b["gallery"][1 if len(b["gallery"]) > 1 else 0]["src"])
    return absu(b["img"])
def absu(p): return p if p.startswith("http") else SITE + "/" + p.lstrip("/")
TITLES = {
 "fredericia": "Fredericia en France | Mobilier design danois | Scanideal",
 "naver": "Naver Collection en France | Bois massif danois | Scanideal",
 "loca": "Loca en France | Patères, miroirs et rangements | Scanideal",
 "cph": "CPH Lighting en France | Luminaires danois | Scanideal",
 "rye": "Rye Sleep en France | Lits et literie danois | Scanideal",
 "viacph": "VIA Copenhagen en France | Mobilier d'art danois | Scanideal",
 "savir": "Savir Design en France | Mobilier collectif | Scanideal",
}
def meta_desc(b):
    base = f"{b['name']} en France, représentée par Scanideal : " + b["desc"]
    if len(base) <= 158: return base
    cut = base[:157].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + "…"

CSS = """body{margin:0;background:#F4F0E9;color:#1C1B19;font-family:'Hanken Grotesk',sans-serif;-webkit-font-smoothing:antialiased}
*{box-sizing:border-box}a{color:#1C1B19;text-decoration:underline;text-underline-offset:3px}a:hover{color:#7D5C36}
.w{max-width:1440px;margin:0 auto;padding:0 clamp(20px,4vw,56px)}
header{padding:22px 0;border-bottom:1px solid rgba(28,27,25,.14)}header .w{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
header img{height:34px;display:block;mix-blend-mode:multiply}nav{display:flex;gap:28px;font-size:12px;letter-spacing:.16em;text-transform:uppercase}nav a{text-decoration:none}
.eyebrow{font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:#6B655C;margin:0 0 18px}
h1,h2,h3{font-family:'Newsreader',serif;font-weight:300;margin:0}h1{font-size:clamp(46px,6.4vw,96px);line-height:.98;letter-spacing:-.02em}
h2{font-size:clamp(28px,3vw,40px);line-height:1.1;margin-bottom:28px}h3{font-weight:400;font-size:22px;margin:0 0 8px}
.lead{font-family:'Newsreader',serif;font-style:italic;font-size:clamp(22px,2.4vw,30px);color:#6B655C;margin:24px 0 0}
.hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:clamp(32px,6vw,96px);align-items:center;padding:clamp(48px,7vw,96px) 0 0}
.hero img{width:100%;height:auto;display:block;background:#EAE4DA}p{font-size:17px;line-height:1.7;color:#4A453E;margin:0 0 16px}
section{padding-top:clamp(56px,8vw,112px)}.btn{display:inline-block;margin-top:12px;padding:15px 28px;background:#1C1B19;color:#F4F0E9;text-decoration:none;font-size:12px;letter-spacing:.2em;text-transform:uppercase}.btn:hover{color:#F4F0E9;background:#7D5C36}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:36px 48px}.grid>div{border-top:1px solid #1C1B19;padding-top:20px}
.grid p{font-size:15px;line-height:1.65}.big{font-family:'Newsreader',serif;font-size:38px;font-weight:300;display:block;margin-bottom:6px}
.plist{columns:3 260px;column-gap:48px;margin:0;padding:0;list-style:none;font-size:15px;line-height:1.7;color:#4A453E}.plist li{break-inside:avoid;padding:2px 0}.plist small{color:#6B655C}
.cat{margin:28px 0 10px;font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:#6B655C}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:20px}.gal figure{margin:0}.gal img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#EAE4DA}.gal figcaption{font-size:13px;color:#6B655C;margin-top:8px;line-height:1.5}
.tl{display:grid;gap:22px;max-width:820px}.tl div{display:grid;grid-template-columns:110px 1fr;gap:20px}.tl b{font-family:'Newsreader',serif;font-weight:400;font-size:24px}.tl p{margin:0;font-size:15px}
.chips{display:flex;flex-wrap:wrap;gap:10px 22px;font-size:14px;margin:0;padding:0;list-style:none}
footer{margin-top:clamp(72px,9vw,128px);padding:48px 0;border-top:1px solid rgba(28,27,25,.14);font-size:14px;line-height:1.8;color:#4A453E}footer .w{display:flex;gap:40px;flex-wrap:wrap;justify-content:space-between}"""

def page(inner, title, desc, canon, og_img, jsonld, og_alt=""):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{ea(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Scanideal">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{ea(title)}">
<meta property="og:description" content="{ea(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300;1,6..72,400&family=Hanken+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<header><div class="w"><a href="/"><img src="/assets/scanideal-logo.png" alt="Scanideal"></a>
<nav aria-label="Navigation principale"><a href="/">Accueil</a><a href="/marques/">Les marques</a><a href="/catalogue/">Catalogue</a><a href="/contact/">Contact</a></nav></div></header>
<main>
{inner}
</main>
<footer><div class="w">
<div>Scanideal SARL, 100 rue Grande, 77430 Champagne-sur-Seine<br>Tél. 06 76 77 55 33 · <a href="mailto:info@scanideal.com">info@scanideal.com</a><br>SIREN 489 193 987, RCS Melun · Zone d'intervention : France entière</div>
<div><a href="/catalogue/">Catalogue</a> · <a href="/contact/">Contact</a><br>Les marques : {" · ".join(f'<a href="/marques/{SLUG[b["id"]]}/">{e(b["name"])}</a>' for b in brands)}</div>
</div></footer>
</body>
</html>
"""

ORG = {"@id": SITE + "/#organization"}
SAMPLES = "Depuis la page Contact : décrivez votre besoin. Scanideal établit un chiffrage et, si cela est pertinent pour votre projet, peut fournir des échantillons, puis suit le projet avec le fabricant jusqu'à l'installation."
def brand_faq(b, n):
    n_ = b["name"]
    qa = [(f"Qui représente {n_} en France ?", f"Scanideal, agent commercial de {n_} en France, basé à Champagne-sur-Seine (77). Nous intervenons dans toute la France auprès des revendeurs, architectes d'intérieur et collectivités."),
          (f"Quelles pièces {n_} Scanideal présente-t-il ?", f"{n} pièce{'s' if n > 1 else ''} au catalogue : {b['cats'].rstrip('.')[:1].lower() + b['cats'].rstrip('.')[1:]}."),
          (f"Comment obtenir un chiffrage {n_} ?", SAMPLES)]
    g = (b.get("facts") or {}).get("guarantee")
    if g and " : " in g: qa.append((f"Quelle garantie offre {n_} ?", g.split(" : ", 1)[1].strip()))
    return qa
def brand_page(b):
    slug = SLUG[b["id"]]; canon = f"{SITE}/marques/{slug}/"
    prods = [p for p in products if p["brand"] == b["id"]]
    cats = {}
    for p in prods: cats.setdefault(p["cat"], []).append(p)
    h = []
    h.append(f'''<div class="w"><div class="hero"><div><p class="eyebrow">Marque représentée en France</p><h1>{e(b["name"])}</h1><p class="lead">{e(b["tagline"])}</p>
<p style="margin-top:32px">{e(b["desc"])}</p><p><strong style="font-weight:500">Gamme :</strong> {e(b["cats"])}</p>
<a class="btn" href="/">Ouvrir le catalogue interactif</a> <a class="btn" style="background:none;color:#1C1B19;border:1px solid #1C1B19" href="/contact/">Nous contacter</a></div>
<img src="{ea(url(b["img"]))}" alt="{ea(b["name"])}, {ea(b["tagline"].lower())}" width="1400" height="1050" fetchpriority="high"></div></div>''')
    st = b.get("story")
    if st:
        h.append(f'<div class="w"><section><h2>{e(st["title"])}</h2><p style="max-width:820px">{e(st["lead"])}</p>')
        if st.get("quote"): h.append(f'<p style="max-width:820px;font-family:\'Newsreader\',serif;font-style:italic;font-size:22px;color:#1C1B19">« {e(st["quote"]["t"])} »<br><small style="font-family:\'Hanken Grotesk\';font-style:normal;font-size:13px;color:#6B655C">{e(st["quote"]["by"])}</small></p>')
        h.append('<div class="tl">' + "".join(f'<div><b>{e(x["y"])}</b><p>{e(x["t"])}</p></div>' for x in st.get("timeline", [])) + '</div></section></div>')
        if st.get("topics"):
            h.append('<div class="w"><section><div class="grid">' + "".join(f'<div><h3>{e(x["t"])}</h3><p>{e(x["p"])}</p></div>' for x in st["topics"]) + '</div></section></div>')
    f = b.get("facts")
    if f:
        h.append(f'<div class="w"><section><h2>{e(f["title"])}</h2><div class="grid">' + "".join(f'<div><span class="big">{e(x["v"])}</span><p>{e(x["l"])}</p></div>' for x in f["items"]) + '</div>')
        if f.get("guarantee"): h.append(f'<p style="margin-top:32px;max-width:820px"><strong style="font-weight:500">{e(f["guarantee"].split(" : ",1)[0])} :</strong> {e(f["guarantee"].split(" : ",1)[1])}</p>')
        if f.get("src"): h.append(f'<p style="font-size:13px;color:#6B655C">{e(f["src"])}</p>')
        h.append('</section></div>')
    if b.get("awards"):
        h.append('<div class="w"><section><h2>Distinctions</h2><ul class="chips">' + "".join(f'<li>{e(a["alt"])}</li>' for a in b["awards"]) + '</ul></section></div>')
    de = e(("de " if b["name"][0] not in "AEIOUY" else "d’") + b["name"])
    h.append(f'<div class="w"><section><h2>' + (f'La pièce {de} que nous présentons' if len(prods) == 1 else f'Les {len(prods)} pièces {de} que nous présentons') + '</h2>')
    for c, ps in cats.items():
        h.append(f'<div class="cat">{e(c)}</div><ul class="plist">' + "".join(f'<li>{e(p["name"])}' + (f' <small>· {e(p["designer"])}</small>' if p.get("designer") else "") + '</li>' for p in ps) + '</ul>')
    h.append('<p style="margin-top:32px">Finitions, dimensions et photos de chaque pièce sont disponibles dans le <a href="/">catalogue interactif</a>.</p></section></div>')
    gal = b.get("gallery") or []
    if gal:
        h.append('<div class="w"><section><h2>En situation</h2><div class="gal">' + "".join(f'<figure><img src="{ea(url(g["src"]))}" alt="{ea(g["cap"])}" loading="lazy" width="800" height="600"><figcaption>{e(g["cap"])}</figcaption></figure>' for g in gal[:6]) + '</div></section></div>')
    qa = brand_faq(b, len(prods))
    h.append('<div class="w"><section><h2>Questions fréquentes</h2>' + "".join(f'<h3>{e(q)}</h3><p>{e(a)}</p>' for q, a in qa) + '</section></div>')
    h.append('''<div class="w"><section><h2>Un projet avec cette marque ?</h2><p style="max-width:720px">Scanideal présente les collections, conseille sur les finitions, établit les chiffrages et, si cela est pertinent pour votre projet, peut fournir des échantillons, puis suit chaque projet avec le fabricant jusqu'à l'installation, partout en France.</p><a class="btn" href="/contact/">Parlons de votre projet</a></section></div>''')
    title = TITLES[b["id"]]
    desc = meta_desc(b)
    img = og_image(b)
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": canon + "#brand"}, "breadcrumb": {"@id": canon + "#breadcrumb"}, "primaryImageOfPage": img},
        {"@type": "Brand", "@id": canon + "#brand", "name": b["name"], "description": b["desc"], "slogan": b["tagline"], "url": canon, "image": img},
        {"@type": "FAQPage", "@id": canon + "#faq", "inLanguage": "fr-FR", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]},
        {"@type": "BreadcrumbList", "@id": canon + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Les marques", "item": SITE + "/marques/"},
            {"@type": "ListItem", "position": 3, "name": b["name"], "item": canon}]},
    ]}
    return slug, page("\n".join(h), title, desc, canon, img, jl)

def index_page():
    canon = SITE + "/marques/"
    cards = "".join(f'''<div><a href="/marques/{SLUG[b["id"]]}/" style="text-decoration:none"><img src="{ea(url(b["img"]))}" alt="{ea(b["name"])}" loading="lazy" width="800" height="600" style="width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#EAE4DA;margin-bottom:16px"><h3>{e(b["name"])}</h3></a><p style="font-size:15px;margin:0 0 8px">{e(b["tagline"])}</p><p style="font-size:14px;color:#6B655C;margin:0">{len([p for p in products if p["brand"]==b["id"]])} pièces · {e(b["cats"])}</p></div>''' for b in brands)
    inner = f'''<div class="w"><section style="padding-top:clamp(48px,7vw,96px)"><p class="eyebrow">Les marques</p><h1>Sept maisons danoises</h1><p class="lead">Mobilier, luminaires et literie design, représentés en France par Scanideal.</p></section>
<section><h2>Les sept marques que nous représentons</h2><div class="grid">{cards}</div></section></div>'''
    desc = "Les sept maisons danoises représentées en France par Scanideal : Fredericia, Naver Collection, Loca, CPH Lighting, VIA Copenhagen, Rye Sleep et Savir Design."
    title = "Les marques danoises représentées en France | Scanideal"
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": canon, "url": canon, "name": title, "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}},
        {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": b["name"], "url": f"{SITE}/marques/{SLUG[b['id']]}/"} for i, b in enumerate(brands)]},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Les marques", "item": canon}]}]}
    return page(inner, title, desc, canon, og_image(brands[0]), jl)

def catalogue_page():
    canon = SITE + "/catalogue/"
    blocks = []
    for b in brands:
        prods = [p for p in products if p["brand"] == b["id"]]
        cats = {}
        for p in prods: cats[p["cat"]] = cats.get(p["cat"], 0) + 1
        chips = "".join(f"<li>{e(c)} <small>({k})</small></li>" for c, k in cats.items())
        blocks.append(f'<div><h2><a href="/marques/{SLUG[b["id"]]}/" style="text-decoration:none">{e(b["name"])}</a></h2><p>{e(b["tagline"])}. {len(prods)} pièce{"s" if len(prods) > 1 else ""} au catalogue.</p><ul class="chips">{chips}</ul><p style="margin-top:16px"><a href="/marques/{SLUG[b["id"]]}/">Voir la fiche {e(b["name"])}</a></p></div>')
    inner = f'''<div class="w"><section style="padding-top:clamp(48px,7vw,96px)"><p class="eyebrow">Catalogue</p><h1>Mobilier et luminaires design danois</h1><p class="lead">{len(products)} pièces de sept maisons danoises, représentées en France par Scanideal.</p>
<a class="btn" href="/">Ouvrir le catalogue interactif</a></section>
<section><div class="grid">{"".join(blocks)}</div></section></div>'''
    title = "Catalogue mobilier et luminaires design danois | Scanideal"
    desc = f"Catalogue Scanideal : {len(products)} pièces de mobilier, luminaires et literie design danois, de sept maisons représentées en France."
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": canon, "url": canon, "name": title, "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Catalogue", "item": canon}]}]}
    return page(inner, title, desc, canon, og_image(brands[0]), jl)

def contact_page():
    canon = SITE + "/contact/"
    inner = '''<div class="w"><section style="padding-top:clamp(48px,7vw,96px)"><p class="eyebrow">Contact</p><h1>Parlons de votre projet</h1><p class="lead">Un interlocuteur unique en France pour sept maisons danoises.</p>
<div class="grid" style="margin-top:48px"><div><h2 style="font-size:28px">Coordonnées</h2><p>Scanideal SARL<br>100 rue Grande<br>77430 Champagne-sur-Seine</p><p>Téléphone : <a href="tel:+33676775533">06 76 77 55 33</a><br>E-mail : <a href="mailto:info@scanideal.com">info@scanideal.com</a><br>Instagram : <a href="https://www.instagram.com/scanideal">@scanideal</a></p><p>Zone d'intervention : France entière.<br>SIREN 489 193 987, RCS Melun.</p></div>
<div><h2 style="font-size:28px">Comment ça se passe</h2><p>Décrivez votre besoin par e-mail ou par téléphone : collections, finitions, conditions revendeurs. Scanideal présente les collections, conseille sur les finitions, établit un chiffrage et, si cela est pertinent pour votre projet, peut fournir des échantillons, puis suit le projet avec le fabricant jusqu'à l'installation.</p><a class="btn" href="mailto:info@scanideal.com">Écrire à Scanideal</a> <a class="btn" style="background:none;color:#1C1B19;border:1px solid #1C1B19" href="/">Formulaire de contact</a></div></div></section></div>'''
    title = "Contact Scanideal | Agent des marques danoises en France"
    desc = "Contactez Scanideal, agent commercial de sept maisons danoises de mobilier et luminaires en France : chiffrage, finitions, conditions revendeurs."
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "ContactPage", "@id": canon, "url": canon, "name": title, "description": desc, "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}, "about": ORG},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Contact", "item": canon}]}]}
    return page(inner, title, desc, canon, og_image(brands[0]), jl)

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(content)

for b in brands:
    slug, content = brand_page(b)
    write(f"{ROOT}/marques/{slug}/index.html", content)
write(f"{ROOT}/marques/index.html", index_page())
write(f"{ROOT}/catalogue/index.html", catalogue_page())
write(f"{ROOT}/contact/index.html", contact_page())

today = datetime.date.today().isoformat()
urls = [SITE + "/", SITE + "/marques/", SITE + "/catalogue/", SITE + "/contact/"] + [f"{SITE}/marques/{SLUG[b['id']]}/" for b in brands]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{'1.0' if u.endswith('.com/') else '0.8'}</priority>\n  </url>\n" for u in urls) + "</urlset>\n"
write(ROOT + "/sitemap.xml", sm)
print("pages:", len(brands) + 3, "urls sitemap:", len(urls))
