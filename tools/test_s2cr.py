import random
import os

def is_numeric(x):
    for c in x:
        if c not in '0123456789':
            return False
    return True

TEST_PER_CASE = 1

def instantiate(code, args):
    for arg_name, val in args:
        code = code.replace('<<%s>>' % (arg_name,), str(val))
    return code

def test_function(name, code, args, function):
    arg_ranges = args
    print '[+] testing function', name
    for i in range(TEST_PER_CASE):
        print '\t-- test case --'
        args = [(arg_name, random.randint(lower, upper)) for (arg_name, lower, upper) in arg_ranges]
        print '\targuments: %s' % (', '.join(['%s: %s' % arg for arg in args]),)
        expected = function(*[value for arg_name, value in args])
        print '\texpected : %s' % (expected,)

        os.system('rm -f test.s test.cr')
        f = file('test.s', 'w')
        f.write(instantiate(code, args))
        f.close()
        os.system('./s2cr.py test.s >/dev/null')
        rd = os.popen('../cratylus.py test.cr -s').read().strip(' \t\r\n')
        if rd == '1':
            reference = 0
        elif rd == '{Answer}':
            reference = 1
        elif rd.startswith('{Answer}') and len(rd.split('^')) == 2 and is_numeric(rd.split('^')[1]):
            reference = int(rd.split('^')[1])
        else:
            assert False
        print '\tgot      : %s' % (reference,)
        assert reference == expected

TESTS = [
    { # shift right
        'name': 'xshr',
        'args': [('value', 0, 2 ** 64), ('shift', 0, 64)],
        'code': '''
        xshr Answer <<shift>>
        ! Answer <<value>>
        ''',
        'function': lambda value, shift: value >> shift
    },
    { # shift left
        'name': 'xshl',
        'args': [('value', 0, 2 ** 40), ('shift', 0, 24)],
        'code': '''
        xshl Answer <<shift>>
        ! Answer <<value>>
        ''',
        'function': lambda value, shift: value << shift
    },
    { # mov constants
        'name': 'xmov1',
        'args': [('x', 0, 2 ** 64), ('y', 0, 2 ** 64)],
        'code': '''
        xmov Answer <<y>>
        ! Answer <<x>>
        ''',
        'function': lambda x, y: y
    },
    { # mov vars
        'name': 'xmov2',
        'args': [('x', 0, 2 ** 64), ('y', 0, 2 ** 64)],
        'code': '''
        xmov X <<x>>
        xmov Answer X
        xzero X
        ! Answer <<y>>
        ''',
        'function': lambda x, y: x
    },
    { # mov vars - leave the second argument untouched
        'name': 'xmov3',
        'args': [('x', 0, 2 ** 64), ('y', 0, 2 ** 64)],
        'code': '''
        xmov X Answer
        xzero X
        ! Answer <<y>>
        ''',
        'function': lambda x, y: y
    },
    { # add vars
        'name': 'xadd1',
        'args': [('x', 0, 2 ** 62), ('y', 0, 2 ** 62)],
        'code': '''
        xadd Answer Y
        xzero Y
        ! Answer <<x>>
        ! Y <<y>>
        ''',
        'function': lambda x, y: x + y
    },
    { # add vars - leave the second argument untouched
        'name': 'xadd2',
        'args': [('x', 0, 2 ** 62), ('y', 0, 2 ** 62)],
        'code': '''
        xadd X Answer
        xzero X
        ! X <<x>>
        ! Answer <<y>>
        ''',
        'function': lambda x, y: y
    },
    { # add constant
        'name': 'xadd3',
        'args': [('x', 0, 2 ** 62), ('y', 0, 2 ** 62)],
        'code': '''
        xadd Answer <<y>>
        ! Answer <<x>>
        ''',
        'function': lambda x, y: x + y
    },
    { # and constant
        'name': 'xand1',
        'args': [('x', 0, 2 ** 62), ('y', 0, 2 ** 62)],
        'code': '''
        xand/1 Answer <<y>>
        ! Answer <<x>>
        ''',
        'function': lambda x, y: x & y & 1
    }
]

def test(*names):
    for t in TESTS:
        if t['name'] in names:
            test_function(**t)

test('xand1')

