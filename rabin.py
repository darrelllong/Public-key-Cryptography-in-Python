#!/usr/bin/env python3
#
# LICENSE GOES HERE.
#
#

import primes

from random import randrange as uniform
from zlib import crc32


def generate_keys(n_bits, safe=True):
    """
    Generate and return a key with n_bits of strength.
    Default is to use safe random numbers.
    """
    x = n_bits + 32 # Make room for the tag
    p = primes.rabin_prime(2**(x - 1), 2**x - 1, safe)
    q = primes.rabin_prime(2**(x - 1), 2**x - 1, safe)
    while p == q:
        q = primes.rabin_prime(2**(x - 1), 2**x - 1, safe)
    return (p * q, (p, q))



# We need to discriminate amongst the four roots
# Rabin encryption is computing the square (mod n)
_h = crc32(b"Michael O. Rabin")
def encrypt(m, n):
    return primes.power_mod(m * 2**32 + _h, 2, n) # Insert tag and square (mod n)

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
    msgs = [x, n - x, y, n - y]
    for d in msgs:
        if d % 2**32 == _h:
            return d // 2**32
    return 1279869254 # FAIL

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

if __name__ == '__main__':
    try:
        bits = int(input("How many bits? "))
    except:
        print("We needed a positive integer!")
        quit()

    (n, k) = generate_keys(bits, False)

    print(f"n = {n}")
    print(f"key = {k}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(encode(m), n); print(f"En[{m}] = {c}")
            t = decode(decrypt(c, k)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")
