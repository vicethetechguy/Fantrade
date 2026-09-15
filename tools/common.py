# -*- coding: utf-8 -*-
"""Fantrade shared shell: design tokens, bespoke icon sprite, nav/footer."""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900'
         '&family=JetBrains+Mono:wght@300;400;500&family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">')

# ─────────────────────────────────────────────────────────────
# Bespoke icon set — 24 grid, 1.1 stroke, round joins.
# Drawn for football + exchange vernacular, not a generic library.
# ─────────────────────────────────────────────────────────────
from icons_data import ICONS as _ICONS

def sprite():
    parts = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">']
    for k, d in _ICONS.items():
        parts.append('<symbol id="i-%s" viewBox="0 0 256 256"><g fill="currentColor">%s</g></symbol>' % (k, d))
    parts.append('</svg>')
    return ''.join(parts)


def ic(name, cls="ic"):
    return '<svg class="%s" aria-hidden="true"><use href="#i-%s"/></svg>' % (cls, name)


# ─────────────────────────────────────────────────────────────
# QR — real, scannable, drawn from a pre-computed matrix so the
# generators keep working without a QR library installed.
# ─────────────────────────────────────────────────────────────
from qr_data import MATRIX as _QR, ADDRESS as QR_ADDRESS

FLAGS = {
    "eng": '<rect width="30" height="20" fill="#fff"/><rect x="12" width="6" height="20" fill="#CE1124"/>'
           '<rect y="7" width="30" height="6" fill="#CE1124"/>',
    "esp": '<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>',
    "ita": '<rect width="10" height="20" fill="#008C45"/><rect x="10" width="10" height="20" fill="#fff"/>'
           '<rect x="20" width="10" height="20" fill="#CD212A"/>',
    "ger": '<rect width="30" height="20" fill="#000"/><rect y="6.7" width="30" height="6.6" fill="#DD0000"/>'
           '<rect y="13.3" width="30" height="6.7" fill="#FFCE00"/>',
    "fra": '<rect width="10" height="20" fill="#002395"/><rect x="10" width="10" height="20" fill="#fff"/>'
           '<rect x="20" width="10" height="20" fill="#ED2939"/>',
    "eur": '<rect width="30" height="20" fill="#003399"/>'
           '<circle cx="15" cy="10" r="5" fill="none" stroke="#FFCC00" stroke-width="1.6" '
           'stroke-dasharray="1.4 1.7"/>',
}


def flag(code):
    return ('<span class="fl"><svg viewBox="0 0 30 20" aria-hidden="true">%s</svg></span>'
            % FLAGS.get(code, FLAGS["eur"]))


def qr_svg(quiet=2, label="Wallet receive address"):
    n = len(_QR)
    size = n + quiet * 2
    runs = []
    for y, row in enumerate(_QR):
        x = 0
        while x < n:
            if row[x] == "1":
                start = x
                while x < n and row[x] == "1":
                    x += 1
                runs.append("M%d %dh%dv1h-%dz" % (start + quiet, y + quiet, x - start, x - start))
            else:
                x += 1
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s" shape-rendering="crispEdges">'
            '<path d="%s" fill="#0A0B0C"/></svg>' % (size, size, label, "".join(runs)))


