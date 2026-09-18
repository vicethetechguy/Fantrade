"""Download the Fomo artwork selected for the requested landing-page reference."""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'landing'
FILES = {
    'space-bg.webp': '/images/landing/space-bg.webp',
    'astronaut.webp': '/images/landing/astronaut.webp',
    'astronaut-mobile.webp': '/images/landing/astronaut-mobile.webp',
    'legends.webp': '/images/landing/legends.webp',
    'inner-circle.webp': '/images/landing/inner-circle.webp',
    'outer-circle.webp': '/images/landing/outer-circle.webp',
    'Aeonik-Regular.woff2': '/fonts/Aeonik-Regular.woff2',
    'Aeonik-Medium.woff2': '/fonts/Aeonik-Medium.woff2',
}

if __name__ == '__main__':
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, path in FILES.items():
        url = 'https://fomo.family' + path
        target = ASSETS / name
        if not target.exists():
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=45) as response:
                target.write_bytes(response.read())
        print(name, target.stat().st_size)
    (ASSETS / 'sources.json').write_text(json.dumps({
        'reference': 'https://fomo.family/',
        'description': 'Reference artwork and typography reused at the project owner\'s request; original artwork belongs to its respective owners. Fantrade content and product previews are implemented separately.',
        'assets': {
            **{name: 'https://fomo.family' + path for name, path in FILES.items()},
            'arrow.svg': 'https://fomo.family/assets/arrow-v2-K0J5ysgQ.js',
        },
    }, indent=2) + '\n', encoding='utf-8')
