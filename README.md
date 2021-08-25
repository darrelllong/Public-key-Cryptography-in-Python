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
