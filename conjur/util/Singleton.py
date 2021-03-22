
"""
Singleton Base Class

Taken from https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
We inherit from the Single Base Class when we need a resource to be created only once and use that single instance throughout the program
"""
class Singleton(type):
    """
    Metaclass to create sindelton classes The usage should be as follows:
    class A(metaclass = Singleton)
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
