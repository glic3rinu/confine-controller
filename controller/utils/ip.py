def int_to_hex_str(number, digits):
    """ Convert an integer number to a HEX string of length digits """
    hex_str = ('%.' + str(digits) + 'x') % number
    err_msg = "Hex representation of %d doesn't fit in %s digits" % (number, digits)
    assert len(hex_str) <= digits, err_msg
    return hex_str


def split_len(seq, length):
    """ Returns seq broken in a list of strings of length length """
    return [seq[i:i+length] for i in range(0, len(seq), length)]
