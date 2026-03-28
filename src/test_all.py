#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Test all cryptosystems with small key sizes (safe=False for speed).

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import random
random.seed(42)

passed = 0
failed = 0

def check(name, result, expected):
    global passed, failed
    if result == expected:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name} — got {repr(result)}, expected {repr(expected)}")
        failed += 1

# ─── primes.py ────────────────────────────────────────────────────────────────
print("=== primes.py ===")
import primes

check("is_prime(2)",   primes.is_prime(2),   True)
check("is_prime(3)",   primes.is_prime(3),   True)
check("is_prime(4)",   primes.is_prime(4),   False)
check("is_prime(97)",  primes.is_prime(97),  True)
check("is_prime(100)", primes.is_prime(100), False)
check("is_prime(561)", primes.is_prime(561), False)  # Carmichael number

check("gcd(12,8)",  primes.gcd(12, 8),  4)
check("gcd(35,14)", primes.gcd(35, 14), 7)
check("lcm(4,6)",   primes.lcm(4, 6),   12)

inv7_11 = primes.inverse(7, 11)
check("inverse(7,11) exists",   inv7_11 is not None,       True)
check("7 * inverse(7,11) ≡ 1", (7 * inv7_11) % 11 == 1,   True)

check("encode/decode roundtrip", primes.decode(primes.encode("Hello")), "Hello")

r = primes.random_prime(2**31, 2**32 - 1)
check("random_prime is prime", primes.is_prime(r), True)

# ─── rsa.py ───────────────────────────────────────────────────────────────────
print("\n=== rsa.py ===")
import rsa

(e, d, n) = rsa.generate_keys(256, False)
for msg in ["Hello", "Test", "RSA works"]:
    m = primes.encode(msg)
    c = rsa.encrypt(m, e, n)
    t = primes.decode(rsa.decrypt(c, d, n))
    check(f'RSA roundtrip "{msg}"', t, msg)

ks = rsa.publicKeyToStr(e, n)
(e2, n2) = rsa.publicKeyFromStr(ks)
check("RSA SSH key roundtrip e", e2, e)
check("RSA SSH key roundtrip n", n2, n)

# ─── elgamal.py ───────────────────────────────────────────────────────────────
print("\n=== elgamal.py ===")
import elgamal

(prv, pub) = elgamal.generate_keys(128, False)
for msg in ["Hello", "ElGamal"]:
    m = primes.encode(msg)
    c = elgamal.encrypt(m, pub)
    t = primes.decode(elgamal.decrypt(c, prv))
    check(f'ElGamal roundtrip "{msg}"', t, msg)

# ─── rabin.py ─────────────────────────────────────────────────────────────────
print("\n=== rabin.py ===")
import rabin

(n_r, k_r) = rabin.generate_keys(128, False)
for msg in ["Hello", "Rabin"]:
    m = primes.encode(msg)
    c = rabin.encrypt(m, n_r)
    t = primes.decode(rabin.decrypt(c, k_r))
    check(f'Rabin roundtrip "{msg}"', t, msg)

# ─── paillier.py ──────────────────────────────────────────────────────────────
print("\n=== paillier.py ===")
import paillier

(prv_p, pub_p) = paillier.generate_keys(256, False)
for msg in ["Hi", "Paillier"]:
    m = primes.encode(msg)
    c = paillier.encrypt(m, pub_p)
    t = primes.decode(paillier.decrypt(c, prv_p))
    check(f'Paillier roundtrip "{msg}"', t, msg)

n_h, λ_h, u_h = prv_p
m1, m2 = 7, 13
c1 = paillier.encrypt(m1, pub_p)
c2 = paillier.encrypt(m2, pub_p)
c_sum = (c1 * c2) % (n_h ** 2)
d_sum = paillier.decrypt(c_sum, prv_p)
check("Paillier homomorphic: E(7)*E(13) decrypts to 20", d_sum, m1 + m2)

# ─── ss.py (Schmidt-Samoa) ────────────────────────────────────────────────────
print("\n=== ss.py (Schmidt-Samoa) ===")
import ss

(en_ss, de_ss) = ss.generate_keys(256, False)
for msg in ["Hello", "Schmidt-Samoa"]:
    m = primes.encode(msg)
    c = ss.encrypt(m, en_ss)
    t = primes.decode(ss.decrypt(c, de_ss))
    check(f'Schmidt-Samoa roundtrip "{msg}"', t, msg)

# ─── cocks.py ─────────────────────────────────────────────────────────────────
print("\n=== cocks.py ===")
import cocks

