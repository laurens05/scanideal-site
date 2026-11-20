/* Scanideal — bascule de langue FR / EN.
 * Le site est écrit en français. En anglais, chaque texte affiché (contenu et attributs alt,
 * title, placeholder, aria-label) est remplacé à la volée à partir du dictionnaire i18n-en.js,
 * chargé uniquement à la demande. Le français reste la langue par défaut. */
(function (root) {
  'use strict';

  /* ---------- Moteur de traduction (sans DOM, testable sous Node) ---------- */
  var COUNTRY = {
    'Danemark': 'Denmark', 'Pologne': 'Poland', 'Croatie': 'Croatia', 'Lettonie': 'Latvia', 'Lituanie': 'Lithuania',
    'Slovénie': 'Slovenia', 'SI': 'Slovenia', 'BE': 'Belgium', 'Belgique': 'Belgium', 'Portugal': 'Portugal', 'Vietnam': 'Vietnam',
    'Italie': 'Italy', 'Suède': 'Sweden', 'Allemagne': 'Germany', 'Chine': 'China', 'Estonie': 'Estonia', 'Espagne': 'Spain',
    'Pays-Bas': 'the Netherlands', 'Roumanie': 'Romania', 'Hongrie': 'Hungary', 'Serbie': 'Serbia', 'Turquie': 'Turkey',
    'Bulgarie': 'Bulgaria', 'Norvège': 'Norway', 'Finlande': 'Finland', 'Inde': 'India', 'Thaïlande': 'Thailand', 'Indonésie': 'Indonesia'
  };
  var WOOD = { 'chêne': 'oak', 'noyer': 'walnut', 'frêne': 'ash', 'hêtre': 'beech', 'orme': 'elm', 'érable': 'maple', 'teck': 'teak', 'cerisier': 'cherry', 'acajou': 'mahogany', 'bambou': 'bamboo' };
  var COLORMOD = { 'noir': 'black', 'blanc': 'white', 'clair': 'light', 'rouge': 'red', 'sauvage': 'wild', 'foncé': 'dark', 'gris': 'grey' };
  var OTHERMOD = { 'huilé': 'oiled', 'savonné': 'soaped', 'laqué': 'lacquered', 'fumé': 'smoked', 'teinté': 'stained', 'mat': 'matt', 'brut': 'raw', 'aubier': 'sapwood', 'vieilli': 'aged' };
  var METAL = { 'inox brossé': 'brushed stainless steel', 'acier brossé': 'brushed steel', 'aluminium brossé': 'brushed aluminium', 'chrome': 'chrome', 'noir': 'black', 'laqué noir': 'black lacquered', 'inox': 'stainless steel', 'acier': 'steel', 'laiton': 'brass', 'verre': 'glass', 'cuir': 'leather' };
  var MONTHS = { 'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April', 'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August', 'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December' };

  var FR_STOP = /(^|[^\p{L}])(le|la|les|de|du|des|un|une|et|ou|en|au|aux|pour|avec|sans|sur|par|dans|est|sont|ce|cette|ses|son|sa|vos|votre|nos|notre|chez|plus|très|qui|que)(?=$|[^\p{L}])/iu;
  function looksFrench(s) {
    return /[àâäçéèêëîïôöûùüœÀÂÇÉÈÊÎÔÛ]/.test(s) || FR_STOP.test(s);
  }
  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }

  function countries(list) {
    var out = [];
    var parts = list.split(/,\s*(?:en |au |aux |à )?/);
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i].replace(/^(en|au|aux)\s+/, '').trim();
      if (!p) continue;
      if (COUNTRY[p]) out.push(COUNTRY[p]); else return null;
    }
    return out.length ? out.join(', ') : null;
  }

  function madeIn(s) {
    var m, c, out = s;
    out = out.replace(/Fabriquée? sur mesure à ([A-Za-zÀ-ÿ-]+), Danemark, livrée? à plat/g, 'Made to measure in $1, Denmark, delivered flat-packed');
    out = out.replace(/Fabriquée? à la main à ([A-Za-zÀ-ÿ-]+), Danemark/g, 'Handmade in $1, Denmark');
    out = out.replace(/Fabriquée? à ([A-Za-zÀ-ÿ-]+), Danemark/g, 'Made in $1, Denmark');
    out = out.replace(/Fabriquée? en : ([^.\n]+)/g, function (all, l) { c = countries(l); return c ? 'Made in: ' + c : all; });
    out = out.replace(/Fabriquée? (?:en|au|aux) ([^.\n]+)/g, function (all, l) {
      c = countries(l.indexOf(',') < 0 ? l : l); return c ? 'Made in ' + c : all;
    });
    return out;
  }

  function finishItem(s) {
    s = s.trim();
    if (METAL[s]) return METAL[s];
    var toks = s.split(/\s+/), wi = -1, i;
    for (i = 0; i < toks.length; i++) if (WOOD[toks[i]]) { wi = i; break; }
    if (wi < 0) return null;
    var colors = [], rest = [];
    for (i = 0; i < toks.length; i++) {
      if (i === wi) continue;
      var t = toks[i];
      if (COLORMOD[t]) colors.push(COLORMOD[t]);
      else if (OTHERMOD[t]) rest.push(OTHERMOD[t]);
      else return null;
    }
    return colors.concat(rest).concat([WOOD[toks[wi]]]).join(' ');
  }

  function ruleDesigned(s) {
    var m = /^(.*?)(?:, dessinée? par (.+?))?\. Plusieurs finitions et revêtements disponibles ; documentation et conditions sur demande\.$/.exec(s);
    if (!m) return null;
    return m[1] + (m[2] ? ', designed by ' + m[2] : '') + '. Several finishes and upholstery options available; documentation and terms on request.';
  }

  function ruleMaterials(s) {
    var m = /^Matières et finitions : ([^;]+?)\.(?: (Revêtement (?:cuir ou tissu|tissu|cuir) au choix)\.)?(?: (Fabriquée? (?:en|au|aux) .+))?$/.exec(s);
    if (!m) return null;
    var items = m[1].split(', '), out = [];
    for (var i = 0; i < items.length; i++) {
      var f = finishItem(items[i]);
      if (!f) return null;
      out.push(f);
    }
    var res = 'Materials and finishes: ' + out.join(', ') + '.';
    if (m[2]) res += ' ' + ({ 'Revêtement cuir ou tissu au choix': 'Leather or fabric upholstery of your choice', 'Revêtement tissu au choix': 'Fabric upholstery of your choice', 'Revêtement cuir au choix': 'Leather upholstery of your choice' })[m[2]] + '.';
    if (m[3]) { var mi = madeIn(m[3]); if (looksFrench(mi)) return null; res += ' ' + mi; }
    return res;
  }

  var DIM_SUBST = [
    [/(\d),(\d)/g, '$1.$2'],
    [/Fabriquée? en : ([^\n]+)/g, function (a, l) { var c = countries(l); return c ? 'Made in: ' + c : a; }],
    [/Consommation \(modèle (\w+)\) : /g, 'Consumption (model $1): '],
    [/ : poids /g, ': weight '], [/poids /g, 'weight '], [/colis \(plusieurs unités\)/g, 'package (several units)'], [/colis /g, 'package '],
    [/\((\d+) pièces\)/g, '($1 pieces)'],
    [/\btissu /g, 'fabric '], [/\bcuir /g, 'leather '],
    [/(\d+(?:\.\d+)?) places?\b/g, '$1 seats'],
    [/ — Assise Papershell/g, ' — Papershell seat'], [/ — Assise garnie/g, ' — Upholstered seat'], [/ — Assise bois/g, ' — Wooden seat'],
    [/ — Entièrement garnie?/g, ' — Fully upholstered'], [/ — Piétement bois/g, ' — Wooden base'], [/ — Sans dossier/g, ' — Without backrest'],
    [/ — Extérieur/g, ' — Outdoor'], [/ — Tables gigognes/g, ' — Nesting tables'], [/ — Configuration /g, ' — Configuration '],
    [/ — Support de rangement/g, ' — Storage stand'],
    [/ — Piétement tube/g, ' — Tube base'], [/ — Pied pivotant (\d) branches/g, ' — Swivel $1-star base'], [/ — Tabouret, h\. /g, ' — Stool, H '],
    [/\bAssise\b/g, 'Seat'], [/\bassise\b/g, 'seat'], [/\bChaise\b/g, 'Chair'], [/\bFauteuil\b/g, 'Armchair'],
    [/\bTables? basses?\b/g, function (a) { return /s$/.test(a) ? 'Coffee tables' : 'Coffee table'; }],
    [/avec accoudoirs/g, 'with armrests'], [/\bsans\b/g, 'without'], [/\bavec\b/g, 'with'],
    [/\bHauteurs\b/g, 'Heights'], [/\bHauteur\b/g, 'Height'],
    [/\bOvale\b/g, 'Oval'], [/\bRonde\b/g, 'Round'], [/\bRectangulaire\b/g, 'Rectangular'],
    [/\bPlateaux de\b/g, 'Tops from'], [/\bjusqu'à\b/g, 'up to'],
    [/\bsur mesure\b/g, 'made to measure'], [/\bsur demande\b/g, 'on request'], [/\bautres longueurs\b/g, 'other lengths'],
    [/\bLargeurs de\b/g, 'Widths from'], [/\bCouchage\b/g, 'Sleeping surface'], [/\bCadre\b/g, 'Frame'], [/\bTête de lit\b/g, 'Headboard'], [/\bSol-cadre\b/g, 'Floor-to-frame'],
    [/(\d) ou (\d)/g, '$1 or $2'], [/ ou /g, ' or '], [/ et /g, ' and '], [/(\d) à (\d)/g, '$1 to $2'],
    [/\bP (\d)/g, 'D $1']
  ];
  function ruleDims(s) {
    if (!/\d/.test(s) || !/(cm|mm|kg|m²|m³|m\b)/.test(s)) return null;
    var out = s, i;
    var lowerL = /(^|[^A-Za-z])l \d/.test(s);
    for (i = 0; i < DIM_SUBST.length; i++) out = out.replace(DIM_SUBST[i][0], DIM_SUBST[i][1]);
    out = lowerL ? out.replace(/\bl (\d)/g, 'W $1') : out.replace(/\bL (\d)/g, 'W $1');
    return out;
  }

  function ruleDate(s) {
    var m = /^(\d{1,2})(?:er)? (janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre) (\d{4})$/.exec(s);
    return m ? m[1] + ' ' + MONTHS[m[2]] + ' ' + m[3] : null;
  }

  function Translator(dict) {
    var map = Object.create(null), k;
    for (k in dict) map[norm(k)] = dict[k];
    var cache = Object.create(null);
    function lookup(s) { return map[norm(s)]; }
    function tryRules(s) {
      var r, m;
      r = ruleDesigned(s); if (r) return r;
      r = ruleMaterials(s); if (r) return r;
      r = ruleDate(s); if (r) return r;
      m = /^Création : (.+)$/.exec(s); if (m) return 'Created: ' + m[1];
      if (/\(née? en \d{4}\)/.test(s)) { r = s.replace(/\(née? en (\d{4})\)/g, '(born $1)'); if (!looksFrench(r)) return r; }
      if (/— à fournir/.test(s)) { r = s.replace(/— à fournir/g, '— to be supplied'); if (!looksFrench(r)) return r; }
      m = /^(\d+)\s+(pièces?|produits?|résultats?|articles?|références?)$/.exec(s);
      if (m) { var base = { 'pièce': 'piece', 'produit': 'product', 'résultat': 'result', 'article': 'article', 'référence': 'reference' }[m[2].replace(/s$/, '')]; return m[1] + ' ' + base + (m[1] === '1' ? '' : 's'); }
      if (/Fabriquée?/.test(s)) { r = madeIn(s); if (r !== s && !looksFrench(r)) return r; }
      r = ruleDims(s); if (r && r !== s && !looksFrench(r)) return r;
      return null;
    }
    function tr(s) {
      var key = norm(s);
      if (!key) return null;
      if (cache[key] !== undefined) return cache[key];
      var out = lookup(key);
      if (out === undefined || out === null) out = tryRules(key);
      if ((out === undefined || out === null) && s.indexOf('\n') >= 0) {
        var lines = s.split('\n'), any = false, res = [];
        for (var i = 0; i < lines.length; i++) {
          var t = lines[i].trim() ? tr(lines[i]) : null;
          if (t !== null) any = true;
          res.push(t !== null ? t : lines[i]);
        }
        out = any ? res.join('\n') : null;
      }
      if ((out === undefined || out === null) && key.indexOf(' · ') >= 0) {
        var parts = key.split(' · '), any2 = false, res2 = [];
        for (var j = 0; j < parts.length; j++) {
          var t2 = tr(parts[j]);
          if (t2 !== null) any2 = true;
          res2.push(t2 !== null ? t2 : parts[j]);
        }
        out = any2 ? res2.join(' · ') : null;
      }
      if (out === undefined) out = null;
      cache[key] = out;
      return out;
    }
    return { tr: tr, looksFrench: looksFrench };
  }

  if (typeof module !== 'undefined' && module.exports) { module.exports = { Translator: Translator, looksFrench: looksFrench, norm: norm }; return; }
  if (typeof document === 'undefined') return;

  /* ---------- Intégration à la page ---------- */
  var KEY = 'sc-lang', ATTRS = ['alt', 'title', 'placeholder', 'aria-label'];
  var lang = 'fr', translator = null, observer = null, touched = new Set(), loading = false;

  function stored() { try { return localStorage.getItem(KEY) === 'en' ? 'en' : 'fr'; } catch (e) { return 'fr'; } }
  function store(l) { try { localStorage.setItem(KEY, l); } catch (e) { } }

  function skip(n) {
    for (var p = n.parentNode; p && p.nodeType === 1; p = p.parentNode) {
      var t = p.nodeName;
      if (t === 'SCRIPT' || t === 'STYLE' || t === 'TEXTAREA' || t === 'NOSCRIPT') return true;
      if (p.hasAttribute && p.hasAttribute('data-no-i18n')) return true;
    }
    return false;
  }
  function textNode(n) {
    var v = n.nodeValue;
    if (n._scEn !== undefined && v === n._scEn) return;
    if (!v || !v.trim() || skip(n)) return;
    var en = translator.tr(v);
    if (en === null) { n._scEn = undefined; return; }
    var lead = /^\s*/.exec(v)[0], trail = /\s*$/.exec(v)[0];
    en = lead + en + trail;
    n._scFr = v; n._scEn = en; n.nodeValue = en; touched.add(n);
  }
  function attrs(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i], v = el.getAttribute(a);
      if (!v) continue;
      var rec = el._scA && el._scA[a];
      if (rec && rec.en === v) continue;
      var en = translator.tr(v);
      if (en === null) continue;
      (el._scA = el._scA || {})[a] = { fr: v, en: en };
      el.setAttribute(a, en); touched.add(el);
    }
  }
  function walk(rootNode) {
    if (rootNode.nodeType === 3) { textNode(rootNode); return; }
    if (rootNode.nodeType !== 1) return;
    if (rootNode.nodeName === 'SCRIPT' || rootNode.nodeName === 'STYLE') return;
    attrs(rootNode);
    var tw = document.createTreeWalker(rootNode, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, null), n;
    while ((n = tw.nextNode())) { if (n.nodeType === 3) textNode(n); else if (n.nodeName !== 'SCRIPT' && n.nodeName !== 'STYLE') attrs(n); }
  }
  function onMutations(recs) {
    if (lang !== 'en' || !translator) return;
    for (var i = 0; i < recs.length; i++) {
      var r = recs[i];
      if (r.type === 'childList') { for (var j = 0; j < r.addedNodes.length; j++) walk(r.addedNodes[j]); }
      else if (r.type === 'characterData') textNode(r.target);
      else if (r.type === 'attributes') attrs(r.target);
    }
  }
  function startObserver() {
    if (observer) return;
    observer = new MutationObserver(onMutations);
    observer.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  }
  function restore() {
    touched.forEach(function (n) {
      if (n.nodeType === 3) { if (n._scFr !== undefined && n.nodeValue === n._scEn) n.nodeValue = n._scFr; n._scEn = undefined; }
      else if (n._scA) {
        for (var a in n._scA) if (n.getAttribute(a) === n._scA[a].en) n.setAttribute(a, n._scA[a].fr);
        n._scA = null;
      }
    });
    touched.clear();
  }
  function loadDict(cb) {
    if (root.SC_EN) return cb();
    if (loading) return;
    loading = true;
    var s = document.createElement('script');
    s.src = './i18n-en.js?v=' + (root.SC_I18N_V || '1');
    s.onload = function () { loading = false; cb(); };
    s.onerror = function () { loading = false; };
    document.head.appendChild(s);
  }
  function apply(l) {
    lang = l;
    document.documentElement.lang = l;
    if (l === 'en') {
      loadDict(function () {
        if (!translator) translator = Translator(root.SC_EN);
        if (lang !== 'en') return;
        startObserver();
        walk(document.body);
      });
    } else {
      restore();
    }
  }
  function setLang(l) { store(l); apply(l); }

  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-lang]') : null;
    if (!b) return;
    e.preventDefault();
    setLang(b.getAttribute('data-lang') === 'en' ? 'en' : 'fr');
  });

  root.scLang = { set: setLang, get: function () { return lang; } };
  lang = stored();
  document.documentElement.lang = lang;
  function boot() { if (lang === 'en') apply('en'); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})(typeof window !== 'undefined' ? window : globalThis);
