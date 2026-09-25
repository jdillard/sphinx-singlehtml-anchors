from __future__ import annotations

import io
import zlib
from html.parser import HTMLParser
from pathlib import Path

from sphinx.application import Sphinx

ROOT = Path(__file__).parent / "roots" / "anchors"
COLLISION_ROOT = Path(__file__).parent / "roots" / "collision"


class OutputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.links: list[dict[str, str | None]] = []
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
            if _tag == "a":
                self.links.append(attributes)
        if classes := attributes.get("class"):
            self.classes.extend(classes.split())


def build(
    tmp_path: Path,
    builder: str,
    *,
    root: Path = ROOT,
    expected_warnings: tuple[str, ...] = (),
) -> tuple[Path, str]:
    outdir = tmp_path / builder
    status = io.StringIO()
    warning = io.StringIO()
    app = Sphinx(
        srcdir=str(root),
        confdir=str(root),
        outdir=str(outdir),
        doctreedir=str(tmp_path / f"{builder}-doctrees"),
        buildername=builder,
        status=status,
        warning=warning,
        freshenv=True,
    )
    app.build(force_all=True)
    assert app.statuscode == 0
    warning_text = warning.getvalue()
    if not expected_warnings:
        assert "sphinx-singlehtml-anchors" not in warning_text
    else:
        for expected_warning in expected_warnings:
            assert expected_warning in warning_text
    assert "undefined label" not in warning_text
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
        "document-api__reference",
        "document-delimiter--reference",
        "document-index--anchor-test",
        "document-doc1--first-document",
        "document-doc1--purpose",
        "document-doc2--second-document",
        "document-doc2--purpose",
        "document-api__reference--function_name",
        "document-api__reference--Widget.__init__",
        "document-api__reference--Payload__Envelope",
        "document-delimiter--reference--target-name",
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
    assert "#document-delimiter--reference--target-name" in internal_hrefs


def test_collisions_warn_and_receive_stable_unique_fallback_ids(tmp_path: Path) -> None:
    warnings = (
        "[singlehtml.target_collision]",
        "[singlehtml.duplicate_target]",
    )
    outdir, _status = build(
        tmp_path / "first",
        "singlehtml",
        root=COLLISION_ROOT,
        expected_warnings=warnings,
    )
    parser, _html = parse_html(outdir / "index.html")

    assert len(parser.ids) == len(set(parser.ids))
    id_counts = {target_id: parser.ids.count(target_id) for target_id in parser.ids}
    internal_hrefs = [href for href in parser.hrefs if href.startswith("#") and href != "#"]
    for href in internal_hrefs:
        assert id_counts.get(href[1:], 0) == 1, href

    assert "document-collision--reference" in parser.ids
    fallback_id = "document-collision--reference--fa1411357bc096dc"
    assert fallback_id in parser.ids
    assert f"#{fallback_id}" in parser.hrefs
    assert "#document-collision--reference" in parser.hrefs
    assert parser.ids.count("document-collision--duplicate") == 1
    assert "#document-collision--duplicate" in parser.hrefs

    second_outdir, _status = build(
        tmp_path / "second",
        "singlehtml",
        root=COLLISION_ROOT,
        expected_warnings=warnings,
    )
    second_parser, _html = parse_html(second_outdir / "index.html")
    assert fallback_id in second_parser.ids

    inventory = inventory_body(outdir / "objects.inv")
    assert f"reference std:label -1 #{fallback_id} Reference" in inventory


def test_python_domain_references_use_document_qualified_targets(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "singlehtml")
    parser, _html = parse_html(outdir / "index.html")

    xrefs = {
        (link.get("title"), link["href"])
        for link in parser.links
        if link.get("title") in {"function_name", "Widget.__init__", "Payload__Envelope"}
    }
    assert {
        ("function_name", "#document-api__reference--function_name"),
        ("Widget.__init__", "#document-api__reference--Widget.__init__"),
        ("Payload__Envelope", "#document-api__reference--Payload__Envelope"),
    } <= xrefs


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
    assert "function_name py:function 1 #document-api__reference--function_name -" in inventory
    assert "Widget.__init__ py:method 1 #document-api__reference--Widget.__init__ -" in inventory
    assert "Payload__Envelope py:class 1 #document-api__reference--Payload__Envelope -" in inventory
    assert (
        "target--name std:label -1 "
        "#document-delimiter--reference--target-name Double-hyphen target" in inventory
    )


def test_regular_html_builder_is_unchanged(tmp_path: Path) -> None:
    outdir, _status = build(tmp_path, "html")
    parser, _html = parse_html(outdir / "doc1.html")

    assert "purpose" in parser.ids
    assert "document-doc1--purpose" not in parser.ids

    api_parser, _html = parse_html(outdir / "api__reference.html")
    assert {"function_name", "Widget.__init__", "Payload__Envelope"} <= set(api_parser.ids)
    assert not any(
        target_id.startswith("document-api__reference--") for target_id in api_parser.ids
    )

    index_parser, _html = parse_html(outdir / "index.html")
    assert "api__reference.html#function_name" in index_parser.hrefs
    assert "api__reference.html#Widget.__init__" in index_parser.hrefs
    assert "api__reference.html#Payload__Envelope" in index_parser.hrefs
    assert "delimiter--reference.html#target-name" in index_parser.hrefs
