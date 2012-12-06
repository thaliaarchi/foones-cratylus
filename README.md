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

