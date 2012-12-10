#!/usr/bin/python
import sys
import re

MAX_BITS = 64
UNROLL_BITS = 4

def range_of_bits():
    return [2 ** x for x in reversed(range(0, MAX_BITS, UNROLL_BITS))]

class S2CrException(Exception):
    pass

def is_numeric(x):
    for c in x:
        if c not in '0123456789':
            return False
    return True

def s_to_cratylus(string):

    string = re.sub('[ \t]+', ' ', string)
    lines = string.split('\n')

    numline = 0
    labels_to_numlines = {}
    initial_values = {}

    # Preprocess labels
    instructions = []
    for line in lines:
        line = line.split('#')[0].strip(' \t\r\n')
        if line == '':
            continue

        if line[-1] == ':':
            label = line[:-1]
            if label in labels_to_numlines:
                raise S2CrException('label "%s" should not occur twice' % (label,))
            labels_to_numlines[label] = numline
        elif line[0] == '!':
            line = line.split(' ')
            if len(line) != 3 or not is_numeric(line[2]): 
                raise S2CrException('variable initialization should be of the form "! <var> <value>"')

            var = line[1]
            value = int(line[2])

            if var in initial_values:
                raise S2CrException('variable "%s" is initialized twice (%u, %u)' % (var, initial_values[var], value))

            initial_values[var] = value
        else:
            instructions.append(line)
            numline += 1

    # Compile instructions
    result = []
    numline = 0
    for op in instructions:
        op = [x.strip(' \t\r\n') for x in op.split(' ')]

        if op[0] in ['inc', 'dec', 'jmp', 'goto', 'xzero'] and len(op) != 2:
            raise S2CrException('operation "%s" takes exactly one argument' % (op[0],))

        if op[0] in ['jz', 'jnz', 'xmov', 'xadd'] and len(op) != 3:
            raise S2CrException('operation "%s" takes exactly two arguments' % (op[0],))

        if op[0] in ['jmp', 'goto', 'jz', 'jnz']:
            label = op[-1]
            if label not in labels_to_numlines:
                raise S2CrException('undefined label "%s"' % (label,))

        if op[0] == 'inc':
            var = op[1]
            result.append('{%u} => {%u}{%s}' % (numline, numline + 1, var))

        elif op[0] == 'dec':
            var = op[1]
            result.append('{%u}{%s} => {%u}' % (numline, var, numline + 1))
            result.append('{%u} => {%u}' % (numline, numline + 1))

        elif op[0] in ['jmp', 'goto']:
            label = op[1]
            result.append('{%u} => {%u}' % (numline, labels_to_numlines[label]))

        elif op[0] in ['jnz']:
            var = op[1]
            label = op[2]
            result.append('{%u}{%s} => {%u}{%s}' % (numline, var, labels_to_numlines[label], var))
            result.append('{%u} => {%u}' % (numline, numline + 1))

        elif op[0] in ['jz']:
            var = op[1]
            label = op[2]
            result.append('{%u}{%s} => {%u}{%s}' % (numline, var, numline + 1, var))
            result.append('{%u} => {%u}' % (numline, labels_to_numlines[label]))

        # extensions

        elif op[0] == 'xzero':
            var = op[1]
            for p in range_of_bits():
                result.append('{%u}{%s}^%u => {%u}' % (numline, var, p, numline))
            result.append('{%u} => {%u}' % (numline, numline + 1))

        elif op[0] == 'xmov':
            dst = op[1]
            src = op[2]
            # zero dst
            for p in range_of_bits():
                result.append('{%u}{%s}^%u => {%u}' % (numline, dst, p, numline))
            result.append('{%u} => {%u,1}' % (numline, numline))

            if is_numeric(src):
                result.append('{%u,1} => {%u}{%s}^%u' % (numline, numline + 1, dst, int(src)))
            else:
                # move src to dst and dst'
                for p in range_of_bits():
                    result.append('{%u,1}{%s}^%u => {%u,1}{%s}^%u{%s,1}^%u' % (numline, src, p, numline, dst, p, dst, p))
                result.append('{%u,1} => {%u,2}' % (numline, numline))

                # move dst' to src
                for p in range_of_bits():
                    result.append('{%u,2}{%s,1}^%u => {%u,2}{%s}^%u' % (numline, dst, p, numline, src, p))
                result.append('{%u,2} => {%u}' % (numline, numline + 1))

        elif op[0] == 'xadd':
            dst = op[1]
            src = op[2]
            if is_numeric(src):
                result.append('{%u} => {%u}{%s}^%u' % (numline, numline + 1, dst, int(src)))
            else:
                # move src to dst and dst'
                for p in range_of_bits():
                    result.append('{%u}{%s}^%u => {%u}{%s}^%u{%s,1}^%u' % (numline, src, p, numline, dst, p, dst, p))
                result.append('{%u} => {%u,1}' % (numline, numline))

                # move dst' to src
                for p in range_of_bits():
                    result.append('{%u,1}{%s,1}^%u => {%u,1}{%s}^%u' % (numline, dst, p, numline, src, p))
                result.append('{%u,1} => {%u}' % (numline, numline + 1))

        numline += 1

    result.append('{%u}' % (numline,))

    goal = ['{0}']
    for var, val in sorted(initial_values.items()):
        goal.append('{%s}^%u' % (var, val))

    result.append('? %s' % (''.join(goal),))

    return '\n'.join(['%s.' % (r,) for r in result])

def usage():
    sys.stderr.write('Dumb S to Cratylus compiler.\n')
    sys.stderr.write('Copyright (c) 2012 - Pablo Barenbaum <foones@gmail.com>\n')
    sys.stderr.write('Usage:\n')
    sys.stderr.write('    %s <infile.s>\n' % (sys.argv[0],))
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()

    in_file = sys.argv[1]

    if in_file.endswith('.s'):
        out_file = in_file[:-2] + '.cr'
    else:
        out_file = in_file + '.cr'

    f = file(sys.argv[1], 'r')
    contents = f.read()
    f.close()

    try:
        result = s_to_cratylus(contents)
    except S2CrException, e:
        print 's2cr:', e
        sys.exit(1) 

    print result

    out = file(out_file, 'w')
    out.write(result)
    out.close()

