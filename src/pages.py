"""Sidor som byggs från innehåll hämtat ur Wix-sidan (content/wix/*.json).

Varje JSON-fil beskriver en sida: titel, beskrivning, datum och en lista med block
(rubriker, stycken, listor, bilder, inbäddade videor) i den ordning de står på Wix.
Texterna återges som de är. Bara HTML-formatering (länkar, fetstil, kursiv) behålls.
"""
import glob
import json
import os
import re
from html.parser import HTMLParser

import build as B
from content import *  # noqa: F401,F403

CONTENT_DIR = os.path.join(B.ROOT, "content", "wix")


# ---------------------------------------------------------------- Inläsning
def load_all():
    pages = {}
    for f in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        for item in (data if isinstance(data, list) else [data]):
            pages[item["path"]] = item
    return pages


class _Clean(HTMLParser):
    """Behåller bara länkar, fetstil, kursiv och radbrytningar."""
    KEEP = {"a", "strong", "b", "em", "i", "u", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.KEEP:
            return
        if tag == "a":
            href = dict(attrs).get("href", "")
            self.out.append(f'<a href="{B.e(rewrite_link(href))}">')
        elif tag == "br":
            self.out.append("<br>")
        else:
            self.out.append(f"<{'strong' if tag == 'b' else 'em' if tag == 'i' else tag}>")

    def handle_endtag(self, tag):
        if tag in self.KEEP and tag != "br":
            self.out.append(f"</{'strong' if tag == 'b' else 'em' if tag == 'i' else tag}>")

    def handle_data(self, data):
        self.out.append(B.e(data, quote=False))


def clean_html(h, fallback=""):
    if not h:
        return B.e(fallback)
    p = _Clean()
    p.feed(h)
    p.close()
    return "".join(p.out).strip()


def rewrite_link(href):
    """Interna länkar till Wix-sidan pekar om till den nya sajtens adresser."""
    m = re.match(r"https?://(?:www\.)?nicklaskarpaty\.com(/[^?#]*)?(#.*)?$", href or "")
    if m:
        return B.url((m.group(1) or "/").rstrip("/") or "/") if not m.group(2) else B.url((m.group(1) or "/") + m.group(2))
    return href


def wix_img(media_id, w=1600):
    return f"https://static.wixstatic.com/media/{media_id}/v1/fit/w_{w},h_{w},q_85,enc_auto/file.jpg"


def embed_target(src):
    m = re.search(r"player\.vimeo\.com/video/(\d+)", src or "")
    if m:
        return "vimeo", m.group(1)
    m = re.search(r"(?:youtube(?:-nocookie)?\.com/embed/|youtu\.be/)([\w-]{11})", src or "")
    if m:
        return "youtube", m.group(1)
    return None, None


# ---------------------------------------------------------------- Brödtext från block
def render_blocks(blocks, skip_title=True, skip_texts=()):
    """Gör om Wix-blocken till ren HTML. Listpunkter samlas i listor, bildtexter hamnar under sin bild."""
    out, ul, first_h1 = [], [], True
    skip = {s.strip().lower() for s in skip_texts}

    def flush():
        if ul:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in ul) + "</ul>")
            ul.clear()

    for b in blocks:
        t = b["t"]
        if t == "li":
            ul.append(clean_html(b.get("h"), b.get("x", "")))
            continue
        flush()
        if t in ("h1",) and skip_title and first_h1:
            first_h1 = False
            continue
        if b.get("x", "").strip().lower() in skip:
            continue
        if t in ("h1", "h2"):
            out.append(f"<h2>{B.e(b['x'])}</h2>")
        elif t in ("h3", "h4", "h5", "h6"):
            out.append(f"<h3>{B.e(b['x'])}</h3>")
        elif t == "p":
            out.append(f"<p>{clean_html(b.get('h'), b.get('x', ''))}</p>")
        elif t == "blockquote":
            out.append(f"<blockquote>{clean_html(b.get('h'), b.get('x', ''))}</blockquote>")
        elif t == "img":
            out.append(f'<figure><img src="{wix_img(b["id"])}" alt="{B.e(b.get("alt", ""))}" loading="lazy"></figure>')
        elif t == "cap" and out and out[-1].startswith("<figure>"):
            out[-1] = out[-1].replace("</figure>", f"<figcaption>{B.e(b['x'])}</figcaption></figure>")
        elif t == "embed":
            prov, vid = embed_target(b.get("src"))
            if prov:
                out.append(f'<button class="video-embed" type="button" data-play="{prov}:{vid}" data-title="Video">'
                           f'{B.PLAY}<span>Play video</span></button>')
    flush()
    return "\n".join(out)


