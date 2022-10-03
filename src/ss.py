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

def generate_keys(nBits, safe=True):
    """
    Generate and return a key with n_bits of strength.
    Default is to use safe random numbers.
    """
    size = nBits // 2
    low  = 2**(size - 1) # Assure the primes are each approximately half of the
    high = 2**size - 1   # bits in the modulus.
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    q = f(low, high)
    while p == q or (p - 1) % (q - 1) == 0 or (q - 1) % (p - q) == 0:
        q = f(low, high)
    𝛄 = p * q
    𝝺 = primes.lcm(p - 1, q - 1) # Carmichael 𝝺(n) = lcm(𝝺(p), 𝝺(q)) = lcm(p - 1, q - 1)
    n = p * p * q
    d = primes.inverse(n, 𝝺)
    return (n, (d, 𝛄))

def encrypt(m, n):
    """
    Write about the algorithm
    """
    return primes.power_mod(m, n, n)

def decrypt(c, key):
    """
    Write about the algorithm
    """
    d, 𝛄 = key
    return primes.power_mod(c, d, 𝛄)

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

    (en, de) = generate_keys(bits, safe)

    print(f"n = {en}")
    print(f"lg(n) = {primes.lg(en)}")
    print(f"(d, 𝛄) = {de}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(primes.encode(m), en); print(f"En[{m}] = {c}")
            t = primes.decode(decrypt(c, de)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")

if __name__ == '__main__': main()
