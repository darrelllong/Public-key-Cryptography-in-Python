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
    Generate a Schmidt-Samoa key pair whose modulus n = p²q has nBits of strength.

    The scheme sits between RSA and Rabin.  Like RSA it uses a public exponent
    and a private inverse, but the modulus n = p²q carries p twice.  This means
    decryption works mod γ = pq, which is strictly smaller than n, so every
    message in [0, γ) round-trips exactly — no probabilistic square-root step is
    needed unlike Rabin.

    The conditions (q-1) ∤ p and (p-1) ∤ q ensure that n is invertible mod
    λ(n) = lcm(p-1, q-1); if either held, gcd(n, λ(n)) > 1 and there would be
    no valid private exponent d.

    Why d = n⁻¹ mod λ(n)?  A CRT argument over the factorisation n = p²q shows
    that m^(nd) ≡ m (mod p) and m^(nd) ≡ m (mod q), so c^d mod γ = m.

    Public key:  n
    Private key: (d, γ)
    """
    size = nBits // 2
    low  = 2**(size - 1) # Assure the primes are each approximately half of the
    high = 2**size - 1   # bits in the modulus.
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    q = f(low, high)
    # Reject q if it would make n non-invertible mod λ(n).
    while p == q or (q - 1) % p == 0 or (p - 1) % q == 0:
        q = f(low, high)
    𝛄 = p * q
    𝝺 = primes.lcm(p - 1, q - 1) # Carmichael λ(n) = lcm(p-1, q-1)
    n = p * p * q
    d = primes.inverse(n, 𝝺)
    return (n, (d, 𝛄))

def encrypt(m, n):
    """
    Apply the public map m^n mod n.

    Unlike textbook RSA, the exponent is the modulus n itself.  The inverse map
    recovers m only for values in [0, γ) where γ = pq; messages above that bound
    are unrecoverable.
    """
    return primes.power_mod(m, n, n)

def decrypt(c, key):
    """
    Recover m by applying the private exponent: c^d mod γ = m.

    Because d ≡ n⁻¹ (mod λ(n)), we have nd ≡ 1 (mod λ(n)), and the CRT argument
    guarantees m^(nd) ≡ m for all m in [0, γ).  Reducing mod γ = pq rather than
    n is the key step that makes exact decryption possible.
    """
    d, 𝛄 = key
    return primes.power_mod(c, d, 𝛄)

import crypto_io as _io

# ── Serialization ─────────────────────────────────────────────────────────────

def ss_public_to_blob(n):       return _io.encode_big_ints([n])
def ss_public_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return r[0] if r and len(r) == 1 else None
def ss_public_to_pem(n):        return _io.pem_wrap("CRYPTOGRAPHY SCHMIDT-SAMOA PUBLIC KEY", ss_public_to_blob(n))
def ss_public_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY SCHMIDT-SAMOA PUBLIC KEY", pem)
    return None if b is None else ss_public_from_blob(b)
def ss_public_to_xml(n):        return _io.xml_wrap("SchmidtSamoaPublicKey", [("n", n)])
def ss_public_from_xml(xml):
    r = _io.xml_unwrap("SchmidtSamoaPublicKey", ["n"], xml)
    return r[0] if r and len(r) == 1 else None

def ss_private_to_blob(d, γ):   return _io.encode_big_ints([d, γ])
def ss_private_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[0], r[1]) if r and len(r) == 2 else None
def ss_private_to_pem(d, γ):    return _io.pem_wrap("CRYPTOGRAPHY SCHMIDT-SAMOA PRIVATE KEY", ss_private_to_blob(d, γ))
def ss_private_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY SCHMIDT-SAMOA PRIVATE KEY", pem)
    return None if b is None else ss_private_from_blob(b)
def ss_private_to_xml(d, γ):    return _io.xml_wrap("SchmidtSamoaPrivateKey", [("d", d), ("gamma", γ)])
def ss_private_from_xml(xml):
    r = _io.xml_unwrap("SchmidtSamoaPrivateKey", ["d", "gamma"], xml)
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