def first_text(blocks):
    for b in blocks:
        if b["t"] == "p" and len(b.get("x", "")) > 60:
            return b["x"]
    return ""


def first_image(blocks):
    for b in blocks:
        if b["t"] == "img":
            return b["id"]
    return None


def nice_case(t):
    """Wix-rubriker är ofta skrivna i versaler. Gör om till vanlig skrivning; CSS sköter versalerna."""
    if t.isupper():
        small = {"and", "or", "of", "the", "a", "an", "in", "on", "for", "to", "with", "&"}
        words = t.lower().split()
        t = " ".join(w if (i and w in small) else (w.upper() if w in {"ai", "vp", "icvfx", "dop", "fsf", "cv", "pdf"} else w.capitalize()) for i, w in enumerate(words))
    return t


def page_title(p):
    for b in p["blocks"]:
        if b["t"] == "h1":
            return nice_case(b["x"].replace("\n", " ").strip())
    return p["title"].split("|")[0].strip()


def fmt_date(iso):
    if not iso:
        return ""
    y, m, d = iso[:10].split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return f"{int(d)} {months[int(m) - 1]} {y}"


def read_minutes(blocks):
    words = sum(len(b.get("x", "").split()) for b in blocks if b["t"] in ("p", "li", "h2", "h3"))
    return max(1, round(words / 220))


# ---------------------------------------------------------------- Blogginlägg
def post_page(p):
    path = p["path"]
    title = page_title(p)
    desc = p.get("desc") or first_text(p["blocks"])[:155]
    img_id = first_image(p["blocks"])
    hero = wix_img(img_id, 1920) if img_id else B.abs_url("media/hero-poster.jpg")
    blocks = list(p["blocks"])
    # Wix lägger samma bild först i inlägget som omslag; den visas som stor bild i stället
    if img_id:
        for i, b in enumerate(blocks):
            if b["t"] == "img" and b["id"] == img_id:
                del blocks[i]
                break
    schema = [B.person_schema(), B.org_schema(),
              {"@type": "BlogPosting", "@id": B.SITE + path + "#article", "headline": title, "description": desc,
               "image": [hero], "datePublished": p.get("pub", "")[:10] or None, "dateModified": (p.get("mod") or p.get("pub", ""))[:10] or None,
               "author": {"@id": B.SITE + "/#person"}, "publisher": {"@id": B.SITE + "/#person"},
               "mainEntityOfPage": B.SITE + path, "inLanguage": "en"},
              B.crumbs_schema([("Home", "/"), ("Blog", "/blog"), (title, path)])]
    schema[2] = {k: v for k, v in schema[2].items() if v is not None}
    dates = f"Published {fmt_date(p.get('pub'))}" if p.get("pub") else ""
    if p.get("mod") and p.get("pub") and p["mod"][:10] != p["pub"][:10]:
        dates += f" · Updated {fmt_date(p['mod'])}"
    body = f"""{B.head(title, desc, path, hero, schema, og_type='article')}
<body class="page">{B.header('/blog')}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{B.url('/')}">Home</a><span>/</span><a href="{B.url('/blog')}">Blog</a></nav>
    <header class="article-head">
      <h1>{B.e(title)}</h1>
      <p class="byline">By <b>{NAME_FULL}</b>{' · ' + dates if dates else ''} · {read_minutes(p['blocks'])} min read</p>
    </header>
  </div>
  {f'<div class="wrap article-hero"><img src="{hero}" alt="{B.e(title)}"></div>' if img_id else ''}
  <article class="article"><div class="wrap"><div class="body">
{render_blocks(blocks)}
<div class="author"><img src="{B.asset('media/portrait.jpg')}" alt="" width="72" height="72" loading="lazy"><div><b>{NAME_FULL}</b><span>Director of Photography. {LOCATION}.</span></div></div>
  </div></div></article>
  <nav class="other" aria-label="Related"><div class="wrap"><p class="label-sm">More</p><ul>
    <li><a href="{B.url('/blog')}">All articles</a></li>
    <li><a href="{B.url('/drama-cinematography')}">Drama &amp; Fiction</a></li>
    <li><a href="{B.url('/#contact')}">Contact</a></li>
  </ul></div></nav>
</main>
{B.footer()}"""
    B.write(path, body)