CSS = r"""
:root{
  --void:#050505;--shell:rgba(255,255,255,.035);--core:#0A0B0C;
  --hair:rgba(255,255,255,.08);--hair-2:rgba(255,255,255,.14);
  --lime:#C4F82A;--amber:#FF6A1F;--ink:#F4F6F1;--dim:#8B918A;--faint:#5A605B;--red:#FF5E5E;
  --r-out:2rem;--r-in:calc(2rem - .5rem);
  --inset:inset 0 1px 1px rgba(255,255,255,.12);
  --ambient:0 30px 80px -20px rgba(0,0,0,.8),0 0 0 1px rgba(255,255,255,.03);
  --ease:cubic-bezier(.32,.72,0,1);--ease-out:cubic-bezier(.16,1,.3,1);--maxw:1280px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;-webkit-tap-highlight-color:transparent}
body{margin:0;background:var(--void);color:var(--ink);
  font-family:Montserrat,system-ui,sans-serif;font-weight:400;font-size:15px;line-height:1.7;
  -webkit-font-smoothing:antialiased;overflow-x:hidden}
h1,h2,h3,h4,.disp{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 125,'wght' 800;
  text-transform:uppercase;line-height:.9;letter-spacing:-.015em;margin:0}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace;font-variant-numeric:tabular-nums}
a{color:inherit;text-decoration:none}
p{margin:0 0 1em}
button,input,select,textarea{font-family:Montserrat,system-ui,sans-serif}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 32px;position:relative}
:focus-visible{outline:1.5px solid var(--lime);outline-offset:4px;border-radius:4px}

/* icons */
.ic{width:20px;height:20px;display:block;color:inherit;flex:none;fill:currentColor}
.ic-lg{width:26px;height:26px;display:block;color:inherit;flex:none;fill:currentColor}
.ic-sm{width:15px;height:15px;display:block;color:inherit;flex:none;fill:currentColor}
.ic-xl{width:34px;height:34px;display:block;color:inherit;flex:none;fill:currentColor}
.ibox{width:40px;height:40px;border-radius:14px;background:rgba(255,255,255,.05);border:1px solid var(--hair);
  display:grid;place-items:center;box-shadow:var(--inset);color:var(--lime);flex:none}
.ibox.am{color:var(--amber);border-color:rgba(255,106,31,.24);background:rgba(255,106,31,.07)}
.ibox.sm{width:32px;height:32px;border-radius:11px}
.ibox.plain{color:var(--dim)}

/* atmosphere */
.orb{position:fixed;border-radius:50%;filter:blur(110px);pointer-events:none;z-index:0;opacity:.5}
.orb-a{width:780px;height:640px;top:-200px;left:50%;transform:translateX(-58%);background:radial-gradient(circle,rgba(196,248,42,.28),transparent 68%)}
.orb-b{width:620px;height:620px;top:48%;right:-240px;background:radial-gradient(circle,rgba(255,106,31,.18),transparent 68%)}
.orb-c{width:700px;height:560px;bottom:-280px;left:-200px;background:radial-gradient(circle,rgba(196,248,42,.14),transparent 70%)}
.grain{position:fixed;inset:0;z-index:90;pointer-events:none;opacity:.04;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E")}
main,header,footer,.nav-island{position:relative;z-index:1}

/* island nav */
.nav-island{position:fixed;top:22px;left:50%;transform:translateX(-50%);z-index:70;
  display:flex;align-items:center;gap:26px;width:max-content;max-width:calc(100vw - 32px);
  padding:8px 8px 8px 22px;border-radius:999px;background:rgba(10,11,12,.62);
  backdrop-filter:blur(22px) saturate(160%);-webkit-backdrop-filter:blur(22px) saturate(160%);
  border:1px solid var(--hair);box-shadow:var(--inset),0 20px 50px -20px rgba(0,0,0,.9)}
.logo{display:flex;align-items:center;gap:10px;font-family:Archivo;font-variation-settings:'wdth' 125,'wght' 900;
  text-transform:uppercase;font-size:16px;white-space:nowrap}
.logo .ic{color:var(--lime);width:22px;height:22px}
.nav-links{display:flex;gap:24px;font-size:13px;color:var(--dim)}
.nav-links a{position:relative;padding:4px 0;transition:color .5s var(--ease)}
.nav-links a::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--lime);
  transform:scaleX(0);transform-origin:left;transition:transform .7s var(--ease)}
.nav-links a:hover,.nav-links a.on{color:var(--ink)}
.nav-links a.on::after,.nav-links a:hover::after{transform:scaleX(1)}

/* buttons */
.btn{position:relative;display:inline-flex;align-items:center;gap:14px;cursor:pointer;border:0;
  padding:9px 9px 9px 24px;border-radius:999px;font-family:Archivo;font-variation-settings:'wdth' 112,'wght' 700;
  text-transform:uppercase;font-size:12px;letter-spacing:.07em;white-space:nowrap;
  transition:transform .6s var(--ease),background .6s var(--ease),border-color .6s var(--ease),color .6s var(--ease)}
.btn .cap{width:30px;height:30px;flex:none;border-radius:999px;display:grid;place-items:center;
  transition:transform .7s var(--ease),background .6s var(--ease)}
.btn .cap .ic{width:13px;height:13px}
.btn:hover .cap{transform:translate(3px,-2px) scale(1.06)}
.btn:active{transform:scale(.975)}
.btn-lime{background:var(--lime);color:#0A0D03;box-shadow:var(--inset),0 14px 34px -14px rgba(196,248,42,.75)}
.btn-lime .cap{background:rgba(10,13,3,.14)}
.btn-lime:hover{background:#d3ff4a}
.btn-glass{background:rgba(255,255,255,.05);color:var(--ink);border:1px solid var(--hair);box-shadow:var(--inset)}
.btn-glass .cap{background:rgba(255,255,255,.08)}
.btn-glass:hover{background:rgba(255,255,255,.09);border-color:var(--hair-2)}
.btn-sm{padding:7px 7px 7px 18px;font-size:11px}
.btn-sm .cap{width:26px;height:26px}
.btn-red{background:rgba(255,94,94,.14);color:#ffb3b3;border:1px solid rgba(255,94,94,.3)}
.btn-red .cap{background:rgba(255,94,94,.16)}

/* burger + overlay */
.burger{display:none;width:44px;height:44px;border-radius:999px;background:rgba(255,255,255,.06);
  border:1px solid var(--hair);cursor:pointer;position:relative;flex:none}
.burger i{position:absolute;left:13px;width:18px;height:1.4px;background:var(--ink);border-radius:2px;
  transition:transform .7s var(--ease)}
.burger i:nth-child(1){top:17px}.burger i:nth-child(2){top:25px}
body.menu-open .burger i:nth-child(1){transform:translateY(4px) rotate(45deg)}
body.menu-open .burger i:nth-child(2){transform:translateY(-4px) rotate(-45deg)}
.overlay{position:fixed;inset:0;z-index:65;background:rgba(5,5,5,.86);backdrop-filter:blur(34px) saturate(140%);
  -webkit-backdrop-filter:blur(34px) saturate(140%);display:flex;flex-direction:column;justify-content:center;
  padding:0 32px;gap:6px;opacity:0;pointer-events:none;visibility:hidden;
  transition:opacity .7s var(--ease),visibility 0s linear .7s}
body.menu-open .overlay{opacity:1;pointer-events:auto;visibility:visible;transition-delay:0s}
.overlay a{font-family:Archivo;font-variation-settings:'wdth' 125,'wght' 800;text-transform:uppercase;
  font-size:clamp(30px,9vw,54px);line-height:1.15;opacity:0;transform:translateY(48px);
  transition:opacity .8s var(--ease),transform .8s var(--ease)}
body.menu-open .overlay a{opacity:1;transform:translateY(0)}
body.menu-open .overlay a:nth-child(1){transition-delay:.10s}
body.menu-open .overlay a:nth-child(2){transition-delay:.16s}
body.menu-open .overlay a:nth-child(3){transition-delay:.22s}
body.menu-open .overlay a:nth-child(4){transition-delay:.28s}
.overlay .btn{align-self:flex-start;margin-top:34px}

/* bezel */
.bezel{background:var(--shell);border:1px solid var(--hair);border-radius:var(--r-out);padding:8px;box-shadow:var(--ambient)}
.bezel>.core{background:var(--core);border-radius:var(--r-in);box-shadow:var(--inset);overflow:hidden;height:100%}
.bezel.tight{padding:6px;--r-out:1.5rem;--r-in:calc(1.5rem - .375rem)}
.pad{padding:36px 34px}.pad-sm{padding:26px 26px}

/* type */
.pill{display:inline-flex;align-items:center;gap:9px;border-radius:999px;padding:6px 15px;
  background:rgba(196,248,42,.08);border:1px solid rgba(196,248,42,.22);
  font-weight:600;font-size:10px;letter-spacing:.2em;color:var(--lime);text-transform:uppercase}
.pill .ic{width:13px;height:13px}
.pill.amber{background:rgba(255,106,31,.08);border-color:rgba(255,106,31,.24);color:var(--amber)}
h2{font-size:clamp(32px,5.4vw,64px)}
.lede{color:var(--dim);font-size:16px;font-weight:300;max-width:56ch;margin-top:22px}
section{padding:130px 0}
.sec-head{margin-bottom:60px;max-width:760px}
.sec-head h2{margin-top:24px}
.sec-head.center{margin-left:auto;margin-right:auto;text-align:center}
.sec-head.center .lede{margin-left:auto;margin-right:auto}
.k-label{font-weight:600;font-size:9.5px;letter-spacing:.18em;color:var(--faint);margin-bottom:14px;text-transform:uppercase}
.num{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}

/* reveal */
[data-reveal]{opacity:0;transform:translateY(60px);filter:blur(10px);
  transition:opacity .9s var(--ease-out),transform .9s var(--ease-out),filter .9s var(--ease-out)}
[data-reveal].in{opacity:1;transform:translateY(0);filter:blur(0)}

/* page header */
.phead{padding:190px 0 70px}
.phead h1{font-size:clamp(40px,7vw,86px);font-variation-settings:'wdth' 125,'wght' 900;margin-top:26px}
.phead .lede{margin-top:26px}
.statbar{display:flex;gap:10px;flex-wrap:wrap;margin-top:40px}
.statbar div{border:1px solid var(--hair);border-radius:999px;padding:10px 20px;background:rgba(255,255,255,.025);
  font-size:12px;color:var(--dim);box-shadow:var(--inset);display:flex;align-items:center;gap:10px}
.statbar b{font-family:'JetBrains Mono',monospace;font-weight:400;color:var(--ink)}
.statbar .ic{width:14px;height:14px;color:var(--lime)}

/* bento */
.bento{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}
.c3{grid-column:span 3}.c4{grid-column:span 4}.c5{grid-column:span 5}.c6{grid-column:span 6}
.c7{grid-column:span 7}.c8{grid-column:span 8}.c9{grid-column:span 9}.c12{grid-column:span 12}

/* market table */
.mtable{width:100%}
.mhead,.mrow{display:grid;grid-template-columns:2fr 1fr .8fr 1.1fr 1fr 96px;gap:14px;align-items:center;padding:14px 24px}
.mhead{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);border-bottom:1px solid var(--hair);text-transform:uppercase}
.mrow{border-bottom:1px solid rgba(255,255,255,.045);transition:background .6s var(--ease)}
.mrow:hover{background:rgba(255,255,255,.025)}
.mrow.sel{background:rgba(196,248,42,.05)}
.asset{display:flex;align-items:center;gap:13px;min-width:0}
.badge{width:34px;height:34px;border-radius:11px;background:rgba(255,255,255,.05);border:1px solid var(--hair);
  display:grid;place-items:center;flex:none;box-shadow:var(--inset);color:var(--dim)}
.badge .ic{width:17px;height:17px}
.badge.coach{border-color:rgba(255,106,31,.32);background:rgba(255,106,31,.08);color:var(--amber)}
.t-sym{font-family:'JetBrains Mono',monospace;font-size:13.5px}
.t-nm{font-size:11px;color:var(--faint);font-weight:500;letter-spacing:.03em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tick{font-family:'JetBrains Mono',monospace;font-size:13px;transition:color .8s var(--ease)}
.up{color:var(--lime)}.down{color:var(--red)}
.spark{height:26px;width:100%;display:block}
.tradebtn{border:1px solid var(--hair);background:rgba(255,255,255,.04);color:var(--ink);border-radius:999px;
  padding:8px 0;width:100%;font-weight:600;font-size:10.5px;letter-spacing:.12em;cursor:pointer;text-transform:uppercase;
  box-shadow:var(--inset);transition:all .6s var(--ease)}
.tradebtn:hover{background:var(--lime);border-color:var(--lime);color:#0A0D03}

/* filter rail */
.rail{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:20px}
.seg{display:flex;gap:4px;padding:5px;border-radius:999px;background:rgba(255,255,255,.035);border:1px solid var(--hair);box-shadow:var(--inset)}
.seg button{border:0;background:transparent;color:var(--dim);border-radius:999px;padding:9px 18px;cursor:pointer;
  font-weight:600;font-size:11px;letter-spacing:.08em;text-transform:uppercase;transition:all .6s var(--ease);display:flex;align-items:center;gap:8px}
.seg button .ic{width:14px;height:14px}
.seg button[aria-pressed="true"]{background:var(--lime);color:#0A0D03;box-shadow:var(--inset)}
.seg button:hover:not([aria-pressed="true"]){color:var(--ink)}
.searchbox{display:flex;align-items:center;gap:10px;border:1px solid var(--hair);border-radius:999px;padding:10px 18px;
  background:rgba(255,255,255,.035);box-shadow:var(--inset);color:var(--faint);flex:1;min-width:200px}
.searchbox input{border:0;background:transparent;color:var(--ink);outline:none;font-size:13px;width:100%}
.searchbox input::placeholder{color:var(--faint)}

/* ticket / forms */
.field{display:flex;align-items:center;justify-content:space-between;gap:12px;border:1px solid var(--hair);
  border-radius:16px;padding:14px 18px;background:rgba(255,255,255,.03);box-shadow:var(--inset);margin-bottom:10px}
.field label{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
.field input{border:0;background:transparent;color:var(--ink);text-align:right;outline:none;width:60%;
  font-family:'JetBrains Mono',monospace;font-size:17px;font-variant-numeric:tabular-nums}
.quick{display:flex;gap:8px;margin:12px 0 20px;flex-wrap:wrap}
.quick button{flex:1;border:1px solid var(--hair);background:rgba(255,255,255,.03);color:var(--dim);border-radius:999px;
  padding:9px 0;font-family:'JetBrains Mono',monospace;font-size:11px;cursor:pointer;transition:all .6s var(--ease);min-width:62px}
.quick button:hover{color:var(--ink);border-color:var(--hair-2)}
.line{display:flex;justify-content:space-between;padding:11px 0;font-size:12.5px;color:var(--dim);border-bottom:1px solid rgba(255,255,255,.05)}
.line b{font-family:'JetBrains Mono',monospace;font-weight:400;color:var(--ink)}
.supply{height:5px;border-radius:99px;background:rgba(255,255,255,.07);margin:16px 0 6px;overflow:hidden}
.supply i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#8fbe00,var(--lime));box-shadow:0 0 16px rgba(196,248,42,.5)}

/* pitch */
.pitch{position:relative;padding:32px 26px;height:100%;
  background:radial-gradient(ellipse at 50% 0%,rgba(196,248,42,.07),transparent 62%),
  repeating-linear-gradient(180deg,rgba(255,255,255,.014) 0 62px,transparent 62px 124px)}
.pitch::before{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;background:rgba(255,255,255,.05)}
.pitch-head{display:flex;align-items:center;gap:14px;margin-bottom:28px;position:relative;z-index:2}
.crest{width:46px;height:50px;flex:none;background:linear-gradient(160deg,var(--lime),#83b300);
  clip-path:polygon(0 0,100% 0,100% 66%,50% 100%,0 66%);display:grid;place-items:center;
  font-family:Archivo;font-variation-settings:'wdth' 100,'wght' 900;font-size:13px;color:#0A0D03;
  filter:drop-shadow(0 8px 18px rgba(196,248,42,.35))}
.pitch-head .name{font-family:Archivo;font-variation-settings:'wdth' 125,'wght' 900;text-transform:uppercase;font-size:24px;line-height:1}
.pitch-head .meta{font-weight:600;font-size:9.5px;color:var(--faint);letter-spacing:.14em;margin-top:7px;text-transform:uppercase}
.pitch-head .coach{margin-left:auto;text-align:right;display:flex;align-items:center;gap:10px}
.pitch-head .coach b{display:block;font-family:'JetBrains Mono',monospace;color:var(--amber);font-size:13px;font-weight:400}
.pitch-head .coach span{font-size:9px;color:var(--faint);letter-spacing:.16em;font-weight:600}
.line-row{display:flex;justify-content:center;gap:10px;margin-bottom:12px;position:relative;z-index:2;flex-wrap:wrap}
.chip{border:1px solid var(--hair);background:rgba(255,255,255,.035);border-radius:12px;padding:9px 12px;
  min-width:102px;text-align:center;box-shadow:var(--inset);transition:transform .7s var(--ease),border-color .7s var(--ease)}
.chip:hover{transform:translateY(-3px);border-color:var(--hair-2)}
.chip .pos{font-weight:600;font-size:8.5px;color:var(--faint);letter-spacing:.16em}
.chip .nm{font-family:'JetBrains Mono',monospace;font-size:12.5px;margin-top:4px}
.chip.cap{border-color:rgba(196,248,42,.45);background:rgba(196,248,42,.07)}
.chip.cap .nm{color:var(--lime)}
.chip .arm{display:flex;align-items:center;justify-content:center;gap:4px;font-weight:600;font-size:8px;
  color:var(--lime);letter-spacing:.1em;margin-top:4px}
.chip .arm .ic{width:10px;height:10px}
.bench{margin-top:26px;padding-top:22px;border-top:1px solid rgba(255,255,255,.07);position:relative;z-index:2}
.bench-row{display:flex;gap:8px;flex-wrap:wrap}
.chip.sm{min-width:90px;padding:7px 10px}
.chip.empty{border-style:dashed;border-color:rgba(255,255,255,.2);color:var(--dim);cursor:pointer;background:transparent;box-shadow:none}
.chip.empty:hover{border-color:rgba(255,94,94,.6);color:var(--red)}
.own-alert{margin-top:0;border:1px solid transparent;background:rgba(255,94,94,.06);border-radius:16px;
  display:flex;gap:18px;align-items:center;position:relative;z-index:2;opacity:0;max-height:0;overflow:hidden;
  padding:0 20px;transition:all .7s var(--ease)}
.own-alert.show{opacity:1;max-height:240px;padding:18px 20px;margin-top:16px;border-color:rgba(255,94,94,.3)}
.own-alert p{margin:0;font-size:13px}
.own-alert strong{font-family:'JetBrains Mono',monospace;color:#ff9a9a;font-weight:400}
.own-alert .btn{margin-left:auto;flex:none}

/* stat minis */
.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.mini{background:rgba(255,255,255,.03);border:1px solid var(--hair);border-radius:16px;padding:20px;box-shadow:var(--inset)}
.mini .k{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
.mini .v{font-family:'JetBrains Mono',monospace;font-weight:300;font-size:26px;margin-top:8px;letter-spacing:-.02em}
.mini .v.lime{color:var(--lime)}.mini .v.amber{color:var(--amber)}
.value-big{font-family:'JetBrains Mono',monospace;font-weight:300;font-size:clamp(34px,3.6vw,46px);
  letter-spacing:-.035em;margin:12px 0 4px;line-height:1}
.value-big small{font-size:15px;color:var(--faint);letter-spacing:0}
.delta{font-weight:500;font-size:11.5px;color:var(--lime)}
.b-row{display:flex;justify-content:space-between;padding:9px 0;font-size:12.5px;color:var(--dim)}
.b-row b{color:var(--ink);font-weight:400;font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}
.b-row.total{border-top:1px solid var(--hair);margin-top:8px;padding-top:14px;color:var(--ink)}

/* tabs / markets */
.tabs{display:flex;gap:8px;padding:8px;border-bottom:1px solid var(--hair);background:rgba(255,255,255,.02)}
.tab{flex:1;padding:20px 22px;border-radius:18px;background:transparent;border:1px solid transparent;color:var(--dim);
  cursor:pointer;text-align:left;display:flex;align-items:center;gap:14px;
  transition:background .7s var(--ease),color .7s var(--ease),border-color .7s var(--ease),box-shadow .7s var(--ease)}
.tab b{display:block;font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 800;text-transform:uppercase;
  font-size:16px;color:inherit;letter-spacing:.02em;margin-bottom:3px}
.tab span{font-size:12.5px;font-weight:300}
.tab .ibox{background:rgba(255,255,255,.05);color:inherit}
.tab[aria-selected="true"]{background:var(--lime);color:#20290A;border-color:var(--lime);box-shadow:var(--inset),0 16px 40px -18px rgba(196,248,42,.8)}
.tab[aria-selected="true"] span{color:rgba(20,26,3,.72)}
.tab[aria-selected="true"] .ibox{background:rgba(10,13,3,.12);border-color:rgba(10,13,3,.18);color:#20290A}
.tab:hover:not([aria-selected="true"]){background:rgba(255,255,255,.04);color:var(--ink)}
.markets{display:flex;flex-wrap:wrap;gap:8px}
.mkt{border:1px solid var(--hair);background:rgba(255,255,255,.03);color:var(--dim);border-radius:999px;
  padding:10px 18px;cursor:pointer;font-weight:600;font-size:11px;letter-spacing:.06em;text-transform:uppercase;
  box-shadow:var(--inset);transition:all .6s var(--ease)}
.mkt:hover{color:var(--ink);border-color:var(--hair-2);transform:translateY(-2px)}
.mkt[aria-pressed="true"]{background:var(--lime);border-color:var(--lime);color:#0A0D03;box-shadow:var(--inset),0 12px 30px -14px rgba(196,248,42,.9)}
.out{margin-top:24px;padding:32px 24px;border-radius:22px;text-align:center;border:1px solid rgba(196,248,42,.28);
  background:radial-gradient(ellipse at 50% 120%,rgba(196,248,42,.18),rgba(196,248,42,.04) 60%);box-shadow:var(--inset)}
.out .k{font-weight:600;font-size:9.5px;letter-spacing:.2em;color:#95ad44;text-transform:uppercase}
.out .v{font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 900;font-size:clamp(44px,5vw,62px);
  color:var(--lime);line-height:1;margin-top:12px;text-shadow:0 0 50px rgba(196,248,42,.4)}
.out .n{font-weight:600;font-size:10px;color:#8d9f4d;margin-top:12px;letter-spacing:.12em;text-transform:uppercase}

/* feature card */
.f h4{font-size:19px;font-variation-settings:'wdth' 118,'wght' 800;margin:18px 0 10px}
.f p{font-size:13.5px;font-weight:300;color:var(--dim);margin:0;line-height:1.6}

/* footer */
footer{border-top:1px solid var(--hair);padding:70px 0 64px;background:rgba(255,255,255,.015)}
.foot{display:flex;gap:56px;flex-wrap:wrap;align-items:flex-start}
.foot .col{min-width:132px}
.foot .col b{font-weight:600;font-size:9.5px;letter-spacing:.18em;color:var(--faint);display:block;margin-bottom:16px;text-transform:uppercase}
.foot .col a{display:block;font-size:13px;color:var(--dim);padding:6px 0;transition:color .5s var(--ease)}
.foot .col a:hover{color:var(--lime)}
.brandcol{margin-right:auto;max-width:300px}
.brandcol p{font-size:12.5px;font-weight:300;color:var(--dim);margin-top:18px}
.legal{margin-top:52px;padding-top:26px;border-top:1px solid var(--hair);font-size:11.5px;color:var(--faint);
  display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}

/* toasts */
.ft-toast-container{position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;pointer-events:none;max-width:calc(100vw - 32px)}
.ft-toast{pointer-events:auto;display:flex;align-items:center;gap:12px;padding:14px 20px;border-radius:14px;background:rgba(10,13,14,.94);backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);border:1px solid var(--hair);box-shadow:var(--inset),0 20px 40px -10px rgba(0,0,0,.85);font-size:13.5px;color:var(--ink);transform:translateY(20px);opacity:0;transition:all .35s cubic-bezier(.16,1,.3,1)}
.ft-toast.show{transform:translateY(0);opacity:1}
.ft-toast.success{border-color:rgba(196,248,42,.45)}
.ft-toast.success .t-icon{color:var(--lime)}
.ft-toast.error{border-color:rgba(255,94,94,.45)}
.ft-toast.error .t-icon{color:var(--red)}
.ft-toast.info{border-color:rgba(255,255,255,.25)}
.ft-toast.info .t-icon{color:var(--ink)}
.ft-toast .t-icon{width:18px;height:18px;flex:none}

/* modal */
.ft-modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.78);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);z-index:9990;display:flex;align-items:center;justify-content:center;padding:20px;opacity:0;pointer-events:none;transition:opacity .25s ease}
.ft-modal-backdrop.open{opacity:1;pointer-events:auto}
.ft-modal-box{background:var(--core);border:1px solid var(--hair);border-radius:24px;box-shadow:var(--ambient),var(--inset);max-width:540px;width:100%;max-height:90vh;overflow-y:auto;padding:32px;position:relative;transform:scale(.95);transition:transform .25s cubic-bezier(.16,1,.3,1)}
.ft-modal-backdrop.open .ft-modal-box{transform:scale(1)}
.ft-modal-close{position:absolute;top:18px;right:20px;background:rgba(255,255,255,.05);border:1px solid var(--hair);color:var(--dim);border-radius:50%;width:32px;height:32px;display:grid;place-items:center;font-size:18px;cursor:pointer;transition:all .2s ease}
.ft-modal-close:hover{background:rgba(255,255,255,.1);color:var(--ink)}
.ft-modal-title{font-family:Archivo,sans-serif;font-variation-settings:'wdth' 120,'wght' 800;text-transform:uppercase;font-size:22px;margin:0 0 8px}
.ft-modal-desc{color:var(--dim);font-size:13.5px;font-weight:300;margin:0 0 20px;line-height:1.5}
.ft-modal-card{border:1px solid var(--hair);border-radius:16px;padding:18px;background:rgba(255,255,255,.03);box-shadow:var(--inset);margin-bottom:16px}
.ft-modal-card .m-row{display:flex;justify-content:space-between;padding:8px 0;font-size:13px;color:var(--dim)}
.ft-modal-card .m-row b{color:var(--ink);font-family:'JetBrains Mono',monospace;font-weight:400}
.ft-modal-card .m-row.total{border-top:1px solid var(--hair);margin-top:6px;padding-top:10px;font-size:14px;color:var(--ink)}
.ft-modal-card .m-row.total b{color:var(--lime);font-weight:600}

/* nav wallet badge */
.nav-wallet{display:inline-flex;align-items:center;gap:8px;padding:6px 14px;border-radius:999px;background:rgba(255,255,255,.04);border:1px solid var(--hair);box-shadow:var(--inset);cursor:pointer;transition:all .3s ease;white-space:nowrap}
.nav-wallet:hover{background:rgba(255,255,255,.08);border-color:var(--hair-2)}
.nav-wallet .num{font-size:12px;color:var(--lime);font-weight:500}

/* responsive */
@media (max-width:1024px){
  .nav-links{display:none}.nav-island>.btn{display:none}.burger{display:block}
  .nav-island{width:calc(100vw - 32px);justify-content:space-between;padding:8px 8px 8px 20px}
  .c3,.c4,.c5,.c6,.c7,.c8,.c9{grid-column:span 12}
  .bento.halves .c6{grid-column:span 6}
  .mhead,.mrow{grid-template-columns:2fr 1fr .8fr 1fr 96px}
  .mhead span:nth-child(5),.mrow>div:nth-child(5){display:none}
}
@media (max-width:900px){
  .bento{gap:12px}.sec-head{margin-bottom:40px}.lede{font-size:15px}.pad{padding:30px 26px}
}
@media (max-width:768px){
  html,body{overflow-x:hidden!important;width:100%;max-width:100vw;-webkit-text-size-adjust:100%}
  input,select,textarea{font-size:16px!important} /* Prevents iOS auto-zoom */
  .wrap{padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right));max-width:100vw;box-sizing:border-box}
  .nav-island{top:max(10px,env(safe-area-inset-top));left:10px;right:10px;transform:none;width:auto;max-width:calc(100vw - 20px)!important;box-sizing:border-box;padding:6px 8px 6px 14px}
  .nav-island #navAccountBtn{display:none!important}
  .nav-wallet{padding:5px 11px;font-size:11.5px;gap:6px}
  .nav-wallet .pulse{width:5px;height:5px}
  .logo{font-size:14px;flex-shrink:0;gap:8px}
  .logo .ic{width:19px;height:19px}
  .burger{width:38px;height:38px}
  .burger i{left:10px;width:16px}
  .burger i:nth-child(1){top:15px}.burger i:nth-child(2){top:22px}
  body.menu-open .burger i:nth-child(1){transform:translateY(3.5px) rotate(45deg)}
  body.menu-open .burger i:nth-child(2){transform:translateY(-3.5px) rotate(-45deg)}
  body.menu-open{overflow:hidden}
  .overlay{padding:calc(82px + env(safe-area-inset-top)) 20px calc(36px + env(safe-area-inset-bottom));overflow-y:auto;overflow-x:hidden;justify-content:flex-start;max-width:100vw}
  .overlay a{font-size:clamp(22px,7.5vw,34px)!important;font-variation-settings:'wdth' 105,'wght' 800!important;overflow-wrap:break-word;word-break:break-word;white-space:normal;line-height:1.25;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05)}
  .overlay .btn{margin-top:24px;width:100%;justify-content:space-between}

  /* Modals on mobile */
  .ft-modal-backdrop{padding:12px;box-sizing:border-box}
  .ft-modal-box{padding:22px 16px;border-radius:20px;max-height:92vh;width:100%;box-sizing:border-box}
  .ft-modal-close{top:12px;right:12px;width:30px;height:30px;font-size:16px}
  .ft-modal-title{font-size:19px;margin-bottom:6px}
  .ft-modal-desc{font-size:12.5px;margin-bottom:16px}
  .ft-modal-card{padding:14px 12px;border-radius:14px;margin-bottom:12px}
  .ft-modal-card .m-row{padding:6px 0;font-size:12.5px}
  .ft-modal-box .btn{min-height:44px;font-size:11.5px}

  /* Toasts on mobile */
  .ft-toast-container{bottom:max(16px,env(safe-area-inset-bottom));left:12px;right:12px;max-width:100%;width:auto}
  .ft-toast{width:100%;box-sizing:border-box;padding:12px 14px;font-size:12.5px;border-radius:12px}

  /* Page Sections & Typography */
  section{padding:80px 0}
  .hero{padding:116px 0 0}
  .hero h1{font-size:clamp(26px,8.5vw,42px)!important;font-variation-settings:'wdth' 105,'wght' 800!important;letter-spacing:-.02em!important;overflow-wrap:break-word;word-break:break-word;margin-top:20px}
  .hero .lede{font-size:14.5px;margin-top:16px}
  .phead{padding:112px 0 40px}
  .phead h1{font-size:clamp(26px,8.5vw,42px)!important;font-variation-settings:'wdth' 105,'wght' 800!important;overflow-wrap:break-word;word-break:break-word;margin-top:18px}
  .phead .lede{font-size:14.5px;margin-top:16px}
  h2{font-size:clamp(23px,7vw,34px)!important;font-variation-settings:'wdth' 105,'wght' 800!important}
  .cta-sec h2{font-size:clamp(25px,7.8vw,38px)!important;font-variation-settings:'wdth' 105,'wght' 800!important}
  /* Bento grids on mobile: strictly flex column to prevent ANY overlapping or implicit grid bugs */
  .bento, .bento.halves{display:flex!important;flex-direction:column!important;gap:16px!important;width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
  .bento > *, .bento.halves > *,
  .c3, .c4, .c5, .c6, .c7, .c8, .c9, .c12{grid-column:auto!important;width:100%!important;max-width:100%!important;min-width:0!important;flex:0 0 auto!important;box-sizing:border-box!important}
  .bezel{padding:6px;--r-out:1.4rem;--r-in:calc(1.4rem - .375rem);width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
  .bezel>.core{width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
  .pad{padding:24px 18px}.pad-sm{padding:18px 14px}
  .btn{min-height:46px;padding:11px 18px;max-width:100%;box-sizing:border-box!important}

  /* Forms & controls */
  .field{padding:12px 14px;border-radius:14px;margin-bottom:8px;box-sizing:border-box!important;width:100%!important}
  .field label{font-size:9px}
  .field input{font-size:16px!important;width:65%}
  .quick{gap:6px;margin:10px 0 16px;width:100%!important;box-sizing:border-box!important}
  .quick button{min-width:52px;padding:8px 0;font-size:10.5px}

  /* Market Table on Exchange */
  .rail .searchbox{width:100%;flex:1 1 100%;min-width:100%;order:-1;padding:8px 14px;box-sizing:border-box!important}
  .rail .seg{width:100%;justify-content:space-between;padding:4px;box-sizing:border-box!important}
  .rail .seg button{flex:1;justify-content:center;padding:8px 10px;font-size:10px}
  .mhead,.mrow{grid-template-columns:1.5fr 1fr 68px;gap:8px;padding:12px 14px;box-sizing:border-box!important}
  .mhead span:nth-child(3),.mhead span:nth-child(4),.mhead span:nth-child(5){display:none}
  .mrow>div:nth-child(3),.mrow>div:nth-child(4),.mrow>div:nth-child(5){display:none}
  .mhead span:nth-child(6),.mrow>div:nth-child(6){display:block}
  .tradebtn{padding:6px 0;font-size:9.5px;width:100%;border-radius:999px}
  .brow{grid-template-columns:1.5fr 1fr .8fr;padding:12px 14px;box-sizing:border-box!important}
  .bhead span:last-child,.brow>div:last-child{display:none}

  /* Pitch & Squad Builder */
  .pitch{padding:20px 10px;box-sizing:border-box!important}
  .pitch-head{flex-wrap:wrap;gap:10px;margin-bottom:20px}
  .pitch-head .name{font-size:18px}
  .pitch-head .coach{margin-left:0;width:100%;border-top:1px solid rgba(255,255,255,.07);padding-top:10px}
  .line-row{gap:5px;margin-bottom:7px;width:100%!important;box-sizing:border-box!important}
  .chip{min-width:0;flex:1 1 66px;max-width:82px;padding:7px 3px;border-radius:10px;box-sizing:border-box!important}
  .chip:hover{transform:none}
  .chip .pos{font-size:7.5px;letter-spacing:.06em}
  .chip .nm{font-size:10px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .chip.cap .arm{font-size:7px;gap:2px}
  .chip.cap .arm .ic{width:8px;height:8px}
  .bench{margin-top:18px;padding-top:14px;width:100%!important;box-sizing:border-box!important}
  .bench-row{display:flex;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding:4px 0 8px 0!important;margin:0!important;width:100%!important;box-sizing:border-box!important;gap:8px}
  .bench-row::-webkit-scrollbar{display:none}
  .chip.sm{flex:0 0 auto;min-width:80px;padding:6px 8px}
  .stepper{display:flex;flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:0 0 6px 0!important;margin:0 0 16px 0!important;width:100%!important;box-sizing:border-box!important;gap:6px}
  .stepper::-webkit-scrollbar{display:none}
  .stepper button{flex:0 0 auto;padding:8px 12px;font-size:9.5px}
  .forms{gap:6px;width:100%!important;box-sizing:border-box!important}
  .forms button{min-width:68px;padding:11px 0;font-size:13px;border-radius:12px}
  .swatches{gap:10px;width:100%!important;box-sizing:border-box!important}
  .sw{width:36px;height:36px;border-radius:10px}

  /* FanPlay components */
  .tabs{flex-direction:row;gap:6px;padding:6px;border-radius:16px;box-sizing:border-box!important;width:100%!important}
  .tab{flex:1;padding:10px 8px;min-height:48px;border-radius:12px;gap:8px;justify-content:center;box-sizing:border-box!important}
  .tab b{font-size:12px;margin-bottom:0}
  .tab span{display:none}
  .tab .ibox{width:26px;height:26px;border-radius:8px}
  .fp-sel{padding:14px;border-radius:16px;margin-bottom:18px;box-sizing:border-box!important;width:100%!important}
  .fp-sel .nm{font-size:16px}
  .fp-sel .sub{font-size:8.5px}
  .markets{display:flex;flex-wrap:nowrap;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 0 10px 0!important;
    margin:0!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;scrollbar-width:none;-webkit-overflow-scrolling:touch;gap:8px}
  .markets::-webkit-scrollbar{display:none}
  .mkt{flex:0 0 auto;scroll-snap-align:start;min-height:40px;padding:8px 14px;font-size:10.5px}
  .mkt:hover{transform:none}
  .calc{width:100%!important;box-sizing:border-box!important}
  .calc .cr,.b-row{display:flex!important;justify-content:space-between!important;align-items:center!important;gap:10px!important;width:100%!important;box-sizing:border-box!important}
  .calc .cr span,.b-row span{min-width:0!important;flex:1 1 auto!important;overflow:hidden!important;text-overflow:ellipsis!important}
  .calc .cr b,.b-row b{flex:0 0 auto!important;text-align:right!important;white-space:nowrap!important}
  .out{padding:20px 14px;border-radius:16px;margin-top:16px;width:100%!important;box-sizing:border-box!important}
  .out .v{font-size:38px;margin-top:8px}
  .out .n{word-break:break-word!important;white-space:normal!important;line-height:1.4!important}
  .countdown{gap:6px;width:100%!important;box-sizing:border-box!important}
  .cd{padding:10px 4px;border-radius:12px}
  .cd b{font-size:18px}
  .cd span{font-size:8px}

  /* Stats and balances */
  .statbar div{width:100%;max-width:100%;box-sizing:border-box;padding:8px 16px;font-size:11.5px}
  .trust div{width:100%;max-width:100%;box-sizing:border-box;padding:8px 16px;font-size:11.5px}
  .balance{font-size:clamp(32px,8.5vw,52px);margin:10px 0 6px}
  .split{gap:8px;margin-top:16px}
  .split div{padding:14px;border-radius:14px}
  .split .v{font-size:18px;margin-top:4px}
  .mini-grid{grid-template-columns:1fr 1fr;gap:6px}
  .mini{padding:14px;border-radius:14px}
  .mini .v{font-size:20px;margin-top:4px}
  .value-big{font-size:clamp(26px,6vw,34px)}

  /* Footers & ledger */
  .foot{gap:26px}.foot .col{min-width:calc(50% - 13px)}.brandcol{min-width:100%;margin-right:0}
  .legal{flex-direction:column;gap:10px}
  footer{padding-bottom:calc(56px + env(safe-area-inset-bottom))}
}
@media (max-width:480px){
  .wrap{padding-left:12px;padding-right:12px}
  .nav-island{left:6px;right:6px;padding:5px 8px 5px 12px}
  .logo{font-size:13px}
  .hero h1{font-size:clamp(22px,7.5vw,30px)!important}
  .phead h1{font-size:clamp(22px,7vw,30px)!important}
  h2{font-size:clamp(19px,6.5vw,26px)!important}
  .overlay a{font-size:clamp(19px,6.5vw,26px)!important}
  .trust div{font-size:10.5px;padding:7px 10px}
  .chip{flex:1 1 62px;max-width:74px;padding:6px 2px}
  .chip .nm{font-size:9.5px}
  .mini-grid{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){
  *{animation-duration:.01ms!important;transition-duration:.01ms!important}
  [data-reveal]{opacity:1;transform:none;filter:none}
  html{scroll-behavior:auto}
}
"""

