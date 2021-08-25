#!/usr/bin/env python3

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
    p = primes.safe_prime(2**(k - 1), 2**k - 1) if safe else primes.random_prime(2**(k - 1), 2**k - 1)
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

def encode(s):
    sum = 0
    pow = 1
    for c in s:
        sum += pow * ord(c)
        pow *= 256
    return sum

def decode(n):
    s = ""
    while n > 0:
        s = s + chr(n % 256)
        n //= 256
    return s

try:
    bits = int(input("How many bits? "))
except:
    print("We needed a positive integer!")
    quit()

(prv, pub) = generate_keys(bits, False)

print(f"pub = {pub}")
print(f"prv = {prv}")

m = ""
try:
    while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
        m = input("?? ")
        c = encrypt(encode(m), pub); print(f"En[{m}] = {c}")
        t = decode(decrypt(c, prv)); print(f"De[{c}] = {t}")
except:
    print("\nSo long!")
