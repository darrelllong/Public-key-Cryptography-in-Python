# Public key Cryptography in Python
Primality and public-key cryptography routines in Python

* RSA
* Rabin
* El Gamal
* Schmidt-Samoa

Originally written for the students at the University of California, Santa Cruz.

## Public-key Algorithms

The traditional RSA algorithm implemented using the Carmichael 𝜆 rather than Euler's 𝜑.

```
@article{rivest1978method,
  title={A method for obtaining digital signatures and public-key cryptosystems},
  author={Rivest, Ronald and Shamir, Adi and Adleman, Leonard},
  journal={Communications of the ACM},
  volume={21},
  number={2},
  pages={120--126},
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
  pages={469--472},
  year={1985},
  publisher={IEEE}
}
```

The Schmidt-Samoa system (related to RSA and Rabin).

```
@article{schmidt2006new,
  title={A new rabin-type trapdoor permutation equivalent to factoring},
  author={Schmidt-Samoa, Katja},
  journal={Electronic Notes in Theoretical Computer Science},
  volume={157},
  number={3},
  pages={79--94},
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
* Miller-Rabin
* Solovay-Strassen

```
@article{solovay1977fast,
  title={A fast Monte-Carlo test for primality},
  author={Solovay, Robert and Strassen, Volker},
  journal={SIAM journal on Computing},
  volume={6},
  number={1},
  pages={84--85},
  year={1977},
  publisher={SIAM}
}

@article{rabin1980probabilistic,
  title={Probabilistic algorithm for testing primality},
  author={Rabin, Michael O},
  journal={Journal of number theory},
  volume={12},
  number={1},
  pages={128--138},
  year={1980},
  publisher={Elsevier}
}
```
While it is impractical for large integers, one could implement the polynomial-time AKS algorithm.
```

@article{agrawal2004primes,
  title={{PRIMES} is in {P}},
  author={Agrawal, Manindra and Kayal, Neeraj and Saxena, Nitin},
  journal={Annals of Mathematics},
  pages={781--793},
  year={2004},
  publisher={Princeton University and the Institute for Advanced Study}
}
```

Numbers such as this (a Carmichael number):
```
29674495668685510550154174642905332730771991799853043350995075531276838753171770199594238596428121188033664754218345562493168782883
```
will pass both Miller-Rabin and Solovay Strassen.

```
@article{arnault1995constructing,
  title={Constructing Carmichael numbers which are strong pseudoprimes to several bases},
  author={Arnault, Fran{\c{c}}ois},
  journal={Journal of Symbolic Computation},
  volume={20},
  number={2},
  pages={151--161},
  year={1995},
  publisher={Elsevier}
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

This implementation provides these utilities:
* `is_odd(x)` and `is_even(x)`
* `power(a, e)`
* `power_mod(a, e, n)`
* `perfect_power(n)`
* `is_prime_MR(n, k)`
* `is_prime_SS(n, k)`
* `is_prime(n, k)` = `is_prime_MR(n, k)` ∧ `is_prime_SS(n, k)`
* `random_prime(low, high, k)`
* `safe_prime(low, high, k)`
* `rabin_prime(low, high safety)`
* `extended_GCD(a, b)`
* `gcd(a, b)`
* `lcm(a, b)`
* `inverse(a, n)`
* `group_generator(n, p)`

![Cutting the Stone](https://darrelllong.github.io/images/Cutting_the_Stone_(Bosch).jpg)
