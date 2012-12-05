#!/usr/bin/python
import string

class CratylusException(Exception):
    pass

def normalize_key(k):
    return tuple(sorted([(v, p) for (v, p) in k if p != 0]))

def cmp_keys(k1, k2):
    all_vars = {}
    for v, p in list(k1) + list(k2):
        all_vars[v] = 1
    k1 = dict(k1)
    k2 = dict(k2)
    all_vars = sorted(all_vars.keys())
    k1 = [k1.get(v, 0) for v in all_vars]
    k2 = [k2.get(v, 0) for v in all_vars]
    return cmp(k1, k2)

def lexisorted(keys):
    return list(reversed(sorted(keys, cmp=cmp_keys)))

def mul_keys(k1, k2):
    vp = {}
    for v, p in list(k1) + list(k2):
        vp[v] = vp.get(v, 0) + p
    return normalize_key(vp.items())

def poly_from_constant(k):
    if k == 0:
        return Poly({})
    else:
        return Poly({(): k})

def poly_from_var(var, power=1):
    return Poly({((var, power),): 1})

class Poly(object):

    # coeffs is a mapping
    # ((var1, pow1), ..., (varN, powN)) -> coeff
    def __init__(self, coeffs):
        self._coeffs = {}
        for k, v in coeffs.items():
            if v == 0: continue
            nk = normalize_key(k)
            assert nk not in self._coeffs
            self._coeffs[nk] = v

    def __add__(self, q):
        coeffs = {}
        for k, v in self._coeffs.items() + q._coeffs.items():
            coeffs[k] = coeffs.get(k, 0) + v
        return Poly(coeffs)

    def __mul__(self, q):
        coeffs = {}
        for k1, v1 in self._coeffs.items():
            for k2, v2 in q._coeffs.items():
                k = mul_keys(k1, k2)
                coeffs[k] = coeffs.get(k, 0) + v1 * v2
        return Poly(coeffs)

    def __pow__(self, p):
        pw = p.as_constant()
        if pw is None or pw < 0:
            raise CratylusException('%s ^ %s -- power should be a non-negative constant' % (self, p))
        res = poly_from_constant(1)
        acc = self
        while pw > 0:
            if pw % 2 == 1:
                res = res * acc 
            acc = acc * acc
            pw /= 2
        return res

    def __eq__(self, q):
        ps = sorted(self._coeffs.items())
        qs = sorted(q._coeffs.items())
        return ps == qs
        
    def __sub__(self, q):
        return self + (-q)

    def __neg__(self):
        coeffs = {}
        for k, v in self._coeffs.items():
            coeffs[k] = -v
        return Poly(coeffs)

    def div_mod(self, d):
        p = self
        q = poly_from_constant(0)
        r = poly_from_constant(0)
        d_leading = d.leading_monomial()
        while not p.is_null():
            p_leading = p.leading_monomial()
            qd = d_leading.monomial_div(p_leading)
            if qd is not None:
                q = q + qd
                p = p - qd * d
            else:
                r = r + p_leading
                p = p - p_leading
        assert q * d + r == self
        return q, r

    def __div__(self, p):
        pass

    def leading_monomial(self):
        k = lexisorted(self._coeffs.keys())[0]
        return Poly({k: self._coeffs[k]})

    def as_constant(self):
        if len(self._coeffs) == 0:
            return 0
        elif len(self._coeffs) == 1 and self._coeffs.keys()[0] == ():
            return self._coeffs.values()[0]
        else:
            return None

    def is_monomial(self):
        return len(self._coeffs) == 1

    def is_null(self):
        return len(self._coeffs) == 0

    def monomial_div(self, monomial):
        assert self.is_monomial()
        assert monomial.is_monomial()
        k1, c1 = self._coeffs.items()[0]
        k2, c2 = monomial._coeffs.items()[0]
        if c2 % c1 != 0:
            return None

        k1 = dict(k1)
        k2 = dict(k2)
        res = []

        for var, pow1 in k1.items(): 
            pow2 = k2.get(var, 0)
            if pow2 < pow1:
                return None

        for var, pow2 in k2.items(): 
            pow1 = k1.get(var, 0)
            res.append((var, pow2 - pow1))

        res = Poly({tuple(res): c2 / c1})
        assert self * res == monomial 
        return res

    def __repr__(self):
        res = []
        fst = True
        for k in lexisorted(self._coeffs.keys()):
            coef = self._coeffs[k]

            if coef < 0:
                if fst:
                    s_pre = '-'
                else:
                    s_pre = ' - '
            elif not fst:
                s_pre = ' + '
            else:
                s_pre = ''

            if fst:
                fst = False

            def s_pow(v, p):
                if p == 1:
                    return '%s' % (v,)
                else:
                    return '%s^%s' % (v, p)

            s_var = ''.join([s_pow(v, p) for v, p in k])

            if abs(coef) == 1 and s_var != '':
                s_coef = ''
            else:
                s_coef = '%s' % (abs(coef),)

            res.append('%s%s%s' % (s_pre, s_coef, s_var))
        if res == []:
            return '0'
        else:
            return ''.join(res)

