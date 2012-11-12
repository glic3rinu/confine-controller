
## auxiliar functions for getting confine address
def less_significant_bits(u16):
    return '%.2x' % (u16 & 0xff)

def more_significant_bits(u16):
    return '%.2x' % (u16 >> 8)

def number_to_hex_str(number, digits):
    assert digits <= 8, "Precision %d too large? (max 8)" % digits
    return ('%.' + str(digits) + 'x') % number

def int_to_ipv6(number):
    words = [
        number_to_hex_str(number >> 32, 4),
        number_to_hex_str((number >> 16) & 0xffff, 4),
        number_to_hex_str(number & 0xffff, 4)
        ]
    return ':'.join(words, )
