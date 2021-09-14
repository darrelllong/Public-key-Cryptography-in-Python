# Public key Cryptography in Python
Primality and public-key cryptography routines in Python

Originally written for the students at the University of California, Santa Cruz.

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

```
@techreport{rabin1979digitalized,
  title={Digitalized signatures and public-key functions as intractable as factorization},
  author={Rabin, Michael O},
  year={1979},
  institution={Massachusetts Institute of Technology Cambridge Laboratory for Computer Science}
}
```

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

The implementation gives you the choice of using *safe primes* for *p* and *q*. This can be
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

# Primality Testing

A primality test is an algorithm for determining whether an input
number is prime. Unlike integer factorization, primality tests do
not generally yield the prime factors, only whether the input number
is prime. Factorization is thought to be a computationally difficult
problem. At the same time, primality testing requires polynomial
time is polynomial in the size of the input (the logarithm of the
cardinality of the number). Some primality tests prove that a number
is prime, while others like Miller–Rabin prove that a number is
composite.

The simplest primality test is trial division: given an input number,
*n*, check whether it is evenly divisible by any prime number between
2 and √*n*. If there is no remainder, then n is composite; else, it
is prime. Of course, trial division is infeasible for large integers.

Probabilistic tests provide provable bounds on the probability of
being fooled by a composite number. Many popular primality tests
are probabilistic tests. Apart from the tested number *n*, these tests
use some other numbers *a*, which are chosen at random from some
sample space; the usual randomized primality tests never report a
prime number as composite, but a composite number can be reported
as prime. Repeating the test can reduce the probability of error
by using several independently chosen values of *a*.

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
