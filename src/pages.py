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
# Wix-bilder som redan finns lokalt i webbstorlek
LOCAL_IMG = {
    "f828c5_322523cf0cf04e52b4bdc170a3c029fb~mv2.jpg": "media/img/doc-01.jpg",
    "f828c5_d0af2914fbfb43589dcea7e99f9160a6~mv2.jpg": "media/img/doc-02.jpg",
    "f828c5_22d631f381f049c9adc8bc2d0926284b~mv2.jpg": "media/img/doc-03.jpg",
    "f828c5_26cadcef717f475299d909816b581e82~mv2.jpg": "media/img/doc-04.jpg",
    "f828c5_a3a2a02d6df84af889b2c27bcddb16e9~mv2.jpg": "media/img/vp-led-volume-hero.jpg",
    "f828c5_fdb75f89757b48a6a4f9bdc027be2090~mv2.jpg": "media/img/vp-01.jpg",
    "f828c5_1a001a1f40574ea0990535ceb79d1e53~mv2.jpg": "media/img/vp-02.jpg",
    "f828c5_7254b8074b8544319812195a0ea984f2~mv2.jpg": "media/img/vp-03.jpg",
    "f828c5_c0e145946c5442348f85e12eae9e6741~mv2.jpg": "media/img/vp-04.jpg",
}

# Wix-mallens platshållartext som syns på en sida; tas inte med
FILLER = ("welcome visitors to your site", "welcome")


def clean_alt(alt):
    """Wix sätter ofta filnamnet som alt-text. Ta bort filändelse och tekniska rester."""
    alt = re.sub(r"\.(jpe?g|png|heic|webp|gif|tiff?)$", "", (alt or "").strip(), flags=re.I)
    alt = re.sub(r"[_]+", " ", alt)
    alt = re.sub(r"\b(edited|copy|kopia|final)\b", "", alt, flags=re.I)
    alt = re.sub(r"^(IMG|DSC|Namnlös design)[ \-]?\d*(\s*\(\d+\))?\s*$", "", alt, flags=re.I)
    return re.sub(r"\s{2,}", " ", alt).strip(" -,")


def img_src(media_id, w=1600):
    return B.asset(LOCAL_IMG[media_id]) if media_id in LOCAL_IMG else wix_img(media_id, w)


def looks_like_heading(b, nxt):
    """Wix-stycken som i praktiken är rubriker: numrerade, slutar med kolon, eller korta och följs av bilder."""
    x = b.get("x", "").strip()
    if b["t"] != "p" or "<a" in (b.get("h") or "") or len(x) > 80 or "\n" in x:
        return False
    if re.match(r"^\d+[.:]\s", x) or x.endswith(":"):
        return True
    return bool(nxt) and nxt["t"] == "img" and not x.endswith((".", "!", "?"))


def strip_before_title(blocks):
    """Tar bort allt före sidans första H1 (Wix-etiketter och toppbild). Returnerar (block, toppbild)."""
    for i, b in enumerate(blocks):
        if b["t"] == "h1":
            hero = next((x["id"] for x in blocks[:i] if x["t"] == "img"), None)
            return blocks[i:], hero
    return blocks, None


