"""Bundle index.html into one self-contained HTML file.

Usage:
    python3 scripts/build_standalone.py dist/minimum-wage-globe.html [--fragment]

--fragment drops the <!doctype>/<html>/<head>/<body> wrapper and meta tags, for
hosts (such as Claude Artifacts) that add their own document skeleton.

Data scripts are inlined; d3 and topojson-client load from pinned CDN URLs.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CDN = {
    "vendor/d3.min.js": "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js",
    "vendor/topojson-client.min.js": "https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js",
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    fragment = "--fragment" in sys.argv
    out = Path(args[0] if args else ROOT / "dist" / "minimum-wage-globe.html")
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    def swap(m):
        src = m.group(1)
        if src in CDN:
            return f'<script src="{CDN[src]}"></script>'
        body = (ROOT / src).read_text(encoding="utf-8")
        return "<script>\n" + body + "\n</script>"

    html = re.sub(r'<script src="([^"]+)"></script>', swap, html)
    if fragment:
        html = re.sub(r"<!doctype html>\s*|</?html[^>]*>\s*|</?head>\s*|</?body>\s*|<meta [^>]*>\s*", "", html, flags=re.I)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
