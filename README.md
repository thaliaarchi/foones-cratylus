Cratylus
========

Cratylus is a polynomial rewriting esolang.

A Cratylus program is a sequence of rewriting rules between multivariate polynomials.
For instance, the following program has only one rule:

    xy => z.

Given a query:

    ? x^2y^2.

it gets rewritten to `xyz`, and this in turn to `z^2`,
which is the normal form.
More precisely, a Cratylus program is a sequence of rules, of the form:

    R1 => S1.
    R2 => S2.
    ...
    Rn => Sn.

where each `Ri` and `Si` are multivariate polynomials with integer coefficients.
Given a polynomial `P`, let `i` be the least index such that `Ri` divides `P`,
that is, `P = Ri Q`. Then `P` gets rewritten as `Si Q`.
If there is no such index, `P` is in normal form.

Turing completeness
-------------------

Cratylus is a superset of [Conway's FRACTRAN](http://en.wikipedia.org/wiki/FRACTRAN).
Restricting ourselves to constant polynomials, a FRACTRAN program:

    (a1/b1, a2/b2, ..., aN/bN)

gets translated to an equivalent Cratylus program:

    b1 => a1.
    b2 => a2.
    ...
    bN => aN.

Syntax for polynomials
----------------------

Multivariate polynomials are formed by operating with variables and 
positive integers.

Variables are either single lowercase characters
or a sequence of valid characters started by uppercase.

    <variable> ::= [a-z] | [A-Z][_a-z0-9]

Notice that variables can start in uppercase but cannot
contain uppercase characters in between. This is
for `FooBar` to be parsed as `Foo * Bar`.
Additionally, any string delimited by braces is a variable:

    <variable> ::= ... | {.*}

Numeric literals are restricted to be digits:

    <num> ::= [0-9]+

More interesting polynomials are built by operating on variables
and numbers. The abstract syntax is given by:

    <poly> ::= <poly> + <poly>
             | <poly> - <poly>
             | <poly> * <poly>
             | <poly> ^ <poly>

The usual precedence rules apply. All operators are left-associative.
More concretely:

    <atom> ::= <variable> | <num> | ( <poly> )

    <factor> ::= <atom>
               | <atom> ^ <atom>

    <monomial> ::= <factor>
                 | <monomial> * <factor>
                 | <monomial> <factor>

    <poly> ::= <monomial>
             | + <monomial>
             | - <monomial>
             | <poly> + <monomial>
             | <poly> - <monomial>

Notice there are two equivalent ways of writing
products: `<poly><poly>` and `<poly> * <poly>`.
Also, the exponentiation operator expects a
constant polynomial (of degree 0) on the right side.

Using Cratylus as a basic polynomial normalizer
-----------------------------------------------

Invoke Cratylus with an empty program (no rewriting rules):

    $ python cratylus.py empty_file

      ____           _         _           
     / ___|_ __ __ _| |_ _   _| |_   _ ___ 
    | |   | '__/ _` | __| | | | | | | / __|
    | |___| | | (_| | |_| |_| | | |_| \__ \
     \____|_|  \__,_|\__|\__, |_|\__,_|___/
                         |___/             

    Copyright (c) 2012 - Pablo Barenbaum <foones@gmail.com>
    ? 42
    42
    ? x
    x
    ? abracadabra
    a^5b^2cdr^2
    ? x^2 - 1
    x^2 - 1
    ? (x + y)(x - y)
    x^2 - y^2
    ? (Foo + Bar)^2
    Bar^2 + 2BarFoo + Foo^2
    ? -({x}-{y}){x}
    -{x}^2 + {x}{y}

Syntax for programs
-------------------

A program is just a list of rules. Rules of the form
`p => 1.` can be abbreviated as `p.`. Additionally, a
Cratylus script can contain goals which are to be solved
as soon as the program is loaded.

    <program> ::= <EMPTY>
                | <program> <rule>
                | <program> <goal>

    <rule> ::= <poly> .
             | <poly> => <poly> .

    <goal> ::= ? <poly> .

Example 1: addition
-------------------

This example is used to model addition.
A polynomial `a x^n y^m` is rewritten to a polynomial `z^(n + m)`.
That is, the exponents of the variables `x` and `y` are added
resulting in the corresponding exponent of `z`.
When the following program is loaded:

    ax => az.
    ay => az.
    a => 1.

    ? a x^3 y^2.

Final result:

    z^5 

When the `-v` command line option is used, Cratylus traces the steps of the reduction. 

    ----------------------------------------
    Current goal : ax^3y^2
    Applying rule: ax => az
    ax^3y^2 = ax * x^2y^2
    New goal     : ax^2y^2z
    ----------------------------------------
    ----------------------------------------
    Current goal : ax^2y^2z
    Applying rule: ax => az
    ax^2y^2z = ax * xy^2z
    New goal     : axy^2z^2
    ----------------------------------------
    ----------------------------------------
    Current goal : axy^2z^2
    Applying rule: ax => az
    axy^2z^2 = ax * y^2z^2
    New goal     : ay^2z^3
    ----------------------------------------
    ----------------------------------------
    Current goal : ay^2z^3
    Applying rule: ay => az
    ay^2z^3 = ay * yz^3
    New goal     : ayz^4
    ----------------------------------------
    ----------------------------------------
    Current goal : ayz^4
    Applying rule: ay => az
    ayz^4 = ay * z^4
    New goal     : az^5
    ----------------------------------------
    ----------------------------------------
    Current goal : az^5
    Applying rule: a => 1
    az^5 = a * z^5
    New goal     : z^5
    ----------------------------------------
    Final result:
    z^5

Rewriting rewriting
-------------------

A different way of presenting the above rules:

    Add X => Add Z.
    Add Y => Add Z.
    Add.

Toplevel interaction:

    ? Add X^9 Y^7
    Z^16

One could question why define addition in such a convoluted way,
given that the interpreter itself is a polynomial calculator
(which was already able to add constants).

The key aspect here is that we are representing information,
and manipulating a representation. The difference is that this way
of doing things "scales", in the sense that allows us to carry
out many other processes.

As in FRACTRAN, each variable can be thought as a register, and
rewriting rules can be thought as simple incrementing / decrementing
operations on exponents.

Example 2: erasing a variable
-----------------------------

The following operation can be used to remove all occurrences of X:

    Erase X => Erase.
    Erase.

Toplevel interaction:

    ? Erase X^9 Y^7
    Y^7

Example 3: copying a variable
-----------------------------

This operation creates two copies of X:

    Copy X => Copy Y Z.
    Copy.

Toplevel interaction:

    ? Copy X^9
    Y^9Z^9

Example 4: multiplication
-------------------------

The combination of these ideas allow us to write a procedure
that does multiplication:

    Mul X Y => Copy X Y.
    Mul => Erase.

    Copy Y => Copy Y1 Z.
    Copy   => Rename.

    Rename Y1 => Rename Y.
    Rename    => Del1.

    Del1 X   => Mul.
    Del1     => Mul.

    Erase Y  => Erase.
    Erase.

Toplevel interaction:

    ? Mul X^10 Y^9
    Z^90

Example 5: quotient and remainder
---------------------------------

Quotient and remainder algorithm:

    DivMod X Y => Copy X Y.
    DivMod => End.

    Copy Y => Copy Y1 Y2.
    Copy => Sub.

    Sub X Y2 => Sub.
    Sub Y2 => Rem Y2.
    Sub => Continue Q.

    Continue Y1 => Continue Y.
    Continue => DivMod.

    Rem Y1 Y2 => Rem.
    Rem Y1 => Rem R.
    Rem.

    End Y => End.
    End.

Toplevel interaction:

    ? DivMod X^62 Y^11           # 62 = 5 * 11 + 7
    Q^5R^7

An equivalent obfuscated version:

    dxy => cxy.
    d => e.
    cy => abc.
    c => s.
    bsx => s.
    bs => bl.
    s => nq.
    an => ny.
    n => d.
    abl => l.
    al => lr.
    l.
    ey => e.
    e.

Toplevel interaction:

    ? d x^62 y^11
    q^5r^7

