Interfaces for Python
=====================

No dependencies! Requires Python 3.6+ (for now).

Installation
------------

.. code-block:: shell

    pip3 install git+https://github.com/gwerbin/python-interface.git


Examples
--------

.. code-block:: python

    # from interface import Interface, implements

    class Addition(Interface):
        max_int: int

        def add(self, x: int, y: int) -> int:
            pass

    @implements(Addition)
    class Calculator():
        max_int: int = 2**8

        def add(self, x: int, y: int) -> int:
            return x + y

    assert hasinterface(Calculator, Addition)


    ## Fails on missing attributes

    try:
        @implements(Addition)
        class Calculator():
            def add(self, x: int, y: int) -> int:
                return x + y
    except Exception as e:
        print(e)


    ## Fails on incorrect signatures

    try:
        @implements(Addition, check_signatures=True)
        class Calculator():
            max_int: int = 2**8

            def add(self, x: float, y: float) -> float:
                return x + y
    except Exception as e:
        print(e)


    ## Fails on incorrect annotations

    try:
        @implements(Addition, check_annotations=True)
        class Calculator():
            max_int: None = None

            def add(self, x: float, y: float) -> float:
                return x + y
    except Exception as e:
        print(e)
