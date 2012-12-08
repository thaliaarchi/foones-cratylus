Cratylus
========

*Si, como el griego afirma en el Cratilo*  
*el nombre es arquetipo de la cosa*  
*en la palabra* rosa *está la rosa*  
*y todo el Nilo en la palabra* Nilo.  

****

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

Hopefully interesting examples
------------------------------

This Cratylus program computes factorials:

    H=>mZ.am=>af.m=>J.af=>aB.f=>k.aB=>u.B=>u.u=>cL.L=>eG.G=>f.
    ck=>cr.k=>d.cr=>b.r=>b.bZ=>yZ.b=>j.yZ=>t.y=>t.t=>iK.K=>lE.
    E=>b.ij=>is.j=>I.is=>x.s=>x.x=>DZ.D=>j.I=>k.dZ=>wZ.d=>h.
    wZ=>o.w=>o.o=>d.hl=>lp.h=>g.lp=>v.p=>v.v=>CZ.C=>h.eg=>en.
    g=>q.en=>z.n=>z.z=>aF.F=>g.aq=>A.q=>A.A=>m.J.

For instance, interacting with the Cratylus toplevel:

    ? H a^5
    Z^120

    ? H a^7
    Z^5040

Bear in mind the second query takes a *really* long time to arrive
to the answer.

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

Since FRACTRAN is Turing complete, Cratylus also is.

Moreover, as part of the Cratylus distribution, the script `s2cr.py`
translates a program in the (theoretical) programming language S, which
is well-known to be Turing complete, into a Cratylus program.
See below for details.

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
             | <poly> / <poly>
             | <poly> % <poly>
             | <poly> ^ <num>

The usual precedence rules apply. All operators are left-associative.
More concretely:

    <atom> ::= <variable> | <num> | ( <poly> )

    <expatom> ::= <expatom>
                | <expatom> ^ <num>

    <factor> ::= <expatom>
               | <factor> <expatom>

    <term> ::= <factor>
             | <term> * <factor>
             | <term> / <factor>
             | <term> % <factor>

    <poly> ::= <term>
             | + <term>
             | - <term>
             | <poly> + <term>
             | <poly> - <term>

Notice there are two ways of writing products:
`<poly><poly>` and `<poly> * <poly>`. The former
has stronger precedence, so:
`10x / 2x = (10 * x) / (2 * x)` and
`10x / 2*x = ((10 * x) / 2) * x`.

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

Cratylus displays the following final result:

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
out other, more complex, processes.

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

S to Cratylus compiler
----------------------

As part of the Cratylus distribution, the script `s2cr.py` translates a program in
the programming language S to Cratylus. The programming language S is introduced
in M. Davis' *Computability, Complexity, and Languages* to study computability.

A program in S works with an infinite set of variables, which
hold natural numbers. A program is a list of operations delimited
by newlines. Labels can be introduced. At the end of the program,
variables are initialized by declarations of the form `! var value`.

    <program> ::= <instructions> <init>

    <instructions> ::= <EMPTY>
                     | <label>: <instructions>
                     | <op> <instructions>

    <op> ::= inc <var>
           | dec <var>
           | jmp <label>
           | jz <var> <label>
           | jnz <var> <label>

    <init> ::= <EMPTY>
              | ! <var> <num> <init>

For instance, the following S program calculates the product of
`X` and `Y`, with input `X = 11` and `Y = 9`:

    mult:
        jz X mult_end

        # Loop to copy Y to Y1 and Z
        copy:
            jz Y copy_end
            dec Y
            inc Y1
            inc Z
            jmp copy
        copy_end:

        # Loop to rename Y1 to Y 
        rename:
            jz Y1 rename_end
            dec Y1
            inc Y
            jmp rename
        rename_end:

        dec X
        jmp mult
    mult_end:

    # Loop to erase all copies of Y
    erase:
        dec Y
        jnz Y erase

    # Initial values    

    ! X 11
    ! Y 9

After translation with `s2cr.py`, we get the following Cratylus program: 

    {0}{X} => {1}{X}.
    {0} => {12}.
    {1}{Y} => {2}{Y}.
    {1} => {6}.
    {2}{Y} => {3}.
    {2} => {3}.
    {3} => {4}{Y1}.
    {4} => {5}{Z}.
    {5} => {1}.
    {6}{Y1} => {7}{Y1}.
    {6} => {10}.
    {7}{Y1} => {8}.
    {7} => {8}.
    {8} => {9}{Y}.
    {9} => {6}.
    {10}{X} => {11}.
    {10} => {11}.
    {11} => {0}.
    {12}{Y} => {13}.
    {12} => {13}.
    {13}{Y} => {12}{Y}.
    {13} => {14}.
    {14}.
    ? {0}{X}^11{Y}^9.

