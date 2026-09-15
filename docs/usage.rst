Using the extension
===================

Install the package and enable it in ``conf.py``:

.. code-block:: python

   extensions = [
       "sphinx_singlehtml_anchors",
   ]

Then build the documentation with Sphinx's ``singlehtml`` builder:

.. code-block:: console

   sphinx-build -M singlehtml docs docs/_build

The extension replaces only the ``singlehtml`` builder. Other builders,
including regular multi-page HTML, retain their normal target format.

Target format
-------------

Document-level targets retain Sphinx's existing form:

.. code-block:: text

   #document-guide/chapter

Targets within a document combine that document target with the original ID:

.. code-block:: text

   #document-guide/chapter--purpose

Because this changes existing ``singlehtml`` deep links, the extension is
experimental while the target scheme and compatibility behavior receive
community testing.
