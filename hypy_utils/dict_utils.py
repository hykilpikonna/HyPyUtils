from hypy_utils import infer


def is_non_empty(o):
    return not hasattr(o, '__len__') or len(o) > 0


def remove_values(d: dict | list, vals: list, preserve_list: bool = False) -> dict | list:
    """
    Recursively remove values from a dict

    :param d: Dict
    :param vals: Values to remove
    :param preserve_list: Whether to ignore list elements
    :return: Dict without specific values
    """
    if isinstance(d, list):
        d = [remove_values(i, vals, preserve_list) for i in d if preserve_list or i not in vals]
        d = [i for i in d if is_non_empty(i)]
        return d

    if isinstance(d, dict):
        d = {k: remove_values(v, vals, preserve_list) for k, v in d.items() if v not in vals}
        d = {k: v for k, v in d.items() if is_non_empty(v)}
        return d

    return d


def remove_nones(d: dict | list, preserve_list: bool = False) -> dict:
    """
    Recursively remove nones from a dict

    >>> remove_nones({'a': {'b': None, 'c': 1}, 'b': [None, {'a': None}], 'c': {'a': None}, 'd': [None, 1]})
    {'a': {'c': 1}, 'd': [1]}

    :param d: Dict
    :param preserve_list: Whether to ignore list elements
    :return: Dict without nones
    """
    return remove_values(d, [None], preserve_list=preserve_list)


def remove_keys(d: dict | list, keys: set) -> dict | list:
    """
    Recursively remove keys

    >>> remove_keys({'a': {'b': None, 'c': 1}, 'b': [None, {'a': None}], 'c': {'a': None}, 'd': [None, 1]}, {'b'})
    {'a': {'c': 1}, 'c': {'a': None}, 'd': [None, 1]}

    :param d: The dictionary that you want to remove keys from
    :param keys: Set of keys you want to remove
    :return: Dict without specific keys
    """
    if isinstance(d, list):
        d = [remove_keys(i, keys) for i in d]
        d = [i for i in d if is_non_empty(i)]
        return d

    if isinstance(d, dict):
        d = {k: remove_keys(v, keys) for k, v in d.items() if k not in keys}
        d = {k: v for k, v in d.items() if is_non_empty(v)}
        return d

    return d


def deep_dict(o: object, exclude: set | None):
    """
    Recursively convert an object into a dictionary

    :param o: Object
    :param exclude: Keys to exclude
    :return: Deep dictionary of the object's variables
    """
    exclude = exclude or {}
    infer_result = infer(o)
    if infer_result:
        return infer_result
    if hasattr(o, '__dict__'):
        return deep_dict(dict(vars(o)), exclude)
    if isinstance(o, dict):
        return {k: deep_dict(v, exclude) for k, v in o.items() if k not in exclude}
    if isinstance(o, list):
        return [deep_dict(v, exclude) for v in o]
    return o


def get_rec(cd: dict, key: str):
    """
    :param cd: Dictionary
    :param key: Recursive key in the format of keya.keyb.keyc...
    """
    if '.' not in key:
        return cd.get(key)

    ks = key.split('.')
    while len(ks) > 0:
        cd = cd.get(ks.pop(0))
        if cd is None:
            break
    return cd
