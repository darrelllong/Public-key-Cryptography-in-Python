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

from random import randrange as uniform
from base64 import standard_b64encode as b64encode
from base64 import standard_b64decode as b64decode

import primes

# Generate a key (e, d, n) of a specified bit-length with optional safe primes

def generate_keys(nBits, safe=True):
    """
    Generates the RSA key pairs: (e, n) and (d, n)
    You have the option of using safe primes, though this is probably unnecessary.

    Each of the generated primes p and q will each have approximately 1/2 of the bits.

    Instead of 𝜑(n), we use λ(n) for the modulus. λ is slightly more efficient.

               16
    e will be 2  + 1 unless gcd(e, λ) ≠ 1, in which case is it will be slightly larger.

    Return the triple (e, d, n)
    """
    size = nBits // 2
    low  = 2**(size - 1) # Assure the primes are each approximately half of the
    high = 2**size - 1   # bits in the modulus.
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    q = f(low, high)
    while p == q:
        q = f(low, high)
    𝝺 = primes.lcm(p - 1, q - 1) # Carmichael 𝝺(n) = lcm(𝝺(p), 𝝺(q)) = lcm(p - 1, q - 1)
    k = 16
    e = 2**k + 1             # Default public exponent
    while primes.gcd(e, 𝝺) != 1: # Happens only if we are very, very unlucky
        k += 1
        e = 2**k + 1
    d = primes.inverse(e, 𝝺) # The private exponent
    n = p * q                # The modulus
    return (e, d, n)

def encrypt(m, e, n): return primes.power_mod(m, e, n)

def decrypt(c, d, n): return primes.power_mod(c, d, n)

# The number of bytes required to hold n.

