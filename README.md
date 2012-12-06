Cratylus
========

Cratylus is a polynomial rewriting esolang.

A Cratylus program is a sequence of rewriting rules between multivariate polynomials.
For instance, the following program has only one rule:

    xy => z.

Given a query: 

    x^2y^2

it gets rewritten to:

    xyz

and this in turn to:

    z^2

which is the normal form.

