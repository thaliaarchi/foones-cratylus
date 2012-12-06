#!/usr/bin/python
#
# Copyright (C) 2012 Pablo Barenbaum <foones@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import string
import readline

PROMPT = 'Cratylus'
OPTIONS = {
    'verbose': False,
    'script': False,
    'modulo': 0,
}

class CratylusException(Exception):

    def __init__(self, msg, pos=None):
        self._msg = msg
        self._pos = pos

    def __str__(self):
        if self._pos == None:
            return self._msg
        else:
            return 'at %s\n%s' % (self._pos, indent(self._msg))

def is_numeric(x):
    for c in x:
        if c not in '0123456789':
            return False
    return True

def modulo(x):
    if OPTIONS['modulo'] == 0:
        return x
    else: 
        return x % OPTIONS['modulo']

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

def poly_from_coeffs(coeffs, var='x'):
    dic = {}
    power = 0
    for c in reversed(coeffs):
        dic[((var, power),)] = c
        power += 1
    return Poly(dic)

class Poly(object):

    # coeffs is a mapping
    # ((var1, pow1), ..., (varN, powN)) -> coeff
    def __init__(self, coeffs):
        self._coeffs = {}
        for k, v in coeffs.items():
            v = modulo(v)
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

    def __pow__(self, pw):
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

def indent(text):
    return '\n'.join(['    ' + t for t in text.split('\n')])

class Position(object): 

    def __init__(self, filename, string, begin, end):
        self._filename = filename
        self._string = string
        self._begin = begin
        self._end = end

    def line(self):
        line = 1
        chunks = self._string.split('\n')
        rd = 0
        for c in chunks:
            rd += len(c) + 1
            if rd >= self._begin:
                break
            line += 1
        return line

    def fragment(self):
        line = self.line() - 1
        chunks = self._string.split('\n')
        lines = chunks[max(0, line - 1):min(len(chunks), line + 1)]
        return '\n'.join(lines)

    def __repr__(self):
        return '\'%s\', line %s:\n%s\n' % (self._filename, self.line(), indent(self.fragment()))

class Token(object):

    def __init__(self, type, value, position):
        self.type = type
        self.value = value
        self.pos = position

    def __repr__(self):
        return '%s "%s"' % (self.type, self.value)

def tokenize(s, filename='...'):
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
            b = i
            num = ''
            while i < len(s) and s[i] in string.digits: 
                num += s[i]
                i += 1
            yield Token('NUM', int(num), Position(filename, s, b, i))
        elif s[i] in string.lowercase:
            yield Token('VAR', s[i], Position(filename, s, i, i + 1))
            i += 1
        elif s[i] == '{':
            b = i
            name = ''
            while i < len(s) and s[i] != '}':
                name += s[i]
                i += 1
            name += '}'
            i += 1
            yield Token('VAR', name, Position(filename, s, b, i))
        elif s[i] in string.uppercase:
            b = i
            name = s[i]
            i += 1
            while i < len(s) and s[i] in '_' + string.lowercase + string.digits:
                name += s[i]
                i += 1
            yield Token('VAR', name, Position(filename, s, b, i))
        elif OPTIONS['modulo'] == 2 and s[i] == '|':
            b = i
            coeffs = []
            i += 1
            while i < len(s) and s[i] in '01':
                coeffs.append(int(s[i]))
                i += 1
            if i >= len(s) or s[i] != '|':
                raise CratylusException('Expected "|"', Position(filename, s, b, i))
            i += 1
            yield Token('POLY', poly_from_coeffs(coeffs), Position(filename, s, b, i))
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
                    yield Token(symbol_type, symbol, Position(filename, s, i, i + len(symbol)))
                    i += len(symbol)
                    break
            else:
                raise CratylusException('Unrecognized symbol: %s' % (s[i],), Position(filename, s, i, i))
    yield Token('EOF', '', Position(filename, s, i, i))

def terminators():
    return ['RPAREN', 'THEN', 'COMMA', 'PERIOD', 'EOF']

