# TODO: README & documentation
# TODO: Tests
# TODO: Look for prior art
# TODO: decide how to handle inconsistency between annotation and type
# TODO: single-source versioning in setup.py


import inspect
from functools import partial


class InterfaceType(type):
    IGNORED_ATTRS = ['__module__', '__qualname__', '__class__', '__annotations__']

    def __new__(meta, name, bases, attrs):
        annotations = attrs.get('__annotations__', {})

        required_attrs = {k: v for k,v in attrs.items() if k not in meta.IGNORED_ATTRS}
        required_attrs.update(annotations)
        attrs['__required_attrs__'] = required_attrs

        new_cls = type.__new__(meta, name, bases, attrs)
        return new_cls


class Interface(metaclass=InterfaceType):
    def __new__(cls, decorated_class, check_signatures=False, check_annotations=False):
        if not isinstance(decorated_class, type):
            raise TypeError('Interfaces can only be applied to classes')

        if check_annotations:
            # get annotations before we start looping,
            # so we don't have to do it every iteration
            actual_annotations = getattr(decorated_class, '__annotations__', {})
            expected_annotations = cls.__annotations__
        else:
            expected_annotations = {}

        for attr_name in cls.__required_attrs__:
            try:
                actual_val = getattr(decorated_class, attr_name)
            except AttributeError:
                raise ValueError('Class {deco.__name__} is missing required attribute {attr_name}'.\
                                 format(deco=decorated_class, attr_name=attr_name))
            expected_val = cls.__required_attrs__[attr_name]

            if attr_name in expected_annotations:
                expected_annotation = expected_annotations[attr_name]
                try:
                    actual_annotation = actual_annotations[attr_name]
                except KeyError:
                    raise ValueError('Attribute {attr_name} has no annotation, but should have annotation {expected_annotation!s}'.\
                                     format(attr_name=attr_name, expected_annotation=expected_annotation))

                if expected_annotation != actual_annotation:
                    raise ValueError('Annotation mismatch for attribute {attr_name}:\n\tActual: {actual_annotation!s}\n\tExpected: {expected_annotation!s}'.\
                                     format(attr_name=attr_name, actual_annotation=actual_annotation, expected_annotation=expected_annotation))
            else:
                if check_signatures and callable(actual_val):
                    expected_signature = inspect.signature(expected_val)
                    actual_signature = inspect.signature(actual_val)

                    if expected_signature != actual_signature:
                        raise ValueError('Signature mismatch for callable attribute {attr_name}:\n\tActual: {actual_signature!s}\n\tExpected: {expected_signature!s}'.\
                                         format(attr_name=attr_name, actual_signature=actual_signature, expected_signature=expected_signature))

        if not hasattr(decorated_class, '__implements__'):
            decorated_class.__implements__ = frozenset({cls})
        else:
            decorated_class.__implements__ |= {cls}

        return decorated_class


def _implements(cls, interfaces, **kwargs):
    if not isinstance(cls, type):
        raise TypeError('implements() can only be applied to types')

    for interface in interfaces:
        if not issubclass(interface, Interface):
            raise TypeError('implements() can only accept Interfaces as arguments')

        cls = interface(cls, **kwargs)

    return cls


def implements(*interfaces, **kwargs):
    kwargs['interfaces'] = interfaces + kwargs.get('interfaces', tuple())

    if len(kwargs['interfaces']) < 1:
        raise ValueError('At least one interface must be specified')

    return partial(_implements, **kwargs)


def hasinterface(cls, interface):
    return interface in getattr(cls, '__implements__', frozenset())


if __name__ == '__main__':
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