def blog_index(posts):
    path = "/blog"
    title = "Blog | Nicklas Karpaty, FSF"
    desc = "Articles by cinematographer Nicklas Karpaty, FSF on drama, documentary, commercials, virtual production and working with directors and producers."
    posts = sorted(posts, key=lambda p: p.get("pub", ""), reverse=True)
    cards = []
    for p in posts:
        img = first_image(p["blocks"])
        t = page_title(p)
        cards.append(f"""<li><a class="postcard" href="{B.url(p['path'])}">
  <div class="frame">{f'<img src="{wix_img(img, 960)}" alt="" loading="lazy">' if img else ''}</div>
  <div class="txt"><p class="label-sm">{fmt_date(p.get('pub'))}</p><h2>{B.e(t)}</h2><p>{B.e(first_text(p['blocks'])[:180].rsplit(' ', 1)[0])}…</p><span class="tlink">Read the article</span></div>
</a></li>""")
    schema = [B.person_schema(), B.org_schema(),
              {"@type": "Blog", "@id": B.SITE + path, "url": B.SITE + path, "name": "Blog", "author": {"@id": B.SITE + "/#person"},
               "blogPost": [{"@type": "BlogPosting", "headline": page_title(p), "url": B.SITE + p["path"],
                             **({"datePublished": p["pub"][:10]} if p.get("pub") else {})} for p in posts]},
              B.crumbs_schema([("Home", "/"), ("Blog", path)])]
    body = f"""{B.head(title, desc, path, B.abs_url('media/hero-poster.jpg'), schema)}
<body class="page">{B.header(path)}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{B.url('/')}">Home</a><span>/</span>Blog</nav>
    <header class="page-head"><h1>Blog</h1><p class="intro">Notes from set and prep: how I work, what I have learned, and what producers and directors ask me about.</p></header>
    <ul class="post-list">{''.join(cards)}</ul>
  </div>
</main>
{B.footer()}"""
    B.write(path, body)


# ---------------------------------------------------------------- Textsidor (process, AI, downloads, juridik)
def text_page(p, current="", extra_html="", extra_schema=None, intro=None):
    path = p["path"]
    title_h1 = page_title(p)
    title = p["title"] if "|" in p["title"] else f"{title_h1} | {NAME_FULL}"
    desc = p.get("desc") or first_text(p["blocks"])[:155]
    schema = [B.person_schema(), B.org_schema(),
              {"@type": "WebPage", "@id": B.SITE + path, "url": B.SITE + path, "name": title, "description": desc, "inLanguage": "en"},
              B.crumbs_schema([("Home", "/"), (title_h1, path)])] + (extra_schema or [])
    body = f"""{B.head(title, desc, path, B.abs_url('media/hero-poster.jpg'), schema)}
<body class="page">{B.header(current or path)}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{B.url('/')}">Home</a><span>/</span>{B.e(title_h1)}</nav>
    <header class="page-head"><h1>{B.e(title_h1)}</h1>{f'<p class="intro">{B.e(intro)}</p>' if intro else ''}</header>
  </div>
  <article class="article textpage"><div class="wrap"><div class="body">
{render_blocks(p['blocks'])}
{extra_html}
  </div></div></article>
</main>
{B.footer()}"""
    B.write(path, body)


def faq_html_and_schema():
    items = "".join(f"<details><summary>{B.e(q)}</summary><p>{B.e(a)}</p></details>" for q, a in FAQ)
    html = f'<section class="faq" aria-labelledby="faq-h"><h2 id="faq-h">Frequently asked questions</h2>{items}</section>'
    schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return html, schema


