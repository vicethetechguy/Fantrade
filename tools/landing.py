"""Standalone Fomo-inspired marketing page, isolated from the in-app styles.

Reference assets are recorded in assets/landing/sources.json. Product visuals
use Fantrade content and local player portraits instead of crypto screenshots.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSS = r"""
:root{
  color-scheme:dark;
  --bg:#050505;
  --card:#0A0B0C;
  --card-hover:#121417;
  --text:#F4F6F1;
  --muted:#8B918A;
  --accent:#1800ad;
  --accent-hover:#3311cc;
  --accent-ink:#fff;
  --amber:#FF6A1F;
  --red:#FF5E5E;
  --line:rgba(255,255,255,.08);
  --line-light:rgba(255,255,255,.14);
  --glow:rgba(24,0,173,.18);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:32px}
/* Base & Typography */
html,body{overflow-x:hidden;width:100%}
body{
  margin:0;background:var(--bg);color:var(--text);
  font-family:Montserrat,system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;font-size:16px;line-height:1.5;
}
a{color:inherit;text-decoration:none}
button{font:inherit}
img{max-width:100%;display:block}
h1,h2,h3,.brand,.wordmark,.screen-brand{
  font-family:Archivo,sans-serif;
  font-variation-settings:'wdth' 120,'wght' 850;
  text-transform:uppercase;
  line-height:1.02;
  letter-spacing:-.018em;
  margin:0;
}
p{margin:0}
button,a{-webkit-tap-highlight-color:transparent}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:4px}
.skip{position:fixed;top:-80px;left:16px;z-index:99;background:var(--accent);color:var(--accent-ink);font-weight:700;padding:12px 18px;border-radius:8px;transition:top .2s}
.skip:focus{top:12px}

