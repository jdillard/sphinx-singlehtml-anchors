project = "singlehtml-anchor-probe"
extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx_singlehtml_anchors",
]
autosectionlabel_prefix_document = True
html_theme = "basic"
html_sidebars = {"**": ["globaltoc.html", "localtoc.html"]}
numfig = True