def byteLength(n: int) -> int:
    return (n.bit_length() // 8) + (1 if n.bit_length() % 8 != 0 else 0)

# Create a public SSH key string from e and n.
#
# The format of an ssh key is:
#     [key-type (always "ssh-rsa" here)] [e] [n]
# Where each field is made up of:
#     a 32-bit integer -- the length n of the field; and
#     n bytes -- the contents of the field.

def publicKeyToStr(e, n):
    key_type = b"ssh-rsa"
    key = bytearray()

    key.extend(len(key_type).to_bytes(4, "big") + key_type)
    key.extend(byteLength(e).to_bytes(4, "big") + e.to_bytes(byteLength(e), "big"))
    key.extend(byteLength(n).to_bytes(4, "big") + n.to_bytes(byteLength(n), "big"))

    key_b64 = b64encode(key).decode("utf-8")

    return "ssh-rsa " + key_b64

# Retrieve (e, n) from a public ssh key string.

def publicKeyFromStr(key):
    assert key.startswith("ssh-rsa")

    # The key-string is a type (i.e., "ssh-rsa") followed by e and n, followed
    # by an optional comment. We only care about e and n.
    key = key.split(" ")[1]
    key = b64decode(bytes(key, "utf-8"))

    # The current index in the key.
    i = 0

    # Read key type.
    length = int.from_bytes(key[i:i + 4], "big")
    key_type = key[i + 4:i + 4 + length]
    assert key_type == b"ssh-rsa"
    i += 4 + length

    # Read e.
    length = int.from_bytes(key[i:i + 4], "big")
    e = int.from_bytes(key[i + 4:i + 4 + length], "big")
    i += 4 + length

    # Read n.
    length = int.from_bytes(key[i:i + 4], "big")
    n = int.from_bytes(key[i + 4:i + 4 + length], "big")

    return (e, n)

import crypto_io as _io

# ── Extended key generation (returns p and q for PKCS#1 CRT fields) ───────────

def generate_rsa_full_keys(nBits, safe=True):
    """Like generate_keys but also returns the primes p and q."""
    size = nBits // 2
    low  = 2**(size - 1)
    high = 2**size - 1
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    q = f(low, high)
    while p == q:
        q = f(low, high)
    𝝺 = primes.lcm(p - 1, q - 1)
    k = 16
    e = 2**k + 1
    while primes.gcd(e, 𝝺) != 1:
        k += 1
        e = 2**k + 1
    d = primes.inverse(e, 𝝺)
    n = p * q
    return (e, d, n, p, q)

# ── RSA PKCS#1 / SPKI / PKCS#8 serialization ─────────────────────────────────

def rsa_public_to_pkcs1_der(e, n):
    body = _io._der_integer(n) + _io._der_integer(e)
    return _io._der_sequence(body)

def rsa_public_from_pkcs1_der(der):
    outer = _io._DerReader(der)
    seq = outer.read_tlv(0x30)
    if seq is None or not outer.done():
        return None
    r = _io._DerReader(seq)
    n = r.read_bigint()
    e = r.read_bigint()
    if n is None or e is None or not r.done() or e <= 1:
        return None
    return (e, n)

def rsa_public_to_spki_der(e, n):
    pkcs1 = rsa_public_to_pkcs1_der(e, n)
    alg   = _io._der_oid(_io._RSA_OID) + _io._der_null()
    body  = _io._der_sequence(alg) + _io._der_bit_string(pkcs1)
    return _io._der_sequence(body)

def rsa_public_from_spki_der(der):
    outer = _io._DerReader(der)
    seq = outer.read_tlv(0x30)
    if seq is None or not outer.done():
        return None
    r = _io._DerReader(seq)
    alg_seq = r.read_tlv(0x30)
    bs      = r.read_tlv(0x03)
    if alg_seq is None or bs is None or not r.done():
        return None
    if not bs or bs[0] != 0x00:
        return None
    alg_r = _io._DerReader(alg_seq)
    oid   = alg_r.read_tlv(0x06)
    alg_r.read_tlv(0x05)
    if oid is None or not alg_r.done() or oid != _io._RSA_OID:
        return None
    return rsa_public_from_pkcs1_der(bs[1:])

def rsa_private_to_pkcs1_der(e, d, n, p, q):
    d_p   = d % (p - 1)
    d_q   = d % (q - 1)
    q_inv = primes.inverse(q, p)
    body  = (_io._der_integer_u8(0) + _io._der_integer(n) + _io._der_integer(e) +
             _io._der_integer(d)    + _io._der_integer(p) + _io._der_integer(q) +
             _io._der_integer(d_p)  + _io._der_integer(d_q) + _io._der_integer(q_inv))
    return _io._der_sequence(body)

def rsa_private_from_pkcs1_der(der):
    outer = _io._DerReader(der)
    seq = outer.read_tlv(0x30)
    if seq is None or not outer.done():
        return None
    r = _io._DerReader(seq)
    ver = r.read_small_uint()
    if ver is None or ver != 0:
        return None
    n = r.read_bigint(); e = r.read_bigint(); d = r.read_bigint()
    p = r.read_bigint(); q = r.read_bigint()
    r.read_bigint(); r.read_bigint(); r.read_bigint()  # consume CRT fields
    if any(v is None for v in [n, e, d, p, q]) or not r.done():
        return None
    return (e, d, n, p, q)

def rsa_private_to_pkcs8_der(e, d, n, p, q):
    pkcs1 = rsa_private_to_pkcs1_der(e, d, n, p, q)
    alg   = _io._der_oid(_io._RSA_OID) + _io._der_null()
    body  = _io._der_integer_u8(0) + _io._der_sequence(alg) + _io._der_octet_string(pkcs1)
    return _io._der_sequence(body)

def rsa_private_from_pkcs8_der(der):
    outer = _io._DerReader(der)
    seq = outer.read_tlv(0x30)
    if seq is None or not outer.done():
        return None
    r = _io._DerReader(seq)
    ver     = r.read_small_uint()
    alg_seq = r.read_tlv(0x30)
    inner   = r.read_tlv(0x04)
    if ver is None or ver != 0 or alg_seq is None or inner is None or not r.done():
        return None
    alg_r = _io._DerReader(alg_seq)
    oid   = alg_r.read_tlv(0x06)
    alg_r.read_tlv(0x05)
    if oid is None or not alg_r.done() or oid != _io._RSA_OID:
        return None
    return rsa_private_from_pkcs1_der(inner)

def rsa_public_to_pkcs1_pem(e, n):       return _io.pem_wrap("RSA PUBLIC KEY",  rsa_public_to_pkcs1_der(e, n))
def rsa_public_from_pkcs1_pem(pem):      b = _io.pem_unwrap("RSA PUBLIC KEY",  pem); return None if b is None else rsa_public_from_pkcs1_der(b)
def rsa_public_to_spki_pem(e, n):        return _io.pem_wrap("PUBLIC KEY",       rsa_public_to_spki_der(e, n))
def rsa_public_from_spki_pem(pem):       b = _io.pem_unwrap("PUBLIC KEY",       pem); return None if b is None else rsa_public_from_spki_der(b)
def rsa_private_to_pkcs1_pem(e,d,n,p,q): return _io.pem_wrap("RSA PRIVATE KEY", rsa_private_to_pkcs1_der(e,d,n,p,q))
def rsa_private_from_pkcs1_pem(pem):     b = _io.pem_unwrap("RSA PRIVATE KEY", pem); return None if b is None else rsa_private_from_pkcs1_der(b)
def rsa_private_to_pkcs8_pem(e,d,n,p,q): return _io.pem_wrap("PRIVATE KEY",     rsa_private_to_pkcs8_der(e,d,n,p,q))
def rsa_private_from_pkcs8_pem(pem):     b = _io.pem_unwrap("PRIVATE KEY",     pem); return None if b is None else rsa_private_from_pkcs8_der(b)

def rsa_public_to_xml(e, n):             return _io.xml_wrap("RsaPublicKey",  [("e", e), ("n", n)])
def rsa_public_from_xml(xml):
    r = _io.xml_unwrap("RsaPublicKey", ["e", "n"], xml)
    return (r[0], r[1]) if r and len(r) == 2 else None
def rsa_private_to_xml(e, d, n, p, q):  return _io.xml_wrap("RsaPrivateKey", [("e", e), ("d", d), ("n", n), ("p", p), ("q", q)])
def rsa_private_from_xml(xml):
    r = _io.xml_unwrap("RsaPrivateKey", ["e", "d", "n", "p", "q"], xml)
    return (r[0], r[1], r[2], r[3], r[4]) if r and len(r) == 5 else None

import getopt, sys

def main():
    safe = False
    list, args = getopt.getopt(sys.argv[1:], "s")
    for l, a in list:
        if "-s" in l:
            safe = True

    # Interactively encrypt/decrypt

    try:
        bits = int(input("How many bits? "))
    except:
        quit("We needed a positive integer!")

    (e, d, n) = generate_keys(bits, safe)

    print(f"e = {e}")
    print(f"d = {d}")
    print(f"lg(d) = {primes.lg(d)}")
    print(f"n = {n}")
    print(f"lg(n) = {primes.lg(n)}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(primes.encode(m), e, n); print(f"En[{m}] = {c}")
            t = primes.decode(decrypt(c, d, n)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")

if __name__ == '__main__': main()