# ---------------------------------------------------------------- Genresidor (dokumentär, branded, VP)
def genre_page(p, key):
    path = p["path"]
    g = next(x for x in GENRES if x["key"] == key)
    h1 = page_title(p)
    title = p["title"] if "|" in p["title"] else f"{g['name']} Cinematographer | {NAME_FULL}"
    desc = p.get("desc") or g["blurb"]
    intro_text = first_text(p["blocks"])
    films = FILMS.get(key, [])
    feature = tiles = extra = ""
    if films:
        f = films[0]
        if f["p"] == "link":
            feature = (f'<div class="feature still"><img src="{B.src(f["img"])}" alt="Still from {B.e(f["t"])}"></div>')
        else:
            feature = (f'<button class="feature" type="button" data-play="{f["p"]}:{f["id"]}" data-title="{B.e(f["t"])} · {B.e(f["s"])}">'
                       f'<img src="{B.src(f["img"])}" alt="Still from {B.e(f["t"])}"><span class="cap"><span><b>{B.e(f["t"])}</b>'
                       f'<small>{B.e(f["s"])}</small></span><span class="pill">{B.PLAY}Play</span></span></button>')
        tiles = '<div class="films"><div class="tiles">' + "".join(B.tile(x) for x in films[1:]) + "</div></div>"
    if key == "vp":
        feature = f'<div class="feature still"><img src="{B.src(VP_POST["img"])}" alt="LED volume at Stockholm VP Studio"></div>'
        extra = f"""<section class="cta-band" aria-labelledby="vp-post-h"><div class="wrap">
  <h2 id="vp-post-h">{B.e(VP_POST['title'])}</h2>
  <p>A day at Stockholm VP Studio: what an LED volume delivers on set, and where it doesn't fit.</p>
  <div class="row"><a href="{B.url('/post/' + VP_POST['slug'])}">Read the article</a></div>
</div></section>"""
    if key == "branded":
        extra = f"""<section class="logo-row clients-all" aria-label="Clients"><div class="wrap">
  <p class="label-sm">Clients</p>
  {B.client_logos(ALL_CLIENTS)}
</div></section>"""
    schema = [B.person_schema(), B.org_schema(),
              {"@type": "Service", "@id": B.SITE + path + "#service", "name": g["name"] + " cinematography",
               "serviceType": "Director of Photography, " + g["name"].lower(), "provider": {"@id": B.SITE + "/#person"},
               "areaServed": ["Sweden", "Europe", "Worldwide"], "url": B.SITE + path, "description": desc},
              {"@type": "WebPage", "@id": B.SITE + path, "url": B.SITE + path, "name": title, "description": desc,
               "about": {"@id": B.SITE + path + "#service"}, "inLanguage": "en"},
              B.crumbs_schema([("Home", "/"), (g["name"], path)])]
    others = "".join(f'<li><a href="{B.url(x["href"])}">{B.e(x["name"])}</a></li>' for x in GENRES if x["key"] != key)
    body = f"""{B.head(title, desc, path, B.abs_url(films[0]['img']) if films else B.abs_url(VP_POST['img']), schema)}
<body class="page">{B.header(path)}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{B.url('/')}">Home</a><span>/</span>{B.e(g['name'])}</nav>
    <header class="page-head"><h1>{B.e(h1)}</h1>{f'<p class="intro">{B.e(intro_text)}</p>' if intro_text else ''}</header>
    {feature}
    {tiles}
  </div>
  <article class="article textpage"><div class="wrap"><div class="body">
{render_blocks(p['blocks'], skip_texts=[intro_text, 'cinematography process'])}
  </div></div></article>
  {extra}
  <section class="cta-band" aria-labelledby="cta-h"><div class="wrap">
    <h2 id="cta-h">Planning a {B.e(g['name'].split(' &')[0].lower())} project?</h2>
    <p>Tell me about the project and I'll tell you how I would approach it.</p>
    <div class="row"><a href="mailto:{EMAIL}">{EMAIL}</a><a href="tel:{TEL}">{PHONE}</a></div>
  </div></section>
  <nav class="other" aria-label="Other work"><div class="wrap"><p class="label-sm">More work</p><ul>{others}</ul></div></nav>
</main>
{B.footer()}"""
    B.write(path, body)


def redirect_files(pages):
    """_redirects för Netlify/Cloudflare (riktiga 301) och små omdirigeringssidor för testadressen."""
    rules = list(REDIRECTS) + [(old, new) for old, new in pages.get("__renames__", [])]
    with open(os.path.join(B.ROOT, "_redirects"), "w", encoding="utf-8") as fh:
        for old, new in rules:
            fh.write(f"{old}  {new}  301\n")
    for old, new in rules:
        target = B.url(new)
        B.write(old, f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>Moved</title><link rel="canonical" href="{B.SITE}{new}"><meta http-equiv="refresh" content="0; url={target}"></head>
<body><p>This page has moved to <a href="{target}">{B.SITE}{new}</a>.</p></body></html>""")