def parse_num(tokens, i=0):
    if tokens[i].type == 'NUM':
        return i + 1, tokens[i].value
    else:
        raise CratylusException('Parse error: expected a number' % (tokens[i],), tokens[i].pos)

def parse_atom(tokens, i=0):
    if i >= len(tokens):
        raise CratylusException('Parse error', tokens[-1].pos)

    if tokens[i].type == 'VAR':
        return i + 1, poly_from_var(tokens[i].value)
    elif tokens[i].type == 'NUM':
        return i + 1, poly_from_constant(tokens[i].value)
    elif tokens[i].type == 'POLY':
        return i + 1, tokens[i].value
    elif tokens[i].type == 'LPAREN':
        j, res = parse_polynomial(tokens, i + 1)
        if tokens[j].type != 'RPAREN':
            raise CratylusException('Unbalanced paren', tokens[j].pos)
        return j + 1, res 
    else:
        raise CratylusException('Parse error: unexpected token found: %s' % (tokens[i],), tokens[i].pos)

def parse_monomial(tokens, i=0):
    res = poly_from_constant(1)
    while i < len(tokens) and tokens[i].type not in ['ADDOP'] + terminators():
        i, a = parse_atom(tokens, i)

        while i < len(tokens) and tokens[i].type in ['EXPOP']:
            i, p = parse_num(tokens, i + 1)
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
            raise CratylusException('Expected an additive operator (+, -)', tokens[i].pos)
        sign = tokens[i].value
        i += 1
    return i, res

def poly_from_string(string):
    return parse_polynomial(list(tokenize(string)), 0)[1]

def parse_clause(tokens, i):
    clause = []
    while i < len(tokens):
        i, poly = parse_polynomial(tokens, i)
        clause.append(poly)
        if tokens[i].type == 'COMMA':
            i += 1
            continue 
        elif tokens[i].type == 'PERIOD':
            i += 1
            break
        else:
            raise CratylusException('Parse error: expected "," or "."', tokens[i].pos)
    return i, clause

class Rule(object):

    def __init__(self, head, clause=[]):
        self.head = head
        self.clause = clause

    def __repr__(self):
        if self.clause == []:
            return '%s' % (self.head,)
        else:
            return '%s => %s' % (self.head, ', '.join([repr(x) for x in self.clause]))

    def is_goal(self):
        return False

class Goal(object):

    def __init__(self, clause=[]):
        self.clause = clause

    def __repr__(self):
        return '? %s' % (', '.join([repr(x) for x in self.clause]),)

    def is_goal(self):
        return True

class Program(object):

    def __init__(self, rules=[]):
        self.rules = rules

    def __repr__(self):
        return '\n'.join(['%s.' % (x,) for x in self.rules])

def parse_rule(tokens, i):
    i, head = parse_polynomial(tokens, i)
    if tokens[i].type == 'PERIOD':
        return i + 1, Rule(head)
    elif tokens[i].type == 'THEN':
        i += 1
        i, clause = parse_clause(tokens, i)
        return i, Rule(head, clause)
    else:
        raise CratylusException('Expected "=>" or "."', tokens[i].pos)

def parse_goal(tokens, i):
    i, clause = parse_clause(tokens, i)
    return i, Goal(clause)

def run_goal(rules, goal):
    p0 = poly_from_constant(0)
    while True:
        for rule in rules:
            q, r = goal.div_mod(rule.head)
            if r == p0:

                if OPTIONS['verbose']:
                    print 40 * '-'
                    print 'Current goal : %s' % (goal,)
                    print 'Applying rule: %s' % (rule,)
                    print '%s = (%s) * (%s)' % (goal, rule.head, q)

                goal = q
                for p in rule.clause:
                    goal = goal * p

                if OPTIONS['verbose']:
                    print 'New goal     : %s' % (goal,)
                    print 40 * '-'

                break
        else:
            if OPTIONS['verbose']:
                print 'Final result:'
            print goal
            break

