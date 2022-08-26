"""
Natual language processing utils
"""
from __future__ import annotations


def camel_split(camel: str) -> list[str]:
    """
    Split camel case string into sentence

    Credit: https://stackoverflow.com/a/58996565/7346633

    :param camel: E.g. HelloWorld or helloWorld
    :return: E.g. ['Hello', 'World']
    """
    # Ignore all caps or all lower
    if camel.isupper() or camel.islower() or camel.isnumeric():
        return [camel]

    idx = list(map(str.isupper, camel))

    # Mark change of case
    word = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:  # "Ul"
            word.append(i)
        elif not x and y:  # "lU"
            word.append(i + 1)
    word.append(len(camel))

    # for "lUl", index of "U" will pop twice, have to filter that
    return [camel[x:y] for x, y in zip(word, word[1:]) if x < y]


def substr_between(s: str, start: str | None = None, end: str | None = None):
    """
    Get substring between two strings

    >>> substr_between('abc { meow } def', '{', '}')
    ' meow '
    """
    if start:
        s = s[s.index(start) + len(start):]
    if end:
        s = s[:s.index(end)]
    return s