When run, the answer is:

    {Z}^99

Cratylus simplifier
-------------------

Also part of the Cratylus distribution is the script `simp_cr.py` which
normalizes Cratylus programs.

Notice that most of the Cratylus programs above, including all the possible
outputs of `s2cr.py`, are written in *monomial form*.
That is, all the polynomials that appear in the source program are monomials
with leading coefficient equal to 1.

It is easy to see that a program in monomial form can be translated to an
equivalent FRACTRAN program, if the set of variables that occur in the
source program is put in 1-1 correspondence with an arbitrary set of primes.
(More generally, a program in monomial form can be translated to an
equivalent program if the set of variables is put in 1-1 correspondence
with a set of different irreducible elements in a unique factorization domain).

Given a Cratylus program in monomial form, `simp_cr.py -f file.cr` translates
it to an equivalent FRACTRAN program.

For instance, as we saw before, the S program which calculates the product
of `X` and `Y` gave output to the following Cratylus program:

    {0}{X} => {1}{X}.
    {0} => {12}.
    {1}{Y} => {2}{Y}.
    {1} => {6}.
    {2}{Y} => {3}.
    {2} => {3}.
    {3} => {4}{Y1}.
    {4} => {5}{Z}.
    {5} => {1}.
    {6}{Y1} => {7}{Y1}.
    {6} => {10}.
    {7}{Y1} => {8}.
    {7} => {8}.
    {8} => {9}{Y}.
    {9} => {6}.
    {10}{X} => {11}.
    {10} => {11}.
    {11} => {0}.
    {12}{Y} => {13}.
    {12} => {13}.
    {13}{Y} => {12}{Y}.
    {13} => {14}.
    {14}.

    ? {0}{X}^11{Y}^9.

The output of `simp_cr.py -f` in this case is:

    # {0} --> 17
    # {10} --> 37
    # {11} --> 29
    # {12} --> 11
    # {13} --> 19
    # {14} --> 59
    # {1} --> 13
    # {2} --> 43
    # {3} --> 41
    # {4} --> 61
    # {5} --> 47
    # {6} --> 3
    # {7} --> 23
    # {8} --> 31
    # {9} --> 53
    # {X} --> 5
    # {Y1} --> 7
    # {Y} --> 2
    # {Z} --> 67

    85 => 65.
    17 => 11.
    26 => 86.
    13 => 3.
    86 => 41.
    43 => 41.
    41 => 427.
    61 => 3149.
    47 => 13.
    21 => 161.
    3 => 37.
    161 => 31.
    23 => 31.
    31 => 106.
    53 => 3.
    185 => 29.
    37 => 29.
    29 => 17.
    22 => 19.
    11 => 19.
    38 => 22.
    19 => 59.
    59.

    ? 425000000000.

The comments indicate the prime that corresponds to each variable in the
original source program.
Notice that the query `425000000000` is equivalent to
`17 * 5^11 * 2^9`. That is, we are asking for the product of
`11` and `9`. The answer will be given as the exponent of
`67`. Indeed we get:

    6045127530961181628652411227196693490382260383969108811846856679868932815922570165203117478978324258618429876174558448218719550835202670830699753771294118292547613370699765040813403

which is exactly `67^99`.

S-with-macros to S compiler
---------------------------

Also part of the Cratylus distribution is the script `ss2s.py` which
translates an S program with macros to a regular S program.

An S program with macros allows defining subroutines with parameters,
and using some basic control constructs (if and while), besides
allowing labels, `inc`, `dec`, `jmp`, `jz` and `jnz`.
The grammar of S-with-macros is a superset of that of S:

    <program> ::= <instructions> <init>

    <instructions> ::= <EMPTY>
                     | <sub> \n <instructions>
                     | <label>: \n <instructions>
                     | <op> \n <instructions>

    <op> ::= inc <var>
           | dec <var>
           | jmp <label>
           | jz <var> <label>
           | jnz <var> <label>
           | <sub_name> <var1> ... <varN>
           | WHILEZ var \n <instructions> \n END
           | WHILENZ var \n <instructions> \n END
           | IFZ var \n <instructions> \n END
           | IFNZ var \n <instructions> \n END

    <sub> ::= SUB <sub_name> <var1> ... <varN> \n <instructions> \n END

    <init> ::= <EMPTY>
              | ! <var> <num> <init>