APP_CSS = r"""
/* ── account cluster in nav ─────────────────────────── */
.acct{position:relative;display:flex;align-items:center}
.avatar{width:36px;height:36px;flex:none;border-radius:999px;border:1px solid var(--hair);cursor:pointer;
  background:linear-gradient(160deg,rgba(196,248,42,.22),rgba(196,248,42,.05));color:var(--lime);
  display:grid;place-items:center;box-shadow:var(--inset);font-family:Archivo;
  font-variation-settings:'wdth' 110,'wght' 800;font-size:12px;letter-spacing:.02em;
  transition:border-color .5s var(--ease),background .5s var(--ease)}
.avatar:hover,.avatar[aria-expanded="true"]{border-color:rgba(196,248,42,.55)}
.bell{position:relative;width:36px;height:36px;flex:none;border-radius:999px;border:1px solid var(--hair);
  background:rgba(255,255,255,.04);color:var(--dim);display:grid;place-items:center;box-shadow:var(--inset);
  cursor:pointer;transition:all .5s var(--ease)}
.bell:hover{color:var(--ink);border-color:var(--hair-2)}
.bell .ic{width:17px;height:17px}
.bell .dot{position:absolute;top:6px;right:7px;width:8px;height:8px;border-radius:99px;background:var(--lime);
  box-shadow:0 0 0 2px #0A0B0C,0 0 12px rgba(196,248,42,.9)}
.menu{position:absolute;right:0;top:calc(100% + 14px);width:252px;padding:10px;border-radius:20px;z-index:95;
  background:rgba(10,11,12,.95);backdrop-filter:blur(24px) saturate(160%);-webkit-backdrop-filter:blur(24px) saturate(160%);
  border:1px solid var(--hair);box-shadow:var(--inset),0 26px 60px -18px rgba(0,0,0,.95);
  opacity:0;pointer-events:none;visibility:hidden;transform:translateY(-10px) scale(.97);transform-origin:top right;
  transition:opacity .35s var(--ease),transform .35s var(--ease),visibility 0s linear .35s}
.menu.open{opacity:1;pointer-events:auto;visibility:visible;transform:none;transition-delay:0s}
.menu .who{padding:10px 14px 14px;border-bottom:1px solid var(--hair);margin-bottom:8px}
.menu .who b{display:block;font-size:13.5px;font-weight:500}
.menu .who span{display:block;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--lime);margin-top:4px}
.menu .who i{display:block;font-style:normal;font-size:10px;color:var(--faint);letter-spacing:.12em;
  font-weight:600;text-transform:uppercase;margin-top:8px}
.menu a,.menu button{display:flex;width:100%;align-items:center;gap:12px;padding:10px 14px;border-radius:12px;
  font-size:13px;color:var(--dim);background:transparent;border:0;cursor:pointer;text-align:left;
  font-family:Montserrat,sans-serif;transition:background .4s var(--ease),color .4s var(--ease)}
.menu a .ic,.menu button .ic{width:16px;height:16px;color:var(--faint)}
.menu a:hover,.menu button:hover{background:rgba(255,255,255,.055);color:var(--ink)}
.menu a:hover .ic,.menu button:hover .ic{color:var(--lime)}
.menu .sep{height:1px;background:var(--hair);margin:8px 4px}
.menu button.danger:hover{color:var(--red)}
.menu button.danger:hover .ic{color:var(--red)}

/* ── text fields ────────────────────────────────────── */
.tf{margin-bottom:15px}
.tf label{display:block;font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);
  text-transform:uppercase;margin-bottom:9px}
.tf .lrow{display:flex;align-items:baseline;justify-content:space-between;gap:14px;margin-bottom:9px}
.tf .lrow label{margin-bottom:0}
.tf .lrow a{font-size:11px;color:var(--faint);font-weight:400;transition:color .4s var(--ease)}
.tf .lrow a:hover{color:var(--lime)}
.tf .inp{display:flex;align-items:center;gap:12px;border:1px solid var(--hair);border-radius:14px;
  padding:13px 16px;background:rgba(255,255,255,.03);box-shadow:var(--inset);
  transition:border-color .5s var(--ease),background .5s var(--ease)}
.tf .inp:focus-within{border-color:rgba(196,248,42,.5);background:rgba(196,248,42,.045)}
.tf .inp>.ic{width:17px;height:17px;color:var(--faint);flex:none}
.tf input,.tf select,.tf textarea{border:0;background:transparent;color:var(--ink);outline:none;width:100%;
  font-size:14px;font-family:Montserrat,sans-serif;font-weight:400;min-width:0}
.tf textarea{resize:vertical;min-height:74px;line-height:1.6}
.tf input::placeholder,.tf textarea::placeholder{color:var(--faint)}
.tf select{cursor:pointer;-webkit-appearance:none;appearance:none}
.tf .chev{width:0;height:0;flex:none;border-left:4.5px solid transparent;border-right:4.5px solid transparent;
  border-top:5px solid var(--faint)}
.tf select option{background:#0A0B0C;color:var(--ink)}
.tf .eye{background:transparent;border:0;color:var(--faint);cursor:pointer;padding:0;display:grid;place-items:center;
  font-size:9.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;flex:none;transition:color .4s var(--ease)}
.tf .eye:hover{color:var(--lime)}
.tf .hint{font-size:11px;color:var(--faint);margin-top:8px;font-weight:300;line-height:1.5}
.tf .err{font-size:11px;color:#ff9a9a;margin-top:8px;display:none;font-weight:400}
.tf.bad .inp{border-color:rgba(255,94,94,.55);background:rgba(255,94,94,.05)}
.tf.bad .err{display:block}
.tf.ok .inp{border-color:rgba(196,248,42,.4)}
.tf-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.strength{display:flex;gap:5px;margin-top:10px}
.strength i{flex:1;height:3px;border-radius:99px;background:rgba(255,255,255,.09);transition:background .5s var(--ease)}
.strength i.on{background:var(--lime)}
.strength i.mid{background:var(--amber)}
.strength i.low{background:var(--red)}
.checkrow{display:flex;align-items:flex-start;gap:12px;cursor:pointer;margin:6px 0 16px;
  font-size:12.5px;color:var(--dim);font-weight:300;line-height:1.6}
.checkrow input{position:absolute;opacity:0;width:0;height:0}
.checkrow .box{width:20px;height:20px;flex:none;border-radius:7px;border:1px solid var(--hair-2);margin-top:1px;
  background:rgba(255,255,255,.04);display:grid;place-items:center;box-shadow:var(--inset);
  transition:all .4s var(--ease);color:transparent}
.checkrow .box .ic{width:12px;height:12px}
.checkrow input:checked+.box{background:var(--lime);border-color:var(--lime);color:#0A0D03}
.checkrow input:focus-visible+.box{outline:1.5px solid var(--lime);outline-offset:3px}
.checkrow a{color:var(--lime);border-bottom:1px solid rgba(196,248,42,.3)}
.splitline{display:flex;align-items:center;gap:16px;margin:24px 0;color:var(--faint);
  font-weight:600;font-size:9.5px;letter-spacing:.18em;text-transform:uppercase}
.splitline::before,.splitline::after{content:"";flex:1;height:1px;background:var(--hair)}
.oauth{display:flex;gap:10px}
.oauth button{flex:1;display:flex;align-items:center;justify-content:center;gap:10px;border:1px solid var(--hair);
  background:rgba(255,255,255,.035);color:var(--dim);border-radius:14px;padding:13px 10px;cursor:pointer;
  font-size:12.5px;font-family:Montserrat,sans-serif;box-shadow:var(--inset);transition:all .5s var(--ease)}
.oauth button:hover{color:var(--ink);border-color:var(--hair-2);background:rgba(255,255,255,.06)}
.oauth button .ic{width:16px;height:16px}

/* ── auth layout ────────────────────────────────────── */
.auth{display:grid;grid-template-columns:1fr 1fr;min-height:100vh;align-items:stretch}
.auth-brand{padding:130px 56px 70px;display:flex;flex-direction:column;justify-content:center;
  border-right:1px solid var(--hair);position:relative}
.auth-brand h1{font-size:clamp(34px,3.9vw,58px);font-variation-settings:'wdth' 125,'wght' 900;margin-top:24px}
.auth-brand .lede{margin-top:24px;font-size:15px}
.auth-form{padding:130px 56px 70px;display:flex;flex-direction:column;justify-content:center}
.auth-form .inner{width:100%;max-width:452px;margin:0 auto}
.auth-form h2{font-size:clamp(26px,2.6vw,36px)}
.auth-sub{color:var(--dim);font-size:13.5px;font-weight:300;margin:14px 0 30px;line-height:1.6}
.auth-alt{margin-top:26px;font-size:12.5px;color:var(--faint);text-align:center}
.auth-alt a{color:var(--lime);border-bottom:1px solid rgba(196,248,42,.3);padding-bottom:1px}
.proof{display:flex;flex-direction:column;gap:14px;margin-top:44px}
.proof .pr{display:flex;align-items:flex-start;gap:15px;font-size:13px;color:var(--dim);font-weight:300}
.proof .pr b{display:block;color:var(--ink);font-weight:500;font-size:13.5px;margin-bottom:3px}
.proof .pr .ibox{width:34px;height:34px;border-radius:12px}
.proof .pr .ibox .ic{width:16px;height:16px}
.demo-note{margin-top:22px;border:1px dashed rgba(196,248,42,.3);border-radius:14px;padding:14px 16px;
  font-size:11.5px;color:var(--dim);font-weight:300;background:rgba(196,248,42,.035);line-height:1.6}
.demo-note b{font-family:'JetBrains Mono',monospace;color:var(--lime);font-weight:400}
.nav-min{position:fixed;top:26px;left:0;right:0;z-index:70;display:flex;align-items:center;
  justify-content:space-between;padding:0 40px}
.nav-min a.back{font-weight:600;font-size:10.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;
  display:flex;align-items:center;gap:9px;transition:color .5s var(--ease)}
.nav-min a.back:hover{color:var(--lime)}
.nav-min a.back .ic{width:13px;height:13px;transform:rotate(180deg)}

/* ── data tables ────────────────────────────────────── */
.dt{width:100%}
.dh,.dr{display:grid;gap:14px;align-items:center;padding:15px 24px}
.dh{font-weight:600;font-size:9.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;
  border-bottom:1px solid var(--hair)}
.dr{border-bottom:1px solid rgba(255,255,255,.045);font-size:13px;transition:background .6s var(--ease)}
.dr:hover{background:rgba(255,255,255,.025)}
.dr:last-child{border-bottom:0}
.dr.you{background:rgba(196,248,42,.055);box-shadow:inset 2px 0 0 var(--lime)}
.dr.you:hover{background:rgba(196,248,42,.08)}
.dr.hide{display:none}
.tag{display:inline-flex;align-items:center;gap:7px;border-radius:8px;padding:5px 10px;white-space:nowrap;
  font-weight:600;font-size:9px;letter-spacing:.12em;text-transform:uppercase;
  background:rgba(255,255,255,.05);border:1px solid var(--hair);color:var(--dim)}
.tag .ic{width:11px;height:11px}
.tag.lime{background:rgba(196,248,42,.09);border-color:rgba(196,248,42,.28);color:var(--lime)}
.tag.amber{background:rgba(255,106,31,.09);border-color:rgba(255,106,31,.3);color:var(--amber)}
.tag.red{background:rgba(255,94,94,.09);border-color:rgba(255,94,94,.3);color:#ff9a9a}
.pl{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums;font-size:13px}
.pl.up{color:var(--lime)}.pl.down{color:var(--red)}
.rk{font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 900;font-size:17px;color:var(--faint);line-height:1}
.rk.top{color:var(--lime)}
.xi{display:flex;gap:5px;flex-wrap:wrap}
.xi i{font-style:normal;font-family:'JetBrains Mono',monospace;font-size:10px;padding:4px 8px;border-radius:7px;
  background:rgba(255,255,255,.05);border:1px solid var(--hair);color:var(--dim);white-space:nowrap}
.sub-line{font-size:10.5px;color:var(--faint);font-weight:500;margin-top:4px;letter-spacing:.03em}
.alloc{height:10px;border-radius:99px;overflow:hidden;display:flex;background:rgba(255,255,255,.06);
  margin:20px 0 18px;box-shadow:var(--inset)}
.alloc i{display:block;height:100%;transition:width .9s var(--ease)}
.empty-state{padding:52px 24px;text-align:center;color:var(--faint);font-size:13px;font-weight:300}
.empty-state .ic-xl{margin:0 auto 16px;color:rgba(255,255,255,.14)}

/* ── toggles / settings ─────────────────────────────── */
.sw-row{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:17px 0;
  border-bottom:1px solid rgba(255,255,255,.05)}
.sw-row:last-child{border-bottom:0}
.sw-row .t{font-size:13.5px;font-weight:500}
.sw-row .d{font-size:11.5px;color:var(--faint);font-weight:300;margin-top:5px;max-width:54ch;line-height:1.55}
.tgl{width:48px;height:27px;flex:none;border-radius:99px;border:1px solid var(--hair);cursor:pointer;
  background:rgba(255,255,255,.05);position:relative;box-shadow:var(--inset);transition:all .45s var(--ease)}
.tgl i{position:absolute;top:3px;left:3px;width:19px;height:19px;border-radius:99px;background:var(--dim);
  transition:all .45s var(--ease)}
.tgl[aria-pressed="true"]{background:rgba(196,248,42,.2);border-color:rgba(196,248,42,.5)}
.tgl[aria-pressed="true"] i{left:24px;background:var(--lime);box-shadow:0 0 14px rgba(196,248,42,.7)}
.setnav{display:flex;flex-direction:column;gap:4px}
.setnav a{display:flex;align-items:center;gap:13px;padding:12px 16px;border-radius:14px;font-size:13px;
  color:var(--dim);border:1px solid transparent;transition:all .5s var(--ease)}
.setnav a .ic{width:16px;height:16px;color:var(--faint)}
.setnav a:hover{background:rgba(255,255,255,.04);color:var(--ink)}
.setnav a.on{background:rgba(196,248,42,.08);border-color:rgba(196,248,42,.22);color:var(--lime)}
.setnav a.on .ic{color:var(--lime)}
.sticky{position:sticky;top:118px}
.danger-zone{border:1px solid rgba(255,94,94,.28);background:rgba(255,94,94,.04);border-radius:18px;padding:24px}

/* ── activity feed ──────────────────────────────────── */
.fd{display:flex;gap:16px;padding:19px 24px;border-bottom:1px solid rgba(255,255,255,.05);
  transition:background .6s var(--ease)}
.fd:hover{background:rgba(255,255,255,.022)}
.fd:last-child{border-bottom:0}
.fd.unread{background:rgba(196,248,42,.035)}
.fd .bd{flex:1;min-width:0}
.fd .tt{font-size:13.5px;font-weight:500;display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.fd.unread .tt::after{content:"";width:6px;height:6px;border-radius:99px;background:var(--lime);
  flex:none;box-shadow:0 0 10px rgba(196,248,42,.9)}
.fd .ms{font-size:12.5px;color:var(--dim);font-weight:300;margin-top:6px;line-height:1.6}
.fd .tm{font-size:9.5px;color:var(--faint);margin-top:9px;letter-spacing:.14em;font-weight:600;text-transform:uppercase}
.fd .amt{font-family:'JetBrains Mono',monospace;font-size:13.5px;flex:none;text-align:right;white-space:nowrap}
.daysep{padding:16px 24px 12px;font-weight:600;font-size:9.5px;letter-spacing:.18em;color:var(--faint);
  text-transform:uppercase;border-bottom:1px solid var(--hair);background:rgba(255,255,255,.015)}

/* ── onboarding ─────────────────────────────────────── */
.prog{display:flex;gap:12px;margin-bottom:38px;flex-wrap:wrap}
.prog .st{flex:1;min-width:118px;border-top:2px solid rgba(255,255,255,.09);padding-top:13px;
  transition:border-color .7s var(--ease)}
.prog .st .n{font-weight:600;font-size:9px;letter-spacing:.2em;color:var(--faint);text-transform:uppercase}
.prog .st .l{font-size:12.5px;color:var(--faint);margin-top:6px;font-weight:300}
.prog .st.done{border-top-color:rgba(196,248,42,.4)}
.prog .st.done .l{color:var(--dim)}
.prog .st.on{border-top-color:var(--lime)}
.prog .st.on .n{color:var(--lime)}
.prog .st.on .l{color:var(--ink);font-weight:400}
.picks{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.pick{border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:16px;padding:16px;
  text-align:left;cursor:pointer;box-shadow:var(--inset);color:var(--ink);font-family:Montserrat,sans-serif;
  transition:all .6s var(--ease)}
.pick:hover{border-color:var(--hair-2);transform:translateY(-2px)}
.pick[aria-pressed="true"]{border-color:var(--lime);background:rgba(196,248,42,.07)}
.pick .sym{font-family:'JetBrains Mono',monospace;font-size:13px}
.pick .nm{font-size:11px;color:var(--faint);margin-top:4px}
.pick .px{font-family:'JetBrains Mono',monospace;font-size:15px;margin-top:12px;font-weight:300}
.step-pane{display:none}
.step-pane.on{display:block}
.wiz-foot{display:flex;gap:12px;margin-top:28px;align-items:center;flex-wrap:wrap}
.wiz-foot .sp{margin-left:auto;font-size:11.5px;color:var(--faint)}

/* ── quick actions / misc ───────────────────────────── */
.qa{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.qa a{display:flex;flex-direction:column;gap:14px;border:1px solid var(--hair);background:rgba(255,255,255,.03);
  border-radius:18px;padding:22px 20px;box-shadow:var(--inset);transition:all .6s var(--ease)}
.qa a:hover{border-color:rgba(196,248,42,.32);background:rgba(196,248,42,.05);transform:translateY(-3px)}
.qa b{font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;text-transform:uppercase;font-size:14px;
  display:block;margin-bottom:5px}
.qa span{font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.5}
.clock{display:flex;gap:8px}
.clock .u{flex:1;border:1px solid var(--hair);background:rgba(255,255,255,.03);border-radius:14px;
  padding:14px 8px;text-align:center;box-shadow:var(--inset)}
.clock .u b{display:block;font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:300;letter-spacing:-.02em}
.clock .u span{display:block;font-weight:600;font-size:8.5px;letter-spacing:.16em;color:var(--faint);
  text-transform:uppercase;margin-top:6px}
.rowlink{display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.05);
  font-size:13px;color:var(--dim);transition:color .5s var(--ease)}
.rowlink:last-child{border-bottom:0}
.rowlink:hover{color:var(--ink)}
.rowlink .ic{color:var(--faint);width:16px;height:16px}
.rowlink b{margin-left:auto;font-family:'JetBrains Mono',monospace;font-weight:400;color:var(--ink)}
.greet{font-weight:600;font-size:10px;letter-spacing:.2em;color:var(--lime);text-transform:uppercase}
.app-head{padding:150px 0 44px}
.app-head h1{font-size:clamp(32px,5vw,58px);font-variation-settings:'wdth' 125,'wght' 900;margin-top:20px}
.app-head .lede{margin-top:20px;font-size:15px}
.head-row{display:flex;align-items:flex-end;justify-content:space-between;gap:28px;flex-wrap:wrap}
.head-row .acts{display:flex;gap:10px;flex-wrap:wrap}

/* ── wallet: balance hero ───────────────────────────── */
.bal-big{font-family:'JetBrains Mono',monospace;font-weight:200;font-size:clamp(36px,5vw,66px);
  letter-spacing:-.045em;line-height:1;margin:14px 0 12px}
.bal-big small{font-size:17px;color:var(--faint);letter-spacing:0;font-weight:300}
.bal-delta{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;color:var(--lime);font-weight:500}
.bal-delta .ic{width:13px;height:13px}
.bal-delta.down{color:var(--red)}
.bal-delta em{font-style:normal;color:var(--faint);font-weight:300}
.bal-chart{height:168px;margin:24px 0 6px;position:relative}
.bal-chart svg{width:100%;height:100%;display:block;overflow:visible}
.range{display:flex;gap:6px;padding:5px;border-radius:999px;background:rgba(255,255,255,.035);
  border:1px solid var(--hair);box-shadow:var(--inset);width:max-content;max-width:100%;flex-wrap:wrap}
.range button{border:0;background:transparent;color:var(--faint);border-radius:999px;padding:8px 18px;
  cursor:pointer;font-family:'JetBrains Mono',monospace;font-size:11.5px;transition:all .5s var(--ease)}
.range button[aria-pressed="true"]{background:var(--lime);color:#0A0D03;box-shadow:var(--inset)}
.range button:hover:not([aria-pressed="true"]){color:var(--ink)}

/* four-up action tiles */
.acts4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:26px}
.acts4 button{display:flex;flex-direction:column;align-items:center;gap:11px;padding:18px 8px 15px;
  border-radius:20px;border:1px solid var(--hair);background:rgba(255,255,255,.04);color:var(--dim);
  cursor:pointer;box-shadow:var(--inset);font-family:Montserrat,sans-serif;transition:all .6s var(--ease)}
.acts4 button .ic{width:19px;height:19px}
.acts4 button span{font-weight:600;font-size:10px;letter-spacing:.14em;text-transform:uppercase}
.acts4 button:hover:not([aria-pressed="true"]){color:var(--ink);border-color:var(--hair-2);transform:translateY(-2px)}
.acts4 button[aria-pressed="true"]{background:var(--lime);border-color:var(--lime);color:#0A0D03;
  box-shadow:var(--inset),0 16px 38px -16px rgba(196,248,42,.8)}

/* asset rows */
.arow{display:grid;grid-template-columns:1.7fr 88px 1fr;gap:16px;align-items:center;padding:15px 24px;
  border-bottom:1px solid rgba(255,255,255,.045);transition:background .6s var(--ease)}
.arow:last-child{border-bottom:0}
.arow:hover{background:rgba(255,255,255,.025)}
.arow .who{display:flex;align-items:center;gap:14px;min-width:0}
.coin{width:40px;height:40px;border-radius:999px;flex:none;display:grid;place-items:center;
  box-shadow:var(--inset);border:1px solid var(--hair);background:rgba(255,255,255,.05);color:var(--dim)}
.coin .ic{width:19px;height:19px}
.coin.lime{border-color:rgba(196,248,42,.35);background:rgba(196,248,42,.1);color:var(--lime)}
.coin.am{border-color:rgba(255,106,31,.32);background:rgba(255,106,31,.09);color:var(--amber)}
.arow .nm{font-size:14px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.arow .qt{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--faint);margin-top:4px}
.arow .val{text-align:right;font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:300}
.arow .chg{text-align:right;font-family:'JetBrains Mono',monospace;font-size:11.5px;margin-top:4px}

/* receive / QR */
.netsel{display:flex;align-items:center;gap:14px;border:1px solid var(--hair);border-radius:18px;
  padding:13px 18px;background:rgba(255,255,255,.03);box-shadow:var(--inset);width:100%;
  color:var(--ink);font-family:Montserrat,sans-serif;text-align:left;cursor:pointer;
  transition:border-color .5s var(--ease),background .5s var(--ease)}
.netsel:hover{border-color:var(--hair-2);background:rgba(255,255,255,.05)}
.netsel .k{display:block;font-weight:600;font-size:9px;letter-spacing:.16em;color:var(--faint);
  text-transform:uppercase}
.netsel .v{display:block;font-size:13.5px;margin-top:5px}
.netsel .chev{margin-left:auto}
.qr{background:#F4F6F1;border-radius:24px;padding:20px;display:grid;place-items:center;margin:18px 0 16px;
  position:relative;box-shadow:0 22px 54px -22px rgba(0,0,0,.95)}
.qr svg{width:100%;height:auto;max-width:238px;display:block}
.qr .mark{position:absolute;width:50px;height:50px;border-radius:15px;background:#0A0B0C;display:grid;
  place-items:center;border:3px solid #F4F6F1}
.qr .mark .ic{width:23px;height:23px;color:var(--lime)}
.addr{font-family:'JetBrains Mono',monospace;font-size:12px;word-break:break-all;line-height:1.75;
  text-align:center;margin-bottom:16px;padding:0 4px}
.addr i{font-style:normal}
.warn{display:flex;gap:13px;align-items:flex-start;border:1px solid rgba(255,106,31,.3);
  background:rgba(255,106,31,.07);border-radius:16px;padding:15px 17px;margin-top:14px}
.warn[hidden]{display:none}
.warn .ic{width:17px;height:17px;color:var(--amber);flex:none;margin-top:2px}
.warn p{margin:0;font-size:12px;color:#d9a37e;font-weight:300;line-height:1.6}
.pane{display:none}
.pane.on{display:block}
.listening{display:inline-flex;align-items:center;gap:8px;border-radius:999px;padding:6px 13px;
  background:rgba(196,248,42,.09);border:1px solid rgba(196,248,42,.25);color:var(--lime);
  font-weight:600;font-size:9px;letter-spacing:.14em;text-transform:uppercase}
.listening i{width:6px;height:6px;border-radius:99px;background:var(--lime);display:block;
  box-shadow:0 0 10px rgba(196,248,42,.9);animation:blip 1.9s var(--ease) infinite}
@keyframes blip{0%,100%{opacity:1}50%{opacity:.25}}

/* ── floating taskbar ───────────────────────────────── */
.topbar{padding:8px 8px 8px 22px}
.topbar .logo{margin-right:26px}
.taskbar{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:75;
  display:flex;align-items:center;gap:4px;padding:8px;border-radius:999px;
  width:max-content;max-width:calc(100vw - 24px);
  background:rgba(9,10,11,.94);backdrop-filter:blur(26px) saturate(170%);
  -webkit-backdrop-filter:blur(26px) saturate(170%);border:1px solid var(--hair);
  box-shadow:var(--inset),0 26px 64px -18px rgba(0,0,0,.96)}
.taskbar a{display:flex;align-items:center;gap:0;height:46px;padding:0 15px;border-radius:999px;
  color:var(--faint);transition:color .5s var(--ease),background .55s var(--ease),padding .55s var(--ease)}
.taskbar a .ic{width:20px;height:20px;flex:none}
.taskbar a span{max-width:0;overflow:hidden;white-space:nowrap;opacity:0;
  font-weight:600;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  transition:max-width .55s var(--ease),opacity .4s var(--ease),margin .55s var(--ease)}
.taskbar a:hover{color:var(--ink)}
.taskbar a.on{background:var(--lime);color:#0A0D03;padding:0 20px;
  box-shadow:var(--inset),0 14px 32px -12px rgba(196,248,42,.85)}
.taskbar a.on span{max-width:130px;opacity:1;margin-left:10px}
.taskbar ~ footer{padding-bottom:calc(126px + env(safe-area-inset-bottom))}
.taskbar ~ .ft-toast-container{bottom:calc(102px + env(safe-area-inset-bottom))}

/* ── wallet: gradient balance card ──────────────────── */
.wcard{position:relative;border-radius:26px;padding:26px 24px 22px;overflow:hidden;
  background:linear-gradient(150deg,#d7ff55 0%,#C4F82A 44%,#8ab800 100%);color:#0A0D03;
  box-shadow:0 26px 62px -22px rgba(196,248,42,.5),var(--inset)}
.wcard::after{content:"";position:absolute;right:-80px;top:-100px;width:270px;height:270px;
  border-radius:50%;background:rgba(255,255,255,.17);pointer-events:none}
.wcard::before{content:"";position:absolute;left:-60px;bottom:-120px;width:230px;height:230px;
  border-radius:50%;background:rgba(10,13,3,.07);pointer-events:none}
.wcard>*{position:relative;z-index:1}
.wcard .k{font-weight:600;font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;
  color:rgba(10,13,3,.58)}
.wcard .amt{font-family:'JetBrains Mono',monospace;font-weight:300;font-size:clamp(32px,4.4vw,52px);
  letter-spacing:-.04em;line-height:1;margin:13px 0 11px}
.wcard .amt small{font-size:16px;color:rgba(10,13,3,.5);letter-spacing:0}
.wcard .sub{display:flex;align-items:center;gap:8px;font-size:12.5px;color:rgba(10,13,3,.74);
  font-weight:500}
.wcard .sub .ic{width:13px;height:13px}
.wcard .tag-id{position:absolute;top:26px;right:24px;font-family:'JetBrains Mono',monospace;
  font-size:11px;color:rgba(10,13,3,.55);z-index:1}
.wacts{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:26px}
.wacts button{display:flex;flex-direction:column;align-items:center;gap:9px;padding:14px 4px 12px;
  border-radius:18px;border:1px solid rgba(10,13,3,.16);background:rgba(10,13,3,.08);color:#0A0D03;
  cursor:pointer;font-family:Montserrat,sans-serif;transition:background .5s var(--ease)}
.wacts button:hover{background:rgba(10,13,3,.16)}
.wacts button[aria-pressed="true"]{background:#0A0D03;color:var(--lime);border-color:#0A0D03}
.wacts button .ic{width:19px;height:19px}
.wacts button span{font-weight:600;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase}

/* quick-send row */
.quickrow{display:flex;gap:16px;overflow-x:auto;padding:6px 0 10px;scrollbar-width:none}
.quickrow::-webkit-scrollbar{display:none}
.qp{flex:none;width:66px;text-align:center;background:transparent;border:0;cursor:pointer;
  color:var(--dim);font-family:Montserrat,sans-serif;padding:0}
.qp .av{width:52px;height:52px;border-radius:999px;margin:0 auto 9px;display:grid;place-items:center;
  border:1px solid var(--hair);box-shadow:var(--inset);font-family:Archivo;
  font-variation-settings:'wdth' 100,'wght' 800;font-size:15px;color:#0A0D03;
  transition:transform .5s var(--ease)}
.qp:hover .av{transform:translateY(-3px)}
.qp .av.add{border-style:dashed;border-color:rgba(196,248,42,.42);color:var(--lime);
  background:rgba(196,248,42,.07)}
.qp .av.add .ic{width:20px;height:20px}
.qp span{display:block;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.qp:hover{color:var(--ink)}

/* transaction history */
.trow{display:flex;align-items:center;gap:14px;padding:14px 0;
  border-bottom:1px solid rgba(255,255,255,.05)}
.trow:last-child{border-bottom:0}
.trow .bd{min-width:0;flex:1}
.trow .t{font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trow .d{font-size:11px;color:var(--faint);margin-top:4px}
.trow .a{font-family:'JetBrains Mono',monospace;font-size:13.5px;flex:none;white-space:nowrap}
.seeall{margin-left:auto;font-size:11.5px;color:var(--lime);display:flex;align-items:center;gap:7px}
.seeall .ic{width:12px;height:12px}
.rowhead{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.rowhead .k-label{margin:0}

/* ── market pages ───────────────────────────────────── */
.crumb{display:inline-flex;align-items:center;gap:9px;font-weight:600;font-size:10.5px;letter-spacing:.14em;
  color:var(--faint);text-transform:uppercase;transition:color .4s var(--ease)}
.crumb:hover{color:var(--lime)}
.crumb .ic{width:13px;height:13px;transform:rotate(180deg)}
.asset-head{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.asset-head .coin{width:62px;height:62px}
.asset-head .coin .ic{width:28px;height:28px}
.asset-head .nm{font-family:Archivo;font-variation-settings:'wdth' 125,'wght' 900;text-transform:uppercase;
  font-size:clamp(26px,3.2vw,40px);line-height:1}
.asset-head .sym{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--lime);margin-top:7px}
.asset-head .px{margin-left:auto;text-align:right}
.asset-head .px .v{font-family:'JetBrains Mono',monospace;font-weight:300;font-size:clamp(26px,3vw,38px);
  letter-spacing:-.03em;line-height:1}
.asset-head .px .d{font-family:'JetBrains Mono',monospace;font-size:13px;margin-top:8px}
.book{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.book .side .h{display:flex;justify-content:space-between;font-weight:600;font-size:9px;letter-spacing:.14em;
  color:var(--faint);text-transform:uppercase;padding-bottom:10px;border-bottom:1px solid var(--hair);
  margin-bottom:4px}
.brow{position:relative;display:flex;justify-content:space-between;padding:7px 8px;
  font-family:'JetBrains Mono',monospace;font-size:12px;border-radius:7px;overflow:hidden}
.brow i{position:absolute;top:0;bottom:0;right:0;display:block;border-radius:7px}
.brow span{position:relative;z-index:1}
.book .bid .brow i{background:rgba(196,248,42,.13)}
.book .bid .brow span:first-child{color:var(--lime)}
.book .ask .brow i{background:rgba(255,94,94,.12)}
.book .ask .brow span:first-child{color:var(--red)}
.spread{text-align:center;padding:12px 0;margin:6px 0;border-top:1px solid var(--hair);
  border-bottom:1px solid var(--hair);font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--faint)}
.sideseg{display:flex;gap:5px;padding:5px;border-radius:16px;background:rgba(255,255,255,.035);
  border:1px solid var(--hair);box-shadow:var(--inset);margin-bottom:18px}
.sideseg button{flex:1;border:0;background:transparent;color:var(--dim);border-radius:12px;padding:13px 0;
  cursor:pointer;font-family:Montserrat,sans-serif;font-weight:600;font-size:11.5px;letter-spacing:.1em;
  text-transform:uppercase;transition:all .5s var(--ease)}
.sideseg button[aria-pressed="true"][data-s="buy"]{background:var(--lime);color:#0A0D03}
.sideseg button[aria-pressed="true"][data-s="sell"]{background:var(--red);color:#1a0505}
.sideseg button:hover:not([aria-pressed="true"]){color:var(--ink)}
.statgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.statgrid .mini{padding:16px}
.statgrid .mini .v{font-size:19px}
.tr-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;padding:9px 0;
  font-family:'JetBrains Mono',monospace;font-size:12px;border-bottom:1px solid rgba(255,255,255,.04)}
.tr-row:last-child{border-bottom:0}
@media (max-width:768px){
  .book{grid-template-columns:1fr;gap:26px}
  .statgrid{grid-template-columns:1fr 1fr}
  .asset-head .px{margin-left:0;text-align:left;width:100%}
}

/* ── account hub ────────────────────────────────────── */
.hub{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.hub a{display:flex;align-items:center;gap:16px;padding:20px;border-radius:20px;
  border:1px solid var(--hair);background:rgba(255,255,255,.03);box-shadow:var(--inset);
  transition:border-color .5s var(--ease),background .5s var(--ease),transform .5s var(--ease)}
.hub a:hover{border-color:rgba(196,248,42,.32);background:rgba(196,248,42,.05);transform:translateY(-3px)}
.hub a .bd{min-width:0;flex:1}
.hub a b{display:block;font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;
  text-transform:uppercase;font-size:14px;margin-bottom:5px}
.hub a p{margin:0;font-size:11.5px;color:var(--faint);font-weight:300;line-height:1.5}
.hub a .go{margin-left:auto;color:var(--faint);flex:none}
.hub a .go .ic{width:15px;height:15px}
.hub a .val{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--lime);
  margin-top:7px;display:block}
.idcard{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.idcard .avatar{width:64px;height:64px;font-size:20px;cursor:default}

/* ── matchday: live accent ──────────────────────────── */
:root{--live:#FF3B47;--live-soft:rgba(255,59,71,.1);--live-line:rgba(255,59,71,.34)}
.dot-live{width:7px;height:7px;border-radius:99px;background:var(--live);display:inline-block;flex:none;
  box-shadow:0 0 10px rgba(255,59,71,.9);animation:blip 1.6s var(--ease) infinite}

/* date strip */
.datestrip{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.dates{display:flex;align-items:center;gap:3px;padding:5px;border-radius:999px;background:rgba(255,255,255,.035);
  border:1px solid var(--hair);box-shadow:var(--inset)}
.dates button{border:0;background:transparent;color:var(--faint);border-radius:999px;padding:8px 16px;
  cursor:pointer;text-align:center;font-family:Montserrat,sans-serif;transition:all .5s var(--ease)}
.dates button small{display:block;font-weight:600;font-size:8.5px;letter-spacing:.14em;text-transform:uppercase;
  margin-bottom:4px}
.dates button b{display:block;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:400}
.dates button:hover{color:var(--dim)}
.dates button[aria-pressed="true"]{background:rgba(255,255,255,.07);color:var(--ink);box-shadow:var(--inset)}
.dates button[aria-pressed="true"] small{color:var(--live)}
.dates .nudge{padding:10px 12px;color:var(--faint);font-size:13px}
.livetgl{display:inline-flex;align-items:center;gap:9px;border-radius:999px;padding:10px 17px;cursor:pointer;
  border:1px solid var(--hair);background:rgba(255,255,255,.04);color:var(--faint);box-shadow:var(--inset);
  font-weight:600;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;font-family:Montserrat,sans-serif;
  transition:all .5s var(--ease)}
.livetgl:hover{color:var(--ink);border-color:var(--hair-2)}
.livetgl[aria-pressed="true"]{background:var(--live);border-color:var(--live);color:#fff}
.livetgl[aria-pressed="true"] .dot-live{background:#fff;box-shadow:none}

/* featured match */
.feat{position:relative;border-radius:22px;padding:24px 22px 30px;border:1px solid var(--hair);
  box-shadow:var(--inset);margin:0 0 6px;
  background:radial-gradient(ellipse at 50% 128%,rgba(196,248,42,.17),rgba(255,255,255,.02) 64%)}
.feat.islive{background:radial-gradient(ellipse at 50% 128%,rgba(255,59,71,.17),rgba(255,255,255,.02) 64%);
  border-color:var(--live-line)}
.feat-top{display:flex;justify-content:space-between;align-items:center;gap:14px;font-weight:600;font-size:9.5px;
  letter-spacing:.16em;color:var(--faint);text-transform:uppercase}
.feat-top .mid{text-align:center;flex:1}
.feat-top .mid b{display:block;font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 800;font-size:15px;
  color:var(--ink);letter-spacing:.02em}
.feat-top .mid span{display:block;margin-top:5px}
.feat-top button{background:transparent;border:0;color:var(--faint);cursor:pointer;font:inherit;
  letter-spacing:.16em;text-transform:uppercase;transition:color .4s var(--ease)}
.feat-top button:hover{color:var(--lime)}
.feat-mid{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:18px;margin-top:22px}
.feat .side{text-align:center;min-width:0}
.feat .side .nm{font-family:Archivo;font-variation-settings:'wdth' 118,'wght' 800;text-transform:uppercase;
  font-size:16px;margin-top:13px;line-height:1.1}
.feat .side .ha{display:flex;align-items:center;justify-content:center;gap:6px;font-weight:600;font-size:9px;
  letter-spacing:.14em;color:var(--faint);margin-top:7px;text-transform:uppercase}
.feat .side .ha .ic{width:11px;height:11px}
.feat .sc{font-family:'JetBrains Mono',monospace;font-size:clamp(28px,3.2vw,40px);font-weight:300;
  letter-spacing:-.03em;white-space:nowrap}
.minute{position:absolute;left:50%;bottom:-13px;transform:translateX(-50%);border-radius:999px;padding:6px 15px;
  background:var(--lime);color:#0A0D03;font-family:'JetBrains Mono',monospace;font-size:11px;white-space:nowrap;
  box-shadow:0 12px 28px -12px rgba(196,248,42,.9)}
.minute.live{background:var(--live);color:#fff;box-shadow:0 12px 28px -12px rgba(255,59,71,.9)}
.minute.done{background:rgba(255,255,255,.1);color:var(--dim);box-shadow:none;border:1px solid var(--hair)}
.tcrest{width:54px;height:54px;border-radius:999px;margin:0 auto;display:grid;place-items:center;flex:none;
  font-family:Archivo;font-variation-settings:'wdth' 100,'wght' 900;font-size:15px;color:#0A0D03;
  box-shadow:var(--inset),0 10px 24px -10px rgba(0,0,0,.9)}
.tcrest.sm{width:26px;height:26px;font-size:7.5px;letter-spacing:-.01em;border-radius:999px;margin:0;
  box-shadow:var(--inset)}

/* competition group + fixture rows */
.comp{display:flex;align-items:center;gap:13px;padding:24px 22px 12px}
.comp .fl{width:24px;height:17px;border-radius:3px;overflow:hidden;flex:none;box-shadow:var(--inset)}
.comp .fl svg{display:block;width:100%;height:100%}
.comp>div{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;min-width:0}
.comp b{font-family:Archivo;font-variation-settings:'wdth' 120,'wght' 800;text-transform:uppercase;font-size:17px}
.comp span{font-size:11.5px;color:var(--faint);font-weight:300}
.comp .more{margin-left:auto;color:var(--faint);display:flex;align-items:center;gap:7px;font-size:11px;
  transition:color .4s var(--ease)}
.comp .more:hover{color:var(--lime)}
.fixt{display:grid;grid-template-columns:64px 1fr 28px;gap:14px;align-items:center;padding:13px 16px;
  border-radius:18px;background:rgba(255,255,255,.03);border:1px solid var(--hair);box-shadow:var(--inset);
  margin:0 14px 8px;transition:border-color .5s var(--ease),background .5s var(--ease)}
.fixt:hover{border-color:var(--hair-2);background:rgba(255,255,255,.055)}
.fixt.live{border-color:var(--live-line);background:var(--live-soft)}
.fixt .stat{text-align:center;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--faint);
  line-height:1.4}
.fixt .stat b{display:block;font-weight:400;color:var(--dim)}
.fixt.live .stat,.fixt.live .stat b{color:var(--live)}
.fixt .teams{display:flex;flex-direction:column;gap:9px;min-width:0}
.fixt .tm{display:flex;align-items:center;gap:11px;min-width:0}
.fixt .tm .n{font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.fixt .tm .g{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:13.5px;flex:none}
.fixt .tm.dim .n,.fixt .tm.dim .g{color:var(--faint)}
.fixt .mine{font-family:'JetBrains Mono',monospace;font-size:9.5px;color:var(--lime);flex:none;
  border:1px solid rgba(196,248,42,.28);background:rgba(196,248,42,.08);border-radius:6px;padding:2px 6px}
.star{background:transparent;border:0;cursor:pointer;color:rgba(255,255,255,.2);padding:0;display:grid;
  place-items:center;transition:color .4s var(--ease),transform .4s var(--ease)}
.star .ic{width:19px;height:19px}
.star:hover{color:var(--dim);transform:scale(1.12)}
.star[aria-pressed="true"]{color:var(--lime)}

/* tab strip */
.tabstrip{display:flex;gap:4px;padding:5px;border-radius:999px;background:rgba(255,255,255,.035);
  border:1px solid var(--hair);box-shadow:var(--inset);overflow-x:auto;scrollbar-width:none}
.tabstrip::-webkit-scrollbar{display:none}
.tabstrip button{border:0;background:transparent;color:var(--faint);border-radius:999px;padding:9px 18px;
  cursor:pointer;white-space:nowrap;font-family:Montserrat,sans-serif;font-weight:600;font-size:10.5px;
  letter-spacing:.12em;text-transform:uppercase;transition:all .5s var(--ease)}
.tabstrip button:hover{color:var(--ink)}
.tabstrip button[aria-pressed="true"]{background:var(--lime);color:#0A0D03;box-shadow:var(--inset)}

/* form pills */
.form5{display:flex;gap:5px}
.form5 i{width:21px;height:21px;border-radius:7px;display:grid;place-items:center;font-style:normal;
  font-family:'JetBrains Mono',monospace;font-size:9.5px;border:1px solid var(--hair);
  background:rgba(255,255,255,.05);color:var(--faint)}
.form5 i.w{background:rgba(196,248,42,.15);border-color:rgba(196,248,42,.36);color:var(--lime)}
.form5 i.l{background:var(--live-soft);border-color:var(--live-line);color:#ff8a92}
.form5 i.d{background:rgba(255,106,31,.1);border-color:rgba(255,106,31,.28);color:var(--amber)}

/* league position gauge */
.gauge{display:grid;grid-template-columns:auto 1fr auto;gap:26px;align-items:center;padding:6px 0}
.gside{text-align:center}
.gbar{width:11px;height:128px;border-radius:99px;background:rgba(255,255,255,.07);position:relative;
  overflow:hidden;margin:0 auto 14px;box-shadow:var(--inset)}
.gbar i{position:absolute;left:0;right:0;bottom:0;border-radius:99px;
  background:linear-gradient(180deg,#C4F82A,#6f9c00);transition:height .9s var(--ease)}
.gbar.rival i{background:linear-gradient(180deg,rgba(255,255,255,.42),rgba(255,255,255,.14))}
.gside .pc{font-family:'JetBrains Mono',monospace;font-size:19px;font-weight:300}
.gside .lb{font-weight:600;font-size:8.5px;letter-spacing:.16em;color:var(--faint);text-transform:uppercase;
  margin-top:5px}
.ladder{display:flex;flex-direction:column;align-items:center;gap:9px;position:relative}
.ladder::before{content:"";position:absolute;top:6px;bottom:6px;width:1px;background:var(--hair)}
.rung{position:relative;z-index:1;min-width:38px;text-align:center;border-radius:11px;padding:7px 10px;
  border:1px solid var(--hair);background:rgba(10,11,12,.96);font-family:'JetBrains Mono',monospace;
  font-size:12px;color:var(--faint);box-shadow:var(--inset)}
.rung.you{border-color:var(--lime);background:rgba(196,248,42,.1);color:var(--lime)}

@media (max-width:1024px){
  .auth{grid-template-columns:1fr}
  .auth-brand{display:none}
  .qa{grid-template-columns:1fr 1fr}
  .nav-island .bell{display:none}
}
@media (max-width:768px){
  .auth-form{padding:104px 20px 54px}
  .nav-min{padding:0 16px;top:18px}
  .nav-min a.back span{display:none}
  .tf-row{grid-template-columns:1fr}
  .picks{grid-template-columns:1fr 1fr}
  .qa{grid-template-columns:1fr}
  .oauth{flex-direction:column}
  .dh,.dr{padding:13px 14px;gap:10px}
  .fd{padding:16px 14px;gap:12px}
  .daysep{padding:14px 14px 10px}
  .app-head{padding:104px 0 30px}
  .app-head h1{font-size:clamp(26px,8vw,40px)!important;font-variation-settings:'wdth' 105,'wght' 800!important}
  .head-row{align-items:flex-start}
  .head-row .acts .btn{flex:1;justify-content:space-between}
  .sticky{position:static}
  .sw-row{gap:14px;padding:15px 0}
  .prog{gap:8px}.prog .st{min-width:0;flex:1 1 42%;padding-top:10px}
  .prog .st .l{font-size:11.5px}
  .menu{width:calc(100vw - 32px);max-width:280px}
  .acts4{grid-template-columns:repeat(2,1fr);gap:7px}
  .acts4 button{padding:15px 6px 13px;border-radius:17px}
  .arow{grid-template-columns:1.4fr 1fr;gap:10px;padding:13px 14px}
  .arow>*:nth-child(2){display:none}
  .coin{width:34px;height:34px}
  .coin .ic{width:16px;height:16px}
  .bal-chart{height:130px}
  .range{width:100%;justify-content:space-between}
  .range button{flex:1;padding:8px 0;text-align:center}
  .qr{padding:14px;border-radius:20px}
  .addr{font-size:11px}
  .datestrip{width:100%}
  .dates{flex:1;justify-content:space-between}
  .dates button{padding:8px 10px}
  .livetgl{padding:9px 13px}
  .feat{padding:20px 14px 28px;border-radius:19px}
  .feat-top{flex-wrap:wrap}
  .feat-top .mid{order:-1;flex:1 1 100%;margin-bottom:12px}
  .feat-mid{gap:10px}
  .feat .side .nm{font-size:13px;margin-top:10px}
  .tcrest{width:44px;height:44px;font-size:13px}
  .comp{padding:20px 14px 10px}
  .comp b{font-size:15px}
  .fixt{grid-template-columns:54px 1fr 24px;gap:10px;padding:11px 12px;margin:0 8px 7px;border-radius:15px}
  .fixt .tm .n{font-size:12.5px}
  .gauge{grid-template-columns:1fr;gap:20px;justify-items:center}
  .ladder{flex-direction:row}
  .ladder::before{top:50%;bottom:auto;left:6px;right:6px;width:auto;height:1px}
  .gbar{height:88px}
  .tabstrip button{padding:9px 14px;font-size:9.5px}
  .taskbar{left:12px;right:12px;bottom:max(12px,env(safe-area-inset-bottom));transform:none;
    width:auto;max-width:none;justify-content:space-between;padding:7px;gap:2px}
  .taskbar a{height:44px;padding:0 13px}
  .taskbar a.on{padding:0 16px}
  .taskbar a.on span{max-width:110px;font-size:10px;margin-left:9px}
  .taskbar a .ic{width:19px;height:19px}
  .taskbar ~ footer{padding-bottom:calc(120px + env(safe-area-inset-bottom))}
  .topbar{padding:6px 8px 6px 14px}
  .topbar .logo{margin-right:0}
  .hub{grid-template-columns:1fr}
  .idcard .avatar{width:54px;height:54px;font-size:17px}
}
"""

