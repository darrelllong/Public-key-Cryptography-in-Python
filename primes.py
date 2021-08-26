#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BSD 2-Clause License
#
# Copyright (c) 2021, Darrell Long
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

def is_even(n): return n % 2 == 0

def is_odd(n): return n % 2 == 1

# a^b (mod n) using the method of repeated squares
#
# The key here is that every integer can be written as a sum of powers of 2 (binary numbers)
# and that includes the exponent. By repeated squaring we get a raised to a power of 2. Also
# recall that a^b * a^c = a^(b + c), so rather than adding we multiply since we are dealing
# with the exponent.

def power_mod(a, d, n):
    v = 1 # Value
    p = a # Powers of a
    while d > 0: # 1 bit in the exponent
        if is_odd(d):
            v = (v * p) % n
        p = p**2 % n # Next power of two
        d //= 2
    return v

# Witness loop of the Miller-Rabin probabilistic primality test

def witness(a, n):
    u = n - 1
    t = 0
    while is_even(u):
        t  += 1
        u //= 2
    x = power_mod(a, u, n)
    for _ in range(0, t):
        y = power_mod(x, 2, n)
        if y == 1 and x != 1 and x != n - 1:
            return True
        x = y
    return x != 1

from random import randrange as uniform

# Miller-Rabin probabilistic primality test

def is_prime_MR(n, k):
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n < 4:
        return True
    for _ in range (0, k):
        a = uniform(2, n - 1) # Euler witness (or liar)
        if witness(a, n):
            return False
    return True

# Compute the Jacobi symbol:
#  n
# (-)
#  k

def Jacobi(n, k):
    assert(k > 0 and is_odd(k))
    n = n % k
    t = 1
    while n != 0:
        while is_even(n):
            n = n // 2
            r = k % 8
            t = -t if r == 3 or r == 5 else t
        n, k = k, n
        t = -t if n % 4 == 3 and k % 4 == 3 else t
        n = n % k
    if k == 1:
        return t
    else:
        return 0

def is_prime_SS(n, k):
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n < 4:
        return True
    for _ in range(0, k):
        a = uniform(2, n - 1) # Euler witness (or liar)
        x = Jacobi(a, n)
        if x == 0 or power_mod(a, (n - 1) // 2, n) != x % n:
            return False
    return True

# Default

is_prime = is_prime_SS

# Routines to generate primes

def random_prime(low, high):
    """
    Generate and return a random prime in the range [low, high].
    """
    guess = 0 # Certainly not prime!
    while not is_prime(guess, 100):
        guess = uniform(low, high) # Half will be even, the rest have Pr[prime] ≈ 1/log(N).
    return guess


def safe_prime(low, high):
    """
    Generate and return a safe prime in the range [low, high].

    A safe prime follows a Sophie German prime. If prime(p) and prime(2p + 1)
    then p is a Sophie Germain prime and 2p + 1 is a safe prime.
    """
    p = random_prime(low, high)
    while not is_prime(2 * p + 1,100):
        p = random_prime(low, high)
    return 2 * p + 1

# Rabin prime

def rabin_prime(low, high, safe=True):
    """
    Generate a Rabin prime in the range [low, high].
    Default is to generate a safe prime.
    Passing safe=False will generate a random prime instead.
    """
    f = safe_prime if safe else random_prime
    p = f(low, high)
    while p % 4 != 3:
        p = f(low, high)
    return p

# Euclidean extended greatest common divisor

def extended_GCD(a, b):
    """
    Run the extended Euclid algorithm on a, b.
    Returns (remainder, (s, t))
    """
    (r, rP) = (a, b)
    (s, sP) = (1, 0)
    (t, tP) = (0, 1)
    while rP != 0:
        q = r // rP
        (r, rP) = (rP, r - q * rP)
        (s, sP) = (sP, s - q * sP)
        (t, tP) = (tP, t - q * tP)
    return (r, (s, t))

# A generator must not be congruent to 1 for any of its powers that are
# proper divisors of p – 1.  Since p is safe prime, there are only two:
# 2 and (p – 1) / 2. The number of such generators is 𝜑(p – 1).

def group_generator(n, p):
    """
    Creates a generator in the neighborhood of n for the group defined by p

    A generator must not be congruent to 1 for any of its powers that are proper divisors
    of p – 1.  Since p is safe prime, there are only two: 2 and (p – 1) / 2. The number of
    such generators is 𝜑(p – 1).
    """
    g = n
    q = (p - 1) // 2
    while power_mod(g, 2, p) == 1 and power_mod(g, q, p) == 1:
        g = g + 1
    return g

# Euclidean greatest common divisor

def gcd(a, b):
    """
    Compute the greatest common divisor gcd(a, b)
    """
    while b != 0:
        a, b = b, a % b
    return a

# Least common multiple

def lcm(a, b):
    """
    Compute the least common multiple lcm(a, b)
    """
    return abs(a * b) // gcd(a, b)

# Multiplicative inverse of a (mod n), using Bézout's identity.

def inverse(a, n):
    """
    Compute the muliplicative inverse of a (mod n) using the Euclidean algorithm and Bézout's
    identity.
    """
    r, rP = n, a
    t, tP = 0, 1
    while rP != 0:
        q = r // rP
        r, rP = rP, r - q * rP
        t, tP = tP, t - q * tP
    if r > 1:
        return "no inverse"
    if t < 0:
        return t + n
    else:
        return t

# Interactive test

if __name__ == '__main__':
    g = 1
    try:
        while g != 0:
            g = int(input("?? "))
            if g == 2 or is_odd(g) and is_prime(g, 100):
                print(f"{g} is probably prime.")
            else:
                print(f"{g} is composite.")
    except:
        print("\nSo long!")
