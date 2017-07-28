# TODO: README & documentation
# TODO: Tests
# TODO: Look for prior art
# TODO: return sentinel values in _check_* methods, rather than blithely throwing errors
# TODO: decide how to handle inconsistency between annotation and type
# TODO: single-source versioning in setup.py


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
    @classmethod
    def _check_callable_signature(cls, actual, expected):
        expected_signature = inspect.signature(expected_val)
        actual_signature = inspect.signature(actual_val)

        if expected_signature != actual_signature:
            return ValueError('Signature mismatch for callable attribute {attr_name}:\n\tActual: {actual_signature!s}\n\tExpected: {expected_signature!s}'.\
                              format(attr_name, actual_signature=actual_signature, expected_signature=expected_signature))

    @classmethod
    def _check_annotation(attr_name, decorated_class):
        if attr_name in cls.__annotations__:
            expected_annotation = cls.__annotations__[attr_name]
            try:
                actual_annotation = decorated_class.__annotations__[attr_name]
            except KeyError:
                return ValueError('Attribute {attr_name} has no annotation, but should have annotation {expected_annotation!s}'.\
                                  format(attr_name=attr_name, expected_annotation=expected_annotation))

            if expected_annotation != actual_annotation:
                return ValueError('Annotation mismatch for attribute {attr_name}:\n\tActual: {actual_annotation!s}\n\tExpected: {expected_annotation!s}'.\
                                  format(attr_name=attr_name, actual_annotation=actual_annotation, expected_annotation=expected_annotation))

    @classmethod
    def _check_attr(cls, attr_name, decorated_class,
                    check_signatures, check_annotations):
        try:
            actual_val = getattr(decorated_class, attr_name)
        except AttributeError:
            return ValueError('Class {deco.__name__} is missing required attribute {attr_name}'.\
                              format(deco=decorated_class, attr_name=attr_name))

        expected_val = cls.__required_attrs__[attr_name]

        if callable(expected_val):
            if check_signatures:
                error = cls._check_callable_signature(actual_val, expected_val)
                if error:
                    return error
        else:
            if check_annotations:
                error = cls._check_annotation(attr_name, decorated_class)
                if error:
                    return error

    def __new__(cls, decorated_class, check_signatures=False, check_annotations=False):
        if not isinstance(decorated_class, type):
            raise TypeError('Interfaces can only be applied to types')

        for attr_name in cls.__required_attrs__:
            error = cls._check_attr(attr_name, decorated_class,
                                    check_signatures=check_signatures,
                                    check_annotations=check_annotations)
            if error:
                raise error

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
    # from interface import Interface, 

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
