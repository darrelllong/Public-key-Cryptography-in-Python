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
from zlib   import crc32

def generate_keys(n_bits, safe=True):
    """
    Generate and return a key with n_bits of strength.
    Default is to use safe random numbers.
    """
    x = n_bits // 2 + 32 // 2 # Make room for the tag (two pieces of 16 bits)
    p = primes.rabin_prime(2**x, 2**(x + 1) - 1, safe)
    q = primes.rabin_prime(2**x, 2**(x + 1) - 1, safe)
    while p == q:
        q = primes.rabin_prime(2**(x - 1), 2**x - 1, safe)
    return (p * q, (p, q))

_h = crc32(b"Michael O. Rabin")

def encrypt(m, n):
    """
    Rabin encryption is squaring the message. We need to make sure that the square exceeds
    n before the modulus, otherwise it is trivial to decode by detecting a perfect power (2
    in this case. We do this by adding n // 2 before squaring.

    We descriminate among the four possible square roots by adding a 32-bit CRC tag.
    """
    return primes.power_mod(m * 2**32 + _h + n // 2, 2, n) # Insert tag and square (mod n)

# Decryption requires us to compute the four square roots (mod n). We can only efficiently
# do this if we know p and q.

def decrypt(m, key):
    (p, q) = key
    n = p * q
    (g, (yP, yQ)) = primes.extended_GCD(p, q)
    mP = primes.power_mod(m, (p + 1) // 4, p)
    mQ = primes.power_mod(m, (q + 1) // 4, q)
    x = (yP * p * mQ + yQ * q * mP) % n
    y = (yP * p * mQ - yQ * q * mP) % n
    msgs = [x - n // 2, n - x - n // 2, y - n // 2, n - y - n // 2]
    for d in msgs:
        if d % 2**32 == _h:
            return d // 2**32
    return 1279869254 # FAIL

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

    (n, k) = generate_keys(bits, safe)

    print(f"n = {n}")
    print(f"lg({n}) = {primes.lg(n)}")
    print(f"key = {k}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(primes.encode(m), n); print(f"En[{m}] = {c}")
            t = primes.decode(decrypt(c, k)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")

if __name__ == '__main__':
    main()