CSS = CSS + APP_CSS

MARKET_NAV = [("exchange.html", "Exchange"), ("clubs.html", "Dream Clubs"),
              ("fanplay.html", "FanPlay"), ("ftr.html", "$FTR"),
              ("how-it-works.html", "How it works")]

NAVITEMS = MARKET_NAV  # kept for backwards compatibility

def head(title, extra_css=""):
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            '<title>%s</title>%s<style>%s%s</style></head><body>' % (title, FONTS, CSS, extra_css))

def atmosphere():
    return ('<div class="orb orb-a"></div><div class="orb orb-b"></div><div class="orb orb-c"></div>'
            '<div class="grain"></div>'
            '<div id="ftToastContainer" class="ft-toast-container" aria-live="polite"></div>'
            '<div id="ftModalBackdrop" class="ft-modal-backdrop" style="display:none">'
            '  <div class="ft-modal-box" id="ftModalBox" role="dialog" aria-modal="true">'
            '    <button class="ft-modal-close" id="ftModalClose" aria-label="Close modal">×</button>'
            '    <div id="ftModalContent"></div>'
            '  </div>'
            '</div>') + sprite()

TASKBAR = [("dashboard.html", "Home", "chart"),
           ("exchange.html", "Exchange", "candle"),
           ("fanplay.html", "FanPlay", "ball"),
           ("leaderboard.html", "Leaderboard", "rank"),
           ("account.html", "Account", "user")]

