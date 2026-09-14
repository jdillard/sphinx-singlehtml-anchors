"""Replacement singlehtml builder with document-qualified target IDs."""

from __future__ import annotations

import re
import zlib

from docutils import nodes
from sphinx.builders.singlehtml import SingleFileHTMLBuilder
from sphinx.errors import ExtensionError

from sphinx_singlehtml_anchors.targets import (
    TargetMap,
    qualified_target_id,
    qualify_doctree_targets,
    rewrite_reference_uri,
    rewrite_toctree_references,
)

_INVENTORY_LINE_RE = re.compile(r"(.+?)\s+(\S+)\s+(-?\d+)\s+?(\S*)\s+(.*)")


class DocumentQualifiedSingleHTMLBuilder(SingleFileHTMLBuilder):
    """Single-page HTML builder that retains each target's source document."""

    name = "singlehtml"
    _qualified_target_map: TargetMap | None = None
    _qualified_body = False

    def assemble_doctree(self) -> nodes.document:
        """Assemble the doctree and qualify targets once."""
        self._qualified_body = False
        self._qualified_target_map = None
        tree = super().assemble_doctree()
        if not self._qualified_body:
            self.fix_refuris(tree)
        return tree

    def fix_refuris(self, tree: nodes.Node) -> None:
        """Qualify body targets or rewrite a separately generated toctree."""
        all_docnames = set(self.env.all_docs)
        if isinstance(tree, nodes.document):
            if self._qualified_target_map is None:
                self._qualified_target_map = qualify_doctree_targets(
                    tree,
                    self.config.root_doc,
                    all_docnames,
                )
            self._qualified_body = True
            return

        if self._qualified_target_map is None:
            raise ExtensionError("singlehtml toctree was rendered before target IDs were qualified")
        rewrite_toctree_references(
            tree,
            mapping=self._qualified_target_map,
            all_docnames=all_docnames,
        )

    def render_partial(self, node: nodes.Node | None) -> dict[str, str]:
        """Rewrite toctree references before Sphinx renders a partial tree."""
        if node is not None and self._qualified_target_map is not None:
            rewrite_toctree_references(
                node,
                mapping=self._qualified_target_map,
                all_docnames=set(self.env.all_docs),
            )
        return super().render_partial(node)

    def assemble_toc_secnumbers(self) -> dict[str, dict[str, tuple[int, ...]]]:
        """Assemble section numbers using qualified target IDs."""
        mapping = self._require_target_map()
        new_secnumbers: dict[str, tuple[int, ...]] = {}
        for docname, secnums in self.env.toc_secnumbers.items():
            for anchor, secnum in secnums.items():
                if anchor:
                    old_id = anchor.removeprefix("#")
                    new_id = mapping.get(
                        (docname, old_id),
                        qualified_target_id(docname, old_id),
                    )
                    alias = f"{docname}/#{new_id}"
                else:
                    alias = f"{docname}/"
                new_secnumbers[alias] = secnum
        return {self.config.root_doc: new_secnumbers}

    def assemble_toc_fignumbers(
        self,
    ) -> dict[str, dict[str, dict[str, tuple[int, ...]]]]:
        """Assemble figure numbers using qualified target IDs."""
        mapping = self._require_target_map()
        new_fignumbers: dict[str, dict[str, tuple[int, ...]]] = {}
        for docname, fignumlist in self.env.toc_fignumbers.items():
            for figtype, fignums in fignumlist.items():
                alias = f"{docname}/{figtype}"
                qualified = new_fignumbers.setdefault(alias, {})
                for old_id, fignum in fignums.items():
                    new_id = mapping.get(
                        (docname, old_id),
                        qualified_target_id(docname, old_id),
                    )
                    qualified[new_id] = fignum
        return {self.config.root_doc: new_fignumbers}

    def dump_inventory(self) -> None:
        """Write the inventory and replace old singlehtml target fragments."""
        super().dump_inventory()
        inventory_path = self.outdir / "objects.inv"
        content = inventory_path.read_bytes()
        header_parts = content.split(b"\n", 4)
        if len(header_parts) != 5:
            raise ExtensionError("could not parse the generated Sphinx inventory header")

        header = b"\n".join(header_parts[:4]) + b"\n"
        body = zlib.decompress(header_parts[4]).decode()
        rewritten = "".join(self._rewrite_inventory_line(line) for line in body.splitlines(True))
        inventory_path.write_bytes(header + zlib.compress(rewritten.encode(), level=9))

    def _rewrite_inventory_line(self, line: str) -> str:
        newline = "\n" if line.endswith("\n") else ""
        match = _INVENTORY_LINE_RE.fullmatch(line.rstrip("\n"))
        if match is None:
            return line

        fullname, object_type, priority, location, display_name = match.groups()
        if location.endswith("$"):
            location = location[:-1] + fullname
        location = rewrite_reference_uri(
            location,
            source_docname=None,
            mapping=self._require_target_map(),
            all_docnames=set(self.env.all_docs),
        )
        return f"{fullname} {object_type} {priority} {location} {display_name}{newline}"

    def _require_target_map(self) -> TargetMap:
        if self._qualified_target_map is None:
            raise ExtensionError("singlehtml target IDs have not been qualified")
        return self._qualified_target_map
