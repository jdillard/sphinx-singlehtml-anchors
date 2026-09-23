Underscore and dunder references
================================

Python APIs routinely use underscores in public names and double underscores
in special-method and class names. Document names can use the same characters.
That makes references such as the ones on this page useful delimiter tests:
rewriting must preserve the complete document name and Python target instead
of treating ``_`` or ``__`` as the boundary between them.

This document deliberately contains ``__`` in its docname. Its
:py:meth:`Widget.__init__` and :py:class:`Payload__Envelope` targets put
double underscores on the other side of the extension's ``--`` separator.
The separator remains visible and unambiguous without altering valid
underscores in either component.

.. py:function:: function_name(argument)

   Return ``argument`` unchanged.

.. py:class:: Widget

   A small example containing a dunder method.

   .. py:method:: __init__(value)

      Initialize the widget.

.. py:class:: Payload__Envelope

   A class whose own name contains a double underscore.

Follow the generated Python-domain links:

* :py:func:`function_name`
* :py:meth:`Widget.__init__`
* :py:class:`Payload__Envelope`