def render_blocks(blocks, skip_title=True, skip_texts=()):
    """Gör om Wix-blocken till ren HTML. Listpunkter blir listor, bildserier blir gallerier, bildtexter hamnar under sin bild."""
    out, ul, gal, first_h1 = [], [], [], True
    skip = {s.strip().lower() for s in skip_texts if s}

    def flush_ul():
        if ul:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in ul) + "</ul>")
            ul.clear()

    def flush_gal():
        if len(gal) == 1:
            i, alt = gal[0]
            out.append(f'<figure><img src="{img_src(i)}" alt="{B.e(alt)}" loading="lazy"></figure>')
        elif gal:
            out.append('<div class="gallery">' + "".join(f'<img src="{img_src(i, 1200)}" alt="{B.e(alt)}" loading="lazy">' for i, alt in gal) + "</div>")
        gal.clear()

    for n, b in enumerate(blocks):
        t = b["t"]
        nxt = blocks[n + 1] if n + 1 < len(blocks) else None
        x = b.get("x", "").strip()
        if t == "img":
            flush_ul()
            gal.append((b["id"], clean_alt(b.get("alt", ""))))
            continue
        if t == "cap" and gal:
            if len(gal) == 1:
                flush_gal()
                out[-1] = out[-1].replace("</figure>", f"<figcaption>{B.e(x)}</figcaption></figure>")
            continue
        flush_gal()
        if t == "li":
            ul.append(clean_html(b.get("h"), x))
            continue
        flush_ul()
        if t == "h1" and skip_title and first_h1:
            first_h1 = False
            continue
        if x.lower() in skip or x.lower().startswith(FILLER[0]) or x.lower() == FILLER[1]:
            continue
        if t in ("h1", "h2", "h3", "h4", "h5", "h6") and x.startswith(("\"", "“")):
            out.append(f"<blockquote>{B.e(x)}</blockquote>")
        elif t in ("h1", "h2"):
            out.append(f"<h2>{B.e(nice_case(x))}</h2>")
        elif t in ("h3", "h4", "h5", "h6"):
            out.append(f"<h3>{B.e(nice_case(x))}</h3>")
        elif looks_like_heading(b, nxt):
            out.append(f"<h2>{B.e(x.rstrip(':'))}</h2>")
        elif t == "p":
            out.append(f"<p>{clean_html(b.get('h'), x).replace(chr(10), '<br>')}</p>")
        elif t == "blockquote":
            out.append(f"<blockquote>{clean_html(b.get('h'), x)}</blockquote>")
        elif t == "embed":
            prov, vid = embed_target(b.get("src"))
            if prov:
                out.append(video_button(prov, vid))
    flush_gal()
    flush_ul()
    return "\n".join(out)


