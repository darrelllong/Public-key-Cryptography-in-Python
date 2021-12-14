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

# Generate an efficient description of a cyclic group G of order p, with generator r.
#
# Choose a random integer a ∊ {(p – 1)/2, ..., p − 1}
#
# Compute b = r^a
#
# The public key consists of the values (p, r, b)
#
# The private key consists of the values (p, a)

def generate_keys(k, safe = True):
    low  = 2**(k - 1)
    high = 2**k - 1
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    r = primes.group_generator(2**16 + 1, p)
    a = uniform((p - 1) // 2, p - 1)
    b = primes.power_mod(r, a, p)
    return ((p, a), (p, r, b))

def encrypt(m, key):
    (p, r, b) = key
    k = uniform(1, p - 2)
    𝛾 = primes.power_mod(r, k, p)
    𝛿 = (m * primes.power_mod(b, k, p)) % p
    return (𝛾, 𝛿)

def decrypt(m, key):
    (p, a) = key
    (𝛾, 𝛿) = m
    return (primes.power_mod(𝛾, p - 1 - a, p) * 𝛿) % p

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

    (prv, pub) = generate_keys(bits, safe)

    print(f"pub = {pub}")
    print(f"prv = {prv}")

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
