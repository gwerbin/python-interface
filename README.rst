Interfaces for Python
=====================

No dependencies! Requires Python 3.6+ (for now).

.. code-block:: python

    # from interface import Interface, implements

    class Addition(Interface):
        max_int: int

        def add(self, x: int, y:int) -> int:
            pass

    @implements(Addition)
    class Calculator():
        max_int: int = 2**8

        def add(self, x: int, y:int) -> int:
            return x + y

        @classmethod
        def print_max_int(cls):
            return 'Max int: ' + str(cls.max_int)

        @staticmethod
        def stringify(x):
            return str(x)

    assert hasinterface(Calculator, Addition)
