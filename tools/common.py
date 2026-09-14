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
  padding:0 32px;gap:6px;opacity:0;pointer-events:none;transition:opacity .7s var(--ease)}
body.menu-open .overlay{opacity:1;pointer-events:auto}
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
  .bento,.bento.halves{grid-template-columns:1fr;gap:12px;width:100%;min-width:0}
  .bento .c6,.bento.halves .c6{grid-column:span 1}
  .bezel{padding:6px;--r-out:1.4rem;--r-in:calc(1.4rem - .375rem);max-width:100%;min-width:0;box-sizing:border-box}
  .bezel>.core{max-width:100%;min-width:0;box-sizing:border-box}
  .pad{padding:26px 20px}.pad-sm{padding:20px 16px}
  .btn{min-height:46px;padding:11px 11px 11px 20px;max-width:100%}

  /* Forms & controls */
  .field{padding:12px 14px;border-radius:14px;margin-bottom:8px}
  .field label{font-size:9px}
  .field input{font-size:16px!important;width:65%}
  .quick{gap:6px;margin:10px 0 16px}
  .quick button{min-width:52px;padding:8px 0;font-size:10.5px}

  /* Market Table on Exchange */
  .rail .searchbox{width:100%;flex:1 1 100%;min-width:100%;order:-1;padding:8px 14px}
  .rail .seg{width:100%;justify-content:space-between;padding:4px}
  .rail .seg button{flex:1;justify-content:center;padding:8px 10px;font-size:10px}
  .mhead,.mrow{grid-template-columns:1.5fr 1fr 68px;gap:8px;padding:12px 14px}
  .mhead span:nth-child(3),.mhead span:nth-child(4),.mhead span:nth-child(5){display:none}
  .mrow>div:nth-child(3),.mrow>div:nth-child(4),.mrow>div:nth-child(5){display:none}
  .mhead span:nth-child(6),.mrow>div:nth-child(6){display:block}
  .tradebtn{padding:6px 0;font-size:9.5px;width:100%;border-radius:999px}
  .brow{grid-template-columns:1.5fr 1fr .8fr;padding:12px 14px}
  .bhead span:last-child,.brow>div:last-child{display:none}

  /* Pitch & Squad Builder */
  .pitch{padding:20px 10px}
  .pitch-head{flex-wrap:wrap;gap:10px;margin-bottom:20px}
  .pitch-head .name{font-size:18px}
  .pitch-head .coach{margin-left:0;width:100%;border-top:1px solid rgba(255,255,255,.07);padding-top:10px}
  .line-row{gap:5px;margin-bottom:7px}
  .chip{min-width:0;flex:1 1 66px;max-width:82px;padding:7px 3px;border-radius:10px}
  .chip:hover{transform:none}
  .chip .pos{font-size:7.5px;letter-spacing:.06em}
  .chip .nm{font-size:10px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .chip.cap .arm{font-size:7px;gap:2px}
  .chip.cap .arm .ic{width:8px;height:8px}
  .bench{margin-top:18px;padding-top:14px}
  .bench-row{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding-bottom:6px;margin-right:-10px;padding-right:10px}
  .bench-row::-webkit-scrollbar{display:none}
  .chip.sm{flex:0 0 auto;min-width:80px;padding:6px 8px}
  .stepper{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding-bottom:6px;margin-bottom:16px}
  .stepper::-webkit-scrollbar{display:none}
  .stepper button{flex:0 0 auto;padding:8px 12px;font-size:9.5px}
  .forms{gap:6px}
  .forms button{min-width:68px;padding:11px 0;font-size:13px;border-radius:12px}
  .swatches{gap:10px}
  .sw{width:36px;height:36px;border-radius:10px}

  /* FanPlay components */
  .tabs{flex-direction:row;gap:6px;padding:6px;border-radius:16px}
  .tab{flex:1;padding:10px 8px;min-height:48px;border-radius:12px;gap:8px;justify-content:center}
  .tab b{font-size:12px;margin-bottom:0}
  .tab span{display:none}
  .tab .ibox{width:26px;height:26px;border-radius:8px}
  .fp-sel{padding:14px;border-radius:16px;margin-bottom:18px}
  .fp-sel .nm{font-size:16px}
  .fp-sel .sub{font-size:8.5px}
  .markets{flex-wrap:nowrap;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px;
    margin-right:-20px;padding-right:20px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .markets::-webkit-scrollbar{display:none}
  .mkt{flex:0 0 auto;scroll-snap-align:start;min-height:40px;padding:8px 14px;font-size:10.5px}
  .mkt:hover{transform:none}
  .out{padding:20px 14px;border-radius:16px;margin-top:16px}
  .out .v{font-size:38px;margin-top:8px}
  .countdown{gap:6px}
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

NAVITEMS = [("exchange.html", "Exchange"), ("clubs.html", "Dream Clubs"),
            ("fanplay.html", "FanPlay"), ("ftr.html", "$FTR"),
            ("how-it-works.html", "How it works")]

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

def nav(active=""):
    links = "".join('<a href="%s"%s>%s</a>' % (h, ' class="on"' if l == active else '', l) for h, l in NAVITEMS)
    over = "".join('<a href="%s" data-close>%s</a>' % (h, l) for h, l in NAVITEMS)
    cta = ('<div class="nav-wallet" id="navWalletBtn" role="button" tabindex="0" title="Click to open Wallet & Account">'
           '<span class="pulse"></span><span class="num" id="navBal">128,450 $FTR</span></div>'
           '<button class="btn btn-lime btn-sm" id="navAccountBtn" type="button">Account<span class="cap">%s</span></button>' % ic("arrow", "ic"))
    return ('<nav class="nav-island"><a class="logo" href="index.html">%s Fantrade</a>'
            '<div class="nav-links">%s</div><div style="display:flex;align-items:center;gap:10px">%s</div>'
            '<button class="burger" id="burger" aria-label="Open menu" aria-expanded="false"><i></i><i></i></button></nav>'
            '<div class="overlay" id="overlay">%s<button class="btn btn-lime" id="overlayAccountBtn" data-close type="button">Account'
            '<span class="cap">%s</span></button></div>') % (ic("ball", "ic"), links, cta, over, ic("arrow", "ic"))

def footer():
    return ('<footer><div class="wrap"><div class="foot">'
            '<div class="col brandcol"><a class="logo" href="index.html">%s Fantrade</a>'
            '<p>A football ownership economy. Own players and coaches, build your Dream Club, play every matchday.</p></div>'
            '<div class="col"><b>Platform</b><a href="exchange.html">Exchange</a><a href="clubs.html">Dream Clubs</a>'
            '<a href="fanplay.html">FanPlay</a><a href="ftr.html">$FTR</a></div>'
            '<div class="col"><b>Learn</b><a href="how-it-works.html">How it works</a><a href="fanplay.html#rules">Scoring rules</a>'
            '<a href="fanplay.html#tiers">Market tiers</a><a href="clubs.html#chem">Club chemistry</a></div>'
            '<div class="col"><b>Company</b><a href="#">About</a><a href="#">Careers</a><a href="#">Press</a><a href="#">Contact</a></div>'
            '</div><div class="legal"><span>© 2026 Fantrade. Prototype interface — figures shown are illustrative.</span>'
            '<span>Terms · Privacy · Responsible play</span></div></div></footer>') % ic("ball", "ic")

JS_SHELL = r"""
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
    if(dx){ dx.textContent=(a.d>=0?'+':'')+a.d.toFixed(1)+'%'; dx.className='tick '+(a.d>=0?'up':'down'); }
  },1500);
}

// Global Fantrade State Management
var FT = (function(){
  var STORAGE_KEY = 'fantrade_v1_state';
  var defaultState = {
    user: {
      name: "Alex Morgan",
      handle: "@alex_trader",
      joined: "Matchday 01 · Sep 2026",
      rank: 124
    },
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
    syncUI: function(){
      document.querySelectorAll('#navBal').forEach(function(el){
        el.textContent = state.wallet.balance.toLocaleString('en-US') + ' $FTR';
      });
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

document.querySelectorAll('#navAccountBtn, #overlayAccountBtn, #navWalletBtn').forEach(function(btn){
  btn.addEventListener('click', function(e){
    e.preventDefault();
    showAccountModal();
  });
});

FT.syncUI();
"""