For instance, the following S-with-macros program calculates factorials:

    SUB rename X Y
        WHILENZ X
            dec X
            inc Y
        END
    END

    SUB bicopy X Y Z
        WHILENZ X
            dec X
            inc Y
            inc Z
        END
    END

    SUB zero X
        WHILENZ X
            dec X
        END
    END

    SUB mult X Y Z
        WHILENZ X 
            dec X
            bicopy Y Y2 Z
            rename Y2 Y
        END
        zero Y
    END

    SUB fact X Y
        inc Y
        WHILENZ X
            bicopy X X1 X2
            mult X1 Y T
            rename T Y
            rename X2 X
            dec X
        END
    END

    fact X Z

    ! X 5

The `ss2s.py` script translates the S-with-macros program to the
following plain S program:

		# fact X Z
		inc Z
	:l:1:
	jz X :l:2
		# bicopy X X1 X2
	:l:3:
	jz X :l:4
		dec X
		inc fact:1:X1
		inc fact:1:X2
	jmp :l:3
	:l:4:
		# mult X1 Y T
	:l:5:
	jz fact:1:X1 :l:6
		dec fact:1:X1
		# bicopy Y Y2 Z
	:l:7:
	jz Z :l:8
		dec Z
		inc mult:1:Y2
		inc fact:1:T
	jmp :l:7
	:l:8:
		# rename Y2 Y
	:l:9:
	jz mult:1:Y2 :l:10
		dec mult:1:Y2
		inc Z
	jmp :l:9
	:l:10:
	jmp :l:5
	:l:6:
		# zero Y
	:l:11:
	jz Z :l:12
		dec Z
	jmp :l:11
	:l:12:
		# rename T Y
	:l:13:
	jz fact:1:T :l:14
		dec fact:1:T
		inc Z
	jmp :l:13
	:l:14:
		# rename X2 X
	:l:15:
	jz fact:1:X2 :l:16
		dec fact:1:X2
		inc X
	jmp :l:15
	:l:16:
		dec X
	jmp :l:1
	:l:2:
		! X 5

By using the S to Cratylus compiler (`s2cr.py` script), this in
turn gets compiled to the following Cratylus program:

    {0} => {1}{Z}.
    {1}{X} => {2}{X}.
    {1} => {32}.
    {2}{X} => {3}{X}.
    {2} => {7}.
    {3}{X} => {4}.
    {3} => {4}.
    {4} => {5}{fact:1:X1}.
    {5} => {6}{fact:1:X2}.
    {6} => {2}.
    {7}{fact:1:X1} => {8}{fact:1:X1}.
    {7} => {19}.
    {8}{fact:1:X1} => {9}.
    {8} => {9}.
    {9}{Z} => {10}{Z}.
    {9} => {14}.
    {10}{Z} => {11}.
    {10} => {11}.
    {11} => {12}{mult:1:Y2}.
    {12} => {13}{fact:1:T}.
    {13} => {9}.
    {14}{mult:1:Y2} => {15}{mult:1:Y2}.
    {14} => {18}.
    {15}{mult:1:Y2} => {16}.
    {15} => {16}.
    {16} => {17}{Z}.
    {17} => {14}.
    {18} => {7}.
    {19}{Z} => {20}{Z}.
    {19} => {22}.
    {20}{Z} => {21}.
    {20} => {21}.
    {21} => {19}.
    {22}{fact:1:T} => {23}{fact:1:T}.
    {22} => {26}.
    {23}{fact:1:T} => {24}.
    {23} => {24}.
    {24} => {25}{Z}.
    {25} => {22}.
    {26}{fact:1:X2} => {27}{fact:1:X2}.
    {26} => {30}.
    {27}{fact:1:X2} => {28}.
    {27} => {28}.
    {28} => {29}{X}.
    {29} => {26}.
    {30}{X} => {31}.
    {30} => {31}.
    {31} => {1}.
    {32}.
    ? {0}{X}^5.

Finally, by using the Cratylus simplifier (script `simp_cr.py` with
the `-v -t "{Z}" Z` command-line switch, we get our first example back:

    H => mZ.
    am => af.
    m => J.
    af => aB.
    f => k.
    aB => u.
    B => u.
    u => cL.
    L => eG.
    G => f.
    ck => cr.
    k => d.
    cr => b.
    r => b.
    bZ => yZ.
    b => j.
    yZ => t.
    y => t.
    t => iK.
    K => lE.
    E => b.
    ij => is.
    j => I.
    is => x.
    s => x.
    x => DZ.
    D => j.
    I => k.
    dZ => wZ.
    d => h.
    wZ => o.
    w => o.
    o => d.
    hl => lp.
    h => g.
    lp => v.
    p => v.
    v => CZ.
    C => h.
    eg => en.
    g => q.
    en => z.
    n => z.
    z => aF.
    F => g.
    aq => A.
    q => A.
    A => m.
    J.
    ? a^5H.

