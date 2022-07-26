def nested_get(dictionary, attribute_list, default=None, separator='.'):
    """
    Returns the nested value by parsing keys in iteration.
    Example:
    ```
    dictionary = {
        'a': {
            'b': {
                'c': {
                    'd': 'Desired Value'
                    }
                }
            }
        }
    }
    ```
    If we wanted to get the value of 'd', we could use:
    `nested_get(dictionary, 'a.b.c.d', separator='.')`
    :param dictionary: The nested dictionary
    :param attribute_list: The path to the desired key
    :param separator: How the attributes can be differentiated.
    :return: nested value or None
    """
    curr = dictionary
    attributes = attribute_list.split(separator)
    for attribute in attributes:
        if not isinstance(curr, dict):
            return curr
        res = curr.get(attribute, default)
        curr = res
    return curr
  
  
def nested_getattr(instance: object, attributes: str, default=None, separator='.', call=True):
    """
    Returns nested getattr and returns default if not found
    :param instance: object to get nested attributes from
    :param attributes: separator separated attributes
    :param separator: separator between nested attributes.
    :param default: default value to return if attribute was not found
    :param call: flag that determines whether to call or not if callable
    :return:
    """
    nested_attrs = attributes.split(separator)
    nested_attrs.insert(0, instance)
    try:
        attr = reduce(
            lambda instance_, attribute_: getattr(instance_, attribute_),
            nested_attrs
        )
        if call and callable(attr):
            return attr()
        return attr
    except AttributeError:
        return default
  