def video_button(prov, vid, title="Video"):
    thumb = f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">' if prov == "youtube" else ""
    return (f'<button class="video-embed" type="button" data-play="{prov}:{vid}" data-title="{B.e(title)}">'
            f'{thumb}<span>{B.PLAY} Play video</span></button>')


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
    return p["title"].split(" | ")[0].strip()


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
    hero = img_src(img_id, 1920) if img_id else B.asset("media/hero-poster.jpg")
    hero_abs = hero if hero.startswith("http") else B.SITE + "/" + LOCAL_IMG.get(img_id, "media/hero-poster.jpg")
    blocks = list(p["blocks"])
    hero_cap = ""
    # Den första bilden visas som stor omslagsbild, med sin bildtext
    if img_id:
        i = next(i for i, b in enumerate(blocks) if b["t"] == "img" and b["id"] == img_id)
        if i + 1 < len(blocks) and blocks[i + 1]["t"] == "cap":
            hero_cap = blocks[i + 1]["x"]
            del blocks[i + 1]
        del blocks[i]
    # YouTube-filmer inbäddade i inlägget (inte sidfotens spellista)
    extra_vids = [v for v in p.get("vids", []) if v != "youtube:DNIW8MwjedE"]
    if extra_vids and not any(b["t"] == "embed" for b in blocks):
        pos = next((i + 1 for i, b in enumerate(blocks) if b["t"] == "p"), 0)
        for v in reversed(extra_vids):
            prov, vid = v.split(":")
            blocks.insert(pos, {"t": "embed", "src": f"https://www.youtube.com/embed/{vid}" if prov == "youtube" else f"https://player.vimeo.com/video/{vid}"})
    schema = [B.person_schema(), B.org_schema(),
              {"@type": "BlogPosting", "@id": B.SITE + path + "#article", "headline": title, "description": desc,
               "image": [hero_abs], "datePublished": p.get("pub", "")[:10] or None, "dateModified": (p.get("mod") or p.get("pub", ""))[:10] or None,
               "author": {"@id": B.SITE + "/#person"}, "publisher": {"@id": B.SITE + "/#person"},
               "mainEntityOfPage": B.SITE + path, "inLanguage": "en"},
              B.crumbs_schema([("Home", "/"), ("Blog", "/blog"), (title, path)])]
    schema[2] = {k: v for k, v in schema[2].items() if v is not None}
    dates = f"Published {fmt_date(p.get('pub'))}" if p.get("pub") else ""
    if p.get("mod") and p.get("pub") and p["mod"][:10] != p["pub"][:10]:
        dates += f" · Updated {fmt_date(p['mod'])}"
    body = f"""{B.head(title, desc, path, hero_abs, schema, og_type='article')}
<body class="page">{B.header('/blog')}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{B.url('/')}">Home</a><span>/</span><a href="{B.url('/blog')}">Blog</a></nav>
    <header class="article-head">
      <h1>{B.e(title)}</h1>
      <p class="byline">By <b>{NAME_FULL}</b>{' · ' + dates if dates else ''} · {read_minutes(p['blocks'])} min read</p>
    </header>
  </div>
  {f'<figure class="wrap article-hero" style="margin:0 auto"><img src="{hero}" alt="{B.e(hero_cap or title)}">' + (f'<figcaption>{B.e(hero_cap)}</figcaption>' if hero_cap else '') + '</figure>' if img_id else ''}
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
    blocks, hero_id = strip_before_title(p["blocks"])
    if not any(b["t"] == "h1" for b in p["blocks"]):
        # Sidor utan H1 (juridik, downloads) har en etikett överst som blir rubrik
        blocks = [b for b in p["blocks"]]
        if blocks and blocks[0]["t"] in ("h2", "h3", "h4"):
            title_h1 = nice_case(blocks[0]["x"])
            blocks = blocks[1:]
        norm = lambda t: t.strip().lower().replace("&", "and")
        if blocks and norm(blocks[0].get("x", "")) == norm(title_h1):
            blocks = blocks[1:]
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
    {f'<div class="feature still"><img src="{img_src(hero_id, 1920)}" alt=""></div>' if hero_id else ''}
  </div>
  <article class="article textpage"><div class="wrap"><div class="body">
{render_blocks(blocks)}
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
    blocks, hero_id = strip_before_title(p["blocks"])
    intro_text = first_text(blocks)
    # Spelbara filmer först, sedan stillbilder från filmer som bara finns på Wix
    films = FILMS.get(key, []) if key != "doc" else []
    playable = [f for f in films if f["p"] != "link"]
    stills = [f for f in films if f["p"] == "link"]
    feature = tiles = extra = ""
    if playable:
        f = playable[0]
        feature = (f'<button class="feature" type="button" data-play="{f["p"]}:{f["id"]}" data-title="{B.e(f["t"])} · {B.e(f["s"])}">'
                   f'<img src="{B.src(f["img"])}" alt="Still from {B.e(f["t"])}"><span class="cap"><span><b>{B.e(f["t"])}</b>'
                   f'<small>{B.e(f["s"])}</small></span><span class="pill">{B.PLAY}Play</span></span></button>')
    elif hero_id:
        feature = f'<div class="feature still"><img src="{img_src(hero_id, 1920)}" alt=""></div>'
    rest = playable[1:] + stills
    if rest:
        def still_tile(f):
            return (f'<div class="tile"><div class="frame"><img src="{B.src(f["img"])}" alt="Still from {B.e(f["t"])}" loading="lazy"></div>'
                    f'<div class="meta">{B.e(f["t"])}<small>{B.e(f["s"])}</small></div></div>')
        tiles = '<div class="films"><div class="tiles">' + "".join(B.tile(f) if f["p"] != "link" else still_tile(f) for f in rest) + "</div></div>"
    if key == "vp":
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
    og = B.abs_url(LOCAL_IMG[hero_id]) if hero_id in LOCAL_IMG else (wix_img(hero_id, 1600) if hero_id else B.abs_url(VP_POST["img"]))
    body = f"""{B.head(title, desc, path, og, schema)}
<body class="page">{B.header(path)}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{B.url('/')}">Home</a><span>/</span>{B.e(g['name'])}</nav>
    <header class="page-head"><h1>{B.e(h1)}</h1>{f'<p class="intro">{B.e(intro_text)}</p>' if intro_text else ''}</header>
    {feature}
    {tiles}
  </div>
  <article class="article textpage"><div class="wrap"><div class="body">
{render_blocks(blocks, skip_texts=[intro_text])}
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
