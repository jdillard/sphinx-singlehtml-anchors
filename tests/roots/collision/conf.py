from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive

project = "singlehtml-anchor-collision"
extensions = ["sphinx_singlehtml_anchors"]
html_theme = "basic"


class DuplicateTargets(Directive):
    has_content = False

    def run(self) -> list[nodes.Node]:
        paragraph = nodes.paragraph()
        paragraph += nodes.reference("", "duplicate target", refid="duplicate")
        return [
            nodes.target("", ids=["duplicate"]),
            nodes.target("", ids=["duplicate"]),
            paragraph,
        ]


def setup(app: Any) -> dict[str, bool]:
    app.add_directive("duplicate-targets", DuplicateTargets)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
