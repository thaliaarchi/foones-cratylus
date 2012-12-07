#!/usr/bin/python
import sys
import cratylus

class SimpCrException(Exception):
    pass

def translate(filename, translation, contents):
    if translation == 'normalize':
        return normalize_program(filename, contents)
    else:
        return translate_program(filename, contents, translation)

def normalize_program(filename, program):
    return repr(cratylus.parse_program(program, filename))

def translate_monomial(poly):
    print poly.coefficients()

def is_prime(p):
    for d in range(2, p):
        if d * d > p:
            break
        if p % d == 0:
            return False
    return True

def gen_primes(n):
    primes = []
    p = 2
    while len(primes) < n:
        if is_prime(p):
            primes.append(p)
        p += 1
    return primes

def gen_irreducible_polys(n):
    polys = [] 
    for i in range(n):
        k = i // 2 + 1
        if i % 2 == 1:
            k = -k
        polys.append(cratylus.poly_from_var('x') + cratylus.poly_from_constant(k))
    return polys

def irreducible_elements(n, translation_type):
    "Return n irreducible elements appropiate for the given translation type"
    if translation_type == 'fractran':
        return [cratylus.poly_from_constant(p) for p in gen_primes(n)]
    elif translation_type == 'univariate':
        return gen_irreducible_polys(n)
    else:
        assert False

def translate_monomial(table, monomial):
    key, coef = monomial.coefficients().items()[0]
    res = cratylus.poly_from_constant(1)
    for var, power in key:
        res = res * table.get(var, var) ** power
    return res

def translate_program(filename, program, translation_type):
    program = cratylus.parse_program(program, filename)

    # Collect all polynomials
    all_polys = []
    for rule in program.rules:
        if rule.is_goal():
            all_polys.extend(rule.clause)
        else:
            all_polys.append(rule.head)
            all_polys.extend(rule.clause)

    # Count variables
    var_count = {}
    for poly in all_polys:
        if not poly.is_monomial():
            raise SimpCrException('"%s" is not a monomial' % (poly,))
        key, coef = poly.coefficients().items()[0]
        if coef != 1:
            raise SimpCrException('"%s" is not in monomial form (coeff should be 1)' % (poly,))
        for var, power in key:
            var_count[var] = var_count.get(var, 0) + 1

    # Build translation table
    num_vars = len(var_count) # number of distinct variables
    old_vars = sorted(var_count.items(), key=lambda (v, c): -c)
    old_vars = [v for v, c in old_vars]
    new_vars = irreducible_elements(num_vars, translation_type)
    table = dict(zip(old_vars, new_vars))

    comment = []
    for old, new in sorted(table.items()):
        msg = '# %s --> %s' % (old, new) 
        comment.append(msg)

    # Translate program
    rules2 = []
    for rule in program.rules:
        if rule.is_goal():
            r = cratylus.Goal([translate_monomial(table, m) for m in rule.clause])
        else:
            r = cratylus.Rule(
                    translate_monomial(table, rule.head),
                    [translate_monomial(table, m) for m in rule.clause])
        rules2.append(r)

    return '\n'.join(comment) + '\n\n' + repr(cratylus.Program(rules2))

def usage():
    sys.stderr.write('Normalize or translate a Cratylus program.\n')
    sys.stderr.write('Usage: %s <infile> [options]\n' % (sys.argv[0],))
    sys.stderr.write('Options:\n')
    sys.stderr.write('    -o <outfile>    write the results in <outfile>\n')
    sys.stderr.write('    -f              translate a monomial form program to FRACTRAN\n')
    sys.stderr.write('    -u              translate a monomial form program to univariate polynomials\n')
    sys.exit(1)

if __name__ == '__main__':

    args = []
    translation = 'normalize'
    outfile = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-f':
            translation = 'fractran'
            i += 1
        elif sys.argv[i] == '-u':
            translation = 'univariate'
            i += 1
        elif sys.argv[i] == '-o':
            i += 1
            if i >= len(sys.argv):
                usage()
            outfile = sys.argv[i]
            i += 1
        else:
            args.append(sys.argv[i])
            i += 1

    if len(args) != 1:
        usage()

    in_file = args[0]
    if in_file.endswith('.cr2'):
        cratylus.OPTIONS['modulo'] = 2

    f = file(in_file)
    contents = f.read()
    f.close()

    result = translate(in_file, translation, contents)

    print result
    if outfile is not None:
        f = file(outfile, 'w')
        f.write(result)
        f.close()

