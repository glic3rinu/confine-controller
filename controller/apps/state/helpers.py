def break_headers(header):
    return header.replace(', <', ',\n                 <')


def break_long_lines(text, every=150):
    result = []
    for line in text.split('\n'):
        if len(line) > every:
            distance = line.find(':') + 3
            prefix = '\n' + ' '*distance
            broken_line = line[:every] + prefix
            trailing = line[every:]
            cevery = every-distance
            broken_line += prefix.join(trailing[i:i+cevery] for i in xrange(0, len(trailing), cevery))
            line = broken_line
        result.append(line)
    return '\n'.join(result)