# Every app page lights up one of the five tabs.
TAB_OF = {"dashboard.html": "dashboard.html", "clubs.html": "dashboard.html",
          "onboarding.html": "dashboard.html",
          "exchange.html": "exchange.html", "asset.html": "exchange.html",
          "trade.html": "exchange.html", "club-builder.html": "dashboard.html",
          "divisions.html": "leaderboard.html",
          "fanplay.html": "fanplay.html",
          "leaderboard.html": "leaderboard.html",
          "account.html": "account.html", "ftr.html": "account.html",
          "portfolio.html": "account.html", "notifications.html": "account.html",
          "settings.html": "account.html"}


def taskbar(current=""):
    """Floating five-item bar — the current tab expands into a filled pill."""
    tab = TAB_OF.get(current, "")
    out = []
    for href, label, icon in TASKBAR:
        on = href == tab
        out.append('<a href="%s"%s%s aria-label="%s">%s<span>%s</span></a>'
                   % (href, ' class="on"' if on else "", ' aria-current="page"' if on else "",
                      label, ic(icon, "ic"), label))
    return '<nav class="taskbar" aria-label="Primary">%s</nav>' % "".join(out)


def nav(current="", app=False):
    """Floating top bar. app=True pairs it with the taskbar and drops every page link."""
    if app:
        top = ('<nav class="nav-island topbar"><a class="logo" href="index.html">%s Fantrade</a>'
               '<div style="display:flex;align-items:center;gap:10px;margin-left:auto">'
               '<a class="nav-wallet" id="navWalletBtn" href="ftr.html" title="Open your $FTR wallet">'
               '<span class="pulse"></span><span class="num" id="navBal">128,450 $FTR</span></a>'
               '<a class="bell" id="navBell" href="notifications.html" aria-label="Notifications">%s'
               '<span class="dot" id="navDot" hidden></span></a>'
               '</div></nav>') % (ic("ball", "ic"), ic("pulse", "ic"))
        return top + taskbar(current)

    links = "".join('<a href="%s"%s>%s</a>' % (h, ' class="on"' if h == current else '', l)
                    for h, l in MARKET_NAV)
    over = "".join('<a href="%s" data-close>%s</a>' % (h, l) for h, l in MARKET_NAV)
    right = ('<a class="btn btn-glass btn-sm" href="signin.html">Sign in<span class="cap">%s</span></a>'
             '<a class="btn btn-lime btn-sm" href="signup.html">Get started<span class="cap">%s</span></a>'
             % (ic("arrow", "ic"), ic("arrow", "ic")))
    foot = ('<a class="btn btn-glass" href="signin.html" data-close>Sign in<span class="cap">%s</span></a>'
            '<a class="btn btn-lime" href="signup.html" data-close>Get started<span class="cap">%s</span></a>'
            % (ic("arrow", "ic"), ic("arrow", "ic")))
    return ('<nav class="nav-island"><a class="logo" href="index.html">%s Fantrade</a>'
            '<div class="nav-links">%s</div><div style="display:flex;align-items:center;gap:10px">%s</div>'
            '<button class="burger" id="burger" aria-label="Open menu" aria-expanded="false"><i></i><i></i>'
            '</button></nav><div class="overlay" id="overlay">%s%s</div>'
            ) % (ic("ball", "ic"), links, right, over, foot)


