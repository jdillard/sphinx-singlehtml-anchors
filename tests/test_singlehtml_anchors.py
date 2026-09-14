from __future__ import annotations

import io
import zlib
from html.parser import HTMLParser
from pathlib import Path

from sphinx.application import Sphinx

ROOT = Path(__file__).parent / "roots" / "anchors"


class OutputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.classes: list[str] = []

    def handle_starttag(
        self,
        _tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        if target_id := attributes.get("id"):
            self.ids.append(target_id)
        if href := attributes.get("href"):
            self.hrefs.append(href)
        if classes := attributes.get("class"):
            self.classes.extend(classes.split())


def build(tmp_path: Path, builder: str) -> tuple[Path, str]:
    outdir = tmp_path / builder
    status = io.StringIO()
    warning = io.StringIO()
    app = Sphinx(
        srcdir=str(ROOT),
        confdir=str(ROOT),
        outdir=str(outdir),
        doctreedir=str(tmp_path / f"{builder}-doctrees"),
        buildername=builder,
        status=status,
        warning=warning,
        freshenv=True,
    )
    app.build(force_all=True)
    assert app.statuscode == 0
    assert "sphinx-singlehtml-anchors" not in warning.getvalue()
    assert "undefined label" not in warning.getvalue()
    return outdir, status.getvalue()


def parse_html(path: Path) -> tuple[OutputParser, str]:
    html = path.read_text(encoding="utf-8")
    parser = OutputParser()
    parser.feed(html)
    return parser, html


def inventory_body(path: Path) -> str:
    content = path.read_bytes().split(b"\n", 4)
    assert len(content) == 5
    return zlib.decompress(content[4]).decode()


def test_singlehtml_ids_are_document_qualified_and_unique(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "singlehtml")
    parser, _html = parse_html(outdir / "index.html")

    assert len(parser.ids) == len(set(parser.ids))
    assert {
        "document-index",
        "document-doc1",
        "document-doc2",
        "document-index--anchor-test",
        "document-doc1--first-document",
        "document-doc1--purpose",
        "document-doc2--second-document",
        "document-doc2--purpose",
        "document-doc1--id1",
        "document-doc1--id2",
        "document-doc2--id1",
        "document-doc2--id2",
    } <= set(parser.ids)


def test_every_internal_link_resolves_to_one_target(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "singlehtml")
    parser, _html = parse_html(outdir / "index.html")
    id_counts = {target_id: parser.ids.count(target_id) for target_id in parser.ids}

    internal_hrefs = [href for href in parser.hrefs if href.startswith("#") and href != "#"]
    assert internal_hrefs
    for href in internal_hrefs:
        assert href.count("#") == 1
        assert id_counts.get(href[1:], 0) == 1, href

    assert "#document-index" in internal_hrefs
    assert "#document-doc1--purpose" in internal_hrefs
    assert "#document-doc2--purpose" in internal_hrefs
    assert "#document-doc1--id2" in internal_hrefs
    assert "#document-doc2--id2" in internal_hrefs


def test_section_and_figure_numbers_are_preserved(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "singlehtml")
    parser, _html = parse_html(outdir / "index.html")

    assert parser.classes.count("section-number") >= 4
    assert parser.classes.count("caption-number") == 2


def test_inventory_uses_qualified_targets(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "singlehtml")
    inventory = inventory_body(outdir / "objects.inv")

    assert "doc1-label std:label" in inventory
    assert "#document-doc1--doc1-label" in inventory
    assert "#document-doc1#doc1-label" not in inventory


def test_regular_html_builder_is_unchanged(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "html")
    parser, _html = parse_html(outdir / "doc1.html")

    assert "purpose" in parser.ids
    assert "document-doc1--purpose" not in parser.ids
