sphinx-singlehtml-anchors
=========================

``sphinx-singlehtml-anchors`` gives every target in Sphinx ``singlehtml``
output a document-qualified ID. This prevents sections, footnotes, and other
targets from different source documents from receiving the same HTML ID.

This site is built as **single-page HTML** on purpose. The two guides below
contain sections with the same names and independently numbered automatic
footnotes, reproducing the collisions described in
`sphinx-doc/sphinx#4814 <https://github.com/sphinx-doc/sphinx/issues/4814>`_.

.. only:: with_extension

   .. note::

      This build uses the extension. Compare it with the
      `same docs built by Sphinx without the extension
      <without-extension/index.html>`__.

.. only:: without_extension

   .. warning::

      This comparison build does **not** use the extension. Its repeated
      section and footnote IDs demonstrate the original problem. Compare it
      with the `fixed build <../index.html>`__.

Try the repeated targets
------------------------

Follow each link and watch both the destination and the fragment in the
browser address bar:

* :ref:`Overview in the first guide <first-guide:overview>`
* :ref:`Overview in the second guide <second-guide:overview>`
* :ref:`Details in the first guide <first-guide:details>`
* :ref:`Details in the second guide <second-guide:details>`

.. only:: with_extension

   Although the visible section names repeat, each link resolves to one
   target. The fragments include the source document, for example
   ``#document-first-guide--overview`` and
   ``#document-second-guide--overview``.

.. only:: without_extension

   The combined page contains duplicate IDs such as ``overview`` and
   ``id1``. A browser can therefore select the first matching target instead
   of the target from the intended source document, and generated links
   cannot address every occurrence reliably.

The automatic footnote links in both guides exercise the same behavior with
generated IDs.

Try underscore-rich targets
---------------------------

Python names make delimiter edge cases concrete. Follow
:py:func:`function_name`, :py:meth:`Widget.__init__`, and
:py:class:`Payload__Envelope` into a source document whose own name contains
double underscores. The :doc:`underscore and dunder reference examples
<underscore__references>` explain why preserving underscores on both sides of
the ``--`` target separator matters.

.. toctree::
   :maxdepth: 2
   :numbered:

   first-guide
   second-guide
   underscore__references
   usage
   how-it-works
