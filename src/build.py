"""Bygger nicklaskarpaty.com som ren, statisk HTML.

Kör:  python3 src/build.py            (testadressen på GitHub Pages)
      python3 src/build.py --live     (riktiga sajten, utan sökmotorspärr)
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import *  # noqa: E402,F403

LIVE = "--live" in sys.argv
BASE = "" if LIVE else "/nicklaskarpaty-pilot"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Sidor som finns i den nya sajten. Övriga länkar går till Wix-sidan tills de är byggda.
BUILT = {"/", "/drama-cinematography", "/post/" + VP_POST["slug"]}

e = html.escape
PLAY = '<svg viewBox="0 0 10 12" aria-hidden="true"><path d="M0 0l10 6-10 6z"/></svg>'


def url(path):
    """Länk inom sajten. Ej byggda sidor pekar till Wix-sidan i piloten."""
    anchor = ""
    if "#" in path:
        path, anchor = path.split("#", 1)
        anchor = "#" + anchor
    path = path or "/"
    if path in BUILT or LIVE:
        if path == "/":
            return (BASE + "/" + anchor) if BASE else ("/" + anchor)
        return BASE + path + "/" + anchor if not LIVE else path + anchor
    return SITE + path + anchor


def asset(p):
    return BASE + "/" + p


def person_schema():
    return {
        "@type": "Person", "@id": SITE + "/#person",
        "name": NAME, "honorificSuffix": "FSF", "jobTitle": "Cinematographer, Director of Photography",
        "url": SITE + "/", "image": SITE + "/media/portrait.jpg",
        "email": "mailto:" + EMAIL, "telephone": TEL,
        "address": {"@type": "PostalAddress", "addressLocality": "Stockholm", "addressCountry": "SE"},
        "workLocation": [{"@type": "Place", "name": "Stockholm, Sweden"}, {"@type": "Place", "name": "Gothenburg, Sweden"}],
        "worksFor": {"@id": SITE + "/#org"},
        "memberOf": {"@type": "Organization", "name": "FSF, Swedish Society of Cinematographers", "alternateName": "Föreningen Sveriges Filmfotografer"},
        "knowsAbout": ["Cinematography", "Drama and fiction", "Documentary", "Commercials", "Branded film", "Virtual Production", "In-camera VFX", "AI previsualisation", "Colour grading"],
        "sameAs": [s[1] for s in SOCIAL],
    }


def org_schema():
    return {
        "@type": "Organization", "@id": SITE + "/#org", "name": "Nordic Light Cinematography AB",
        "url": SITE + "/", "logo": SITE + "/media/nlc-symbol.png", "founder": {"@id": SITE + "/#person"},
        "address": {"@type": "PostalAddress", "addressLocality": "Stockholm", "addressCountry": "SE"},
        "areaServed": ["Stockholm", "Gothenburg", "Sweden", "Europe", "Worldwide"],
    }


def crumbs_schema(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(items)]}


def head(title, desc, path, image, schema, og_type="website"):
    canon = SITE + ("/" if path == "/" else path)
    robots = "" if LIVE else '\n  <meta name="robots" content="noindex, nofollow">'
    graph = json.dumps({"@context": "https://schema.org", "@graph": schema}, ensure_ascii=False, indent=1)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">{robots}
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{canon}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="{NAME_FULL}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{canon}">
  <meta property="og:image" content="{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#000000">
  <link rel="icon" href="{asset('media/nlc-symbol.png')}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Montserrat:wght@300;400;500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{asset('assets/site.css')}">
  <script type="application/ld+json">
{graph}
  </script>
</head>"""


