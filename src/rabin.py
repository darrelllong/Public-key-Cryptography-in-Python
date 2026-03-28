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
    Generate a Rabin key pair whose modulus n = p*q has n_bits of strength.

    Primes are grown by 16 bits each (x = n_bits//2 + 16) to make room for the
    32-bit disambiguation tag that is prepended to the plaintext before squaring.
    Without the extra headroom the tagged payload could overflow n, making
    decryption ambiguous.
    """
    x = n_bits // 2 + 32 // 2 # Make room for the tag (two pieces of 16 bits)
    p = primes.rabin_prime(2**x, 2**(x + 1) - 1, safe)
    q = primes.rabin_prime(2**x, 2**(x + 1) - 1, safe)
    while p == q:
        q = primes.rabin_prime(2**(x - 1), 2**x - 1, safe)
    return (p * q, (p, q))

# Arbitrary 32-bit disambiguation tag — same constant used by the Rust crate.
# It is not a cryptographic checksum; its only job is to let the decryptor pick
# the right one of the four square roots that squaring mod n can produce.
_h = crc32(b"Michael O. Rabin")

def encrypt(m, n):
    """
    Encrypt by squaring the tagged payload mod n.

    The message is shifted left by 32 bits and the tag _h is inserted in the low
    word, then n//2 is added so the payload is large enough that its square
    cannot be trivially detected as a perfect power without knowing the factors.
    Encryption is simply squaring: c = payload² mod n.
    """
    return primes.power_mod(m * 2**32 + _h + n // 2, 2, n) # Insert tag and square (mod n)

def decrypt(m, key):
    """
    Recover the plaintext by finding the unique square root that carries the tag.

    Squaring mod n = p*q has four square roots.  We compute all four via the
    Chinese Remainder Theorem — each factor p and q independently admits two
    square roots (±√m mod p and ±√m mod q), which CRT combines into four roots
    mod n.  Only the root whose low 32 bits equal _h is the true payload; the
    other three are discarded.  The original message is the payload >> 32.
    """
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
    raise ValueError("Decryption failed: no valid square root with matching CRC tag found.")

import crypto_io as _io

# ── Serialization ─────────────────────────────────────────────────────────────

def rabin_public_to_blob(n):          return _io.encode_big_ints([n])
def rabin_public_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return r[0] if r and len(r) == 1 else None
def rabin_public_to_pem(n):           return _io.pem_wrap("CRYPTOGRAPHY RABIN PUBLIC KEY", rabin_public_to_blob(n))
def rabin_public_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY RABIN PUBLIC KEY", pem)
    return None if b is None else rabin_public_from_blob(b)
def rabin_public_to_xml(n):           return _io.xml_wrap("RabinPublicKey", [("n", n)])
def rabin_public_from_xml(xml):
    r = _io.xml_unwrap("RabinPublicKey", ["n"], xml)
    return r[0] if r and len(r) == 1 else None

def rabin_private_to_blob(n, p, q):   return _io.encode_big_ints([n, p, q])
def rabin_private_from_blob(blob):
    r = _io.decode_big_ints(blob)
    return (r[1], r[2]) if r and len(r) == 3 else None  # return (p, q)
def rabin_private_to_pem(n, p, q):    return _io.pem_wrap("CRYPTOGRAPHY RABIN PRIVATE KEY", rabin_private_to_blob(n, p, q))
def rabin_private_from_pem(pem):
    b = _io.pem_unwrap("CRYPTOGRAPHY RABIN PRIVATE KEY", pem)
    return None if b is None else rabin_private_from_blob(b)
def rabin_private_to_xml(n, p, q):    return _io.xml_wrap("RabinPrivateKey", [("n", n), ("p", p), ("q", q)])
def rabin_private_from_xml(xml):
    r = _io.xml_unwrap("RabinPrivateKey", ["n", "p", "q"], xml)
    return (r[1], r[2]) if r and len(r) == 3 else None  # return (p, q)

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

if __name__ == '__main__': main()
