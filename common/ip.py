import re

from IPy import IP

# TODO unificate with slices.utils

def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]


def int_to_hex_str(number, digits):
    return ('%.' + str(digits) + 'x') % number