def header(current=""):
    def a(label, path, cls=""):
        cur = ' aria-current="page"' if current == path else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a{c} href="{url(path)}"{cur}>{label}</a>'
    return f"""
<a class="skip" href="#main">Skip to content</a>
<header class="site-header" id="top"><div class="wrap">
  <a class="brand" href="{url('/')}" aria-label="{NAME_FULL}, home"><img src="{asset('media/nk-logo.png')}" alt="{NAME_FULL}" width="704" height="299"></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <nav class="nav" id="nav" aria-label="Primary">
    {a('Drama', '/drama-cinematography')}{a('Documentary', '/documentary-cinematography')}{a('Branded', '/branded-cinematography')}{a('VP', '/virtualproduction-cinematography')}{a('About', '/#about')}{a('Contact', '/#contact', 'cta')}
  </nav>
</div></header>"""


def logo_list(items, four=False):
    lis = []
    for it in items:
        name, src, h = it[0], it[1], it[2]
        jpg = " jpg" if len(it) > 3 and it[3] else ""
        lis.append(f'<li><img class="lg{jpg}" style="--h:{h}px" src="{src}" alt="{e(name)}" loading="lazy"></li>')
    return f'<ul class="logos{" four" if four else ""}">' + "".join(lis) + "</ul>"


def footer():
    social = "".join(f'<a href="{u}" rel="noopener">{n}</a>' for n, u in SOCIAL)
    return f"""
<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap">
    <h2 id="contact-h">Contact</h2>
    <a class="big" href="mailto:{EMAIL}">{EMAIL}</a>
    <a class="big" href="tel:{TEL}">{PHONE}</a>
    <p>{LOCATION}.</p>
    <div class="social">{social}</div>
  </div>
  <div class="logo-row" aria-label="Camera systems"><div class="wrap">
    <p class="label-sm">Shooting on</p>
    {logo_list(GEAR, four=True)}
  </div></div>
</section>
<footer><div class="wrap">
  <img src="{asset('media/nlc-symbol.png')}" alt="Nordic Light Cinematography" width="746" height="742" loading="lazy">
  <nav aria-label="Footer">
    <a href="{url('/cinematography-process')}">Process</a><a href="{url('/blog')}">Blog</a><a href="{url('/downloads')}">CV &amp; downloads</a><a href="{url('/privacypolicy')}">Privacy</a><a href="{url('/termsandconditions')}">Terms</a>
  </nav>
  <span>© 2026 {NAME_FULL} · Nordic Light Cinematography AB</span>
</div></footer>
<script src="{asset('assets/site.js')}" defer></script>
</body>
</html>
"""


def tile(f, big=False):
    title = e(f["t"])
    if f["p"] == "link":
        open_ = f'<a class="tile" href="{url(f["href"])}">'
        close, act = "</a>", "OPEN"
    else:
        open_ = f'<button class="tile" type="button" data-play="{f["p"]}:{f["id"]}" data-title="{title} · {e(f["s"])}">'
        close, act = "</button>", "&#9654; PLAY"
    return (f'{open_}<div class="frame"><img src="{f["img"]}" alt="Still from {title}" loading="lazy">'
            f'<span class="act">{act}</span></div><div class="meta">{title}<small>{e(f["s"])}</small></div>{close}')


def quotes_row():
    on = ' class="on"'
    figs = "".join(f'<figure{on if i == 0 else ""}><blockquote>{e(q)}</blockquote><figcaption><b>{e(n)}</b>{e(r)}</figcaption></figure>'
                   for i, (q, n, r) in enumerate(QUOTES))
    dots = "".join("<i></i>" for _ in QUOTES)
    return f"""
<section class="refs" id="references" aria-labelledby="refs-h"><div class="wrap">
  <h2 class="label-sm" id="refs-h">References</h2>
  <div class="qbox" aria-live="polite">{figs}</div>
  <div class="qctl"><span class="qdots" aria-hidden="true">{dots}</span><button id="qp" type="button" aria-label="Previous reference">&larr;</button><button id="qn" type="button" aria-label="Next reference">&rarr;</button></div>
</div></section>"""


def write(path, text):
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("skrev", os.path.relpath(out, ROOT))


