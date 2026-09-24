"""Fetch and normalize football portraits from Wikimedia for local UI use."""

from __future__ import annotations

import io
import json
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import date
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "players"
USER_AGENT = "FantradePrototype/1.0 (local UI asset build)"
MANIFEST = OUT / "attribution.json"

PLAYERS = {
    "saka": "Bukayo Saka",
    "haaland": "Erling Haaland",
    "mbappe": "Kylian Mbappé",
    "vinicius": "Vinícius Júnior",
    "bellingham": "Jude Bellingham",
    "palmer": "Cole Palmer",
    "yamal": "Lamine Yamal",
    "musiala": "Jamal Musiala",
    "wirtz": "Florian Wirtz",
    "rodri": "Rodri (footballer, born 1996)",
    "foden": "Phil Foden",
    "pedri": "Pedri",
    "saliba": "William Saliba",
    "bruno": "Bruno Fernandes",
    "jackson": "Nicolas Jackson",
    "arteta": "Mikel Arteta",
    "pep": "Pep Guardiola",
    "maresca": "Enzo Maresca",
    "rice": "Declan Rice",
    "odegaard": "Martin Ødegaard",
    "davies": "Alphonso Davies",
    "vandijk": "Virgil van Dijk",
    "white": "Ben White (footballer)",
    "raya": "David Raya",
    "alisson": "Alisson Becker",
    "gabriel": "Gabriel Magalhães",
    # The women's game
    "bonmati": "Aitana Bonmatí",
    "putellas": "Alexia Putellas",
    "russo": "Alessia Russo",
    "james": "Lauren James",
    "kerr": "Sam Kerr",
    "williamson": "Leah Williamson",
    "earps": "Mary Earps",
    "wiegman": "Sarina Wiegman",
}


def request(url: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=45) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            retryable = not isinstance(error, HTTPError) or error.code == 429 or error.code >= 500
            if not retryable or attempt == 5:
                raise
            time.sleep(min(2 ** attempt * 3, 30))
    raise RuntimeError(f"Unable to download {url}") from last_error


def request_json(base: str, params: dict[str, str]) -> dict:
    url = base + "?" + urllib.parse.urlencode(params)
    return json.loads(request(url).decode("utf-8"))


def request_bytes(url: str) -> bytes:
    return request(url)


def value(meta: dict, key: str) -> str:
    return meta.get(key, {}).get("value", "")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, str]] = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # A file with no record of where it came from is not kept: it is replaced
    # by the Wikimedia portrait, so the record written below always describes
    # the picture that is actually on disk.
    sourced = {slug for slug, entry in manifest.items()
               if entry.get("source") and entry.get("license")}
    missing: list[str] = []

    for slug, article in PLAYERS.items():
        data = request_json(
            "https://en.wikipedia.org/w/api.php",
            {
                "action": "query",
                "format": "json",
                "redirects": "1",
                "prop": "pageimages",
                "piprop": "thumbnail|name",
                "pithumbsize": "480",
                "titles": article,
            },
        )
        page = next(iter(data["query"]["pages"].values()))
        thumbnail = page.get("thumbnail", {}).get("source")
        image_name = page.get("pageimage")
        if not thumbnail or not image_name:
            # Not every article has a usable portrait. Leave this one to the
            # app's initials rather than stopping the whole run.
            print(f"no portrait on Wikipedia for {article}; skipped")
            missing.append(article)
            continue

        target = OUT / f"{slug}.webp"
        if not target.exists() or slug not in sourced:
            image = Image.open(io.BytesIO(request_bytes(thumbnail))).convert("RGB")
            image.thumbnail((480, 480), Image.Resampling.LANCZOS)
            image.save(target, "WEBP", quality=84, method=6)

        commons = request_json(
            "https://commons.wikimedia.org/w/api.php",
            {
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "titles": "File:" + image_name,
            },
        )
        common_page = next(iter(commons["query"]["pages"].values()))
        info = common_page.get("imageinfo", [{}])[0]
        metadata = info.get("extmetadata", {})
        manifest[slug] = {
            "name": page.get("title", article),
            "file": f"assets/players/{slug}.webp",
            "article": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page.get("title", article).replace(" ", "_")),
            "source": info.get("descriptionurl", thumbnail),
            "license": value(metadata, "LicenseShortName"),
            "artist": value(metadata, "Artist"),
            "credit": value(metadata, "Credit"),
            "fetched": date.today().isoformat(),
        }
        MANIFEST.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"saved {target.name}: {page.get('title', article)}")
        time.sleep(1.25)

    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if missing:
        print("no portrait found for: " + ", ".join(missing))
    print("done. Rebuild the pages so the new photos are picked up.")


if __name__ == "__main__":
    main()
