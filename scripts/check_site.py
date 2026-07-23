"""Local, dependency-free checks for the public static website."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://yonesit.github.io"
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = 0
        self.h1 = 0
        self.description = False
        self.canonical: list[str] = []
        self.robots = ""
        self.hrefs: list[str] = []
        self.ids: list[str] = []
        self.jsonld: list[str] = []
        self._title_depth = 0
        self._jsonld_depth = 0
        self._jsonld_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "title":
            self.title += 1
            self._title_depth = 1
        elif self._title_depth:
            self._title_depth += 1
        if tag == "h1":
            self.h1 += 1
        if data.get("id"):
            self.ids.append(data["id"] or "")
        if tag == "a" and "href" in data:
            self.hrefs.append(data["href"] or "")
        if tag == "link" and data.get("rel", "").lower() == "canonical":
            self.canonical.append(data.get("href", "") or "")
        if tag == "meta" and data.get("name", "").lower() == "description":
            self.description = bool(data.get("content", "").strip())
        if tag == "meta" and data.get("name", "").lower() == "robots":
            self.robots = data.get("content", "") or ""
        if tag == "script" and data.get("type") == "application/ld+json":
            self._jsonld_depth = 1
            self._jsonld_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if self._title_depth:
            self._title_depth -= 1
        if tag == "script" and self._jsonld_depth:
            self.jsonld.append("".join(self._jsonld_buffer).strip())
            self._jsonld_depth = 0

    def handle_data(self, data: str) -> None:
        if self._jsonld_depth:
            self._jsonld_buffer.append(data)


def local_target(href: str) -> Path | None:
    if not href or href == "#":
        fail("leerer oder nutzloser Link: href={!r}".format(href))
        return None
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path or "index.html"
    if path.startswith("/"):
        path = path[1:]
    return ROOT / path


def check_html() -> None:
    for path in sorted(ROOT.glob("*.html")):
        parser = SiteParser()
        parser.feed(path.read_text(encoding="utf-8"))
        indexed = path.name not in {"404.html", "google3c3f89b6a3da8de0.html"} and "noindex" not in parser.robots.lower()
        if indexed:
            if parser.title != 1:
                fail(f"{path.name}: genau ein title erwartet")
            if not parser.description:
                fail(f"{path.name}: Meta-Description fehlt")
            if len(parser.canonical) != 1:
                fail(f"{path.name}: genau eine Canonical-URL erwartet")
            if parser.h1 != 1:
                fail(f"{path.name}: genau ein h1 erwartet")
        if len(parser.ids) != len(set(parser.ids)):
            fail(f"{path.name}: doppelte IDs")
        for href in parser.hrefs:
            target = local_target(href)
            if target and not target.exists():
                fail(f"{path.name}: internes Ziel fehlt: {href}")
        for block in parser.jsonld:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                fail(f"{path.name}: ungültiges JSON-LD: {exc}")


def check_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        fail(f"sitemap.xml: ungültiges XML: {exc}")
        return
    for loc in root.findall("{*}url/{*}loc"):
        url = (loc.text or "").strip()
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "yonesit.github.io":
            fail(f"sitemap.xml: URL gehört nicht zur Website: {url}")
        target = ROOT / (parsed.path.lstrip("/") or "index.html")
        if not target.exists():
            fail(f"sitemap.xml: lokale Seite fehlt: {url}")


def check_text() -> None:
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and p.name != "check_site.py"]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"<<<<<<<|=======|>>>>>>>", text):
            fail(f"Konfliktmarker in {path.relative_to(ROOT)}")
        if re.search(r"(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?\S+", text, re.I):
            fail(f"mögliche Zugangsdaten in {path.relative_to(ROOT)}")
        if re.search(r"\b(?:\+49|0049)\s?\d[\d\s/-]{7,}\b", text):
            fail(f"mögliche Telefonnummer in {path.relative_to(ROOT)}")


def check_robots() -> None:
    text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "User-agent: *" not in text or "Allow: /" not in text:
        fail("robots.txt: Allow-Regel fehlt")
    if "Sitemap: " + SITE_ORIGIN + "/sitemap.xml" not in text:
        fail("robots.txt: falsche oder fehlende Sitemap")


check_html()
check_sitemap()
check_robots()
check_text()
if ERRORS:
    print("Site check FAILED")
    print("\n".join(f"- {error}" for error in ERRORS))
    sys.exit(1)
print("Site check passed: HTML, interne Links, JSON-LD, Sitemap, robots.txt und Sicherheitsprüfungen.")
print("Externe Links wurden nicht per Netzwerk validiert.")
