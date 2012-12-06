import re


def lsb(u16):
    """ less significant bits """
    return '%.2x' % (u16 & 0xff)


def msb(u16):
    """ more ignificant bits """
    return '%.2x' % (u16 >> 8)


def int_to_ipv6(number):
    # TODO deprecate ?
    words = [
        number_to_hex_str(number >> 32, 4),
        number_to_hex_str((number >> 16) & 0xffff, 4),
        number_to_hex_str(number & 0xffff, 4)
        ]
    return ':'.join(words, )


def int_to_hex_str(number, length):
    """ convert a integer number to a HEX string of length length """
    # TODO Why ? 
#    assert digits <= 8, "Precision %d too large? (max 8)" % digits
    return ('%.' + str(length) + 'x') % number


def split_len(seq, length):
    """ returns a seq string broken in a list of strings of length length """
    return [seq[i:i+length] for i in range(0, len(seq), length)]
