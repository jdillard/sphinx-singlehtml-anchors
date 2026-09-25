"""Target-ID and reference rewriting for merged singlehtml doctrees."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator, Mapping

from docutils import nodes
from sphinx import addnodes
from sphinx.util import logging

TargetKey = tuple[str, str]
TargetMap = dict[TargetKey, str]

logger = logging.getLogger(__name__)


def document_target_id(docname: str) -> str:
    """Return the existing singlehtml document-level target ID."""
    return f"document-{docname}"


def qualified_target_id(docname: str, target_id: str) -> str:
    """Return a document-qualified target ID."""
    return f"{document_target_id(docname)}--{target_id}"


def _collision_fallback_id(
    target_id: str,
    key: TargetKey,
    unavailable_ids: set[str],
) -> str:
    """Return a stable unused ID for a colliding document/target pair."""
    digest = hashlib.sha256(f"{key[0]}\0{key[1]}".encode()).hexdigest()[:16]
    stem = f"{target_id}--{digest}"
    candidate = stem
    suffix = 2
    while candidate in unavailable_ids:
        candidate = f"{stem}-{suffix}"
        suffix += 1
    unavailable_ids.add(candidate)
    return candidate


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
    document_owners: dict[str, tuple[str, None]] = {
        document_target_id(docname): (docname, None) for docname in all_docnames
    }
    scoped_nodes = list(_iter_scoped_nodes(tree, root_docname))
    keys_by_target_id: dict[str, list[TargetKey]] = {}
    seen_keys: set[TargetKey] = set()

    for docname, node in scoped_nodes:
        if not isinstance(node, nodes.Element):
            continue
        old_ids: list[str] = node.get("ids", [])
        retained_ids: list[str] = []
        for old_id in old_ids:
            key = (docname, old_id)
            new_id = qualified_target_id(docname, old_id)
            if key in seen_keys:
                logger.warning(
                    "singlehtml target %r occurs more than once in %r; "
                    "keeping the first occurrence and removing this duplicate ID",
                    old_id,
                    docname,
                    type="singlehtml",
                    subtype="duplicate_target",
                )
                continue
            seen_keys.add(key)
            retained_ids.append(old_id)
            keys_by_target_id.setdefault(new_id, []).append(key)
        if retained_ids != old_ids:
            node["ids"] = retained_ids

    unavailable_ids = set(document_owners) | set(keys_by_target_id)
    for new_id, keys in keys_by_target_id.items():
        document_owner = document_owners.get(new_id)
        if len(keys) == 1 and document_owner is None:
            mapping[keys[0]] = new_id
            continue

        owners: list[TargetKey | tuple[str, None]] = list(keys)
        if document_owner is not None:
            owners.append(document_owner)
        owner_summary = ", ".join(repr(owner) for owner in sorted(owners, key=repr))
        for key in sorted(keys):
            fallback_id = _collision_fallback_id(new_id, key, unavailable_ids)
            mapping[key] = fallback_id
            logger.warning(
                "document-qualified singlehtml target %r is produced by %s; "
                "using fallback ID %r for %r",
                new_id,
                owner_summary,
                fallback_id,
                key,
                type="singlehtml",
                subtype="target_collision",
            )

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