(en_c, de_c) = cocks.generate_keys(256, False)
for msg in ["Hi", "Cocks"]:
    m = primes.encode(msg)
    c = cocks.encrypt(m, en_c)
    t = primes.decode(cocks.decrypt(c, de_c))
    check(f'Cocks roundtrip "{msg}"', t, msg)

# ─── RSA serialization ────────────────────────────────────────────────────────
print("\n=== rsa.py serialization ===")

(e_f, d_f, n_f, p_f, q_f) = rsa.generate_rsa_full_keys(256, False)

pkcs1_pub = rsa.rsa_public_to_pkcs1_der(e_f, n_f)
check("RSA PKCS#1 pub DER roundtrip", rsa.rsa_public_from_pkcs1_der(pkcs1_pub), (e_f, n_f))

pkcs1_prv = rsa.rsa_private_to_pkcs1_der(e_f, d_f, n_f, p_f, q_f)
got = rsa.rsa_private_from_pkcs1_der(pkcs1_prv)
check("RSA PKCS#1 prv DER roundtrip e", got[0], e_f)
check("RSA PKCS#1 prv DER roundtrip d", got[1], d_f)
check("RSA PKCS#1 prv DER roundtrip n", got[2], n_f)

spki = rsa.rsa_public_to_spki_der(e_f, n_f)
check("RSA SPKI DER roundtrip",        rsa.rsa_public_from_spki_der(spki), (e_f, n_f))

pkcs8 = rsa.rsa_private_to_pkcs8_der(e_f, d_f, n_f, p_f, q_f)
got8  = rsa.rsa_private_from_pkcs8_der(pkcs8)
check("RSA PKCS#8 DER roundtrip e", got8[0], e_f)
check("RSA PKCS#8 DER roundtrip d", got8[1], d_f)
check("RSA PKCS#8 DER roundtrip n", got8[2], n_f)

check("RSA PKCS#1 pub PEM roundtrip", rsa.rsa_public_from_pkcs1_pem(rsa.rsa_public_to_pkcs1_pem(e_f, n_f)), (e_f, n_f))
check("RSA SPKI PEM roundtrip",       rsa.rsa_public_from_spki_pem(rsa.rsa_public_to_spki_pem(e_f, n_f)),   (e_f, n_f))
got_p8 = rsa.rsa_private_from_pkcs8_pem(rsa.rsa_private_to_pkcs8_pem(e_f, d_f, n_f, p_f, q_f))
check("RSA PKCS#8 PEM roundtrip e", got_p8[0], e_f)
check("RSA PKCS#8 PEM roundtrip d", got_p8[1], d_f)

check("RSA public XML roundtrip",  rsa.rsa_public_from_xml(rsa.rsa_public_to_xml(e_f, n_f)), (e_f, n_f))
got_xml = rsa.rsa_private_from_xml(rsa.rsa_private_to_xml(e_f, d_f, n_f, p_f, q_f))
check("RSA private XML roundtrip e", got_xml[0], e_f)
check("RSA private XML roundtrip d", got_xml[1], d_f)
check("RSA private XML roundtrip n", got_xml[2], n_f)

# ─── Non-RSA serialization ────────────────────────────────────────────────────
print("\n=== non-RSA serialization ===")

# ElGamal — reuse keys from above
(p_eg, a_eg)     = prv
(p_eg2, r_eg, b_eg) = pub
check("ElGamal pub blob roundtrip",  elgamal.elgamal_public_from_blob(elgamal.elgamal_public_to_blob(p_eg2, r_eg, b_eg)), (p_eg2, r_eg, b_eg))
check("ElGamal prv blob roundtrip",  elgamal.elgamal_private_from_blob(elgamal.elgamal_private_to_blob(p_eg, a_eg)), (p_eg, a_eg))
check("ElGamal pub PEM roundtrip",   elgamal.elgamal_public_from_pem(elgamal.elgamal_public_to_pem(p_eg2, r_eg, b_eg)), (p_eg2, r_eg, b_eg))
check("ElGamal prv PEM roundtrip",   elgamal.elgamal_private_from_pem(elgamal.elgamal_private_to_pem(p_eg, a_eg)), (p_eg, a_eg))
check("ElGamal pub XML roundtrip",   elgamal.elgamal_public_from_xml(elgamal.elgamal_public_to_xml(p_eg2, r_eg, b_eg)), (p_eg2, r_eg, b_eg))
check("ElGamal prv XML roundtrip",   elgamal.elgamal_private_from_xml(elgamal.elgamal_private_to_xml(p_eg, a_eg)), (p_eg, a_eg))

