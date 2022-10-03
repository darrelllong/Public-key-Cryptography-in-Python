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

import primes

from random import randrange as uniform

def L(x, n): return (x - 1) // n

def generate_keys(nBits, safe = False):
    """
    Write about the math
    """
    k = nBits // 2
    lo = 2**(k - 1) # Assure the primes are approximately equal in size.
    hi = 2**k - 1
    f = primes.safe_prime if safe else primes.random_prime
    g = 0
    # Should only loop once, but we have to be certain.
    while g != 1:
        p, q = f(lo, hi), f(lo, hi)
        n = p * q
        g = primes.gcd(n, (p - 1) * (q - 1))
    𝝀 = primes.lcm(p - 1, q - 1) # Carmichael 𝝀 function
    𝜻 = uniform(2, n * n)
    u = primes.inverse(L(primes.power_mod(𝜻, 𝝀, n * n), n), n)
    return ((n, 𝝀, u), (n, 𝜻))

def encrypt(m, key):
    """
    Write about the math
    """
    n, 𝜻 = key
    r = uniform(1, n - 1)
    f = primes.power_mod
    return (f(𝜻, m, n * n) * f(r, n, n * n)) % (n * n)

def decrypt(c, key):
    """
    Write about the math
    """
    n, 𝝀, u = key
    f = primes.power_mod
    return (L(f(c, 𝝀, n * n), n) * u) % n

import sys, getopt

def main():
    safe = False

    list, args = getopt.getopt(sys.argv[1:], "s")

    for l, a in list:
        if "-s" in l:
            safe = True

    try:
        bits = int(input("How many bits? "))
    except:
        quit("We needed a positive integer!")

    prv, pub = generate_keys(bits, safe)

    print(f"pub = {pub}")
    print(f"prv = {prv}")
    n = pub[1]
    print(f"lg(n) = {primes.lg(n)}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(primes.encode(m), pub); print(f"En[{m}] = {c}")
            t = primes.decode(decrypt(c, prv)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")

if __name__ == '__main__':
    main()