def nav_min(back="index.html", label="Back to Fantrade"):
    """Stripped nav for auth screens — logo and one way out."""
    return ('<div class="nav-min"><a class="logo" href="index.html">%s Fantrade</a>'
            '<a class="back" href="%s">%s<span>%s</span></a></div>'
            % (ic("ball", "ic"), back, ic("arrow", "ic"), label))

def footer():
    return ('<footer><div class="wrap"><div class="foot">'
            '<div class="col brandcol"><a class="logo" href="index.html">%s Fantrade</a>'
            '<p>A football ownership economy. Own players and coaches, build your Dream Club, play every matchday.</p></div>'
            '<div class="col"><b>Platform</b><a href="dashboard.html">Home</a><a href="exchange.html">Exchange</a>'
            '<a href="fanplay.html">FanPlay</a><a href="leaderboard.html">Leaderboard</a></div>'
            '<div class="col"><b>Your account</b><a href="account.html">Account</a><a href="ftr.html">$FTR wallet</a>'
            '<a href="portfolio.html">Portfolio &amp; ledger</a><a href="settings.html">Settings</a></div>'
            '<div class="col"><b>Learn</b><a href="how-it-works.html">How it works</a><a href="fanplay.html#rules">Scoring rules</a>'
            '<a href="fanplay.html#tiers">Market tiers</a><a href="clubs.html#chem">Club chemistry</a></div>'
            '<div class="col"><b>Company</b><a href="signup.html">Create account</a><a href="signin.html">Sign in</a>'
            '<a href="#">Press</a><a href="#">Contact</a></div>'
            '</div><div class="legal"><span>© 2026 Fantrade. Prototype interface — figures shown are illustrative.</span>'
            '<span>Terms · Privacy · Responsible play</span></div></div></footer>') % ic("ball", "ic")

