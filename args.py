import argparse
import re


def aptyp_unsigned(string):
    errmsg = '{} is NOT unsigned int'.format(string)
    try:
        v = int(string)
        if v < 0:
            raise argparse.ArgumentTypeError(errmsg)
        return v
    except ValueError:
        raise argparse.ArgumentTypeError(errmsg)


def aptype_regex(string):
    errmsg = '{} is invalid regular expression string'.format(string)
    try:
        return re.compile(string)
    except BaseException:
        raise argparse.ArgumentTypeError(errmsg)


def gen_help_combset(desc, separator, default, items):
    """
    :param desc:
    :param separator:
    :param default:
    :param items: (dict[str: str])
    """
    predesc = "{} (separator: '{}', default: '{}'). \
Fields can be combination of followings. ".format(desc, separator, default)
    combdescs = ["'{}'({})".format(k, v) for k, v in items.iteritems()]
    return predesc + ', '.join(combdescs)


def make_aptype_comboset(items, separator=','):
    """
    :param separator: (str) separator character. default is ','
    :param items: (set[str])
    """
    def aptype_combo(string):
        """
        :return: (set[str])
        """
        errmsg = "'{}' is invalid combination".format(string)
        comb = set()
        toks = string.split(separator)
        toks = set(toks)
        if '' in toks:
            toks.remove('')
        for tok in toks:
            if tok not in items:
                raise argparse.ArgumentTypeError(errmsg)
            comb.add(tok)
        return comb
    return aptype_combo


def build_arg_comboset(desc, separator, default, items):
    """
    :param desc:
    :param separator:
    :param default:
    :param items: (dict[str: str])
    """
    ahelp = gen_help_combset(desc, separator, default, items)
    atype = make_aptype_comboset(set(items.iterkeys()), separator)
    return ahelp, atype
