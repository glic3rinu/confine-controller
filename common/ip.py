import re


def less_significant_bits(u16):
    return '%.2x' % (u16 & 0xff)


def more_significant_bits(u16):
    return '%.2x' % (u16 >> 8)


def int_to_ipv6(number):
    words = [
        number_to_hex_str(number >> 32, 4),
        number_to_hex_str((number >> 16) & 0xffff, 4),
        number_to_hex_str(number & 0xffff, 4)
        ]
    return ':'.join(words, )


def int_to_hex_str(number, digits):
    # TODO Why ? 
#    assert digits <= 8, "Precision %d too large? (max 8)" % digits
    return ('%.' + str(digits) + 'x') % number


def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]
