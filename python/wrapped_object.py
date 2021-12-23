class WrappedObject():
    """
    A wrapper for another class that can be used to add extra attributes
    """

    def __init__(self, instance, **attrs):
        self._instance = instance
        self._keys = attrs.keys()
        self.__dict__.update(**attrs)

    def __getattr__(self, item):
        return getattr(self._instance, item)

    def __setattr__(self, key, value):
        print("setting", key)
        if key in ['_instance', '_keys']:
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__[key] = value
        elif key in self._keys:
            self.__dict__[key] = value
        else:
            setattr(self._instance, key, value)