class Token(object):

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return '%s:%s' % (self.type, self.value)

def tokenize(s):
    i = 0
    while i < len(s):

        # Eat whitespace
        while i < len(s) and (s[i] in string.whitespace or s[i] == '#'):
            if s[i] == '#':
                while i < len(s) and s[i] != '\n':
                    i += 1
            else:
                i += 1

        if i >= len(s):
            break

        if s[i] in string.digits:
            num = ''
            while i < len(s) and s[i] in string.digits: 
                num += s[i]
                i += 1
            yield Token('NUM', int(num))
        elif s[i] in string.lowercase:
            yield Token('VAR', s[i])
            i += 1
        elif s[i] in '{':
            name = ''
            while i < len(s) and s[i] != '}':
                name += s[i]
                i += 1
            name += '}'
            i += 1
            yield Token('VAR', name)
        else:
            symbols = {
                '+': 'ADDOP',
                '-': 'ADDOP',
                '*': 'MULOP',
                '^': 'EXPOP',
                '(': 'LPAREN',
                ')': 'RPAREN',
                '?': 'QUERY',
                ',': 'COMMA',
                '.': 'PERIOD',
                '=>': 'THEN',
            }
            for symbol, symbol_type in symbols.items():
                if i + len(symbol) <= len(s) and s[i:i + len(symbol)] == symbol:
                    yield Token(symbol_type, symbol)
                    i += len(symbol)
                    break
            else:
                raise CratylusException('Unrecognized symbol: %s' % (s[i],))
    yield Token('EOF', '')

def terminators():
    return ['RPAREN', 'THEN', 'COMMA', 'PERIOD', 'EOF']

def parse_atom(tokens, i=0):
    if i >= len(tokens):
        raise CratylusException('Parse error')

    if tokens[i].type == 'VAR':
        return i + 1, poly_from_var(tokens[i].value)
    elif tokens[i].type == 'NUM':
        return i + 1, poly_from_constant(tokens[i].value)
    elif tokens[i].type == 'LPAREN':
        j, res = parse_polynomial(tokens, i + 1)
        if tokens[j].type != 'RPAREN':
            raise CratylusException('Unbalanced paren')
        return j + 1, res
    else:
        raise CratylusException('Parse error: unexpected token found: %s' % (tokens[i],))

def parse_monomial(tokens, i=0):
    res = poly_from_constant(1)
    while i < len(tokens) and tokens[i].type not in ['ADDOP'] + terminators():
        i, a = parse_atom(tokens, i)

        while i < len(tokens) and tokens[i].type in ['EXPOP']:
            i, p = parse_atom(tokens, i + 1)
            a = a ** p

        if i < len(tokens) and tokens[i].type in ['MULOP']:
            i += 1

        res = res * a
    return i, res

def parse_polynomial(tokens, i=0):
    res = poly_from_constant(0)

    sign = '+'
    if i < len(tokens) and tokens[i].type in 'ADDOP':
        sign = tokens[i].value
        i += 1

    while i < len(tokens):
        i, f = parse_monomial(tokens, i)
        if sign == '-':
            f = -f
        res = res + f
        if tokens[i].type in ['RPAREN'] + terminators():
            break
        if tokens[i].type not in 'ADDOP':
            raise CratylusException('Expected an additive operator (+, -)')
        sign = tokens[i].value
        i += 1
    return i, res

#def parse_poly(string):
#    return parse_polynomial(list(tokenize(string)))[1]

def parse_rule(tokens, i):
    i, head = parse_polynomial(tokens, i)
    if tokens[i].type == 'PERIOD':
        return i + 1, [head]

def parse_program(string):
    tokens = list(tokenize(string))
    rules = []
 
    i = 0
    while i < len(tokens):
        if tokens[i].type == 'QUERY':
            print tokens[i]
        else:
            i, rule = parse_rule(tokens, i)
            rules.append(rule)
    print rule

def parse_program_from_file(filename):
    try:
        f = file(filename, 'r')
    except IOError:
        raise CratylusException('Cannot open file: %s' % (filename,))
    contents = f.read()
    f.close()
    return parse_program(contents)

parse_program_from_file('in.txt')

