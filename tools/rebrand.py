"""Apply the supplied October identity to source templates, not generated pages."""
from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
mark = ROOT / 'assets/brand/fantrade-mark-source.png'
data = base64.b64encode(mark.read_bytes()).decode()
for name, white in [('fantrade-mark.svg', False), ('fantrade-mark-white.svg', True)]:
    # Viewport trims the original's empty canvas; original pixels remain intact.
    filter_def = '<defs><filter id="white" color-interpolation-filters="sRGB"><feFlood flood-color="white"/><feComposite in2="SourceAlpha" operator="in"/></filter></defs>' if white else ''
    attr = ' filter="url(#white)"' if white else ''
    (mark.parent / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="680 10 890 694">{filter_def}<image width="2172" height="724" href="data:image/png;base64,{data}"{attr}/></svg>', encoding='utf-8')

replacements = {
    'assets/landing/fantrade-outline-logo.png': 'assets/brand/fantrade-mark-white.svg',
    'assets/landing/fantrade-logo.png': 'assets/brand/fantrade-mark.svg',
    'assets/fantrade-outline-logo.png': 'assets/brand/fantrade-mark-white.svg',
    'assets/fantrade-outline.png': 'assets/brand/fantrade-mark-white.svg',
    'assets/fantrade-logo.png': 'assets/brand/fantrade-mark.svg',
    'assets/logo.png': 'assets/brand/fantrade-mark.svg',
}
files = list((ROOT/'tools').glob('*.py')) + list((ROOT/'public').glob('*.css')) + list((ROOT/'public').glob('*.js')) + [ROOT/'admin.html']
for file in files:
    if file.name == 'rebrand.py':
        continue
    text = file.read_text(encoding='utf-8')
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"font-family:\s*(?:'Space Grotesk'|Space Grotesk|\"Space Grotesk\")[^;}\]\"]*", 'font-family:Montserrat,system-ui,sans-serif', text)
    text = text.replace("--head:'Space Grotesk'", "--head:'Montserrat'")
    text = text.replace("'Space Grotesk',Montserrat,sans-serif", 'Montserrat,system-ui,sans-serif')
    text = text.replace('Space Grotesk,sans-serif', 'Montserrat,system-ui,sans-serif')
    text = re.sub(r"@font-face\{font-family:Aeonik;[^}]*\}\n", '', text)
    if file.name == 'landing.py':
        text = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/[^\"]*" rel="stylesheet">', '<link rel="icon" href="assets/brand/fantrade-mark.svg" type="image/svg+xml">', text)
        text = text.replace('</style></head>', '</style><link rel="stylesheet" href="public/brand.css"></head>')
        text = text.replace('<span>fantrade<span class="brand-dot">.</span></span>', '<span>Fantrade</span>')
        text = text.replace('aria-hidden="true">fantrade</div>', 'aria-hidden="true">Fantrade</div>')
    if file.name == 'pages3.py':
        text = text.replace('class="home-claim-mark" src="assets/brand/fantrade-mark.svg"', 'class="home-claim-mark" src="assets/brand/fantrade-mark-white.svg"')
    file.write_text(text, encoding='utf-8')
