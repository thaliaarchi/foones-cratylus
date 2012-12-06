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

Syntax
------

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

	  ____           _         _           
	 / ___|_ __ __ _| |_ _   _| |_   _ ___ 
	| |   | '__/ _` | __| | | | | | | / __|
	| |___| | | (_| | |_| |_| | | |_| \__ \
	 \____|_|  \__,_|\__|\__, |_|\__,_|___/
						 |___/             

	Copyright (c) 2012 - Pablo Barenbaum <foones@gmail.com>
	? 1
	1
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
	? ({x}-{y}){x}
	{x}^2 - {x}{y}