JS_CHART = r"""
// Shared lime area chart. Draws into `el` from a plain array of numbers.
function drawArea(el, vals, up){
  if(!el || !vals || vals.length < 2) return;
  up = up !== false;
  var w = 600, h = 168, pad = 10;
  var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), rng = (hi - lo) || 1;
  var id = 'g' + Math.random().toString(36).slice(2, 8);
  var col = up ? '#C4F82A' : '#FF5E5E';
  var pts = vals.map(function(v, i){
    var x = i * (w / (vals.length - 1));
    var y = h - ((v - lo) / rng) * (h - pad * 2) - pad;
    return x.toFixed(1) + ',' + y.toFixed(1);
  });
  var last = pts[pts.length - 1].split(',');
  el.innerHTML = '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">'
    + '<defs><linearGradient id="' + id + '" x1="0" y1="0" x2="0" y2="1">'
    + '<stop offset="0%" stop-color="' + col + '" stop-opacity=".30"/>'
    + '<stop offset="100%" stop-color="' + col + '" stop-opacity="0"/></linearGradient></defs>'
    + '<polygon points="0,' + h + ' ' + pts.join(' ') + ' ' + w + ',' + h + '" fill="url(#' + id + ')"/>'
    + '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + col + '" stroke-width="1.9" '
    + 'stroke-linejoin="round" stroke-linecap="round"/>'
    + '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="3.4" fill="' + col + '"/>'
    + '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="8" fill="' + col + '" opacity=".22"/>'
    + '</svg>';
}
// Deterministic-ish series generator for the range pills.
function series(n, drift, vol, seed){
  var out = [], v = 100, s = seed || 7;
  for(var i = 0; i < n; i++){
    s = (s * 9301 + 49297) % 233280;
    v += drift + ((s / 233280) - 0.5) * vol;
    out.push(Math.max(4, v));
  }
  return out;
}
"""

