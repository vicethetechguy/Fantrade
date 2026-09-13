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
  .wrap{padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
  .nav-island{top:max(12px,env(safe-area-inset-top));left:12px;right:12px;transform:none;width:auto;max-width:none}
  body.menu-open{overflow:hidden}
  .overlay{padding:100px 22px 48px;overflow-y:auto;justify-content:flex-start}
  section{padding:88px 0}
  .phead{padding:126px 0 46px}
  .bento,.bento.halves{grid-template-columns:1fr;gap:12px}
  .bento .c6,.bento.halves .c6{grid-column:span 1}
  .bezel{padding:6px;--r-out:1.5rem;--r-in:calc(1.5rem - .375rem)}
  .btn{min-height:46px;padding:11px 11px 11px 22px}
  .tab{min-height:60px}.tabs{flex-direction:column}
  .markets{flex-wrap:nowrap;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px;
    margin-right:-22px;padding-right:22px;scrollbar-width:none}
  .markets::-webkit-scrollbar{display:none}
  .mkt{flex:0 0 auto;scroll-snap-align:start;min-height:44px;display:inline-flex;align-items:center}
  .mkt:hover{transform:none}
  .mhead,.mrow{grid-template-columns:1.6fr 1fr .8fr;gap:10px;padding:13px 16px}
  .mhead span:nth-child(n+4),.mrow>div:nth-child(n+4){display:none}
  .pitch{padding:24px 14px}
  .line-row{gap:6px;margin-bottom:8px}
  .chip{min-width:0;flex:0 1 104px;padding:8px 6px}
  .chip:hover{transform:none}.chip .nm{font-size:11px}
  .bench-row{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-bottom:8px;margin-right:-16px;padding-right:16px}
  .bench-row::-webkit-scrollbar{display:none}
  .chip.sm{flex:0 0 auto;min-width:94px}
  .own-alert{flex-direction:column;align-items:flex-start}.own-alert .btn{margin-left:0;width:100%;justify-content:space-between}
  .statbar div{width:100%}
  .foot{gap:26px}.foot .col{min-width:calc(50% - 13px)}.brandcol{min-width:100%;margin-right:0}
  .legal{flex-direction:column;gap:10px}
  footer{padding-bottom:calc(56px + env(safe-area-inset-bottom))}
}
@media (max-width:560px){
  h2{font-size:clamp(28px,8.6vw,42px)}
  .t-nm{display:none}
  .pitch-head{flex-wrap:wrap;gap:12px}
  .pitch-head .coach{margin-left:0;width:100%;border-top:1px solid rgba(255,255,255,.07);padding-top:12px}
  .mini-grid{grid-template-columns:1fr 1fr}
  .value-big{font-size:32px}
}
@media (max-width:400px){
  .wrap{padding-left:14px;padding-right:14px}
  .chip{flex:0 1 88px;padding:7px 5px}.chip .nm{font-size:10px}
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
            '<div class="grain"></div>') + sprite()

def nav(active=""):
    links = "".join('<a href="%s"%s>%s</a>' % (h, ' class="on"' if l == active else '', l) for h, l in NAVITEMS)
    over = "".join('<a href="%s" data-close>%s</a>' % (h, l) for h, l in NAVITEMS)
    cta = ('<a class="btn btn-lime btn-sm" href="#">Create account<span class="cap">%s</span></a>' % ic("arrow", "ic"))
    return ('<nav class="nav-island"><a class="logo" href="index.html">%s Fantrade</a>'
            '<div class="nav-links">%s</div>%s'
            '<button class="burger" id="burger" aria-label="Open menu" aria-expanded="false"><i></i><i></i></button></nav>'
            '<div class="overlay" id="overlay">%s<a class="btn btn-lime" href="#" data-close>Create account'
            '<span class="cap">%s</span></a></div>') % (ic("ball", "ic"), links, cta, over, ic("arrow", "ic"))

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
"""
