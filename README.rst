sphinx-singlehtml-anchors
=========================

``sphinx-singlehtml-anchors`` is an experimental Sphinx extension that gives
targets in ``singlehtml`` output document-qualified IDs. It is intended to
provide community testing for a future fix to
`sphinx-doc/sphinx#4814 <https://github.com/sphinx-doc/sphinx/issues/4814>`_.

Documentation
-------------

The `live singlehtml demonstration
<https://sphinx-singlehtml-anchors.readthedocs.io/>`_ contains repeated
section and footnote targets and compares builds with and without the
extension.

Development
-----------

Run the complete compatibility and static-check suite:

.. code-block:: console

   tox

The compatibility matrix covers Sphinx 8.1, 8.2, 9.1, and the proposed
``fix_refuris()`` restoration.

Compatibility
--------------

The extension supports released Sphinx versions from 8.1 through 9.x across
both ``SingleFileHTMLBuilder.fix_refuris()`` lifecycle behaviors:

* Sphinx 8.1.x, where Sphinx calls ``fix_refuris()``
* Sphinx 8.2.x through 9.x, where the extension supplies the omitted calls
* Sphinx versions containing the restoration proposed by
  `sphinx-doc/sphinx#14241
  <https://github.com/sphinx-doc/sphinx/pull/14241>`_

Prior art
---------

The implementation builds on lessons from:

* `sphinx-doc/sphinx#13739 <https://github.com/sphinx-doc/sphinx/pull/13739>`_
* `sphinx-doc/sphinx#9652 <https://github.com/sphinx-doc/sphinx/pull/9652>`_
* `sphinx-doc/sphinx#10106 <https://github.com/sphinx-doc/sphinx/issues/10106>`_
