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
    Generate a Cocks key pair whose modulus n = p*q has nBits of strength.

    Cocks (1973) predates RSA by five years.  It was classified by GCHQ and not
    published until 1997.  The scheme is historically important as the first
    known public-key construction, though impractical for bulk data because
    ciphertexts are as large as n.

    We enforce p < q so that q is the unambiguous "private prime" stored in the
    serialized key.  The inversion π = p⁻¹ mod (q-1) must exist; if it does not
    (i.e. gcd(p, q-1) > 1) we pick a fresh q and retry — this happens rarely.

    Public key:  n
    Private key: (π, q)
    """
    size = nBits // 2
    low  = 2**(size - 1) # Assure the primes are each approximately half of the
    high = 2**size - 1   # bits in the modulus.
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    q = f(low, high)
    while p == q:
        q = f(low, high)
    if p > q:
        p, q = q, p   # enforce p < q so q is unambiguously the stored private prime
    π = primes.inverse(p, q - 1)
    while π is None:  # retry if p is not invertible mod q – 1 (gcd(p, q-1) ≠ 1)
        q = f(low, high)
        while p == q:
            q = f(low, high)
        if p > q:
            p, q = q, p
        π = primes.inverse(p, q - 1)
    n = p * q
    return (n, (π, q))

def encrypt(m, n):
    """
    Raise m to the n-th power mod n.

    The security of the scheme relies on the difficulty of computing n-th roots
    modulo a product of two unknown primes — analogous to the RSA problem.
    """
    return primes.power_mod(m, n, n)

def decrypt(c, key):
    """
    Recover m by computing c^π mod q = m^(n·π) mod q = m^1 mod q = m.

    The exponent chain works because n = p*q ≡ p (mod q-1) (since q ≡ 1 mod q-1
    is false — actually q mod (q-1) = 1, so pq mod (q-1) = p*1 = p mod (q-1)),
    and π ≡ p⁻¹ (mod q-1), so n*π ≡ 1 (mod q-1).  Fermat's little theorem then
    gives m^(n*π) ≡ m^1 (mod q) for any m not divisible by q.
    """
    (π, q) = key
    return primes.power_mod(c, π, q)

import crypto_io as _io

# ── Serialization ─────────────────────────────────────────────────────────────

def cocks_public_to_blob(n):       return _io.encode_big_ints([n])
def cocks_public_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return r[0] if r and len(r) == 1 else None
def cocks_public_to_pem(n):        return _io.pem_wrap("CRYPTOGRAPHY COCKS PUBLIC KEY", cocks_public_to_blob(n))
def cocks_public_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY COCKS PUBLIC KEY", pem)
    return None if b is None else cocks_public_from_blob(b)
def cocks_public_to_xml(n):        return _io.xml_wrap("CocksPublicKey", [("n", n)])
def cocks_public_from_xml(xml):
    r = _io.xml_unwrap("CocksPublicKey", ["n"], xml)
    return r[0] if r and len(r) == 1 else None

def cocks_private_to_blob(π, q):   return _io.encode_big_ints([π, q])
def cocks_private_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[0], r[1]) if r and len(r) == 2 else None
def cocks_private_to_pem(π, q):    return _io.pem_wrap("CRYPTOGRAPHY COCKS PRIVATE KEY", cocks_private_to_blob(π, q))
def cocks_private_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY COCKS PRIVATE KEY", pem)
    return None if b is None else cocks_private_from_blob(b)
def cocks_private_to_xml(π, q):    return _io.xml_wrap("CocksPrivateKey", [("pi", π), ("q", q)])
def cocks_private_from_xml(xml):
    r = _io.xml_unwrap("CocksPrivateKey", ["pi", "q"], xml)
    return (r[0], r[1]) if r and len(r) == 2 else None

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
    print(f"(π, q) = {de}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(primes.encode(m), en); print(f"En[{m}] = {c}")
            t = primes.decode(decrypt(c, de)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")

if __name__ == '__main__': main()
