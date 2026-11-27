"""Allt innehåll på sajten. Texter, filmer, loggor och kontaktuppgifter ändras här, inte i HTML-filerna."""

SITE = "https://www.nicklaskarpaty.com"
NAME = "Nicklas Karpaty"
NAME_FULL = "Nicklas Karpaty, FSF"
LOCATION = "Stockholm & Gothenburg, working internationally"
EMAIL = "info@nicklaskarpaty.com"
PHONE = "+46 703 61 20 49"
TEL = "+46703612049"

SOCIAL = [
    ("IMDb", "https://www.imdb.com/name/nm1597947/"),
    ("Vimeo", "https://vimeo.com/nicklaskarpaty"),
    ("LinkedIn", "https://www.linkedin.com/in/nkarpaty/"),
    ("Instagram", "https://www.instagram.com/nicklaskarpaty_dp"),
    ("Facebook", "https://www.facebook.com/cinematographer.nk"),
]

SHOWREEL = {"p": "vimeo", "id": "908412577", "t": "Showreel", "s": NAME_FULL}


def wix(media_id, w=1280, h=None):
    """Bild från Wix. Byts mot originalfiler i media/ inför lansering."""
    if h:
        return f"https://static.wixstatic.com/media/{media_id}/v1/fill/w_{w},h_{h},al_c,q_85,enc_auto/file.jpg"
    return f"https://static.wixstatic.com/media/{media_id}/v1/fit/w_{w},h_{w},q_85,enc_auto/file.jpg"


def vimeo_img(h):
    return "https://i.vimeocdn.com/video/" + h


def yt_img(i):
    return f"https://i.ytimg.com/vi/{i}/maxresdefault.jpg"


# Filmerna är samma Vimeo- och YouTube-länkar som på Wix-sidan.
FILMS = {
    "drama": [
        {"t": "Black Lake S2", "s": "Series, short sequence", "p": "vimeo", "id": "905125396", "img": vimeo_img("1786249766-18f5787ae5be890677a21ea2e534db5dfbacf83149ac4ed9a065fac9e1ce5164-d")},
        {"t": "Belief", "s": "Short fiction", "p": "vimeo", "id": "904803629", "img": vimeo_img("1785649490-4cc3ab5755b26600eb275c687a155ec292c36f5ee6025c611b277db7b64a816c-d")},
        {"t": "Golden Disc", "s": "Short sequence", "p": "vimeo", "id": "905171684", "img": vimeo_img("1786312084-34e5a7f2259132ea88b90a78019e351739599fb2f4753c169e5d92d7fb51348a-d")},
        {"t": "The Silence", "s": "Drama", "p": "vimeo", "id": "201880526", "img": vimeo_img("1785661089-8e2552cc61a32eb39164d51c3f85380ef4c0ffd38960b6f8f636489e58148988-d_1920x1080")},
        {"t": "SVT Molanders", "s": "Intro scene", "p": "vimeo", "id": "251651412", "img": vimeo_img("678164383-f007c2d7f6376d7f7d7e7061a2ba3783233a787367a7419a9358dec904ae6c57-d")},
    ],
    "branded": [
        {"t": "ZEEKR 007", "s": "Design film", "p": "link", "href": "/branded-cinematography", "img": "media/img/branded-zeekr-007.jpg"},
        {"t": "Volvo, In good hands", "s": "Campaign film", "p": "link", "href": "/branded-cinematography", "img": "media/img/branded-volvo-in-good-hands.jpg"},
        {"t": "Polestar Precept", "s": "From Concept to Car, ep. 3", "p": "youtube", "id": "GmVsIdWZknA", "img": yt_img("GmVsIdWZknA")},
        {"t": "LO", "s": "Campaign film", "p": "link", "href": "/branded-cinematography", "img": "media/img/branded-lo.jpg"},
        {"t": "Reach for Change", "s": "Film", "p": "link", "href": "/branded-cinematography", "img": "media/img/branded-reach-for-change.jpg"},
        {"t": "Speedy Casino", "s": "TVC", "p": "youtube", "id": "ILgqP-ep7sE", "img": yt_img("ILgqP-ep7sE")},
    ],
    # Stillbilder från dokumentärsidan på Wix. Fler klipp kommer.
    "doc": [
        {"t": "Documentary", "s": "Observational", "p": "link", "href": "/documentary-cinematography", "img": "media/img/doc-01.jpg"},
        {"t": "Documentary", "s": "Long-form", "p": "link", "href": "/documentary-cinematography", "img": "media/img/doc-02.jpg"},
        {"t": "Documentary", "s": "On location", "p": "link", "href": "/documentary-cinematography", "img": "media/img/doc-03.jpg"},
        {"t": "Documentary", "s": "Observational", "p": "link", "href": "/documentary-cinematography", "img": "media/img/doc-04.jpg"},
    ],
}

