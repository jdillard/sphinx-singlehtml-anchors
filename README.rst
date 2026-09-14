sphinx-singlehtml-anchors
=========================

``sphinx-singlehtml-anchors`` is an experimental Sphinx extension that gives
targets in ``singlehtml`` output document-qualified IDs. It is intended to
provide community testing for a future fix to
`sphinx-doc/sphinx#4814 <https://github.com/sphinx-doc/sphinx/issues/4814>`_.

The extension supports released Sphinx versions from 8.1 through 9.x across
both ``SingleFileHTMLBuilder.fix_refuris()`` lifecycle behaviors:

* Sphinx 8.1.x, where Sphinx calls ``fix_refuris()``
* Sphinx 8.2.x through 9.x, where the extension supplies the omitted calls
* Sphinx versions containing the restoration proposed by
  `sphinx-doc/sphinx#14241 <https://github.com/sphinx-doc/sphinx/pull/14241>`_

Installation
------------

Install the package and add it to ``conf.py``:

.. code-block:: python

   extensions = [
       "sphinx_singlehtml_anchors",
   ]

Then build normally:

.. code-block:: console

   sphinx-build -M singlehtml docs docs/_build

Target format
-------------

Document targets retain Sphinx's existing form:

.. code-block:: text

   #document-guide/chapter

Targets within a document include both the source document and original ID:

.. code-block:: text

   #document-guide/chapter--purpose

This changes existing ``singlehtml`` deep links. The extension is therefore
published as experimental while the target scheme and compatibility behavior
are tested.

Development
-----------

Run the complete compatibility and static-check suite:

.. code-block:: console

   tox

The compatibility matrix covers Sphinx 8.1, 8.2, 9.1, and the proposed
``fix_refuris()`` restoration.

Prior art
---------

The implementation builds on lessons from:

* `sphinx-doc/sphinx#13739 <https://github.com/sphinx-doc/sphinx/pull/13739>`_
* `sphinx-doc/sphinx#9652 <https://github.com/sphinx-doc/sphinx/pull/9652>`_
* `sphinx-doc/sphinx#10106 <https://github.com/sphinx-doc/sphinx/issues/10106>`_
