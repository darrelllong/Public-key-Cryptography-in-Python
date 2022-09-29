# Public key Cryptography in Python
Primality and public-key cryptography routines in Python

* Cocks — First public-key algorithm (1973, *classified*)
* RSA
* Rabin
* El Gamal
* Schmidt-Samoa

Originally written for the students at the University of California, Santa Cruz.

## Public-key Algorithms

Clifford Cocks' original proposal for public-key cryptopgraphy. Originally a classified memorandum at GCHQ in 1973.

```
article{cocks1973note,
  title={A note on non-secret encryption},
  author={Cocks, Clifford C},
  journal={CESG Memo},
  year={1973}
}
```

The traditional RSA algorithm implemented using Carmichael's 𝜆 rather than Euler's 𝜑.

```
@article{rivest1978method,
  title={A method for obtaining digital signatures and public-key cryptosystems},
  author={Rivest, Ronald and Shamir, Adi and Adleman, Leonard},
  journal={Communications of the ACM},
  volume={21},
  number={2},
  pages={120-126},
  year={1978},
  publisher={ACM New York, NY, USA}
}
```

Rabin's public-key system based on squaring.

```
@techreport{rabin1979digitalized,
  title={Digitalized signatures and public-key functions as intractable as factorization},
  author={Rabin, Michael O},
  year={1979},
  institution={Massachusetts Institute of Technology Cambridge Laboratory for Computer Science}
}
```

The El Gamal public-key system.

```
@article{elgamal1985public,
  title={A public key cryptosystem and a signature scheme based on discrete logarithms},
  author={ElGamal, Taher},
  journal={IEEE transactions on information theory},
  volume={31},
  number={4},
  pages={469-472},
  year={1985},
  publisher={IEEE}
}
```

The Schmidt-Samoa public-key system (related to RSA and Rabin).

```
@article{schmidt2006new,
  title={A new rabin-type trapdoor permutation equivalent to factoring},
  author={Schmidt-Samoa, Katja},
  journal={Electronic Notes in Theoretical Computer Science},
  volume={157},
  number={3},
  pages={79-94},
  year={2006},
  publisher={Elsevier}
}
```

## Primality Testing

A primality test is an algorithm for determining whether an input
number is prime. Unlike integer factorization, primality tests do
not generally yield the prime factors, only whether the input number
is prime. Factorization is thought to be a computationally *hard*
problem. While at the same time, primality testing has been recently shown to
require polynomial
time. It is polynomial in the size of the input (the logarithm of the
cardinality of the number). Some primality tests prove that a number
is prime, while others like probabilistic Miller–Rabin prove that a number is
composite.

The simplest primality test is trial division: given an input number,
*n*, check whether it is evenly divisible by any prime number between
2 and √*n*. If there is no remainder, then *n* is composite; else, it
is prime. Of course, trial division is infeasible for large integers.

Probabilistic tests provide provable bounds on the probability of
being fooled by a composite number. Many popular primality tests
are probabilistic tests. Apart from the tested number *n*, these tests
use some other numbers *a*, called *witnesses*, which are chosen at random from some
sample space; the usual randomized primality tests never report a
prime number as composite, but a composite number can be reported
as prime. Repeating the test can reduce the probability of error
by using several independently chosen values of *a*.

Implemented here are:
* Solovay-Strassen
* Miller-Rabin
* Baillie-Pomerance-Selfridge-Wagstaff

