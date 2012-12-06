import re


def lsb(u16):
    """ Less significant bits """
    return '%.2x' % (u16 & 0xff)


def msb(u16):
    """ More significant bits """
    return '%.2x' % (u16 >> 8)


def int_to_ipv6(number):
    # TODO deprecate ?
    words = [
        number_to_hex_str(number >> 32, 4),
        number_to_hex_str((number >> 16) & 0xffff, 4),
        number_to_hex_str(number & 0xffff, 4)
        ]
    return ':'.join(words, )


def int_to_hex_str(number, digits):
    """ Convert an integer number to a HEX string of length digits """
    hex_str = ('%.' + str(digits) + 'x') % number
    err_msg = "Hex representation of %d doesn't fit in %s digits" % (number, digits)
    assret len(hex_str) <= digits, err_msg
    return hex_str


def split_len(seq, length):
    """ Returns seq broken in a list of strings of length length """
    return [seq[i:i+length] for i in range(0, len(seq), length)]
