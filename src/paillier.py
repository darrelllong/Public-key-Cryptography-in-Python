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

def generate_keys(nBits, safe=True):
    """
    Generate a Paillier key pair whose modulus n = p*q has nBits of strength.

    Security rests on the decisional composite residuosity assumption: it is hard
    to decide whether a random element of Z_{n²}* is an n-th power.  The scheme
    is additively homomorphic — multiplying two ciphertexts mod n² decrypts to
    the sum of the plaintexts — which enables computation on encrypted data.

    ζ = n+1 is the standard choice because the binomial theorem gives
        (n+1)^m ≡ 1 + mn  (mod n²),
    so the L map applied during decryption is exact without an extra inversion.

    u = L(ζ^λ mod n², n)⁻¹ mod n is precomputed so each decryption uses one
    exponentiation and two multiplications instead of recomputing the inverse.

    Public key:  (n, ζ)
    Private key: (n, λ, u)
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
    𝝀 = primes.lcm(p - 1, q - 1) # Carmichael λ(n) = lcm(p-1, q-1); smaller than φ(n)
    𝜻 = n + 1              # Standard choice: (n+1)^m ≡ 1 + mn (mod n²)
    u = primes.inverse(L(primes.power_mod(𝜻, 𝝀, n * n), n), n)
    return ((n, 𝝀, u), (n, 𝜻))

def encrypt(m, key):
    """
    Encrypt plaintext m as c = ζ^m · r^n  mod n².

    The random nonce r blinds the ciphertext so that the same message produces
    a different output each time (semantic security).  Different nonces live in
    different cosets of the n-th-power subgroup but all decrypt the same way
    because λ annihilates every n-th power: r^(nλ) ≡ 1 mod n².
    """
    n, 𝜻 = key
    r = uniform(1, n - 1)
    f = primes.power_mod
    return (f(𝜻, m, n * n) * f(r, n, n * n)) % (n * n)

def decrypt(c, key):
    """
    Decrypt by computing m = L(c^λ mod n²) · u  mod n.

    Raising c to λ kills the blinding nonce (r^(nλ) ≡ 1 mod n²), leaving only
    ζ^(mλ) mod n².  Because ζ = n+1, the binomial theorem gives
    ζ^(mλ) ≡ 1 + mnλ (mod n²), so L produces mλ mod n.  Multiplying by
    u = (λ mod n)⁻¹ recovers m.
    """
    n, 𝝀, u = key
    f = primes.power_mod
    return (L(f(c, 𝝀, n * n), n) * u) % n

import crypto_io as _io

# ── Serialization ─────────────────────────────────────────────────────────────

def paillier_public_to_blob(n, ζ):      return _io.encode_big_ints([n, ζ])
def paillier_public_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[0], r[1]) if r and len(r) == 2 else None
def paillier_public_to_pem(n, ζ):       return _io.pem_wrap("CRYPTOGRAPHY PAILLIER PUBLIC KEY", paillier_public_to_blob(n, ζ))
def paillier_public_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY PAILLIER PUBLIC KEY", pem)
    return None if b is None else paillier_public_from_blob(b)
def paillier_public_to_xml(n, ζ):       return _io.xml_wrap("PaillierPublicKey", [("n", n), ("zeta", ζ)])
def paillier_public_from_xml(xml):
    r = _io.xml_unwrap("PaillierPublicKey", ["n", "zeta"], xml)
    return (r[0], r[1]) if r and len(r) == 2 else None

def paillier_private_to_blob(n, λ, u):  return _io.encode_big_ints([n, λ, u])
def paillier_private_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[0], r[1], r[2]) if r and len(r) == 3 else None
def paillier_private_to_pem(n, λ, u):   return _io.pem_wrap("CRYPTOGRAPHY PAILLIER PRIVATE KEY", paillier_private_to_blob(n, λ, u))
def paillier_private_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY PAILLIER PRIVATE KEY", pem)
    return None if b is None else paillier_private_from_blob(b)
def paillier_private_to_xml(n, λ, u):   return _io.xml_wrap("PaillierPrivateKey", [("n", n), ("lambda", λ), ("u", u)])
def paillier_private_from_xml(xml):
    r = _io.xml_unwrap("PaillierPrivateKey", ["n", "lambda", "u"], xml)
    return (r[0], r[1], r[2]) if r and len(r) == 3 else None

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

if __name__ == '__main__': main()