```
@article{solovay1977fast,
  title={A fast Monte-Carlo test for primality},
  author={Solovay, Robert and Strassen, Volker},
  journal={SIAM journal on Computing},
  volume={6},
  number={1},
  pages={84-85},
  year={1977},
  publisher={SIAM}
}

@article{rabin1980probabilistic,
  title={Probabilistic algorithm for testing primality},
  author={Rabin, Michael O},
  journal={Journal of number theory},
  volume={12},
  number={1},
  pages={128-138},
  year={1980},
  publisher={Elsevier}
}

@article{baillie1980lucas,
  title={Lucas pseudoprimes},
  author={Baillie, Robert and Wagstaff, Samuel S},
  journal={Mathematics of Computation},
  volume={35},
  number={152},
  pages={1391--1417},
  year={1980}
}

@article{pomerance1980pseudoprimes,
  title={The pseudoprimes to 25×10⁹},
  author={Pomerance, Carl and Selfridge, John L and Wagstaff, Samuel S},
  journal={Mathematics of Computation},
  volume={35},
  number={151},
  pages={1003--1026},
  year={1980}
}
```
While it is impractical for large integers, one could implement the polynomial-time AKS algorithm.
```

@article{agrawal2004primes,
  title={{PRIMES} is in {P}},
  author={Agrawal, Manindra and Kayal, Neeraj and Saxena, Nitin},
  journal={Annals of Mathematics},
  pages={781-793},
  year={2004},
  publisher={Princeton University and the Institute for Advanced Study}
}
```
Be cautious of Carmichel pseudoprimes.
```
@article{arnault1995constructing,
  title={Constructing Carmichael numbers which are strong pseudoprimes to several bases},
  author={Arnault, Fran{\c{c}}ois},
  journal={Journal of Symbolic Computation},
  volume={20},
  number={2},
  pages={151-161},
  year={1995},
  publisher={Elsevier}
}
```
# Factoring
Currently only Pollard's &#961; method is implemented. It is useful
for *medium*-sized composites, but not for the sizes used for
public-key cryptography.
The General Number Field Sieve is not really Python-friendly.

If you want to factor numbers used for public keys, you should not be doing it in
Python and should expect to rent time at a data center.

```
@article{cite-key,
        author = {Pollard, J.  M.},
        date = {1975/09/01},
        doi = {10.1007/BF01933667},
        id = {Pollard1975},
        isbn = {1572-9125},
        journal = {BIT Numerical Mathematics},
        number = {3},
        pages = {331--334},
        title = {A monte carlo method for factorization},
        url = {https://doi.org/10.1007/BF01933667},
        volume = {15},
        year = {1975},
}

@inproceedings{valenta2016factoring,
  title={Factoring as a service},
  author={Valenta, Luke and Cohney, Shaanan and Liao, Alex and Fried, Joshua and Bodduluri, Satya and Heninger, Nadia},
  booktitle={International Conference on Financial Cryptography and Data Security},
  pages={321--338},
  year={2016},
  organization={Springer}
}
```
# Utility Routines
This implementation gives you the choice of using *safe primes* for *p* and *q*. This can be
a little slow, but you do not need to do this more than once.

```
@misc{cryptoeprint:2001:007,
    author       = {Ronald Rivest and Robert Silverman},
    title        = {Are 'Strong' Primes Needed for {RSA}?},
    howpublished = {Cryptology ePrint Archive, Report 2001/007},
    year         = {2001},
    note         = {\url{https://ia.cr/2001/007}},
}
```

This implementation provides these utilities (these provide the same functionality as some built-ins, but the point is to teach):
* `is_odd(x)` and `is_even(x)`
* `power(a, e)`
* `power_mod(a, e, n)`
* `perfect_power(n)`
* `is_prime_MR(n, k)` &mdash; Miller-Rabin
* `is_prime_SS(n, k)` &mdash; Solovay-Strassen
* `is_prime_LS(n)` &mdash; Lucas (probable prime)
* `is_prime_F(n)` &mdash; Fermat
* `is_prime_BPSW(n)` &mdash; Baillie-Pomerance-Selfridge-Wagstaff
* `is_prime(n, k)` = `is_prime_MR(n, k)`
* `random_prime(low, high, k)`
* `safe_prime(low, high, k)`
* `rabin_prime(low, high safety)`
* `extended_GCD(a, b)`
* `gcd(a, b)`
* `lcm(a, b)`
* `inverse(a, n)`
* `group_generator(n, p)`
* `rho(n)`
* `factor(n)`

![Cutting the Stone](https://darrelllong.github.io/images/Cutting_the_Stone_(Bosch).jpg)