# Rabin — reuse (n_r, k_r) from above
(p_r, q_r) = k_r
check("Rabin pub blob roundtrip",  rabin.rabin_public_from_blob(rabin.rabin_public_to_blob(n_r)), n_r)
check("Rabin prv blob roundtrip",  rabin.rabin_private_from_blob(rabin.rabin_private_to_blob(n_r, p_r, q_r)), (p_r, q_r))
check("Rabin pub PEM roundtrip",   rabin.rabin_public_from_pem(rabin.rabin_public_to_pem(n_r)), n_r)
check("Rabin prv PEM roundtrip",   rabin.rabin_private_from_pem(rabin.rabin_private_to_pem(n_r, p_r, q_r)), (p_r, q_r))
check("Rabin pub XML roundtrip",   rabin.rabin_public_from_xml(rabin.rabin_public_to_xml(n_r)), n_r)
check("Rabin prv XML roundtrip",   rabin.rabin_private_from_xml(rabin.rabin_private_to_xml(n_r, p_r, q_r)), (p_r, q_r))

# Paillier — reuse (prv_p, pub_p) from above
(n_p2, λ_p2, u_p2) = prv_p
(n_p2b, ζ_p2)      = pub_p
check("Paillier pub blob roundtrip",  paillier.paillier_public_from_blob(paillier.paillier_public_to_blob(n_p2b, ζ_p2)), (n_p2b, ζ_p2))
check("Paillier prv blob roundtrip",  paillier.paillier_private_from_blob(paillier.paillier_private_to_blob(n_p2, λ_p2, u_p2)), (n_p2, λ_p2, u_p2))
check("Paillier pub PEM roundtrip",   paillier.paillier_public_from_pem(paillier.paillier_public_to_pem(n_p2b, ζ_p2)), (n_p2b, ζ_p2))
check("Paillier prv PEM roundtrip",   paillier.paillier_private_from_pem(paillier.paillier_private_to_pem(n_p2, λ_p2, u_p2)), (n_p2, λ_p2, u_p2))
check("Paillier pub XML roundtrip",   paillier.paillier_public_from_xml(paillier.paillier_public_to_xml(n_p2b, ζ_p2)), (n_p2b, ζ_p2))
check("Paillier prv XML roundtrip",   paillier.paillier_private_from_xml(paillier.paillier_private_to_xml(n_p2, λ_p2, u_p2)), (n_p2, λ_p2, u_p2))

# Schmidt-Samoa — reuse (en_ss, de_ss) from above
(d_ss2, γ_ss2) = de_ss
check("SS pub blob roundtrip",  ss.ss_public_from_blob(ss.ss_public_to_blob(en_ss)), en_ss)
check("SS prv blob roundtrip",  ss.ss_private_from_blob(ss.ss_private_to_blob(d_ss2, γ_ss2)), (d_ss2, γ_ss2))
check("SS pub PEM roundtrip",   ss.ss_public_from_pem(ss.ss_public_to_pem(en_ss)), en_ss)
check("SS prv PEM roundtrip",   ss.ss_private_from_pem(ss.ss_private_to_pem(d_ss2, γ_ss2)), (d_ss2, γ_ss2))
check("SS pub XML roundtrip",   ss.ss_public_from_xml(ss.ss_public_to_xml(en_ss)), en_ss)
check("SS prv XML roundtrip",   ss.ss_private_from_xml(ss.ss_private_to_xml(d_ss2, γ_ss2)), (d_ss2, γ_ss2))

# Cocks — reuse (en_c, de_c) from above
(π_c, q_c) = de_c
check("Cocks pub blob roundtrip",  cocks.cocks_public_from_blob(cocks.cocks_public_to_blob(en_c)), en_c)
check("Cocks prv blob roundtrip",  cocks.cocks_private_from_blob(cocks.cocks_private_to_blob(π_c, q_c)), (π_c, q_c))
check("Cocks pub PEM roundtrip",   cocks.cocks_public_from_pem(cocks.cocks_public_to_pem(en_c)), en_c)
check("Cocks prv PEM roundtrip",   cocks.cocks_private_from_pem(cocks.cocks_private_to_pem(π_c, q_c)), (π_c, q_c))
check("Cocks pub XML roundtrip",   cocks.cocks_public_from_xml(cocks.cocks_public_to_xml(en_c)), en_c)
check("Cocks prv XML roundtrip",   cocks.cocks_private_from_xml(cocks.cocks_private_to_xml(π_c, q_c)), (π_c, q_c))

# ─── Summary ──────────────────────────────────────────────────────────────────
total = passed + failed
print(f"\n{total} tests: {passed} passed, {failed} failed.")