def parse_program(string, filename='...'):
    tokens = list(tokenize(string, filename))
    rules = []
    i = 0
    while i < len(tokens) and tokens[i].type != 'EOF':
        if tokens[i].type == 'QUERY':
            i += 1
            i, goal = parse_goal(tokens, i)
            rules.append(goal)
        else:
            i, rule = parse_rule(tokens, i)
            rules.append(rule)
    return Program(rules)

def load_program(string, filename='...'):
    program = parse_program(string, filename='...')
    rules = []
    for p in program.rules:
        if p.is_goal():
            for goal in p.clause:
                run_goal(rules, goal)
        else:
            rules.append(p)
    return rules

def load_program_from_file(filename):
    if not OPTIONS['script']:
        sys.stderr.write('! Loading file "%s"\n' % (filename,))

    if filename.endswith('.cr2'):
        if not OPTIONS['script']:
            sys.stderr.write('! Coefficients in Z_2.\n')
        OPTIONS['modulo'] = 2

    try:
        f = file(filename, 'r')
    except IOError:
        raise CratylusException('Cannot open file \'%s\'' % (filename,))
    contents = f.read()
    f.close()
    return load_program(contents, filename)

def banner():
    sys.stderr.write(r"""
  ____           _         _           
 / ___|_ __ __ _| |_ _   _| |_   _ ___ 
| |   | '__/ _` | __| | | | | | | / __|
| |___| | | (_| | |_| |_| | | |_| \__ \
 \____|_|  \__,_|\__|\__, |_|\__,_|___/
                     |___/             

Copyright (c) 2012 - Pablo Barenbaum <foones@gmail.com>
""")

def cratylus_help():
    print '    Cratylus is an esolang based on polynomial rewriting.'
    print
    print '    Its terms are multivariate polynomials with integer coefficients:'
    print '        42'
    print '        x'
    print '        2x + xy + 2y'
    print '        3x^2 - 1'
    print
    print '    A Cratylus program is a sequence of rewriting rules:'
    print '        2x => x.'
    print '        xy => x.'
    print
    print '    Once loaded, the prompt asks for an input polynomial and'
    print '    in case the process terminates, it outputs the normal form:'
    print '        ? 12xy^9'
    print '        3x'
    print
    print '    help        displays this message'
    print '    exit        quit the Cratylus interpreter'

def toplevel(rules):
    while True:
        goal_string = raw_input('? ')
        if goal_string in ['bye', 'quit', 'exit']:
            print 'Bye.'
            break
        elif goal_string in ['help']:
            cratylus_help()
            continue
        try:
            goal = poly_from_string(goal_string)
            run_goal(rules, goal)
        except CratylusException, e:
            print e
        except KeyboardInterrupt, e:
            pass

def usage(exit=True):
    banner()
    sys.stderr.write('Usage: %s [options] <file>\n' % (sys.argv[0],))
    sys.stderr.write('Options:\n')
    sys.stderr.write('    -v, --verbose          trace every step\n')
    sys.stderr.write('    -s, --script           do not start toplevel interaction\n')
    sys.stderr.write('    -b, --binary           coefficients are in Z_2\n')
    if exit:
        sys.exit(1)

if __name__ == '__main__':
    args = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ['-h', '--help']:
            usage()
        elif sys.argv[i] in ['-v', '--verbose']:
            OPTIONS['verbose'] = True
            i += 1
        elif sys.argv[i] in ['-s', '--script']:
            OPTIONS['script'] = True
            i += 1
        elif sys.argv[i] in ['-b', '--binary']:
            OPTIONS['modulo'] = 2
            i += 1
        else:
            args.append(sys.argv[i])
            i += 1

    if len(args) != 1:
        usage(False)
        if not OPTIONS['script']:
            toplevel([])
        sys.exit(1)

    try:
        if not OPTIONS['script']:
            banner()
        rules = load_program_from_file(args[0])
        if not OPTIONS['script']:
            toplevel(rules)

    except CratylusException, e:
        sys.stderr.write('%s: %s\n' % (PROMPT, e,))