GENRES = [
    {"key": "drama", "name": "Drama & Fiction", "href": "/drama-cinematography",
     "blurb": "Series, features and festival shorts. Light and lens chosen for the character, not for the frame on its own."},
    {"key": "doc", "name": "Documentary", "href": "/documentary-cinematography",
     "blurb": "Observational work where nothing happens twice. Being ready matters more than being in control."},
    {"key": "branded", "name": "Branded & Fashion", "href": "/branded-cinematography",
     "blurb": "Campaigns and brand films for agencies and brands, from Nordic design to international reach."},
    {"key": "vp", "name": "Virtual Production", "href": "/virtualproduction-cinematography",
     "blurb": "LED volume and in-camera VFX. I tested a volume to answer one question for producers: when is it worth it?"},
]

VP_POST = {
    "slug": "virtual-production-led-volume-cinematographer",
    "title": "What I Learned Testing an LED Volume as a Cinematographer",
    "img": "media/img/vp-led-volume-hero.jpg",
}

# Citaten är hämtade från Wix-startsidan. Där står namnet före citatet
# (bekräftat av att Karin Sylwans LinkedIn-länk sitter på "highly skilled"-citatet,
# och att dramasidan tillskriver "never just decorative" David Stavenow).
QUOTES = [
    ("Nicklas is a source of reassurance for a director, while also possessing an open, experimental, and creative eye.", "Peter Lindmark", "Film Director, Writer"),
    ("His technical decisions are never just decorative. They serve emotion, purpose and story. As a storyteller, Nicklas is quite simply my preferred creative partner.", "David Stavenow", "Film Director, Writer"),
    ("A highly skilled Director of Photography. Very professional and a pleasure to work with. He always has the best interest of the production in mind without compromising quality.", "Karin Sylwan", "Project Manager"),
    ("I can always rely on his flexibility, sense of style, and skill as a cinematographer. A clear recommendation when a director has yet to choose a Director of Photography.", "Setareh Lundgren", "Film Producer"),
]

# Loggor länkas från Wikimedia Commons i piloten. Inför lansering: egna kopior i media/logos/.
WM = "https://upload.wikimedia.org/wikipedia/"
# Startsidan: bara de största namnen. Officiella loggor (Wikimedia Commons), gjorda vita, i media/logos/top/.
CLIENTS = [(n, "media/logos/top/" + f + ".png") for n, f in [
    ("SVT", "svt"), ("BBC", "bbc"), ("FOX", "fox"), ("ICA", "ica"),
    ("Google", "google"), ("Spotify", "spotify"), ("Klarna", "klarna"), ("Polestar", "polestar"),
]]

# Hela kundlistan från Wix-sidan, till branded-sidan. Utklippta ur skärmdumpen, byts mot riktiga loggfiler.
ALL_CLIENTS = [(n, "media/logos/" + f + ".png") for n, f in [
    ("Google", "google"), ("Liseberg", "liseberg"), ("Polestar", "polestar"), ("Ascom", "ascom"),
    ("IKEA", "ikea"), ("Pinchos", "pinchos"), ("Spotify", "spotify"), ("BBC", "bbc"),
    ("ICA", "ica"), ("AstraZeneca", "astrazeneca"), ("Zeekr", "zeekr"), ("Lynk & Co", "lynk-co"),
    ("Android", "android"), ("JM", "jm"), ("Mat.se", "mat-se"), ("Einride", "einride"),
    ("H&M", "hm"), ("Uniqlo", "uniqlo"), ("Apoteket", "apoteket"), ("Klarna", "klarna"),
    ("AJ", "aj"), ("Reach for Change", "reach-for-change"), ("Schweppes", "schweppes"), ("Stena Line", "stena-line"),
]]
GEAR = [
    ("ARRI", WM + "commons/d/de/Arri_logo.svg", 30, False),
    ("Panavision", WM + "commons/7/73/Panavision_logo.svg", 46, False),
    ("Sony CineAlta", WM + "commons/e/e4/Sony_CineAlta_logo_V3.png", 64, False),
    ("RED Digital Cinema", WM + "en/3/36/Red-Camera-Logo.jpeg", 70, True),
]