.landing{position:relative;overflow-x:hidden;width:100%;background:radial-gradient(ellipse 80% 50% at 50% -20%,rgba(24,0,173,.06),transparent 70%),var(--bg)}
.space-bg{position:absolute;inset:0 0 auto;width:100%;height:auto;z-index:0;pointer-events:none;opacity:.35;mix-blend-mode:screen}
.bg-deco{position:absolute;pointer-events:none;user-select:none;z-index:0}
.bg-deco img{width:100%;height:auto;display:block}
.bg-deco-hero{top:20px;left:50%;transform:translateX(-50%);width:min(860px,94vw);opacity:.10;filter:drop-shadow(0 0 50px rgba(24,0,173,.35))}
.bg-deco-features{top:40px;right:-120px;width:min(560px,60vw);opacity:.07;transform:rotate(-22deg);filter:drop-shadow(0 0 40px rgba(24,0,173,.25))}
.masthead{position:absolute;z-index:100;left:0;right:0;top:0;display:flex;justify-content:space-between;align-items:center;padding:24px 36px;gap:24px;max-width:1440px;margin:0 auto}
.brand{font-size:28px;letter-spacing:-.02em;color:#fff;display:inline-flex;align-items:center;gap:10px;text-decoration:none}
.brand-mark{width:30px;height:30px;object-fit:contain;flex-shrink:0;display:block}
.brand-dot{color:var(--accent)}
.nav-right{display:flex;gap:12px;align-items:center}
.nav-link{font-size:14px;font-weight:500;padding:8px 16px;color:#c0c4be;border-radius:999px;transition:color .2s,background .2s}
.nav-link:hover{color:#fff;background:rgba(255,255,255,.05)}
.nav-login{
  background:rgba(255,255,255,.08);
  backdrop-filter:blur(24px) saturate(190%);-webkit-backdrop-filter:blur(24px) saturate(190%);
  border:1px solid rgba(255,255,255,.18);
  box-shadow:inset 0 1px 1.5px rgba(255,255,255,.32), 0 4px 16px rgba(0,0,0,.25);
  border-radius:999px;padding:9px 24px;font-size:14px;font-weight:600;color:#fff;
  transition:all .25s cubic-bezier(.16,1,.3,1);
}
.nav-login:hover{
  background:rgba(255,255,255,.16);
  border-color:rgba(255,255,255,.35);
  box-shadow:inset 0 1px 2px rgba(255,255,255,.45), 0 8px 24px rgba(0,0,0,.35);
  transform:translateY(-1px);color:#fff;
}
.menu-toggle{
  display:none;border:none;background:transparent;color:var(--text);
  width:48px;height:48px;align-items:center;justify-content:center;
  cursor:pointer;padding:0;transition:transform .2s,color .2s;
  -webkit-tap-highlight-color:transparent;
}
.menu-toggle:hover{color:#fff;transform:scale(1.06)}
.menu-toggle:focus-visible{outline:none}
.menu-toggle svg{width:32px;height:32px;display:block}
.menu-toggle[aria-expanded="true"] .icon-bars{display:none}
.menu-toggle[aria-expanded="true"] .icon-close{display:block}
.menu-toggle[aria-expanded="false"] .icon-bars{display:block}
.menu-toggle[aria-expanded="false"] .icon-close{display:none}

.mobile-menu{
  display:none;position:fixed;inset:0;width:100vw;height:100vh;height:100dvh;
  z-index:90;background:rgba(5,5,5,.96);
  backdrop-filter:blur(36px);-webkit-backdrop-filter:blur(36px);
  padding:max(88px, calc(72px + env(safe-area-inset-top))) 32px 40px;
  flex-direction:column;justify-content:flex-start;
  align-items:flex-start;text-align:left;overflow-y:auto;
  box-shadow:0 30px 100px rgba(0,0,0,.95), inset 0 0 80px rgba(24,0,173,.15);
}
.mobile-menu.open{display:flex;animation:menu-fade-in .3s ease-out forwards}
.mobile-menu-inner{width:100%;max-width:440px;display:flex;flex-direction:column;gap:clamp(14px,2.8vh,22px);margin-top:10px}
.mobile-menu a{
  font-family:Archivo,sans-serif;font-size:clamp(26px,7vw,38px);
  font-variation-settings:'wdth' 120,'wght' 850;text-transform:none;
  line-height:1.08;letter-spacing:-.02em;color:#fff;text-decoration:none;
  padding:6px 0;display:flex;align-items:center;justify-content:space-between;
  text-shadow:0 4px 24px rgba(0,0,0,.9), 0 0 40px rgba(24,0,173,.25);
  opacity:0;transform:translateX(-30px);
  transition:transform .2s, color .2s, text-shadow .2s;
}
.mobile-menu.open a{animation:menu-slide-in .4s cubic-bezier(.16,1,.3,1) forwards}
.mobile-menu.open a:nth-child(1){animation-delay:.05s}
.mobile-menu.open a:nth-child(2){animation-delay:.10s}
.mobile-menu.open a:nth-child(3){animation-delay:.15s}
.mobile-menu.open a:nth-child(4){animation-delay:.20s}
.mobile-menu.open a:nth-child(5){animation-delay:.25s}
.mobile-menu a:hover,.mobile-menu a:active{
  color:var(--accent);transform:translateX(10px);
  text-shadow:0 4px 30px rgba(24,0,173,.6), 0 0 60px rgba(24,0,173,.4);
}
.mobile-menu a.menu-highlight{color:var(--accent);margin-top:12px}
.mobile-menu a.menu-highlight .arrow{font-size:28px;transition:transform .2s}
.mobile-menu a.menu-highlight:hover .arrow{transform:translateX(8px)}

@keyframes menu-fade-in{from{opacity:0}to{opacity:1}}
@keyframes menu-slide-in{from{opacity:0;transform:translateX(-30px)}to{opacity:1;transform:translateX(0)}}

.hero{position:relative;text-align:center;padding:140px 24px 0}
.wordmark{font-size:clamp(34px,11vw,180px);letter-spacing:-.03em;line-height:.85;color:rgba(255,255,255,.04);user-select:none;margin-bottom:-10px;width:100%;text-align:center;overflow:hidden;white-space:nowrap}
.hero h1{font-size:clamp(28px,5.5vw,56px);margin:0 0 14px;letter-spacing:-.02em}
.hero h1 span{color:var(--accent)}
.hero-copy{color:var(--muted);font-size:clamp(15px,2vw,20px);line-height:1.55;max-width:680px;margin:0 auto}

.actions{display:flex;justify-content:center;align-items:center;gap:14px;margin-top:32px;position:relative;z-index:2;flex-wrap:wrap}
.action{
  display:inline-flex;align-items:center;justify-content:center;gap:10px;
  min-height:52px;min-width:190px;padding:14px 30px;border-radius:999px;
  font-size:15px;font-weight:700;letter-spacing:.02em;transition:all .25s cubic-bezier(.16,1,.3,1);
  background:rgba(255,255,255,.08);
  backdrop-filter:blur(24px) saturate(190%);-webkit-backdrop-filter:blur(24px) saturate(190%);
  border:1px solid rgba(255,255,255,.18);
  box-shadow:inset 0 1px 1.5px rgba(255,255,255,.28), 0 8px 24px rgba(0,0,0,.3);
  color:#fff;
}
.action.primary{
  background:var(--accent);color:var(--accent-ink);border-color:var(--accent);
  box-shadow:0 8px 24px rgba(24,0,173,.22);backdrop-filter:none;-webkit-backdrop-filter:none;
}
.action.primary:hover{background:var(--accent-hover);transform:translateY(-2px);box-shadow:0 12px 32px rgba(24,0,173,.35)}
.action:not(.primary):hover{
  background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.35);
  box-shadow:inset 0 1px 2px rgba(255,255,255,.45), 0 12px 32px rgba(0,0,0,.4);
  transform:translateY(-2px);color:#fff;
}
.action img{width:16px;height:16px}
/* Explore FanPlay: a premium dark elevated panel — deep charcoal, polished, floating. */
.action.action-premium{
  width:280px;max-width:100%;height:72px;min-height:72px;padding:0 28px;border-radius:15px;
  border:1px solid rgba(255,255,255,.08);
  background:radial-gradient(120% 90% at 50% 0%,rgba(255,255,255,.06),rgba(255,255,255,0) 62%),linear-gradient(180deg,#312d39 0%,#292631 52%,#221f29 100%);
  backdrop-filter:none;-webkit-backdrop-filter:none;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 28px 56px -14px rgba(0,0,0,.6),0 10px 24px -8px rgba(0,0,0,.35);
  color:#fff;font-size:22px;font-weight:700;letter-spacing:-.01em;line-height:1;
}
.action.action-premium:hover{
  transform:translateY(-2px);filter:brightness(1.06);border-color:rgba(255,255,255,.1);
  background:radial-gradient(120% 90% at 50% 0%,rgba(255,255,255,.07),rgba(255,255,255,0) 62%),linear-gradient(180deg,#35313d 0%,#2c2934 52%,#25212c 100%);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 34px 64px -14px rgba(0,0,0,.65),0 12px 28px -8px rgba(0,0,0,.4);
}
.action.action-premium:active{transform:translateY(0);filter:none}

/* Transparent hero character — placed directly on the page background. */
.hero-media-wrap{position:relative;width:min(920px,100%);margin:18px auto -18px;display:flex;justify-content:center;align-items:flex-end;isolation:isolate}
.hero-media-wrap::before{content:"";position:absolute;z-index:-1;left:12%;right:12%;bottom:7%;height:62%;background:radial-gradient(ellipse,rgba(24,0,173,.18),transparent 70%);filter:blur(34px);pointer-events:none}
.character-img{width:min(860px,100%);height:auto;object-fit:contain;filter:drop-shadow(0 34px 30px rgba(0,0,0,.58));animation:float 7s ease-in-out infinite}
.chip{position:absolute;z-index:3;display:flex;align-items:center;gap:9px;background:rgba(10,11,12,.88);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--line-light);padding:10px 18px;border-radius:999px;font-size:12px;font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,.6);white-space:nowrap}
.chip-top{top:25px;left:-25px;border-color:rgba(24,0,173,.35);animation:chip-float-1 5s ease-in-out infinite}
.chip-right{top:45%;right:-35px;border-color:rgba(24,0,173,.4);animation:chip-float-2 6s ease-in-out infinite}
.chip-bottom{bottom:25px;left:15px;animation:chip-float-1 7s ease-in-out infinite}
.chip-pulse{width:8px;height:8px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent);animation:pulse 1.8s infinite}
.chip b{color:var(--accent)}
.chip-badge{background:rgba(24,0,173,.15);color:var(--accent);padding:3px 8px;border-radius:999px;font-size:10px;font-weight:700}

.section-heading h2{font-size:clamp(28px,5vw,56px);letter-spacing:-.02em}
.section-heading p{font-size:clamp(15px,2vw,20px);color:var(--muted);margin-top:14px}
.eyebrow{display:inline-block;font-size:11.5px;color:var(--accent);font-weight:700;letter-spacing:normal;margin-bottom:14px;text-transform:uppercase}

/* Supplied phone artwork with live text over its lower edge. */
.anywhere{position:relative;text-align:center;padding:36px 24px 40px}
.product-preview{position:relative;isolation:isolate;display:grid;width:min(960px,100%);margin:0 auto;padding-top:32px;overflow:hidden}
.phone-mockup{grid-area:1/1;justify-self:center;align-self:start;width:min(560px,90%);height:auto;transform:translateX(-4%) rotate(-8deg);filter:drop-shadow(0 24px 36px rgba(0,0,0,.55))}
.product-preview::after{content:"";grid-area:1/1;z-index:1;pointer-events:none;background:linear-gradient(to bottom,transparent 42%,rgba(5,5,5,.28) 60%,rgba(5,5,5,.88) 82%,var(--bg) 98%)}
.anywhere-copy{grid-area:1/1;align-self:end;position:relative;z-index:2;padding:160px 20px 28px;text-shadow:0 2px 20px rgba(0,0,0,.85)}
.anywhere-copy h2{font-size:clamp(28px,4.2vw,52px);font-variation-settings:'wdth' 100,'wght' 700;text-transform:none;line-height:1.08;letter-spacing:-.035em}
.anywhere-copy p{max-width:600px;margin:16px auto 0;font-size:18px;line-height:1.5;color:#b9bcb7;text-wrap:balance}
.green{color:var(--accent);font-weight:600}

.features{position:relative;max-width:1440px;margin:0 auto;padding:60px 48px 0}
.features .section-heading{margin-bottom:44px}
.feature-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.feature{position:relative;border:1px solid var(--line);background:var(--card);border-radius:24px;min-height:390px;overflow:hidden;padding:32px 28px 0;display:flex;flex-direction:column;cursor:default;user-select:none;-webkit-tap-highlight-color:transparent}
.feature:hover,.feature:active,.feature:focus{background:var(--card)!important;border-color:var(--line)!important;transform:none!important;box-shadow:none!important;outline:none!important}
.feature .eyebrow{font-size:11px;letter-spacing:normal;margin-bottom:10px}
.feature h3{font-size:28px;line-height:1.08;position:relative;z-index:2;max-width:340px;text-wrap:balance}
.feature-art{height:240px;margin-top:auto;position:relative}
.feature-art:after{content:'';position:absolute;left:-30px;right:-30px;bottom:0;height:45px;background:linear-gradient(transparent,var(--card));pointer-events:none}

.ranking{padding:6px 0}
.rank-row{display:flex;align-items:center;gap:12px;padding:11px 0;font-size:12.5px;border-bottom:1px solid rgba(255,255,255,.04)}
.rank-row img{width:32px;height:32px;border-radius:50%;object-fit:cover;border:1px solid var(--line)}
.rank-row small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.rank-row .points{color:var(--accent);margin-left:auto;font-size:12px;font-weight:700}
.medal{font-size:16px;width:18px}
.rank-row:nth-child(3){opacity:.75}
.rank-row:nth-child(4){opacity:.4}

.squad-mini{width:220px;max-width:100%;height:220px;margin:0 auto;position:relative;border:1px solid var(--line-light);border-radius:14px;background:radial-gradient(ellipse at 50% 60%,rgba(24,0,173,.08),transparent 70%),#07080A;box-shadow:0 0 25px rgba(0,0,0,.6);transform:rotate(-4deg);padding:14px}
.squad-mini>span{display:block;font-size:10px;color:var(--muted);letter-spacing:normal;font-weight:700}
.mini-pitch{margin-top:12px;border:1px solid rgba(255,255,255,.1);height:155px;border-radius:4px;position:relative}
.mini-pitch:before{content:'';position:absolute;top:50%;left:0;width:100%;border-top:1px solid rgba(255,255,255,.1)}
.mini-pitch:after{content:'';position:absolute;top:36%;left:36%;width:28%;height:28%;border:1px solid rgba(255,255,255,.1);border-radius:50%}
.mini-player{position:absolute;z-index:1;text-align:center;transform:translateX(-50%);font-size:8.5px;font-weight:600}
.mini-player img{width:34px;height:34px;border-radius:50%;border:2px solid var(--accent);object-fit:cover;object-position:50% 20%;margin-bottom:3px}

.notice-art{display:flex;align-items:center;justify-content:center;margin-top:0}
.notification{display:flex;gap:12px;align-items:center;border:1px solid var(--line-light);background:linear-gradient(130deg,#16181C,#0D0F12);padding:14px 14px;border-radius:20px;box-shadow:0 12px 30px rgba(0,0,0,.6);transform:rotate(-3deg);width:100%}
.notification-icon{width:38px;height:38px;flex:none;display:grid;place-items:center;background:var(--accent);border-radius:10px;padding:7px;box-shadow:0 0 16px rgba(24,0,173,.4)}
.notification-icon img{width:100%;height:100%;object-fit:contain;filter:brightness(0) invert(1)}
.notification div{font-size:12px;line-height:1.45}
.notification b{font-weight:600}
.notification small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.notification time{font-size:8.5px;color:var(--muted);align-self:flex-start;margin-left:auto;white-space:nowrap}

.signup-art{position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:10px;padding-bottom:24px}
.signup-option{
  display:flex;align-items:center;justify-content:center;gap:10px;
  background:#F4F6F1;color:#050505;border-radius:10px;width:94%;
  padding:13px 8px;font-size:13px;font-weight:700;
  box-shadow:0 6px 20px rgba(255,255,255,.1);
  cursor:pointer;transition:transform .2s,background .2s,box-shadow .2s;
  text-decoration:none;
}
.signup-option:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(255,255,255,.18)}
.signup-option.dark{
  background:rgba(255,255,255,.08);
  backdrop-filter:blur(20px) saturate(180%);-webkit-backdrop-filter:blur(20px) saturate(180%);
  color:#fff;border:1px solid rgba(255,255,255,.18);
  box-shadow:inset 0 1px 1.5px rgba(255,255,255,.28), 0 4px 16px rgba(0,0,0,.25);
}
.signup-option.dark:hover{
  background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.35);
  transform:translateY(-2px);color:#fff;
  box-shadow:inset 0 1px 2px rgba(255,255,255,.45), 0 8px 24px rgba(0,0,0,.35);
}
.signup-option svg{width:16px;height:16px}
.signup-art .cursor{
  position:absolute;bottom:30px;left:57%;width:38px;height:45px;
  filter:drop-shadow(0 4px 7px rgba(0,0,0,.6));transform:rotate(-12deg);
  pointer-events:none;
}

.coin-art{perspective:700px;display:flex;align-items:center;justify-content:center;gap:0}
.token{position:relative;display:grid;place-items:center;width:120px;height:138px;flex:none;border-radius:26px;background:linear-gradient(135deg,#4422dd,#1800ad 40%,#FFAE19 75%,#FF6A1F);border:3px solid #5533ee;box-shadow:9px 9px 0 #0a0050,15px 16px 30px rgba(0,0,0,.8),inset 0 0 20px rgba(255,255,255,.5);transform:rotate(-18deg) rotateY(-24deg);color:#fff;font-family:Archivo;font-size:44px;font-weight:900;letter-spacing:-2px}
.token.small{font-size:22px;width:82px;height:95px;transform:rotate(16deg) rotateY(-18deg);margin-top:85px;margin-left:-10px;box-shadow:6px 6px 0 #0a0050,12px 12px 25px rgba(0,0,0,.8)}
.token span{text-shadow:0 1px 2px rgba(255,255,255,.4)}

.entry-art{display:flex;align-items:center;justify-content:center}
.entry-slip{width:240px;background:#08090C;border:1px solid var(--line-light);box-shadow:0 14px 34px rgba(0,0,0,.6);border-radius:14px;padding:16px;transform:rotate(3deg)}
.entry-slip>small{font-size:9.5px;color:var(--muted);font-weight:700;letter-spacing:normal}
.entry-slip>b{display:block;font-weight:700;font-size:20px;margin:10px 0;letter-spacing:-.01em}
.entry-slip .entry-line{display:flex;justify-content:space-between;font-size:10.5px;color:var(--muted);margin:10px 0}
.entry-slip .entry-line strong{font-weight:600;color:var(--text)}
.entry-confirm{display:flex;justify-content:center;align-items:center;gap:8px;margin-top:16px;padding:10px;border-radius:8px;background:var(--accent);color:var(--accent-ink);font-weight:700;font-size:11.5px}
.entry-confirm svg{width:14px;height:14px}

.final-cta{position:relative;min-height:960px;display:flex;align-items:center;justify-content:center;text-align:center;margin-top:80px;isolation:isolate;padding:140px 24px}
.legends{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2;pointer-events:none;opacity:.4}
.final-cta:after{content:'';position:absolute;inset:0;z-index:-1;background:linear-gradient(var(--bg),transparent 20%,transparent 75%,var(--bg));pointer-events:none}
.orbit{position:absolute;left:50%;top:50%;width:min(900px,78vw);transform:translate(-50%,-50%);pointer-events:none;z-index:-1;animation:orbit 55s linear infinite;opacity:.4}
.orbit.inner{width:min(470px,42vw);animation-direction:reverse;animation-duration:40s;opacity:.5}
.final-copy{max-width:680px;position:relative;z-index:1}
.final-copy h2{font-size:clamp(34px,5.5vw,58px);line-height:1.05;letter-spacing:-.02em}
.final-copy p{font-size:clamp(15px,2vw,20px);color:var(--muted);margin:20px auto 36px;max-width:540px}
.final-copy .actions{margin-top:0}

.footer{padding:50px 40px 60px;max-width:1440px;margin:auto;position:relative}
.footer-top{display:grid;grid-template-columns:2.5fr repeat(3,1fr);gap:40px}
.footer-brand .brand{font-size:36px;letter-spacing:-.02em;line-height:1.1}
.footer-brand .brand-mark{width:36px;height:36px}
.footer-brand p{font-size:12px;max-width:none;color:var(--muted);margin-top:4px;line-height:1.4}
.footer-col h2{font-size:11px;font-weight:700;color:var(--muted);margin:4px 0 16px;text-transform:uppercase;letter-spacing:.14em}
.footer-col a{display:block;font-size:13.5px;margin:10px 0;color:#c0c4be;transition:color .2s}
.footer-col a:hover{color:var(--accent)}
.copyright{margin-top:40px;color:var(--muted);font-size:12px}
.demo-note{color:#5A605B;font-size:11px;margin-top:6px}

@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
@keyframes orbit{from{transform:translate(-50%,-50%) rotate(0)}to{transform:translate(-50%,-50%) rotate(360deg)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
@keyframes chip-float-1{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes chip-float-2{0%,100%{transform:translateY(0)}50%{transform:translateY(8px)}}

@media(max-width:1100px){
  .features{padding-left:32px;padding-right:32px}
  .feature{padding:26px 22px 0;min-height:360px}
  .feature h3{font-size:24px}
  .feature-art{height:210px}
}
@media(max-width:799px){
  .masthead{padding:18px 20px}
  .brand{font-size:22px;gap:8px}
  .brand-mark{width:24px;height:24px}
  .bg-deco-hero{top:10px;width:min(400px,92vw);opacity:.08}
  .bg-deco-features{display:none}
  .nav-link{display:none}
  .nav-login{font-size:13px;padding:8px 18px}
  .menu-toggle{display:flex}
  .hero{padding:105px 20px 0}
  .wordmark{font-size:clamp(32px,10vw,80px);margin-bottom:-6px}
  .hero h1{font-size:clamp(24px,7.2vw,36px);line-height:1.08}
  .hero-copy{font-size:14.5px;line-height:1.5}
  .actions{gap:10px;margin-top:22px}
  .action{min-width:0;width:100%;font-size:14px;min-height:46px;padding:12px 20px}
  .action.action-premium{width:100%;height:64px;min-height:64px;font-size:20px}
  .hero-media-wrap{width:100%;margin:28px auto 8px}
  .character-img{width:92%;max-width:570px}

  .anywhere{padding:24px 12px 0}
  .section-heading h2{font-size:clamp(23px,6.8vw,32px);line-height:1.15}
  .section-heading p{font-size:14px;max-width:340px;margin:10px auto 0;line-height:1.5}

  .product-preview{width:100%;padding-top:24px}
  .phone-mockup{width:min(420px,82%)}
  .anywhere-copy{padding:100px 4px 16px}
  .anywhere-copy h2{font-size:clamp(25px,6.8vw,40px);line-height:1.1}
  .anywhere-copy p{max-width:440px;font-size:14px;margin:12px auto 0;line-height:1.5}

  .features{padding:40px 18px 0}
  .features .section-heading{text-align:center;margin-bottom:32px}
  .features .section-heading p{max-width:340px;margin:10px auto 0}
  .feature-grid{grid-template-columns:1fr;gap:16px}
  .feature{min-height:330px;padding:24px 20px 0}
  .feature h3{font-size:24px}
  .final-cta{min-height:600px;margin-top:40px;padding:80px 20px}
  .final-copy h2{font-size:clamp(26px,7.5vw,36px);line-height:1.1}
  .final-copy p{font-size:14.5px;margin:16px auto 28px}
  .footer{padding:35px 20px 40px}
  .footer-top{grid-template-columns:1fr 1fr;gap:30px 16px}
  .footer-brand{grid-column:1/-1;text-align:left}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*:before,*:after{animation:none!important;transition:none!important}}
"""

def actions(primary='Start trading',secondary='Explore FanPlay'):
    return f'<div class="actions"><a class="action primary" href="signup.html">{primary}</a><a class="action action-premium" href="signin.html?next=fanplay.html">{secondary}</a></div>'

def hero_media():
    return '''<div class="hero-media-wrap" role="img" aria-label="Fantrade character checking the market on a phone">
      <img class="character-img" src="assets/landing/fantrade-character-market.png" alt="Fantrade character checking player markets on a phone" width="1306" height="1205" fetchpriority="high">
    </div>'''

def product_preview():
    return '''<div class="product-preview">
      <img class="phone-mockup" src="assets/landing/fantrade-phone-market.png" alt="Fantrade player markets and portfolio on a phone" width="1038" height="1515" loading="lazy" decoding="async">
      <div class="anywhere-copy">
        <h2 id="anywhereTitle">trade from anywhere.<br>stay close to the game.</h2>
        <p>From your phone to your desktop - your Activity Shares, club and matchday in one place.</p>
      </div>
    </div>'''

def feature(label,title,art,href=None):
    return f'<div class="feature"><span class="eyebrow">{label}</span><h3>{title}</h3>{art}</div>'

def build_landing():
    ranking='<div class="feature-art ranking" aria-hidden="true">'
    for i,(slug,name,points) in enumerate([('saka','Zero FC','812 FP'),('haaland','North Bank XI','786 FP'),('mbappe','The Galácticos','754 FP'),('palmer','Blue Revolution','721 FP')]):
        ranking+=f'<div class="rank-row"><span class="medal">{["🥇","🥈","🥉","4"][i]}</span><img src="assets/players/{slug}.webp" alt="" loading="lazy"><div>{name}<small>Matchday 06</small></div><span class="points">{points}</span></div>'
    ranking+='</div>'
    squad='<div class="feature-art" aria-hidden="true"><div class="squad-mini"><span>ZERO FC &nbsp; · &nbsp; 4–3–3</span><div class="mini-pitch">'
    for slug,name,left,top in [('haaland','Haaland',50,8),('saka','Saka',22,70),('bruno','Bruno',78,70),('saliba','Saliba',50,122)]:
        squad+=f'<div class="mini-player" style="left:{left}%;top:{top}px"><img src="assets/players/{slug}.webp" alt="" loading="lazy">{name}</div>'
    squad+='</div></div></div>'
    notice='<div class="feature-art notice-art" aria-hidden="true"><div class="notification"><span class="notification-icon"><img src="assets/landing/fantrade-logo.png" alt="Fantrade" width="22" height="22"></span><div><b>Matchday 06 settled</b><small><span class="green">+6,200 $FTR</span> · Your club made the top 20.</small></div><time>9:41 AM</time></div></div>'
    signup='''<div class="feature-art signup-art"><a class="signup-option" href="signup.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m3 6 9 7 9-7"/></svg>Create your Fantrade account</a><a class="signup-option dark" href="exchange.html">Explore the player market <span>→</span></a><svg class="cursor" viewBox="0 0 36 44" aria-hidden="true"><path d="M4 3 29 25l-12 1 5 12-7 3-5-12-9 8Z" fill="#f0efff" stroke="#9e9bc7" stroke-width="2"/></svg></div>'''
    coins='<div class="feature-art coin-art" aria-hidden="true"><div class="token"><span>$FTR</span></div><div class="token small"><span>10M</span></div></div>'
    entry='''<div class="feature-art entry-art" aria-hidden="true"><div class="entry-slip"><small>FANPLAY · MATCHDAY 06</small><b>Back your football IQ.</b><div class="entry-line"><span>Entry</span><strong>$Saka · Solo</strong></div><div class="entry-line"><span>Scoring</span><strong>Goals + assists + more</strong></div><div class="entry-confirm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 12 4 4L19 6"/></svg>Ready for matchday</div></div></div>'''
    features=''.join([
        feature('Leaderboard','make your name.<br>climb the leaderboard.',ranking,'leaderboard.html'),
        feature('Dream Clubs','your players.<br>your dream club.',squad,'clubs.html'),
        feature('Alerts','every goal. every trade.<br>stay in the know.',notice,'notifications.html'),
        feature('Easy onboarding','your first Activity Share<br>is just the beginning.',signup,'signup.html'),
        feature('Activity Shares','10 million shares.<br>one activity asset.',coins,'how-it-works.html'),
        feature('FanPlay','turn football knowledge<br>into matchday points.',entry,'fanplay.html'),
    ])
    html='''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#050505"><meta name="description" content="Trade Fantrade Activity Shares tied to football player and coach activity, build your Dream Club and use eligible shares in FanPlay. Welcome to Fantrade."><title>Fantrade — Own the game.</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Montserrat:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"><link rel="preload" as="image" href="assets/landing/fantrade-character-market.png"><style>'''+CSS+'''</style></head><body><a class="skip" href="#main">Skip to content</a><div class="landing"><header class="masthead"><a class="brand" href="index.html" aria-label="Fantrade home"><img class="brand-mark" src="assets/landing/fantrade-logo.png" alt="Fantrade"><span>fantrade<span class="brand-dot">.</span></span></a><nav class="nav-right" aria-label="Main navigation"><a class="nav-link" href="exchange.html">Explore players</a><a class="nav-link" href="how-it-works.html">How it works</a><a class="nav-login" href="signin.html">Log in</a><button class="menu-toggle" id="landingMenu" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="landingNav"><svg class="icon-bars" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M3 6h18M3 12h18M3 18h18" stroke-linecap="round"/></svg><svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M18 6 6 18M6 6l12 12" stroke-linecap="round"/></svg></button></nav></header><nav class="mobile-menu" id="landingNav" aria-label="Mobile navigation" inert><div class="mobile-menu-inner"><a href="exchange.html">Explore Players</a><a href="clubs.html">Dream Clubs</a><a href="fanplay.html">FanPlay</a><a href="how-it-works.html">How It Works</a><a href="signup.html" class="menu-highlight">Create Account <span class="arrow">&rarr;</span></a></div></nav><main id="main"><section class="hero" aria-labelledby="heroTitle"><div class="wordmark" aria-hidden="true">fantrade</div><h1 id="heroTitle">where football fans<br><span>own the game.</span></h1><p class="hero-copy">Trade Activity Shares tied to football player and coach performance. Build your Dream Club, then use eligible shares in FanPlay when matchday starts.</p>'''+actions()+hero_media()+'''</section><section class="anywhere" aria-labelledby="anywhereTitle">'''+product_preview()+'''</section><section class="features" aria-labelledby="featuresTitle"><div class="bg-deco bg-deco-features" aria-hidden="true"><img src="assets/landing/fantrade-outline-logo.png" alt="" width="560" height="560"></div><div class="section-heading"><span class="eyebrow">THE FOOTBALL ECONOMY</span><h2 id="featuresTitle">more than a spectator.</h2><p>Fantrade turns verified football activity into digital markets, ownership accounting, exchange trading and FanPlay utility.</p></div><div class="feature-grid">'''+features+'''</div></section><section class="final-cta" aria-labelledby="finalTitle"><img class="legends" src="assets/landing/legends.webp" alt="" loading="lazy" aria-hidden="true"><img class="orbit" src="assets/landing/outer-circle.webp" alt="" loading="lazy" aria-hidden="true"><img class="orbit inner" src="assets/landing/inner-circle.webp" alt="" loading="lazy" aria-hidden="true"><div class="final-copy"><h2 id="finalTitle">a trading platform<br>for the football in us.</h2><p>Start with an Activity Share tied to a player you follow.<br>Your squad starts right here.</p>'''+actions()+'''</div></section></main><footer class="footer"><div class="footer-top"><div class="footer-brand"><a class="brand" href="index.html"><img class="brand-mark" src="assets/landing/fantrade-logo.png" alt="Fantrade"><span>fantrade<span class="brand-dot">.</span></span></a><p>where football fans own the game.</p></div><div class="footer-col"><h2>Platform</h2><a href="exchange.html">Player market</a><a href="clubs.html">Dream Clubs</a><a href="fanplay.html">FanPlay</a><a href="leaderboard.html">Leaderboard</a></div><div class="footer-col"><h2>Get started</h2><a href="how-it-works.html">How it works</a><a href="signup.html">Create account</a><a href="signin.html">Log in</a><a href="ftr.html">$FTR wallet</a></div><div class="footer-col"><h2>Your Fantrade</h2><a href="portfolio.html">Portfolio</a><a href="account.html">Your profile</a><a href="settings-play.html">Responsible play</a><a href="settings-data.html">Data &amp; account</a></div></div><p class="copyright">© 2026 Fantrade.</p><p class="demo-note">Prototype experience. Player prices, balances and rewards shown are illustrative.</p></footer></div><script>
const toggle=document.getElementById('landingMenu'), menu=document.getElementById('landingNav');
function setMenu(open){
  toggle.setAttribute('aria-expanded',String(open));
  toggle.setAttribute('aria-label',open?'Close menu':'Open menu');
  menu.classList.toggle('open',open);
  menu.inert=!open;
  document.body.style.overflow=open?'hidden':'';
}
toggle.addEventListener('click',()=>setMenu(toggle.getAttribute('aria-expanded')!=='true'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){setMenu(false);toggle.focus();}});
document.addEventListener('click',e=>{if(!menu.contains(e.target)&&!toggle.contains(e.target))setMenu(false);});
menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
matchMedia('(min-width:800px)').addEventListener('change',e=>{if(e.matches)setMenu(false);});
</script></body></html>'''
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    print('built index.html — transparent Fantrade character hero')

if __name__=='__main__':
    build_landing()
