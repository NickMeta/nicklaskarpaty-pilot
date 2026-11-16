/* Delad data för alla utkast. Videor och bilder hämtade ur nuvarande nicklaskarpaty.com 2026-11-12. */
(function () {
  var W = function (id, ext) { return 'https://static.wixstatic.com/media/f828c5_' + id + '~mv2.' + ext + '/v1/fill/w_960,h_540,al_c,q_80,enc_auto/file.jpg'; };
  var V = function (h) { return 'https://i.vimeocdn.com/video/' + h; };
  var Y = function (id) { return 'https://i.ytimg.com/vi/' + id + '/maxresdefault.jpg'; };
  var SITE = 'https://www.nicklaskarpaty.com/';
  var items = [
    // Drama & Fiction (Vimeo)
    { g: 'drama', t: 'Black Lake S2', s: 'Series, short sequence', p: 'vimeo', id: '905125396', img: V('1786249766-18f5787ae5be890677a21ea2e534db5dfbacf83149ac4ed9a065fac9e1ce5164-d') },
    { g: 'drama', t: 'Belief', s: 'Short fiction', p: 'vimeo', id: '904803629', img: V('1785649490-4cc3ab5755b26600eb275c687a155ec292c36f5ee6025c611b277db7b64a816c-d') },
    { g: 'drama', t: 'Golden Disc', s: 'Short sequence', p: 'vimeo', id: '905171684', img: V('1786312084-34e5a7f2259132ea88b90a78019e351739599fb2f4753c169e5d92d7fb51348a-d') },
    { g: 'drama', t: 'The Silence', s: 'Drama', p: 'vimeo', id: '201880526', img: V('1785661089-8e2552cc61a32eb39164d51c3f85380ef4c0ffd38960b6f8f636489e58148988-d_1920x1080') },
    { g: 'drama', t: 'SVT Molanders', s: 'Intro scene', p: 'vimeo', id: '251651412', img: V('678164383-f007c2d7f6376d7f7d7e7061a2ba3783233a787367a7419a9358dec904ae6c57-d') },
    // Branded & Fashion (YouTube, eller länk till nuvarande sidan där filmen ligger på Wix)
    { g: 'branded', t: 'ZEEKR 007', s: 'Design film', p: 'link', href: SITE + 'branded-cinematography', img: W('e203017198d947bc924ce6f3e8b7063e', 'png') },
    { g: 'branded', t: 'Volvo, In good hands', s: 'Campaign film', p: 'link', href: SITE + 'branded-cinematography', img: W('2f7e37be8a364a9dbc5de43046c63c3d', 'png') },
    { g: 'branded', t: 'Polestar Precept', s: 'From Concept to Car, ep. 3', p: 'youtube', id: 'GmVsIdWZknA', img: Y('GmVsIdWZknA') },
    { g: 'branded', t: 'LO', s: 'Campaign film', p: 'link', href: SITE + 'branded-cinematography', img: W('6b77a66c0b5840ae8abe7586c4413f46', 'png') },
    { g: 'branded', t: 'Reach for Change', s: 'Film', p: 'link', href: SITE + 'branded-cinematography', img: W('109ab19d596c4a8c88fca14ec5e3fdc5', 'png') },
    { g: 'branded', t: 'Speedy Casino', s: 'TVC', p: 'youtube', id: 'ILgqP-ep7sE', img: Y('ILgqP-ep7sE') },
    // Documentary och VP: stillbilder från respektive undersida (titlar saknas, byt mot rätt projektnamn)
    { g: 'doc', t: 'Documentary', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'documentary-cinematography', img: W('322523cf0cf04e52b4bdc170a3c029fb', 'jpg') },
    { g: 'doc', t: 'Documentary', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'documentary-cinematography', img: W('d0af2914fbfb43589dcea7e99f9160a6', 'jpg') },
    { g: 'doc', t: 'Documentary', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'documentary-cinematography', img: W('22d631f381f049c9adc8bc2d0926284b', 'jpg') },
    { g: 'doc', t: 'Documentary', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'documentary-cinematography', img: W('26cadcef717f475299d909816b581e82', 'jpg') },
    { g: 'vp', t: 'Virtual Production', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'virtualproduction-cinematography', img: W('7604f7a22e4c4c6bb00c6de290553d8b', 'jpg') },
    { g: 'vp', t: 'Virtual Production', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'virtualproduction-cinematography', img: W('fdb75f89757b48a6a4f9bdc027be2090', 'jpg') },
    { g: 'vp', t: 'Virtual Production', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'virtualproduction-cinematography', img: W('1a001a1f40574ea0990535ceb79d1e53', 'jpg') },
    { g: 'vp', t: 'Virtual Production', s: 'Still, byt mot projektnamn', p: 'link', href: SITE + 'virtualproduction-cinematography', img: W('c0e145946c5442348f85e12eae9e6741', 'jpg') }
  ];
  var genres = {
    drama: { name: 'Drama & Fiction', blurb: 'Series, features and festival shorts. Light and lens built around the character.', href: SITE + 'drama-cinematography' },
    doc: { name: 'Documentary', blurb: 'Observational work where the scene is never repeated.', href: SITE + 'documentary-cinematography' },
    branded: { name: 'Branded & Fashion', blurb: 'Campaigns and brand films for agencies and brands, from Nordic design to international reach.', href: SITE + 'branded-cinematography' },
    vp: { name: 'Virtual Production', blurb: 'LED volume and in-camera VFX, planned with the cinematographer in front of the wall.', href: SITE + 'virtualproduction-cinematography' }
  };
  var quotes = [
    { q: 'Nicklas is a source of reassurance for a director, while also possessing an open, experimental, and creative eye.', n: 'Karin Sylwan', r: 'Project Manager' },
    { q: 'Very professional and a pleasure to work with. He always has the best interest of the production in mind without compromising quality.', n: 'David Stavenow', r: 'Film Director, Writer' },
    { q: 'His technical decisions are never just decorative. They serve emotion, purpose and story. Quite simply my preferred creative partner.', n: 'Peter Lindmark', r: 'Film Director, Writer' },
    { q: 'Whenever I get to choose the Director of photography for a project, I always choose Nicklas Karpaty.', n: 'Setareh Lundgren', r: 'Film Producer' }
  ];
  // Testloggor: neutrala ordmärken i enhetlig stil. Byts mot riktiga loggor (SVG) när de finns.
  var clients = ['Volvo', 'Polestar', 'Zeekr', 'SVT', 'LO', 'Reach for Change', 'Ascom', 'Speedy Casino'];
  var contact = { email: 'info@nicklaskarpaty.com', phone: '+46 703 61 20 49', tel: '+46703612049' };
  var social = [['IMDb', 'https://www.imdb.com/name/nm1597947/'], ['Vimeo', 'https://vimeo.com/nicklaskarpaty'], ['LinkedIn', 'https://www.linkedin.com/in/nkarpaty/'], ['Instagram', 'http://www.instagram.com/nicklaskarpaty_dp'], ['Facebook', 'https://www.facebook.com/cinematographer.nk']];
  window.NK = { items: items, genres: genres, quotes: quotes, clients: clients, contact: contact, social: social, site: SITE,
    byGenre: function (g) { return items.filter(function (i) { return i.g === g; }); } };
})();
