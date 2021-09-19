import re

from zoovendor import six


def camelToNice(strInput, space=" "):
    """ Camel case to nicely formatted string

    eg. theQuickBrownFox ==> the Quick Brown Fox

    :param strInput: String to convert
    :type strInput: basestring
    :param space:
    :return:
    :rtype: basestring
    """
    splitted = re.sub('(?!^)([A-Z][a-z]+)', r' \1', strInput).split()
    ret = space.join(splitted)

    return ret


def titleCase(strInput):
    """ Turn to title case

    :param strInput:
    :type strInput: str
    :return: The resulting title case of a camel case string
    :rtype: str
    """
    if not strInput:
        return ''
    splitted = re.sub('(?!^)([A-Z][a-z]+)', r' \1', strInput).split()
    ret = " ".join(splitted)
    return ret.replace('_', ' ').title()


def substrCount(text, substr):
    """ Get the number of a certain substring in a string.

    Eg.
        "Hello World", 'l' ==> 3
        "Hello\n\n World", '\n' ==> 2
        "Hello World. el. Hello World", 'el' ==> 3

    :param text:
    :return:
    :rtype: int
    """
    res = sum(1 for i in range(len(text))
              if text.startswith(substr, i))
    return res


def newLines(text):
    """ Get new lines

    :param text:
    :return:
    :rtype: int
    """
    return substrCount(text, "\n")


def isStr(text):
    """ If text is a string

    :param text: Text to check if its a string
    :type text: object
    :return: is String
    :rtype: bool
    """
    return isinstance(text, six.string_types)
