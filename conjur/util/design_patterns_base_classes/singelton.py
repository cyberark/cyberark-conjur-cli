# -*- coding: utf-8 -*-

"""
singleton module

Represent a base class implement singleton design pattern
"""


class Singleton(type):
    """
    Base class that make sure an inherit class is a singleton
    Should be used like this 'class A(metaclass=Singleton)'
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        override the __call__ function (). return an instance if already exist
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