JS_SHELL = JS_CHART + r"""
var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var io = new IntersectionObserver(function(es){
  es.forEach(function(e){
    if(e.isIntersecting){ var el=e.target;
      setTimeout(function(){ el.classList.add('in'); }, reduce?0:parseInt(el.dataset.delay||0,10));
      io.unobserve(el); }
  });
},{rootMargin:'0px 0px -12% 0px',threshold:.12});
document.querySelectorAll('[data-reveal]').forEach(function(el,i){ el.dataset.delay=(i%4)*80; io.observe(el); });

var burger=document.getElementById('burger');
if(burger){
  burger.addEventListener('click',function(){
    var open=document.body.classList.toggle('menu-open');
    burger.setAttribute('aria-expanded',open?'true':'false');
    burger.setAttribute('aria-label',open?'Close menu':'Open menu');
  });
  document.querySelectorAll('[data-close]').forEach(function(a){
    a.addEventListener('click',function(){ document.body.classList.remove('menu-open');
      burger.setAttribute('aria-expanded','false'); });
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&document.body.classList.contains('menu-open')){
      document.body.classList.remove('menu-open'); burger.setAttribute('aria-expanded','false'); burger.focus(); }
  });
}
function spark(up,w,h){
  var pts=[],x=0,y=h*0.6,n=16,step=w/(n-1);
  for(var i=0;i<n;i++){ y+=(Math.random()-(up?.6:.4))*(h*.28); y=Math.max(h*.15,Math.min(h*.85,y));
    pts.push(x.toFixed(1)+','+y.toFixed(1)); x+=step; }
  return "<svg class='spark' viewBox='0 0 "+w+" "+h+"' preserveAspectRatio='none'><polyline points='"+pts.join(' ')+
    "' fill='none' stroke='"+(up?'#C4F82A':'#FF5E5E')+"' stroke-width='1.2' stroke-linejoin='round' opacity='.9'/></svg>";
}
var ASSETS=[
 {t:'$Saka',n:'Bukayo Saka',p:48.20,d:6.4,c:false,cap:'482.0M',h:37.1},
 {t:'$Haaland',n:'Erling Haaland',p:71.40,d:-1.8,c:false,cap:'714.0M',h:52.4},
 {t:'$Bruno',n:'Bruno Fernandes',p:39.75,d:2.1,c:false,cap:'397.5M',h:41.8},
 {t:'$Vinicius',n:'Vinícius Júnior',p:63.10,d:0.7,c:false,cap:'631.0M',h:48.2},
 {t:'$Bellingham',n:'Jude Bellingham',p:58.90,d:3.3,c:false,cap:'589.0M',h:44.6},
 {t:'$Musiala',n:'Jamal Musiala',p:46.70,d:5.1,c:false,cap:'467.0M',h:33.9},
 {t:'$Pedri',n:'Pedri González',p:41.15,d:-0.9,c:false,cap:'411.5M',h:29.7},
 {t:'$Saliba',n:'William Saliba',p:33.80,d:2.7,c:false,cap:'338.0M',h:26.3},
 {t:'$Jackson',n:'Nicolas Jackson',p:14.85,d:11.2,c:false,cap:'148.5M',h:18.4},
 {t:'$Arteta',n:'Mikel Arteta',p:22.05,d:4.9,c:true,cap:'220.5M',h:24.1},
 {t:'$Pep',n:'Pep Guardiola',p:29.60,d:-0.4,c:true,cap:'296.0M',h:31.5},
 {t:'$Maresca',n:'Enzo Maresca',p:18.30,d:1.2,c:true,cap:'183.0M',h:16.8}
];
function liveTicks(sel){
  if(reduce) return;
  setInterval(function(){
    var rows=document.querySelectorAll(sel);
    if(!rows.length) return;
    var r=rows[Math.floor(Math.random()*rows.length)];
    var i=+r.dataset.i, a=ASSETS[i]; if(!a) return;
    var move=(Math.random()-.48)*(a.p*.0045);
    a.p=Math.max(1,a.p+move); a.d+=move/a.p*100;
    var px=r.querySelector('[data-px]'), dx=r.querySelector('[data-dx]');
    if(px){ px.textContent=a.p.toFixed(2); px.style.color=move>=0?'#C4F82A':'#FF5E5E';
      setTimeout(function(){ px.style.color=''; },900); }
    if(dx){ dx.textContent=(a.d>=0?'+':'')+a.d.toFixed(1)+'%';
      dx.classList.remove('up','down'); dx.classList.add(a.d>=0?'up':'down'); }
  },1500);
}

// Global Fantrade State Management
var FT = (function(){
  var STORAGE_KEY = 'fantrade_v1_state';
  var defaultState = {
    auth: {
      signedIn: true,
      email: "alex.morgan@fantrade.app",
      onboarded: true,
      verified: true,
      since: "Sep 2026"
    },
    user: {
      name: "Alex Morgan",
      handle: "@alex_trader",
      joined: "Matchday 01 · Sep 2026",
      rank: 124,
      region: "United Kingdom",
      league: "Premier League"
    },
    favourites: ["m-ars"],
    prefs: {
      settleAlerts: true,
      orderFills: true,
      clubAlerts: true,
      priceMoves: false,
      digest: true,
      marketing: false,
      twoFactor: false,
      autoSub: true,
      stakeCap: 5000
    },
    notifications: [
      { id:"n-1", kind:"settle", icon:"trophy", title:"Matchday 06 settled", read:false, day:"Today",
        msg:"Zero FC finished 18th of 1,420 clubs with 812 FP. Your Elite-tier stake returned at 2.48x.",
        time:"09:14 · 2h ago", amt:"+6,200 $FTR", tone:"up" },
      { id:"n-2", kind:"order", icon:"candle", title:"Buy order filled", read:false, day:"Today",
        msg:"10,000 $Saka filled at an average of 48.20 $FTR. Average cost basis moved to 31.40.",
        time:"08:02 · 3h ago", amt:"-483,928 $FTR", tone:"down" },
      { id:"n-3", kind:"club", icon:"whistle", title:"Teamsheet risk on Zero FC", read:false, day:"Today",
        msg:"W. Saliba is listed as a late fitness test. Auto-sub will field Gabriel if he is withdrawn.",
        time:"07:40 · 4h ago", amt:"", tone:"" },
      { id:"n-4", kind:"settle", icon:"coin", title:"Dividend distributed", read:true, day:"Yesterday",
        msg:"$Saka clean sheet and man-of-the-match distribution paid to all holders on the ledger.",
        time:"Yesterday · 22:10", amt:"+420 $FTR", tone:"up" },
      { id:"n-5", kind:"club", icon:"bolt", title:"Coach synergy unlocked", read:true, day:"Yesterday",
        msg:"$Arteta now matches your 4-3-3 shape. Club multiplier rose from 10.0% to 15.0%.",
        time:"Yesterday · 19:22", amt:"", tone:"" },
      { id:"n-6", kind:"order", icon:"swap", title:"Limit order expired", read:true, day:"Yesterday",
        msg:"Your limit buy for 2,000 $Pedri at 38.00 $FTR expired unfilled. Nothing was charged.",
        time:"Yesterday · 11:05", amt:"", tone:"" },
      { id:"n-7", kind:"system", icon:"shield", title:"New sign-in on Chrome, London", read:true, day:"Sep 12",
        msg:"If this was not you, change your password and revoke the session from Settings → Security.",
        time:"Sep 12 · 08:30", amt:"", tone:"" },
      { id:"n-8", kind:"settle", icon:"rank", title:"Promoted to Apex division", read:true, day:"Sep 11",
        msg:"Zero FC crossed the top-150 cutoff and now competes for 50% of the weekly prize pool.",
        time:"Sep 11 · 23:59", amt:"", tone:"" }
    ],
    wallet: {
      balance: 128450,
      locked: 5000,
      seasonEarned: 19640,
      gbpRate: 12.40
    },
    holdings: {
      '$Saka': { n: 'Bukayo Saka', shares: 10000, avg: 31.40, p: 48.20, c: false, inClub: 'RW' },
      '$Bruno': { n: 'Bruno Fernandes', shares: 5000, avg: 38.00, p: 39.75, c: false, inClub: 'CAM' },
      '$Haaland': { n: 'Erling Haaland', shares: 3000, avg: 68.50, p: 71.40, c: false, inClub: 'ST' },
      '$Arteta': { n: 'Mikel Arteta', shares: 1000, avg: 20.50, p: 22.05, c: true, inClub: 'COACH' }
    },
    club: {
      name: "Zero FC",
      stadium: "Emirates of the North",
      colors: ["#C4F82A", "#83b300"],
      colorName: "Lime",
      formation: "4-3-3",
      coach: "$Arteta",
      rank: 124,
      fp: 8420,
      boost: 15.0,
      value: 245800
    },
    fanplay: {
      activeEntries: [
        { id: "e-1", mode: "Dream Club", target: "Zero FC", tier: "Elite", mult: 2.0, stake: 2500, projectedFP: 230, status: "Active in MD 07" },
        { id: "e-2", mode: "Individual", target: "$Saka", tier: "PRO", mult: 1.4, stake: 2500, projectedFP: 140, status: "Active in MD 07" }
      ]
    },
    transactions: [
      { type: "BUY", asset: "$Saka", shares: 10000, price: 48.20, total: 483928, time: "Today, 14:22" },
      { type: "STAKE", asset: "FanPlay MD 07", shares: 1, price: 2500, total: 2500, time: "Yesterday, 19:10" },
      { type: "PAYOUT", asset: "Matchday 06 Settle", shares: 1, price: 6200, total: 6200, time: "Sep 08, 02:15" },
      { type: "CONVERT", asset: "GBP Deposit (£1,000)", shares: 1000, price: 12.40, total: 12338, time: "Sep 07, 11:45" }
    ]
  };

  function load(){
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      if(s) return Object.assign({}, defaultState, JSON.parse(s));
    } catch(e){}
    return JSON.parse(JSON.stringify(defaultState));
  }
  function save(s){
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    } catch(e){}
  }
  var state = load();

  return {
    getState: function(){ return state; },
    save: function(){ save(state); },
    initials: function(){
      return (state.user.name || 'Manager').trim().split(/\s+/).slice(0,2)
        .map(function(w){ return w.charAt(0).toUpperCase(); }).join('') || 'FT';
    },
    unread: function(){
      return (state.notifications || []).filter(function(n){ return !n.read; }).length;
    },
    holdingsValue: function(){
      return Object.keys(state.holdings).reduce(function(t,k){
        var h = state.holdings[k]; return t + h.shares * h.p;
      }, 0);
    },
    syncUI: function(){
      var bal = state.wallet.balance.toLocaleString('en-US') + ' $FTR';
      document.querySelectorAll('#navBal').forEach(function(el){ el.textContent = bal; });
      var ini = FT.initials();
      document.querySelectorAll('#navInitials').forEach(function(el){ el.textContent = ini; });
      document.querySelectorAll('#menuName').forEach(function(el){ el.textContent = state.user.name; });
      document.querySelectorAll('#menuHandle').forEach(function(el){ el.textContent = state.user.handle; });
      document.querySelectorAll('#menuRank').forEach(function(el){
        el.textContent = 'Apex division · rank #' + state.club.rank;
      });
      var n = FT.unread();
      document.querySelectorAll('#navDot').forEach(function(el){ el.hidden = n === 0; });
      document.querySelectorAll('[data-unread]').forEach(function(el){ el.textContent = n; });
      document.querySelectorAll('[data-bind]').forEach(function(el){
        var k = el.getAttribute('data-bind'), v;
        if(k === 'name') v = state.user.name;
        else if(k === 'first') v = (state.user.name || 'Manager').split(' ')[0];
        else if(k === 'handle') v = state.user.handle;
        else if(k === 'email') v = state.auth.email;
        else if(k === 'club') v = state.club.name;
        else if(k === 'formation') v = state.club.formation;
        else if(k === 'balance') v = state.wallet.balance.toLocaleString('en-US');
        else if(k === 'locked') v = state.wallet.locked.toLocaleString('en-US');
        else if(k === 'earned') v = state.wallet.seasonEarned.toLocaleString('en-US');
        else if(k === 'clubvalue') v = state.club.value.toLocaleString('en-US');
        else if(k === 'rank') v = '#' + state.club.rank;
        else if(k === 'fp') v = state.club.fp.toLocaleString('en-US');
        else if(k === 'boost') v = state.club.boost.toFixed(1) + '%';
        else if(k === 'assets') v = Math.round(FT.holdingsValue()).toLocaleString('en-US');
        else if(k === 'net') v = Math.round(FT.holdingsValue() + state.wallet.balance + state.wallet.locked).toLocaleString('en-US');
        if(v !== undefined) el.textContent = v;
      });
    },
    isAuthed: function(){ return !!(state.auth && state.auth.signedIn); },
    signIn: function(email, name){
      state.auth.signedIn = true;
      state.auth.email = email || state.auth.email;
      if(name) state.user.name = name;
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    signUp: function(data){
      state.auth.signedIn = true;
      state.auth.onboarded = false;
      state.auth.email = data.email;
      state.auth.since = 'Sep 2026';
      state.user.name = data.name;
      state.user.handle = '@' + (data.name || 'manager').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      state.user.region = data.region || state.user.region;
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    signOut: function(){
      state.auth.signedIn = false;
      save(state);
      window.location.href = 'index.html';
    },
    completeOnboarding: function(data){
      if(data.handle) state.user.handle = data.handle;
      if(data.region) state.user.region = data.region;
      if(data.league) state.user.league = data.league;
      if(data.clubName) state.club.name = data.clubName;
      if(data.formation) state.club.formation = data.formation;
      if(data.colors){ state.club.colors = data.colors; state.club.colorName = data.colorName; }
      state.auth.onboarded = true;
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    updateProfile: function(patch){
      Object.assign(state.user, patch || {});
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    setPref: function(key, val){
      state.prefs[key] = val; save(state);
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    isFav: function(id){ return (state.favourites || []).indexOf(id) > -1; },
    toggleFav: function(id){
      state.favourites = state.favourites || [];
      var i = state.favourites.indexOf(id);
      if(i > -1) state.favourites.splice(i, 1); else state.favourites.push(id);
      save(state);
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return i === -1;
    },
    readAll: function(){
      (state.notifications || []).forEach(function(n){ n.read = true; });
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    readOne: function(id){
      var n = (state.notifications || []).filter(function(x){ return x.id === id; })[0];
      if(n && !n.read){ n.read = true; save(state); FT.syncUI(); }
    },
    executeTrade: function(side, assetSymbol, assetName, shares, price, isCoach){
      var subtotal = shares * price;
      var fee = subtotal * 0.004;
      var total = Math.round(side === 'buy' ? subtotal + fee : subtotal - fee);

      if(side === 'buy'){
        if(state.wallet.balance < total){
          throw new Error("Insufficient $FTR balance (" + state.wallet.balance.toLocaleString('en-US') + " $FTR available, need " + total.toLocaleString('en-US') + " $FTR).");
        }
        state.wallet.balance -= total;
        if(!state.holdings[assetSymbol]){
          state.holdings[assetSymbol] = { n: assetName, shares: 0, avg: price, p: price, c: isCoach, inClub: isCoach ? 'COACH' : 'SUB' };
        }
        var cur = state.holdings[assetSymbol];
        var newTotal = cur.shares + shares;
        cur.avg = ((cur.shares * cur.avg) + (shares * price)) / newTotal;
        cur.shares = newTotal;
        cur.p = price;
      } else {
        var cur = state.holdings[assetSymbol];
        if(!cur || cur.shares < shares){
          throw new Error("You only hold " + (cur ? cur.shares.toLocaleString('en-US') : "0") + " shares of " + assetSymbol + ".");
        }
        state.wallet.balance += total;
        cur.shares -= shares;
        if(cur.shares <= 0){
          delete state.holdings[assetSymbol];
        }
      }

      state.transactions.unshift({
        type: side.toUpperCase(),
        asset: assetSymbol,
        shares: shares,
        price: price,
        total: total,
        time: "Just now"
      });

      save(state);
      FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return { total: total, remainingBalance: state.wallet.balance, shares: shares };
    },
    saveClub: function(clubData){
      Object.assign(state.club, clubData);
      save(state);
      FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    activateFanPlayEntry: function(entryData){
      var stake = entryData.stake || 2500;
      if(state.wallet.balance < stake){
        throw new Error("Insufficient $FTR balance. Need " + stake.toLocaleString('en-US') + " $FTR.");
      }
      state.wallet.balance -= stake;
      state.wallet.locked += stake;
      var newEntry = {
        id: "e-" + Date.now(),
        mode: entryData.mode,
        target: entryData.target,
        tier: entryData.tier,
        mult: entryData.mult,
        stake: stake,
        projectedFP: entryData.projectedFP,
        status: "Active in MD 07"
      };
      state.fanplay.activeEntries.unshift(newEntry);
      state.transactions.unshift({
        type: "STAKE",
        asset: "FanPlay MD 07 (" + entryData.tier + ")",
        shares: 1,
        price: stake,
        total: stake,
        time: "Just now"
      });
      save(state);
      FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return newEntry;
    },
    convertGbp: function(gbpAmount){
      var grossFtr = gbpAmount * state.wallet.gbpRate;
      var fee = grossFtr * 0.005;
      var netFtr = Math.round(grossFtr - fee);
      state.wallet.balance += netFtr;
      state.transactions.unshift({
        type: "CONVERT",
        asset: "GBP Deposit (£" + gbpAmount.toLocaleString('en-US') + ")",
        shares: gbpAmount,
        price: state.wallet.gbpRate,
        total: netFtr,
        time: "Just now"
      });
      save(state);
      FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return netFtr;
    },
    sendFtr: function(amount, dest, kind){
      if(amount <= 0) throw new Error("Enter an amount to send.");
      var fee = kind === 'withdraw' ? Math.max(50, Math.round(amount * 0.005)) : 0;
      if(state.wallet.balance < amount + fee){
        throw new Error("Insufficient $FTR. You have " + state.wallet.balance.toLocaleString('en-US')
          + " and this needs " + (amount + fee).toLocaleString('en-US') + ".");
      }
      state.wallet.balance -= (amount + fee);
      state.transactions.unshift({
        type: kind === 'withdraw' ? "WITHDRAW" : "SEND",
        asset: dest, shares: 1, price: amount, total: amount + fee, time: "Just now"
      });
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return { sent: amount, fee: fee, remaining: state.wallet.balance };
    },
    swapAssets: function(fromSym, toSym, shares, prices){
      var from = state.holdings[fromSym];
      if(!from) throw new Error("You do not hold any " + fromSym + ".");
      if(from.shares < shares) throw new Error("You hold " + from.shares.toLocaleString('en-US')
        + " " + fromSym + ", not " + shares.toLocaleString('en-US') + ".");
      var gross = shares * from.p, fee = gross * 0.004, net = gross - fee;
      var toPrice = prices[toSym];
      if(!toPrice) throw new Error("No market price for " + toSym + ".");
      var got = Math.floor(net / toPrice);
      if(got < 1) throw new Error("That is not enough to buy a whole share of " + toSym + ".");

      from.shares -= shares;
      if(from.shares <= 0) delete state.holdings[fromSym];
      if(!state.holdings[toSym]){
        state.holdings[toSym] = { n: prices[toSym + ':name'] || toSym, shares: 0, avg: toPrice,
          p: toPrice, c: !!prices[toSym + ':coach'], inClub: 'SUB' };
      }
      var to = state.holdings[toSym];
      to.avg = ((to.shares * to.avg) + (got * toPrice)) / (to.shares + got);
      to.shares += got;
      to.p = toPrice;
      state.wallet.balance += Math.round(net - got * toPrice);

      state.transactions.unshift({
        type: "SWAP", asset: fromSym + " → " + toSym, shares: shares,
        price: from.p, total: Math.round(gross), time: "Just now"
      });
      save(state); FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
      return { spent: shares, received: got, fee: Math.round(fee) };
    },
    depositFtr: function(amount){
      state.wallet.balance += amount;
      state.transactions.unshift({
        type: "DEPOSIT",
        asset: "Direct Deposit",
        shares: 1,
        price: amount,
        total: amount,
        time: "Just now"
      });
      save(state);
      FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    },
    resetState: function(){
      state = JSON.parse(JSON.stringify(defaultState));
      save(state);
      FT.syncUI();
      window.dispatchEvent(new CustomEvent('fantrade:statechange', { detail: state }));
    }
  };
})();

// Toast Notification
function showToast(msg, type){
  type = type || 'success';
  var cont = document.getElementById('ftToastContainer');
  if(!cont) return;
  var el = document.createElement('div');
  el.className = 'ft-toast ' + type;
  var icon = type==='success'
    ? '<svg class="t-icon" aria-hidden="true"><use href="#i-check"/></svg>'
    : (type==='error' ? '<svg class="t-icon" aria-hidden="true"><use href="#i-cross"/></svg>'
    : '<svg class="t-icon" aria-hidden="true"><use href="#i-coin"/></svg>');
  el.innerHTML = icon + '<span>' + msg + '</span>';
  cont.appendChild(el);
  requestAnimationFrame(function(){ el.classList.add('show'); });
  setTimeout(function(){
    el.classList.remove('show');
    setTimeout(function(){ el.remove(); }, 400);
  }, 3600);
}

// Universal Modal
function openModal(html){
  var bd = document.getElementById('ftModalBackdrop');
  var ct = document.getElementById('ftModalContent');
  if(!bd || !ct) return;
  ct.innerHTML = html;
  bd.style.display = 'flex';
  requestAnimationFrame(function(){ bd.classList.add('open'); });
}
function closeModal(){
  var bd = document.getElementById('ftModalBackdrop');
  if(!bd) return;
  bd.classList.remove('open');
  setTimeout(function(){ bd.style.display = 'none'; }, 260);
}
var mc = document.getElementById('ftModalClose');
if(mc) mc.addEventListener('click', closeModal);
var bd = document.getElementById('ftModalBackdrop');
if(bd) bd.addEventListener('click', function(e){ if(e.target === bd) closeModal(); });
document.addEventListener('keydown', function(e){
  var b = document.getElementById('ftModalBackdrop');
  if(e.key === 'Escape' && b && b.classList.contains('open')) closeModal();
});

// Global Account / Wallet Modal Handler
function showAccountModal(){
  var s = FT.getState();
  var holdingsList = Object.keys(s.holdings).map(function(k){
    var h = s.holdings[k];
    return '<div class="m-row"><span>' + k + ' (' + h.shares.toLocaleString('en-US') + ' sh)</span><b>' + (h.shares * h.avg).toLocaleString('en-US') + ' $FTR</b></div>';
  }).join('') || '<div style="color:var(--faint);font-size:12px;padding:6px 0">No player shares held yet. Visit the Exchange to buy.</div>';

  var html = '' +
    '<h3 class="ft-modal-title">Manager Account</h3>' +
    '<p class="ft-modal-desc">' + s.user.name + ' · <span style="color:var(--lime)">' + s.user.handle + '</span> · ' + s.user.joined + '</p>' +
    '<div class="ft-modal-card">' +
      '<div class="m-row"><span>Available Balance</span><b style="font-size:16px;color:var(--lime)">' + s.wallet.balance.toLocaleString('en-US') + ' $FTR</b></div>' +
      '<div class="m-row"><span>Locked in FanPlay Entries</span><b>' + s.wallet.locked.toLocaleString('en-US') + ' $FTR</b></div>' +
      '<div class="m-row"><span>Season Payouts</span><b>' + s.wallet.seasonEarned.toLocaleString('en-US') + ' $FTR</b></div>' +
      '<div class="m-row total"><span>Active Club</span><b>' + s.club.name + ' (' + s.club.formation + ')</b></div>' +
    '</div>' +
    '<div class="k-label" style="margin-top:16px">Your Portfolio</div>' +
    '<div class="ft-modal-card">' + holdingsList + '</div>' +
    '<div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap">' +
      '<button class="btn btn-lime" id="faucetBtn" type="button" style="flex:1;justify-content:center">+50,000 $FTR (Faucet)</button>' +
      '<button class="btn btn-glass" id="resetStateBtn" type="button" style="flex:1;justify-content:center">Reset Demo</button>' +
    '</div>';

  openModal(html);

  var fc = document.getElementById('faucetBtn');
  if(fc) fc.addEventListener('click', function(){
    FT.depositFtr(50000);
    showToast("+50,000 $FTR added to wallet!", "success");
    closeModal();
  });
  var rb = document.getElementById('resetStateBtn');
  if(rb) rb.addEventListener('click', function(){
    FT.resetState();
    showToast("Demo wallet and club reset to defaults.", "info");
    closeModal();
    setTimeout(function(){ location.reload(); }, 600);
  });
}

document.querySelectorAll('[data-acct-modal], #overlayAccountBtn').forEach(function(btn){
  btn.addEventListener('click', function(e){
    e.preventDefault();
    var m = document.getElementById('navMenu');
    if(m) m.classList.remove('open');
    showAccountModal();
  });
});

// Account dropdown
(function(){
  var trigger = document.getElementById('navAccountBtn');
  var menu = document.getElementById('navMenu');
  if(!trigger || !menu) return;
  function setOpen(open){
    menu.classList.toggle('open', open);
    trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  trigger.addEventListener('click', function(e){
    e.preventDefault(); e.stopPropagation();
    setOpen(!menu.classList.contains('open'));
  });
  document.addEventListener('click', function(e){
    if(menu.classList.contains('open') && !menu.contains(e.target) && e.target !== trigger) setOpen(false);
  });
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && menu.classList.contains('open')){ setOpen(false); trigger.focus(); }
  });
})();

document.querySelectorAll('[data-signout]').forEach(function(b){
  b.addEventListener('click', function(e){
    e.preventDefault();
    showToast('Signed out. See you at the next matchday.', 'info');
    setTimeout(function(){ FT.signOut(); }, 700);
  });
});

// Generic toggle switches — bound to FT.prefs by data-pref
document.querySelectorAll('.tgl[data-pref]').forEach(function(t){
  var key = t.getAttribute('data-pref');
  var on = !!FT.getState().prefs[key];
  t.setAttribute('aria-pressed', on ? 'true' : 'false');
  t.addEventListener('click', function(){
    var next = t.getAttribute('aria-pressed') !== 'true';
    t.setAttribute('aria-pressed', next ? 'true' : 'false');
    FT.setPref(key, next);
  });
});

FT.syncUI();
"""

