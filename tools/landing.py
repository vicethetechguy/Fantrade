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
  --accent:#C4F82A;
  --accent-hover:#d5fa52;
  --accent-ink:#050505;
  --amber:#FF6A1F;
  --red:#FF5E5E;
  --line:rgba(255,255,255,.08);
  --line-light:rgba(255,255,255,.14);
  --glow:rgba(196,248,42,.18);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:32px}
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

.landing{position:relative;overflow:hidden;background:radial-gradient(ellipse 80% 50% at 50% -20%,rgba(196,248,42,.06),transparent 70%),var(--bg)}
.space-bg{position:absolute;inset:0 0 auto;width:100%;height:auto;z-index:0;pointer-events:none;opacity:.35;mix-blend-mode:screen}
.masthead{position:absolute;z-index:10;left:0;right:0;top:0;display:flex;justify-content:space-between;align-items:center;padding:24px 36px;gap:24px;max-width:1440px;margin:0 auto}
.brand{font-size:28px;letter-spacing:-.02em;color:#fff;display:flex;align-items:center;gap:6px}
.brand-dot{color:var(--accent)}
.nav-right{display:flex;gap:12px;align-items:center}
.nav-link{font-size:14px;font-weight:500;padding:8px 16px;color:#c0c4be;border-radius:999px;transition:color .2s,background .2s}
.nav-link:hover{color:#fff;background:rgba(255,255,255,.05)}
.nav-login{background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:999px;padding:9px 24px;font-size:14px;font-weight:600;color:#fff;transition:all .2s}
.nav-login:hover{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.menu-toggle{display:none;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);width:42px;height:42px;align-items:center;justify-content:center;cursor:pointer}
.menu-toggle svg{width:21px;height:21px}
.mobile-menu{display:none;position:absolute;top:74px;right:20px;left:20px;z-index:20;background:#0A0B0CF8;backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid var(--line);border-radius:18px;padding:12px;box-shadow:0 24px 60px rgba(0,0,0,.8)}
.mobile-menu.open{display:grid}
.mobile-menu a{padding:14px 16px;border-radius:10px;font-size:15px;font-weight:500}
.mobile-menu a:hover{background:rgba(196,248,42,.08);color:var(--accent)}

.hero{position:relative;text-align:center;padding:140px 24px 0}
.wordmark{font-size:clamp(80px,14vw,180px);letter-spacing:-.04em;line-height:.85;color:rgba(255,255,255,.04);user-select:none;margin-bottom:-10px}
.hero-pill{display:inline-flex;align-items:center;gap:8px;padding:6px 16px;border-radius:999px;background:rgba(196,248,42,.08);border:1px solid rgba(196,248,42,.24);color:var(--accent);font-size:11px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;margin-bottom:18px}
.hero-pill .dot{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent);animation:pulse 2s infinite}
.hero h1{font-size:clamp(32px,5.5vw,56px);margin:0 0 14px;letter-spacing:-.02em}
.hero h1 span{color:var(--accent)}
.hero-copy{color:var(--muted);font-size:clamp(16px,2vw,20px);line-height:1.55;max-width:680px;margin:0 auto}

.actions{display:flex;justify-content:center;align-items:center;gap:14px;margin-top:32px;position:relative;z-index:2;flex-wrap:wrap}
.action{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:52px;min-width:190px;padding:14px 30px;border-radius:999px;font-size:15px;font-weight:700;letter-spacing:.02em;transition:all .2s;background:rgba(255,255,255,.06);color:var(--text);border:1px solid var(--line)}
.action.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);box-shadow:0 8px 24px rgba(196,248,42,.22)}
.action.primary:hover{background:var(--accent-hover);transform:translateY(-2px);box-shadow:0 12px 32px rgba(196,248,42,.35)}
.action:hover{background:rgba(255,255,255,.12);border-color:var(--line-light);transform:translateY(-2px)}
.action img{width:16px;height:16px}

/* Hero Toilet Trader Media (Humorous & High Tech) */
.hero-media-wrap{position:relative;width:min(620px,94%);margin:32px auto 0;display:flex;justify-content:center;align-items:center}
.character-box{position:relative;border-radius:32px;overflow:visible;animation:float 6s ease-in-out infinite}
.character-img{width:100%;max-width:540px;height:auto;border-radius:28px;box-shadow:0 24px 80px rgba(0,0,0,.8),0 0 70px rgba(196,248,42,.12);border:1px solid rgba(196,248,42,.25);background:radial-gradient(circle at 50% 30%,rgba(196,248,42,.15),#050505 75%)}
.character-aura{position:absolute;inset:-20px;border-radius:40px;background:radial-gradient(circle,rgba(196,248,42,.18) 0%,transparent 65%);filter:blur(30px);z-index:-1;pointer-events:none}
.chip{position:absolute;z-index:3;display:flex;align-items:center;gap:9px;background:rgba(10,11,12,.88);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--line-light);padding:10px 18px;border-radius:999px;font-size:12px;font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,.6);white-space:nowrap}
.chip-top{top:25px;left:-25px;border-color:rgba(196,248,42,.35);animation:chip-float-1 5s ease-in-out infinite}
.chip-right{top:45%;right:-35px;border-color:rgba(196,248,42,.4);animation:chip-float-2 6s ease-in-out infinite}
.chip-bottom{bottom:25px;left:15px;animation:chip-float-1 7s ease-in-out infinite}
.chip-pulse{width:8px;height:8px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent);animation:pulse 1.8s infinite}
.chip b{color:var(--accent)}
.chip-badge{background:rgba(196,248,42,.15);color:var(--accent);padding:3px 8px;border-radius:999px;font-size:10px;font-weight:700}

.section-heading h2{font-size:clamp(34px,5vw,56px);letter-spacing:-.02em}
.section-heading p{font-size:clamp(16px,2vw,20px);color:var(--muted);margin-top:14px}
.eyebrow{display:inline-block;font-size:11px;color:var(--accent);font-weight:700;letter-spacing:.18em;margin-bottom:14px;text-transform:uppercase}

.anywhere{position:relative;text-align:center;padding:70px 24px 100px}
.product-preview{position:relative;width:min(1080px,94%);margin:60px auto 0;padding:0 80px 80px 0}
.monitor{position:relative;z-index:1;background:linear-gradient(145deg,#16171b,#08090a);border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:12px 12px 26px;box-shadow:0 24px 80px rgba(0,0,0,.7),0 0 50px rgba(196,248,42,.06)}
.monitor:after{content:'FANTRADE TERMINAL';font-family:Archivo;font-size:8px;letter-spacing:1.5px;position:absolute;left:0;right:0;bottom:7px;color:#5A605B;text-align:center}
.monitor-stand{position:absolute;top:calc(100% - 98px);left:34%;width:20%;height:100px;background:linear-gradient(90deg,#1c1e22,#2e3138 50%,#141619);clip-path:polygon(23% 0,77% 0,82% 85%,100% 92%,100% 100%,0 100%,0 92%,18% 85%)}
.screen{background:#060708;border:1px solid rgba(255,255,255,.06);border-radius:6px;overflow:hidden;text-align:left;aspect-ratio:1.77}
.screen-top{height:38px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:11px;background:#090A0C}
.screen-brand{font-size:16px;letter-spacing:-.01em;color:#fff}
.screen-top span:last-child{color:var(--accent);font-weight:700}
.screen-body{display:grid;grid-template-columns:26% 51% 23%;height:calc(100% - 38px)}
.market-list{border-right:1px solid var(--line);padding:12px 10px;background:#08090A}
.micro-label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;font-weight:700;display:block;margin-bottom:8px}
.preview-row{display:flex;align-items:center;gap:8px;border-bottom:1px solid rgba(255,255,255,.04);padding:9px 0;font-size:11px}
.preview-row img{width:26px;height:26px;border-radius:50%;object-fit:cover;object-position:center 20%;border:1px solid var(--line)}
.preview-row b{font-weight:600}
.preview-row small{font-size:9px;color:var(--muted);display:block;margin-top:1px}
.preview-row .quote{margin-left:auto;text-align:right}
.green{color:var(--accent);font-weight:600}
.chart-area{padding:14px;border-right:1px solid var(--line);overflow:hidden;background:#070809}
.chart-title{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600}
.chart-title img{width:24px;height:24px;border-radius:50%;object-fit:cover}
.chart-price{font-size:26px;font-weight:800;margin:14px 0 4px;font-family:Montserrat,sans-serif}
.chart-price small{font-size:11px;margin-left:8px;color:var(--accent)}
.chart-tools{display:flex;gap:14px;font-size:9px;color:var(--muted);margin:10px 0}
.chart-tools b{color:var(--accent);border-bottom:1.5px solid var(--accent);padding-bottom:2px}
.price-chart{display:block;width:100%;height:165px;overflow:visible;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:25% 25%}
.chart-bottom{display:flex;gap:20px;border-top:1px solid var(--line);margin-top:10px;padding-top:10px;font-size:10px;color:var(--muted)}
.order-preview{padding:12px 10px;background:#08090A}
.order-tabs{display:flex;background:#101215;border-radius:8px;font-size:10px;text-align:center;margin-bottom:14px;padding:2px}
.order-tabs span{padding:6px 0;flex:1;color:var(--muted)}
.order-tabs b{flex:1;background:var(--accent);color:var(--accent-ink);border-radius:6px;padding:6px 0;font-weight:700}
.order-field{border:1px solid var(--line);border-radius:8px;margin-top:8px;padding:8px 10px;font-size:11px;background:#0D0E11}
.order-field small{display:block;color:var(--muted);font-size:8.5px;margin-bottom:4px;text-transform:uppercase}
.order-note{display:flex;justify-content:space-between;font-size:9px;color:var(--muted);margin:10px 0}
.order-buy{background:var(--accent);color:var(--accent-ink);font-weight:700;text-align:center;border-radius:8px;padding:9px;font-size:11px;cursor:pointer}

.phone{position:absolute;right:0;bottom:20px;z-index:3;width:225px;background:#08090A;border:4px solid #282A2F;outline:1px solid rgba(255,255,255,.1);border-radius:36px;padding:11px 10px 15px;transform:rotate(8deg);box-shadow:0 0 35px rgba(196,248,42,.12),15px 18px 45px rgba(0,0,0,.8);text-align:left;animation:phone-float 6s ease-in-out infinite}
.phone-status{display:flex;justify-content:space-between;font-size:9px;padding:4px 8px 10px;color:#c0c4be}
.phone-notch{background:#000;width:60px;height:12px;border-radius:8px}
.phone-head{font-size:9px;color:var(--muted);margin:8px 0 2px;text-transform:uppercase;letter-spacing:.08em}
.phone-balance{font-size:26px;letter-spacing:-1px;font-weight:800;font-family:Montserrat,sans-serif}
.phone-gain{font-size:10px;color:var(--accent);margin-top:2px;font-weight:600}
.phone-actions{display:flex;gap:6px;margin:12px 0}
.phone-actions span{background:rgba(255,255,255,.06);flex:1;border-radius:8px;padding:8px 0;text-align:center;font-size:9px;font-weight:600;border:1px solid var(--line)}
.phone-actions span:first-child{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.phone-tabs{display:flex;gap:14px;font-size:10px;padding:8px 0;border-bottom:1px solid var(--line)}
.phone-tabs b{font-weight:600;color:var(--accent)}
.phone-tabs span{color:var(--muted)}
.phone .preview-row{padding:8px 0;font-size:9.5px}
.phone .preview-row img{width:22px;height:22px}
.phone-nav{display:flex;justify-content:space-around;margin-top:12px;color:var(--muted);font-size:8px}
.phone-nav span:first-child{color:var(--accent);font-weight:700}

.features{position:relative;max-width:1440px;margin:0 auto;padding:60px 48px 0}
.features .section-heading{margin-bottom:44px}
.feature-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.feature{position:relative;border:1px solid var(--line);background:var(--card);border-radius:24px;min-height:390px;overflow:hidden;padding:32px 28px 0;transition:all .25s;display:flex;flex-direction:column}
.feature:hover{background:var(--card-hover);border-color:rgba(196,248,42,.28);transform:translateY(-3px)}
.feature .eyebrow{font-size:10.5px;margin-bottom:10px}
.feature h3{font-size:28px;line-height:1.08;position:relative;z-index:2;max-width:320px}
.feature-art{height:240px;margin-top:auto;position:relative;transition:transform .35s}
.feature:hover .feature-art{transform:translateY(-4px)}
.feature-art:after{content:'';position:absolute;left:-30px;right:-30px;bottom:0;height:45px;background:linear-gradient(transparent,var(--card));pointer-events:none}

.ranking{padding:6px 0}
.rank-row{display:flex;align-items:center;gap:12px;padding:11px 0;font-size:12.5px;border-bottom:1px solid rgba(255,255,255,.04)}
.rank-row img{width:32px;height:32px;border-radius:50%;object-fit:cover;border:1px solid var(--line)}
.rank-row small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.rank-row .points{color:var(--accent);margin-left:auto;font-size:12px;font-weight:700}
.medal{font-size:16px;width:18px}
.rank-row:nth-child(3){opacity:.75}
.rank-row:nth-child(4){opacity:.4}

.squad-mini{width:220px;max-width:100%;height:220px;margin:0 auto;position:relative;border:1px solid var(--line-light);border-radius:14px;background:radial-gradient(ellipse at 50% 60%,rgba(196,248,42,.08),transparent 70%),#07080A;box-shadow:0 0 25px rgba(0,0,0,.6);transform:rotate(-4deg);padding:14px}
.squad-mini>span{display:block;font-size:10px;color:var(--muted);letter-spacing:.08em;font-weight:700}
.mini-pitch{margin-top:12px;border:1px solid rgba(255,255,255,.1);height:155px;border-radius:4px;position:relative}
.mini-pitch:before{content:'';position:absolute;top:50%;left:0;width:100%;border-top:1px solid rgba(255,255,255,.1)}
.mini-pitch:after{content:'';position:absolute;top:36%;left:36%;width:28%;height:28%;border:1px solid rgba(255,255,255,.1);border-radius:50%}
.mini-player{position:absolute;z-index:1;text-align:center;transform:translateX(-50%);font-size:8.5px;font-weight:600}
.mini-player img{width:34px;height:34px;border-radius:50%;border:2px solid var(--accent);object-fit:cover;object-position:50% 20%;margin-bottom:3px}

.notice-art{display:flex;align-items:center;justify-content:center;margin-top:0}
.notification{display:flex;gap:12px;align-items:center;border:1px solid var(--line-light);background:linear-gradient(130deg,#16181C,#0D0F12);padding:14px 14px;border-radius:20px;box-shadow:0 12px 30px rgba(0,0,0,.6);transform:rotate(-3deg);width:100%}
.notification-icon{width:36px;height:36px;flex:none;display:grid;place-items:center;background:var(--accent);color:var(--accent-ink);border-radius:10px;font-family:Archivo;font-weight:900;font-size:17px}
.notification div{font-size:12px;line-height:1.45}
.notification b{font-weight:600}
.notification small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.notification time{font-size:8.5px;color:var(--muted);align-self:flex-start;margin-left:auto;white-space:nowrap}

.signup-art{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:10px;padding-bottom:24px}
.signup-option{display:flex;align-items:center;justify-content:center;gap:10px;background:#F4F6F1;color:#050505;border-radius:10px;width:94%;padding:13px 8px;font-size:13px;font-weight:700;box-shadow:0 6px 20px rgba(255,255,255,.1)}
.signup-option.dark{background:rgba(255,255,255,.07);color:var(--text);border:1px solid var(--line)}
.signup-option svg{width:16px;height:16px}
.signup-art .cursor{position:absolute;bottom:30px;left:57%;width:38px;height:45px;filter:drop-shadow(0 4px 7px rgba(0,0,0,.6));transform:rotate(-12deg)}

.coin-art{perspective:700px;display:flex;align-items:center;justify-content:center;gap:0}
.token{position:relative;display:grid;place-items:center;width:120px;height:138px;flex:none;border-radius:26px;background:linear-gradient(135deg,#E6FF66,#C4F82A 40%,#FFAE19 75%,#FF6A1F);border:3px solid #F2FFAA;box-shadow:9px 9px 0 #3b4707,15px 16px 30px rgba(0,0,0,.8),inset 0 0 20px rgba(255,255,255,.5);transform:rotate(-18deg) rotateY(-24deg);color:#0A0D03;font-family:Archivo;font-size:44px;font-weight:900;letter-spacing:-2px}
.token.small{font-size:22px;width:82px;height:95px;transform:rotate(16deg) rotateY(-18deg);margin-top:85px;margin-left:-10px;box-shadow:6px 6px 0 #3b4707,12px 12px 25px rgba(0,0,0,.8)}
.token span{text-shadow:0 1px 2px rgba(255,255,255,.4)}

.entry-art{display:flex;align-items:center;justify-content:center}
.entry-slip{width:240px;background:#08090C;border:1px solid var(--line-light);box-shadow:0 14px 34px rgba(0,0,0,.6);border-radius:14px;padding:16px;transform:rotate(3deg)}
.entry-slip>small{font-size:9.5px;color:var(--muted);font-weight:700;letter-spacing:.08em}
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
.final-copy h2{font-size:clamp(36px,5.5vw,58px);line-height:1.05;letter-spacing:-.02em}
.final-copy p{font-size:clamp(16px,2vw,20px);color:var(--muted);margin:20px auto 36px;max-width:540px}
.final-copy .actions{margin-top:0}

.footer{padding:50px 40px 60px;max-width:1440px;margin:auto;position:relative;border-top:1px solid var(--line)}
.footer-top{display:grid;grid-template-columns:2.5fr repeat(3,1fr);gap:40px}
.footer-brand .brand{font-size:36px;letter-spacing:-.02em}
.footer-brand p{font-size:16px;max-width:280px;color:var(--muted);margin-top:12px;line-height:1.4}
.footer-col h2{font-size:11px;font-weight:700;color:var(--muted);margin:4px 0 16px;text-transform:uppercase;letter-spacing:.14em}
.footer-col a{display:block;font-size:13.5px;margin:10px 0;color:#c0c4be;transition:color .2s}
.footer-col a:hover{color:var(--accent)}
.copyright{margin-top:40px;color:var(--muted);font-size:12px}
.demo-note{color:#5A605B;font-size:11px;margin-top:6px}

@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
@keyframes phone-float{0%,100%{transform:rotate(8deg) translateY(0)}50%{transform:rotate(8deg) translateY(-10px)}}
@keyframes orbit{from{transform:translate(-50%,-50%) rotate(0)}to{transform:translate(-50%,-50%) rotate(360deg)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
@keyframes chip-float-1{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes chip-float-2{0%,100%{transform:translateY(0)}50%{transform:translateY(8px)}}

@media(max-width:1100px){
  .features{padding-left:32px;padding-right:32px}
  .feature{padding:26px 22px 0;min-height:360px}
  .feature h3{font-size:24px}
  .feature-art{height:210px}
  .product-preview{width:96%;padding-right:60px}
  .phone{width:195px}
  .screen-body{grid-template-columns:28% 48% 24%}
  .price-chart{height:120px}
}
@media(max-width:799px){
  .masthead{padding:18px 20px}
  .brand{font-size:24px}
  .nav-link{display:none}
  .nav-login{font-size:13px;padding:8px 18px}
  .menu-toggle{display:flex}
  .hero{padding:110px 20px 0}
  .hero-pill{font-size:9.5px}
  .hero h1{font-size:32px}
  .hero-copy{font-size:15px}
  .actions{gap:10px;margin-top:24px}
  .action{min-width:0;width:100%;font-size:14px;min-height:46px;padding:12px 20px}
  .hero-media-wrap{width:100%;margin-top:24px}
  .character-img{border-radius:20px}
  .chip{padding:6px 12px;font-size:10px}
  .chip-top{top:10px;left:0}
  .chip-right{right:0;top:auto;bottom:40px}
  .chip-bottom{display:none}
  .anywhere{padding:50px 20px 60px}
  .section-heading h2{font-size:32px}
  .section-heading p{font-size:15px}
  .product-preview{width:100%;margin-top:30px;padding:0 0 40px}
  .monitor{padding:6px 6px 14px;border-radius:12px;width:94%}
  .monitor-stand{display:none}
  .screen-top{height:28px;padding:0 8px;font-size:7px}
  .screen-brand{font-size:11px}
  .screen-body{height:calc(100% - 28px);grid-template-columns:35% 65%}
  .market-list{padding:6px 4px}
  .preview-row{font-size:7px;padding:4px 0}
  .preview-row img{width:16px;height:16px}
  .chart-area{padding:6px;border-right:0}
  .chart-title{font-size:8px}
  .chart-title img{width:16px;height:16px}
  .chart-price{font-size:18px;margin:6px 0 2px}
  .chart-tools{font-size:6px;gap:8px;margin:4px 0}
  .price-chart{height:80px}
  .chart-bottom,.order-preview{display:none}
  .phone{width:125px;right:2%;bottom:5px;border-width:3px;border-radius:20px;padding:6px}
  .phone-balance{font-size:17px}
  .features{padding:40px 18px 0}
  .feature-grid{grid-template-columns:1fr;gap:16px}
  .feature{min-height:330px;padding:24px 20px 0}
  .feature h3{font-size:24px}
  .final-cta{min-height:650px;margin-top:50px;padding:100px 20px}
  .final-copy h2{font-size:32px}
  .final-copy p{font-size:15px}
  .footer{padding:35px 20px 40px}
  .footer-top{grid-template-columns:1fr 1fr;gap:30px 16px}
  .footer-brand{grid-column:1/-1}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*:before,*:after{animation:none!important;transition:none!important}}
"""

PLAYERS = [('saka','Saka','Arsenal','48.20','+6.40%'),('haaland','Haaland','Manchester City','71.40','−1.80%'),('mbappe','Mbappé','Real Madrid','78.50','+4.80%'),('vinicius','Vinícius','Real Madrid','63.10','+0.70%'),('palmer','Palmer','Chelsea','52.80','+8.20%')]

def rows(phone=False):
    return ''.join(f'<div class="preview-row"><img src="assets/players/{slug}.webp" alt="" loading="lazy" width="32" height="32"><div><b>{name}</b><small>{club}</small></div><div class="quote"><b>{price}</b><small class="green">{change}</small></div></div>' for slug,name,club,price,change in PLAYERS[:4 if phone else 5])

def actions(primary='Start trading',secondary='Explore FanPlay'):
    return f'<div class="actions"><a class="action primary" href="signup.html">{primary}</a><a class="action" href="fanplay.html">{secondary}<img src="assets/landing/arrow.svg" alt="" width="18" height="18"></a></div>'

def hero_media():
    return '''<div class="hero-media-wrap" role="region" aria-label="Fantrade trader on the toilet illustration">
      <div class="character-box">
        <div class="character-aura"></div>
        <img class="character-img" src="assets/landing/toilet-trader.jpg" alt="Passionate football fan trading player shares from the toilet" width="700" height="700" fetchpriority="high">
        <div class="chip chip-top">
          <span class="chip-pulse"></span>
          <span><b>Trade from anywhere</b> (yes, even here)</span>
        </div>
        <div class="chip chip-right">
          <span class="chip-badge">LIVE</span>
          <span><b>$Saka</b> 48.20 <span class="green">+6.40%</span></span>
        </div>
        <div class="chip chip-bottom">
          <span>⚡ Instant Settlement in <b>$FTR</b></span>
        </div>
      </div>
    </div>'''

def product_preview():
    candles = []
    values = [132,140,124,116,130,107,111,90,101,85,96,76,82,68,90,73,65,53,68,48,60,34,44,29,37,20,32,24]
    for i,y in enumerate(values):
        prev=values[max(0,i-1)]+7
        color='var(--accent)' if y<prev else 'var(--red)'
        candles.append(f'<path d="M{i*12+12} {min(y,prev)-9}V{max(y,prev)+9}" stroke="{color}"/><rect x="{i*12+8}" y="{min(y,prev)}" width="8" height="{max(3,abs(prev-y))}" rx="1" fill="{color}"/>')
    return '''<div class="product-preview" role="img" aria-label="Fantrade on desktop and mobile: player markets, a Saka price chart and your portfolio. Illustrative prices.">
      <div class="monitor"><div class="screen"><div class="screen-top"><b class="screen-brand">fantrade</b><span>Markets &nbsp; Dream Clubs &nbsp; FanPlay</span><span>128,450 $FTR</span></div><div class="screen-body">
      <div class="market-list"><span class="micro-label">Player markets</span>''' + rows() + '''</div><div class="chart-area"><div class="chart-title"><img src="assets/players/saka.webp" alt="" loading="lazy"><b>Saka / FTR</b></div><div class="chart-price">48.20 <small class="green">+6.40%</small></div><div class="chart-tools"><b>1D</b><span>1W</span><span>1M</span><span>1Y</span><span>All time</span></div><svg class="price-chart" viewBox="0 0 360 175" aria-hidden="true">''' + ''.join(candles) + '''</svg><div class="chart-bottom"><span>Holdings</span><span>Open orders</span><span>Activity</span></div></div>
      <div class="order-preview"><div class="order-tabs"><b>Buy</b><span>Sell</span></div><span class="micro-label">Market order</span><div class="order-field"><small>Player share</small>$Saka</div><div class="order-field"><small>Quantity</small>10 shares</div><div class="order-note"><span>Price</span><span>48.20 FTR</span></div><div class="order-note"><span>Subtotal</span><span>482.00 FTR</span></div><div class="order-buy">Review order</div></div></div></div></div><div class="monitor-stand"></div>
      <div class="phone"><div class="phone-status"><b>9:41</b><span class="phone-notch"></span><span>▰</span></div><div class="phone-head">Your portfolio</div><div class="phone-balance">128,450<span style="font-size:.36em"> FTR</span></div><div class="phone-gain">+6.42% this week</div><div class="phone-actions"><span>Buy shares</span><span>FanPlay</span><span>My club</span></div><div class="phone-tabs"><b>Watchlist</b><span>All players</span></div>''' + rows(True) + '''<div class="phone-nav"><span>Home</span><span>Markets</span><span>FanPlay</span><span>Assets</span></div></div></div>'''

def feature(label,title,art,href):
    return f'<a class="feature" href="{href}"><span class="eyebrow">{label}</span><h3>{title}</h3>{art}</a>'

def build_landing():
    ranking='<div class="feature-art ranking" aria-hidden="true">'
    for i,(slug,name,points) in enumerate([('saka','Zero FC','812 FP'),('haaland','North Bank XI','786 FP'),('mbappe','The Galácticos','754 FP'),('palmer','Blue Revolution','721 FP')]):
        ranking+=f'<div class="rank-row"><span class="medal">{["🥇","🥈","🥉","4"][i]}</span><img src="assets/players/{slug}.webp" alt="" loading="lazy"><div>{name}<small>Matchday 06</small></div><span class="points">{points}</span></div>'
    ranking+='</div>'
    squad='<div class="feature-art" aria-hidden="true"><div class="squad-mini"><span>ZERO FC &nbsp; · &nbsp; 4–3–3</span><div class="mini-pitch">'
    for slug,name,left,top in [('haaland','Haaland',50,8),('saka','Saka',22,70),('bruno','Bruno',78,70),('saliba','Saliba',50,122)]:
        squad+=f'<div class="mini-player" style="left:{left}%;top:{top}px"><img src="assets/players/{slug}.webp" alt="" loading="lazy">{name}</div>'
    squad+='</div></div></div>'
    notice='<div class="feature-art notice-art" aria-hidden="true"><div class="notification"><span class="notification-icon">ft</span><div><b>Matchday 06 settled</b><small><span class="green">+6,200 $FTR</span> · Your club made the top 20.</small></div><time>9:41 AM</time></div></div>'
    signup='''<div class="feature-art signup-art" aria-hidden="true"><div class="signup-option"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m3 6 9 7 9-7"/></svg>Create your Fantrade account</div><div class="signup-option dark">Explore the player market <span>→</span></div><svg class="cursor" viewBox="0 0 36 44"><path d="M4 3 29 25l-12 1 5 12-7 3-5-12-9 8Z" fill="#f0efff" stroke="#9e9bc7" stroke-width="2"/></svg></div>'''
    coins='<div class="feature-art coin-art" aria-hidden="true"><div class="token"><span>$FTR</span></div><div class="token small"><span>10M</span></div></div>'
    entry='''<div class="feature-art entry-art" aria-hidden="true"><div class="entry-slip"><small>FANPLAY · MATCHDAY 06</small><b>Back your football IQ.</b><div class="entry-line"><span>Entry</span><strong>$Saka · Solo</strong></div><div class="entry-line"><span>Scoring</span><strong>Goals + assists + more</strong></div><div class="entry-confirm"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 12 4 4L19 6"/></svg>Ready for matchday</div></div></div>'''
    features=''.join([
        feature('Leaderboard','make your name.<br>climb the leaderboard.',ranking,'leaderboard.html'),
        feature('Dream Clubs','your players.<br>your dream club.',squad,'clubs.html'),
        feature('Alerts','every goal. every trade.<br>stay in the know.',notice,'notifications.html'),
        feature('Easy onboarding','your first share is<br>just the beginning.',signup,'signup.html'),
        feature('Real ownership','10 million shares.<br>one football economy.',coins,'how-it-works.html'),
        feature('FanPlay','turn football knowledge<br>into matchday points.',entry,'fanplay.html'),
    ])
    html='''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#050505"><meta name="description" content="Trade shares in football players, build your Dream Club and put your football knowledge into play with FanPlay. Welcome to Fantrade."><title>Fantrade — Own the game.</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Montserrat:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"><link rel="preload" as="image" href="assets/landing/toilet-trader.jpg"><style>'''+CSS+'''</style></head><body><a class="skip" href="#main">Skip to content</a><div class="landing"><header class="masthead"><a class="brand" href="index.html" aria-label="Fantrade home">fantrade<span class="brand-dot">.</span></a><nav class="nav-right" aria-label="Main navigation"><a class="nav-link" href="exchange.html">Explore players</a><a class="nav-link" href="how-it-works.html">How it works</a><a class="nav-login" href="signin.html">Log in</a><button class="menu-toggle" id="landingMenu" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="landingNav"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button></nav></header><nav class="mobile-menu" id="landingNav" aria-label="Mobile navigation" inert><a href="exchange.html">Explore players</a><a href="clubs.html">Dream Clubs</a><a href="fanplay.html">FanPlay</a><a href="how-it-works.html">How it works</a><a href="signup.html">Create account</a></nav><main id="main"><section class="hero" aria-labelledby="heroTitle"><div class="hero-pill"><span class="dot"></span> The Football Player Stock Market</div><div class="wordmark" aria-hidden="true">fantrade</div><h1 id="heroTitle">where football fans<br><span>own the game.</span></h1><p class="hero-copy">Trade real fractional shares in world-class footballers. Build your dream club squad. Put your football IQ into play anytime, anywhere.</p>'''+actions()+hero_media()+'''</section><section class="anywhere" aria-labelledby="anywhereTitle"><div class="section-heading"><span class="eyebrow">YOUR FOOTBALL WORLD, ON WEB</span><h2 id="anywhereTitle">trade from anywhere.<br>stay close to the game.</h2><p>From your phone to your desktop — your players, club and matchday in one place.</p></div>'''+product_preview()+'''</section><section class="features" aria-labelledby="featuresTitle"><div class="section-heading"><span class="eyebrow">THE FOOTBALL ECONOMY</span><h2 id="featuresTitle">more than a spectator.</h2><p>The sports trading ecosystem built around passion, performance and true ownership.</p></div><div class="feature-grid">'''+features+'''</div></section><section class="final-cta" aria-labelledby="finalTitle"><img class="legends" src="assets/landing/legends.webp" alt="" loading="lazy" aria-hidden="true"><img class="orbit" src="assets/landing/outer-circle.webp" alt="" loading="lazy" aria-hidden="true"><img class="orbit inner" src="assets/landing/inner-circle.webp" alt="" loading="lazy" aria-hidden="true"><div class="final-copy"><h2 id="finalTitle">a trading platform<br>for the football in us.</h2><p>Start with a share in a player you believe in.<br>Your squad starts right here.</p>'''+actions()+'''</div></section></main><footer class="footer"><div class="footer-top"><div class="footer-brand"><a class="brand" href="index.html">fantrade<span class="brand-dot">.</span></a><p>where football fans<br>own the game.</p></div><div class="footer-col"><h2>Platform</h2><a href="exchange.html">Player market</a><a href="clubs.html">Dream Clubs</a><a href="fanplay.html">FanPlay</a><a href="leaderboard.html">Leaderboard</a></div><div class="footer-col"><h2>Get started</h2><a href="how-it-works.html">How it works</a><a href="signup.html">Create account</a><a href="signin.html">Log in</a><a href="ftr.html">$FTR wallet</a></div><div class="footer-col"><h2>Your Fantrade</h2><a href="portfolio.html">Portfolio</a><a href="account.html">Your profile</a><a href="settings-play.html">Responsible play</a><a href="settings-data.html">Data &amp; account</a></div></div><p class="copyright">© 2026 Fantrade.</p><p class="demo-note">Prototype experience. Player prices, balances and rewards shown are illustrative.</p></footer></div><script>
const toggle=document.getElementById('landingMenu'), menu=document.getElementById('landingNav');
function setMenu(open){toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Close menu':'Open menu');menu.classList.toggle('open',open);menu.inert=!open;}
toggle.addEventListener('click',()=>setMenu(toggle.getAttribute('aria-expanded')!=='true'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){setMenu(false);toggle.focus();}});
document.addEventListener('click',e=>{if(!menu.contains(e.target)&&!toggle.contains(e.target))setMenu(false);});
menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
matchMedia('(min-width:800px)').addEventListener('change',e=>{if(e.matches)setMenu(false);});
</script></body></html>'''
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    print('built index.html — Fantrade brand & toilet trader hero')

if __name__=='__main__':
    build_landing()
