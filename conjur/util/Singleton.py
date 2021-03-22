
"""
Singelton baseClass. took from https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
We inherit from this baseClass where we have resources that we want to be configured once for all across
the application
"""
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
