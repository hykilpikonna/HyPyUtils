from __future__ import annotations

import io
import pickle


def pickle_encode(obj: any, protocol=None, fix_imports=True) -> bytes:
    """
    Encode object to pickle bytes

    >>> by = pickle_encode({'function': pickle_encode})
    >>> len(by)
    57
    >>> decoded = pickle_decode(by)
    >>> by = decoded['function']({'meow': 565656})
    >>> pickle_decode(by)
    {'meow': 565656}
    """
    with io.BytesIO() as bio:
        pickle.dump(obj, bio, protocol=protocol, fix_imports=fix_imports)
        return bio.getvalue()


def pickle_decode(by: bytes) -> any:
    """
    Decode pickle bytes to object
    """
    with io.BytesIO(by) as bio:
        return pickle.load(bio)
