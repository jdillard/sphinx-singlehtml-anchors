"""Target-ID and reference rewriting for merged singlehtml doctrees."""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from docutils import nodes
from sphinx import addnodes
from sphinx.errors import ExtensionError

TargetKey = tuple[str, str]
TargetMap = dict[TargetKey, str]


def document_target_id(docname: str) -> str:
    """Return the existing singlehtml document-level target ID."""
    return f"document-{docname}"


def qualified_target_id(docname: str, target_id: str) -> str:
    """Return a document-qualified target ID."""
    return f"{document_target_id(docname)}--{target_id}"


def _iter_scoped_nodes(
    node: nodes.Node,
    docname: str,
) -> Iterator[tuple[str, nodes.Node]]:
    if isinstance(node, addnodes.start_of_file):
        docname = node["docname"]

    yield docname, node
    for child in node.children:
        yield from _iter_scoped_nodes(child, docname)


def qualify_doctree_targets(
    tree: nodes.document,
    root_docname: str,
    all_docnames: set[str],
) -> TargetMap:
    """Qualify every target and its references in a merged singlehtml doctree."""
    mapping: TargetMap = {}
    owners: dict[str, TargetKey | tuple[str, None]] = {
        document_target_id(docname): (docname, None) for docname in all_docnames
    }
    scoped_nodes = list(_iter_scoped_nodes(tree, root_docname))

    for docname, node in scoped_nodes:
        if not isinstance(node, nodes.Element):
            continue
        old_ids: list[str] = node.get("ids", [])
        for old_id in old_ids:
            key = (docname, old_id)
            new_id = qualified_target_id(docname, old_id)
            if key in mapping:
                raise ExtensionError(
                    f"singlehtml target {old_id!r} occurs more than once in {docname!r}"
                )
            if new_id in owners:
                other = owners[new_id]
                raise ExtensionError(
                    "document-qualified singlehtml target collision between "
                    f"{key!r} and {other!r}: {new_id!r}"
                )
            mapping[key] = new_id
            owners[new_id] = key

    for docname, node in scoped_nodes:
        if not isinstance(node, nodes.Element):
            continue

        current_ids: list[str] = node.get("ids", [])
        node["ids"] = [mapping[(docname, old_id)] for old_id in current_ids]

        if isinstance(refid := node.get("refid"), str):
            node["refid"] = mapping.get((docname, refid), refid)

        if backrefs := node.get("backrefs"):
            node["backrefs"] = [mapping.get((docname, backref), backref) for backref in backrefs]

        if isinstance(refuri := node.get("refuri"), str):
            node["refuri"] = rewrite_reference_uri(
                refuri,
                source_docname=docname,
                mapping=mapping,
                all_docnames=all_docnames,
            )

    root_target = nodes.target("", ids=[document_target_id(root_docname)])
    tree.insert(0, root_target)
    return mapping


def rewrite_reference_uri(
    uri: str,
    *,
    source_docname: str | None,
    mapping: Mapping[TargetKey, str],
    all_docnames: set[str],
) -> str:
    """Rewrite one same-page URI to its document-qualified target."""
    if not uri.startswith("#"):
        return uri

    fragment = uri[1:]
    for target_docname in sorted(all_docnames, key=len, reverse=True):
        document_id = document_target_id(target_docname)
        if fragment == document_id:
            return uri

        prefix = f"{document_id}#"
        if fragment.startswith(prefix):
            old_id = fragment.removeprefix(prefix)
            new_id = mapping.get((target_docname, old_id))
            return f"#{new_id}" if new_id is not None else uri

    if source_docname is not None:
        new_id = mapping.get((source_docname, fragment))
        if new_id is not None:
            return f"#{new_id}"
    return uri


def rewrite_toctree_references(
    tree: nodes.Node,
    *,
    mapping: Mapping[TargetKey, str],
    all_docnames: set[str],
) -> None:
    """Rewrite references in a separately generated global or local toctree."""
    for reference in tree.findall(nodes.reference):
        if isinstance(refuri := reference.get("refuri"), str):
            reference["refuri"] = rewrite_reference_uri(
                refuri,
                source_docname=None,
                mapping=mapping,
                all_docnames=all_docnames,
            )