# ---------------------------------------------------------------- Startsida
def home():
    title = "Nicklas Karpaty, FSF | Cinematographer & Director of Photography, Stockholm"
    desc = "Nicklas Karpaty, FSF is a director of photography for drama, documentary, commercials and virtual production. Stockholm & Gothenburg, working internationally."
    schema = [person_schema(), org_schema(), {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": NAME_FULL, "publisher": {"@id": SITE + "/#person"}, "inLanguage": "en"}]
    blocks = []
    for g in GENRES:
        if g["key"] == "vp":
            right = f"""<a class="postcard" href="{url('/post/' + VP_POST['slug'])}">
  <div class="frame"><img src="{VP_POST['img']}" alt="LED volume at Stockholm VP Studio" loading="lazy"></div>
  <div class="txt"><p class="label-sm">From the blog</p><h3>{e(VP_POST['title'])}</h3><p>An honest assessment of what an LED volume delivers on set, and where it doesn't fit.</p><span class="tlink">Read the article</span></div>
</a>"""
        else:
            right = '<div class="tiles">' + "".join(tile(f) for f in FILMS[g["key"]]) + "</div>"
        blocks.append(f"""
<section class="block" id="{g['key']}" aria-labelledby="{g['key']}-h"><div class="wrap grid">
  <div class="label"><h2 id="{g['key']}-h">{e(g['name'])}</h2><p>{e(g['blurb'])}</p><a class="tlink" href="{url(g['href'])}">More {e(g['name'].split(' &')[0].lower())}</a></div>
  {right}
</div></section>""")
    body = f"""{head(title, desc, '/', SITE + '/media/hero-poster.jpg', schema)}
<body>{header()}
<main id="main">
<section class="hero" aria-label="Showreel">
  <video id="hero-video" autoplay muted loop playsinline preload="metadata" poster="{asset('media/hero-poster.jpg')}"><source src="{asset('media/hero.mp4')}" type="video/mp4"></video>
  <div class="guide" id="guide" aria-hidden="true">
    <div class="g-top"></div><div class="g-bot"></div><div class="g-mask"></div>
    <div class="g-frame"><i></i><i></i><i></i><i></i></div><div class="g-cross"></div>
    <div class="hud t"><span><b>ARRI ALEXA 35</b></span><span>4.6K 3:2 · S35</span><span>25 fps · 180°</span><span>ISO 800 · 5600 K</span><span class="rec">REC <span class="tc" id="tc">00:00:00:00</span></span></div>
    <div class="hud b"><span class="opt">2.39:1</span><span>T2.8 · 35 mm</span><span class="opt">LUT: NLC</span></div>
  </div>
  <div class="hero-copy"><div class="wrap">
    <p class="role">Cinematographer · Director of Photography</p>
    <h1>Nicklas Karpaty<span class="fsf">, FSF</span></h1>
    <p class="where">{LOCATION}</p>
    <button class="reel" type="button" data-play="vimeo:{SHOWREEL['id']}" data-title="Showreel · {NAME_FULL}">{PLAY}Play showreel</button>
  </div></div>
  <button class="gtoggle" id="gt" type="button" aria-pressed="true">Frame guide: on</button>
</section>

<section class="logo-row" aria-label="Clients"><div class="wrap">
  <p class="label-sm">Trusted by</p>
  {logo_list(CLIENTS)}
</div></section>

<div id="work">{''.join(blocks)}</div>
{quotes_row()}

<section class="craft" aria-labelledby="craft-h"><div class="wrap">
  <div>
    <h2 id="craft-h">From sensor to screen</h2>
    <p>The look is decided before the camera rolls: lens, light, exposure and a show LUT built for the story. The grade finishes what was planned on set.</p>
    <p class="note">Test image. Replaced with a real LOG frame and its final grade.</p>
  </div>
  <div class="wipe">
    <img src="{asset('media/grade-flat.jpg')}" alt="The frame as recorded in LOG, before grading" loading="lazy">
    <img class="after" src="{asset('media/grade-graded.jpg')}" alt="The same frame after the final grade" loading="lazy">
    <span class="bar"></span><span class="tag l">LOG</span><span class="tag r">GRADE</span>
    <input id="wr" type="range" min="0" max="100" value="50" aria-label="Compare the LOG image with the final grade">
  </div>
</div></section>

<section class="about" id="about" aria-labelledby="about-h"><div class="wrap">
  <img src="{asset('media/portrait.jpg')}" alt="Portrait of Nicklas Karpaty, FSF" width="1200" height="1200" loading="lazy">
  <div>
    <h2 id="about-h">About</h2>
    <p class="lead">Storytelling dictates the language.</p>
    <p>I've worked as a cinematographer for more than 20 years, across international drama, award-winning festival films and premium commercial work. I don't carry a fixed style from job to job. Each script tells me what the image needs to be.</p>
    <p>Directors tend to describe me as a steady hand with an open, experimental eye. Clear communication and structure on set, and room to try things. I'm rooted in traditional craft, and I use new tools where they earn their place, such as AI-driven previsualisation that lets us test ideas long before the camera rolls.</p>
    <p>I run Nordic Light Cinematography AB from Stockholm and work from Gothenburg as well, on productions in Sweden and abroad. I'm a member of FSF, the Swedish Society of Cinematographers.</p>
    <div class="links"><a class="tlink" href="{url('/cinematography-process')}">My process</a><a class="tlink" href="{url('/downloads')}">CV &amp; downloads</a></div>
  </div>
</div></section>
</main>
{footer()}"""
    write("/", body)


# ---------------------------------------------------------------- Drama
DRAMA_SECTIONS = [
    ("Story first, then style",
     ["I don't bring a fixed look to drama. A gritty urban series and an intimate period piece need different answers, and the script decides which.",
      "I read for subtext. What a character can't say, the image has to carry. Light, lens and movement are chosen for that, not for how a frame looks on its own."]),
    ("Nordic light as a compass",
     ["My company is called Nordic Light Cinematography, and the name is a working principle more than a brand. Northern light is low and honest, with subtle contrasts and a long blue hour.",
      "I bring that sensibility to drama: atmospheric, motivated light that feels like part of the world rather than something put there for the camera. The aim is the emotional truth of the scene, so the light becomes an extension of the character's inner journey."]),
    ("Decisions made in prep, not on the day",
     ["Time on set is the most expensive thing a production buys. I use AI-driven previsualisation to build moving storyboards and test lighting and blocking before the shoot.",
      "The director, the producer and I can look at the same images, try angles and agree on the approach weeks ahead. It doesn't replace the craft. It protects the shooting day for the performances."]),
    ("The director's closest ally",
     ["Cinematography is a conversation. My job is to turn the director's intent into something a camera, grip and lighting team can execute, and to say early when an idea will cost more than it gives.",
      "Working on international productions has taught me to adapt quickly and decide clearly, from the first treatment to the final grade."]),
]


def drama():
    path = "/drama-cinematography"
    title = "Drama & Fiction Cinematographer | Nicklas Karpaty, FSF"
    desc = "Nicklas Karpaty, FSF is a cinematographer for drama and fiction. Script-first, Nordic light and AI-driven previs. Stockholm & Gothenburg, working internationally."
    films = FILMS["drama"]
    first, rest = films[0], films[1:]
    schema = [person_schema(), org_schema(),
              {"@type": "Service", "@id": SITE + path + "#service", "name": "Drama & fiction cinematography",
               "serviceType": "Director of Photography for drama, series and fiction",
               "provider": {"@id": SITE + "/#person"}, "areaServed": ["Sweden", "Europe", "Worldwide"],
               "url": SITE + path, "description": desc},
              {"@type": "WebPage", "@id": SITE + path, "url": SITE + path, "name": title, "description": desc,
               "about": {"@id": SITE + path + "#service"}, "inLanguage": "en"},
              crumbs_schema([("Home", "/"), ("Drama & Fiction", path)])]
    prose = "".join(f'<section><h2>{e(h)}</h2><div class="body">' + "".join(f"<p>{e(p)}</p>" for p in ps) + "</div></section>"
                    for h, ps in DRAMA_SECTIONS)
    q = QUOTES[1]
    others = "".join(f'<li><a href="{url(g["href"])}">{e(g["name"])}</a></li>' for g in GENRES if g["key"] != "drama")
    body = f"""{head(title, desc, path, first['img'], schema)}
<body class="page">{header(path)}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Home</a><span>/</span>Drama &amp; Fiction</nav>
    <header class="page-head">
      <h1>Drama &amp; Fiction Cinematography</h1>
      <p class="intro">Every script asks for its own visual language. My job is to find it, and to make sure the image serves the emotional core of the story.</p>
    </header>
    <button class="feature" type="button" data-play="vimeo:{first['id']}" data-title="{e(first['t'])} · {e(first['s'])}">
      <img src="{first['img']}" alt="Still from {e(first['t'])}">
      <span class="cap"><span><b>{e(first['t'])}</b><small>{e(first['s'])}</small></span><span class="pill">{PLAY}Play scene</span></span>
    </button>
    <div class="films"><div class="tiles">{''.join(tile(f) for f in rest)}</div></div>
  </div>

  <div class="prose"><div class="wrap">{prose}</div></div>

  <figure class="pullquote" style="margin:0"><div class="wrap">
    <blockquote>{e(q[0])}</blockquote>
    <figcaption><b>{e(q[1])}</b>{e(q[2])}</figcaption>
  </div></figure>

  <section class="cta-band" aria-labelledby="cta-h"><div class="wrap">
    <h2 id="cta-h">Planning a drama or fiction project?</h2>
    <p>Send me the script or treatment and I'll tell you how I would approach it.</p>
    <div class="row"><a href="mailto:{EMAIL}">{EMAIL}</a><a href="tel:{TEL}">{PHONE}</a></div>
  </div></section>

  <nav class="other" aria-label="Other work"><div class="wrap"><p class="label-sm">More work</p><ul>{others}</ul></div></nav>
</main>
{footer()}"""
    write(path, body)


# ---------------------------------------------------------------- VP-inlägget
def vp_post():
    path = "/post/" + VP_POST["slug"]
    title = VP_POST["title"]
    desc = "A cinematographer's honest assessment of Virtual Production after testing an LED volume: what ICVFX delivers on set, and where it doesn't fit."
    imgs = {k: wix(k, 1600) for k in [
        "f828c5_fdb75f89757b48a6a4f9bdc027be2090~mv2.jpg", "f828c5_1a001a1f40574ea0990535ceb79d1e53~mv2.jpg",
        "f828c5_7254b8074b8544319812195a0ea984f2~mv2.jpg", "f828c5_c0e145946c5442348f85e12eae9e6741~mv2.jpg"]}
    k = list(imgs.values())
    schema = [person_schema(), org_schema(),
              {"@type": "BlogPosting", "@id": SITE + path + "#article", "headline": title, "description": desc,
               "image": [VP_POST["img"]], "datePublished": "2026-08-18", "dateModified": "2026-10-08",
               "author": {"@id": SITE + "/#person"}, "publisher": {"@id": SITE + "/#person"},
               "mainEntityOfPage": SITE + path, "inLanguage": "en-GB",
               "about": ["Virtual Production", "LED volume", "In-camera VFX", "Cinematography"]},
              crumbs_schema([("Home", "/"), ("Blog", "/blog"), (title, path)])]
    P = lambda t: f"<p>{t}</p>"  # noqa: E731
    article = "".join([
        P("I spent a day at Stockholm VP Studio testing their LED volume. Not to be impressed by the technology. I already knew what it could do on paper. I went to answer a narrower question: when a producer asks me whether Virtual Production is right for their project, what should I tell them?"),
        P("Here is what I found."),
        "<h2>The wall is not a screen. It is a light source.</h2>",
        P("The distinction matters more than any other."),
        P("A green screen gives you a background in post-production. An LED volume gives you a background and the light that background would cast. Film a car in a tunnel and the tunnel lighting falls across the bonnet and the actor's face as it actually would. The reflections are real. The ambient wrap is real. Nobody paints it in later."),
        P("This is what separates ICVFX (in-camera visual effects) from compositing. The environment is rendered in real time and tracks with the camera, producing genuine parallax and depth. What the sensor sees is close to what the audience will see."),
        P("But it is a light source with a specific limitation. Most VP panels are built on RGB diodes, and RGB does not give you a full spectrum. The gaps sit in cyan and deep red, precisely where skin lives. Use the wall as your key on a face and you risk tones that read plastic, magenta-pushed, or simply dead."),
        P("In practice this means the volume handles ambience, wrap and reflection beautifully, and you still light your actors with high-CRI fixtures matched to the wall's colour temperature. The wall is an extraordinary environment light. It is not a replacement for knowing how to light a face."),
        "<h2>What it changes on set</h2>",
        P("<strong>The director sees the film, not a placeholder.</strong> The monitor shows something very near the final image. Creative decisions get made on the day, in the room, with everyone looking at the same thing, instead of being deferred into a post-production conversation weeks later."),
        P("<strong>Actors have somewhere to look.</strong> Performance improves when there is a world to react to rather than a blank green expanse and a description of what will eventually be there."),
        P("<strong>Time stops being an adversary.</strong> A sunset can hold for an entire shooting day. No chasing the light, no re-lighting between takes to match a sky that has moved on. The team spends its attention on performance and framing."),
        f'<figure><img src="{k[0]}" alt="Car on set in front of the LED volume at Stockholm VP Studio" loading="lazy"></figure>',
        "<h2>Where it falls short</h2>",
        P("This is the part most articles leave out."),
        P("<strong>It suits some scripts and not others.</strong> Driving sequences, science fiction, inaccessible or expensive locations: these are where the volume earns its cost. A dialogue scene in a real apartment does not become better inside a volume. It becomes more complicated."),
        P("<strong>The savings arrive only if the preparation does.</strong> Every virtual environment has to be built, lit and optimised before anyone walks into the studio. Cost moves from production into pre-production; it does not disappear. For a producer used to a different rhythm, this is the real adjustment: decisions that normally live in post now have to be made, and locked, months earlier. You cannot fix it in post. You fix it in prep."),
        P("<strong>The colour pipeline still needs work.</strong> Getting the direction of light right in camera is an enormous advantage over green-screen spill. But marrying a physical foreground to a rendered background so they read as one photographic space is genuinely difficult, and it takes a rigorous pipeline and real grading. Without it, you get the exact impression you were trying to avoid: actors standing in front of a screen."),
        P("<strong>The wall dictates your optics.</strong> Distance to the LED panels and depth of field are not free choices. Stop down too far and you resolve the pixel structure, or invite moiré. In practice you often work with faster glass and shallower focus than the scene might otherwise want. That is a real constraint on framing, not a footnote."),
        P("<strong>The lighting problem becomes harder, not easier.</strong> Physical foreground light must match the virtual background precisely, or the illusion collapses. The technology does not remove the cinematographer's judgement. It raises the cost of getting it wrong."),
        '<div class="gallery">' + "".join(f'<img src="{u}" alt="Behind the scenes in the LED volume, Stockholm VP Studio" loading="lazy">' for u in k[1:]) + "</div>",
        "<h2>The honest conclusion</h2>",
        P("Virtual Production is not the future of everything. It is a precise instrument that solves a specific set of problems extremely well and adds friction everywhere else."),
        P("For a producer, the useful question is not whether the technology is impressive. It is whether this particular script has scenes where controlled light, controlled time, or an unreachable location are what stands between the budget and the vision. Sometimes the answer is clearly yes. More often it is no, and knowing which is worth more than any amount of enthusiasm for the tool."),
        P(f'If you are weighing this workflow for an upcoming production, I am glad to look at the script and give you a straight answer on whether it fits, creatively and on budget. Write to me at <a class="tlink" href="mailto:{EMAIL}" style="text-transform:none;letter-spacing:0;font-size:inherit">{EMAIL}</a>.'),
        '<p class="credits">Thanks to Stockholm VP Studio, Storyline, and Michael Petersen, FSF, for behind-the-scenes footage and stills.</p>',
        f'<div class="author"><img src="{asset("media/portrait.jpg")}" alt="" width="72" height="72" loading="lazy"><div><b>{NAME_FULL}</b><span>Director of Photography. {LOCATION}.</span></div></div>',
    ])
    body = f"""{head(title, desc, path, VP_POST['img'], schema, og_type='article')}
<body class="page">{header()}
<main id="main">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Home</a><span>/</span><a href="{url('/blog')}">Blog</a><span>/</span>Virtual Production</nav>
    <header class="article-head">
      <h1>{e(title)}</h1>
      <p class="dek">A DoP's honest assessment of Virtual Production: what it delivers, and where it doesn't.</p>
      <p class="byline">By <b>{NAME_FULL}</b> · Published 18 August 2026 · Updated 8 October 2026 · 6 min read</p>
    </header>
  </div>
  <div class="wrap article-hero"><img src="{VP_POST['img']}" alt="LED volume at Stockholm VP Studio"></div>
  <article class="article"><div class="wrap"><div class="body">{article}</div></div></article>
  <nav class="other" aria-label="Related"><div class="wrap"><p class="label-sm">Related</p><ul>
    <li><a href="{url('/virtualproduction-cinematography')}">Virtual Production</a></li>
    <li><a href="{url('/drama-cinematography')}">Drama &amp; Fiction</a></li>
    <li><a href="{url('/blog')}">All articles</a></li>
  </ul></div></nav>
</main>
{footer()}"""
    write(path, body)


# ---------------------------------------------------------------- Filer för sökmotorer och AI
def seo_files():
    pages = [("/", "2026-11-26"), ("/drama-cinematography", "2026-11-26"), ("/post/" + VP_POST["slug"], "2026-10-08")]
    urls = "".join(f"<url><loc>{SITE}{'/' if p == '/' else p}</loc><lastmod>{d}</lastmod></url>" for p, d in pages)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    robots = ("User-agent: *\nAllow: /\n\n# AI-tjänster välkomna\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\n"
              "User-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\n"
              f"Sitemap: {SITE}/sitemap.xml\n") if LIVE else "# Testadress, spärrad för sökmotorer\nUser-agent: *\nDisallow: /\n"
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(robots)
    genres = "\n".join(f"- [{g['name']}]({SITE}{g['href']}): {g['blurb']}" for g in GENRES)
    llms = f"""# {NAME_FULL}

> Cinematographer and director of photography (DoP) for drama, documentary, commercials and virtual production. Member of FSF, the Swedish Society of Cinematographers. Runs Nordic Light Cinematography AB. {LOCATION}.

Contact: {EMAIL}, {PHONE}

## Work
{genres}

## Articles
- [{VP_POST['title']}]({SITE}/post/{VP_POST['slug']}): what an LED volume delivers on set, and where it doesn't fit.

## Profiles
""" + "\n".join(f"- [{n}]({u})" for n, u in SOCIAL) + "\n"
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as fh:
        fh.write(llms)
    print("skrev sitemap.xml, robots.txt, llms.txt")


if __name__ == "__main__":
    home(); drama(); vp_post(); seo_files()
    print("klart,", "riktiga sajten" if LIVE else "testadressen")
