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

def generate_keys(k, safe=True):
    """
    Generate an ElGamal key pair whose prime modulus p has k bits of strength.

    Security rests on the discrete logarithm problem: given p, r, and b = rᵃ mod p,
    it is computationally infeasible to recover the secret exponent a.  The scheme is
    probabilistic — each encryption draws a fresh random session key, so the same
    plaintext produces a different ciphertext every time.

    The generator r is bounded below by 2¹⁶ + 1 to avoid degenerate small generators
    that expose group structure.  The secret exponent a is drawn from the upper half
    of [0, p-1] so it is large enough to resist baby-step / giant-step attacks sized
    for small exponents.

    Public key:  (p, r, b)  where b = rᵃ mod p
    Private key: (p, a)
    """
    low  = 2**(k - 1)
    high = 2**k - 1
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    r = primes.group_generator(2**16 + 1, p)
    a = uniform((p - 1) // 2, p - 1)
    b = primes.power_mod(r, a, p)
    return ((p, a), (p, r, b))

def encrypt(m, key):
    """
    Encrypt m by masking it with b^k, then publishing the hint γ = r^k.

    The session key k is chosen freshly at random so the ciphertext (γ, δ) is
    computationally indistinguishable from a random pair in Z_p × Z_p to anyone
    who does not know a.  The mask b^k = r^(ak) is only recoverable from γ by
    someone who knows a, because computing a from b = r^a is the discrete-log problem.
    """
    p, r, b = key
    k = uniform(1, p - 2)
    𝛾 = primes.power_mod(r, k, p)
    𝛿 = (m * primes.power_mod(b, k, p)) % p
    return (𝛾, 𝛿)

def decrypt(m, key):
    """
    Decrypt by stripping the mask: δ · γ^(p−1−a) ≡ m (mod p).

    Fermat's little theorem gives γ^(p−1) ≡ 1 (mod p), so
        γ^(p−1−a) = γ^(−a) mod p = r^(−ak) mod p.
    Multiplying δ = m · r^(ak) by this inverse cancels the mask and recovers m.
    """
    p, a = key
    𝛾, 𝛿 = m
    return (primes.power_mod(𝛾, p - 1 - a, p) * 𝛿) % p

import crypto_io as _io

# ── Serialization ─────────────────────────────────────────────────────────────
# Public key layout:  [p, exponent_bound, generator, public_component] = [p, p-1, g, b]
# Private key layout: [p, exponent_modulus, a] = [p, p-1, a]

def elgamal_public_to_blob(p, g, b):      return _io.encode_big_ints([p, p - 1, g, b])
def elgamal_public_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[0], r[2], r[3]) if r and len(r) == 4 else None  # (p, g, b)
def elgamal_public_to_pem(p, g, b):       return _io.pem_wrap("CRYPTOGRAPHY ELGAMAL PUBLIC KEY", elgamal_public_to_blob(p, g, b))
def elgamal_public_from_pem(pem):
    b2 = _io.pem_unwrap("CRYPTOGRAPHY ELGAMAL PUBLIC KEY", pem)
    return None if b2 is None else elgamal_public_from_blob(b2)
def elgamal_public_to_xml(p, g, b):
    return _io.xml_wrap("ElGamalPublicKey", [("p", p), ("exponent-bound", p - 1), ("generator", g), ("public-component", b)])
def elgamal_public_from_xml(xml):
    r = _io.xml_unwrap("ElGamalPublicKey", ["p", "exponent-bound", "generator", "public-component"], xml)
    return (r[0], r[2], r[3]) if r and len(r) == 4 else None  # (p, g, b)

def elgamal_private_to_blob(p, a):        return _io.encode_big_ints([p, p - 1, a])
def elgamal_private_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[0], r[2]) if r and len(r) == 3 else None  # (p, a)
def elgamal_private_to_pem(p, a):         return _io.pem_wrap("CRYPTOGRAPHY ELGAMAL PRIVATE KEY", elgamal_private_to_blob(p, a))
def elgamal_private_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY ELGAMAL PRIVATE KEY", pem)
    return None if b is None else elgamal_private_from_blob(b)
def elgamal_private_to_xml(p, a):
    return _io.xml_wrap("ElGamalPrivateKey", [("p", p), ("exponent-modulus", p - 1), ("a", a)])
def elgamal_private_from_xml(xml):
    r = _io.xml_unwrap("ElGamalPrivateKey", ["p", "exponent-modulus", "a"], xml)
    return (r[0], r[2]) if r and len(r) == 3 else None  # (p, a)

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

if __name__ == '__main__': main()
