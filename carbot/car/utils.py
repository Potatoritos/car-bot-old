import string_stuff
import re
import discord

__all__ = [
    'fuzzy_match',
    'edit_dist',
    'join_and',
    'embed',
    'time_to_seconds',
    'zwsp'
]

def fuzzy_match(query, against, amount=1, key=None):
    amount = min(amount, len(against))
    if key is None:
        lst = against
    else:
        lst = [key(a) for a in against]

    ret = []

    for index, similarity in string_stuff.fuzzy_match(query, lst, amount):
        ret.append((against[index], similarity))

    return ret

def edit_dist(s, t, w_del=1, w_ins=1, w_sub=1):
    return string_stuff.edit_dist(s, t, w_del, w_ins, w_sub)

def join_and(lst):
    if len(lst) == 2:
        return " and ".join(lst)
    return ", and ".join(", ".join(lst[:-1]), lst[-1])

def embed(*args, **kwargs):
    return discord.Embed(*args, **kwargs)

def time_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second + t.microsecond/1000000

def zwsp(text, chars):
    ZWSP = '​'
    for char in chars:
        text = text.replace(char, ZWSP+char+ZWSP)

    return text
