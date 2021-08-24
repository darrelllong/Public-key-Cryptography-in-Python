#!/usr/bin/env python3
#
# LICENSE GOES HERE.
#
#

from random import randrange as uniform
from zlib import crc32 as crc32

def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 == 1

# a^b (mod n) using the method of repeated squares
#
# The key here is that every integer can be written as a sum of powers of 2 (binary numbers)
# and that includes the exponent. By repeated squaring we get a raised to a power of 2. Also
# recall that a^b * a^c = a^(b + c), so rather than adding we multiply since we are dealing
# with the exponent.

def power_mod(a, d, n):
    v = 1 # Value
    p = a # Powers of a
    while d > 0: # 1 bit in the exponent
        if is_odd(d):
            v = (v * p) % n
        p = p**2 % n # Next power of two
        d //= 2
    return v

# Witness loop of the Miller-Rabin probabilistic primality test

def witness(a, n):
    u = n - 1
    t = 0
    while is_even(u):
        t  += 1
        u //= 2
    x = power_mod(a, u, n)
    for _ in range(0, t):
        y = power_mod(x, 2, n)
        if y == 1 and x != 1 and x != n - 1:
            return True
        x = y
    return x != 1

# Miller-Rabin probabilistic primality test

def is_prime(n, k):
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n < 4:
        return True
    for _ in range (0, k):
        a = uniform(2, n)
        if witness(a, n):
            return False
    return True


def random_prime(low, high):
    """
    Generate and return a random prime in the range [low, high].
    """
    guess = 0 # Certainly not prime!
    while not is_prime(guess, 100):
        guess = uniform(low, high) # Half will be even, the rest have Pr[prime] ≈ 1/log(N).
    return guess


def safe_prime(low, high):
    """
    Generate and return a safe prime in the range [low, high].

    A safe prime follows a Sophie German prime. If prime(p) and prime(2p + 1)
    then p is a Sophie Germain prime and 2p + 1 is a safe prime.
    """
    p = random_prime(low, high)
    while not is_prime(2 * p + 1,100):
        p = random_prime(low, high)
    return 2 * p + 1

# Rabin prime

def rabin_prime(low, high, safe = True):
    """
    Generate a Rabin prime in the range [low, high].
    Default is to generate a safe prime.
    Passing safe=False will generate a random prime instead.
    """
    f = safe_prime if safe else random_prime
    p = f(low, high)
    while p % 4 != 3:
        p = f(low, high)
    return p

# Extended greatest common divisor, Euclidean version.

def extendedGCD(a, b):
    """
    Run the extended Euclid algorithm on a, b.
    Returns (remainder, (s, t))
    """
    (r, rP) = (a, b)
    (s, sP) = (1, 0)
    (t, tP) = (0, 1)
    while rP != 0:
        q = r // rP
        (r, rP) = (rP, r - q * rP)
        (s, sP) = (sP, s - q * sP)
        (t, tP) = (tP, t - q * tP)
    return (r, (s, t))


def genkey(n_bits, safe=True):
    """
    Generate and return a key with n_bits of strength.
    Default is to use safe random numbers.
    """
    x = n_bits + 32 # Make room for the tag
    p = rabin_prime (safe, 2**(x - 1), 2**x - 1)
    q = rabin_prime (safe, 2**(x - 1), 2**x - 1)
    while p == q:
        q = rabin_prime (safe, 2**(x - 1), 2**x - 1)
    return (p * q, (p, q))



# We need to discriminate amongst the four roots
# Rabin encryption is computing the square (mod n)
h = crc32(b"Michael O. Rabin")
def encrypt(m, n):
    return power_mod(m * 2**32 + h, 2, n) # Insert tag and square (mod n)

# Decryption requires us to compute the four square roots (mod n). We can only efficiently
# do this if we know p and q.

def decrypt(m, key):
    (p, q) = key
    n = p * q
    (g, (yP, yQ)) = extendedGCD(p, q)
    mP = power_mod(m, (p + 1) // 4, p)
    mQ = power_mod(m, (q + 1) // 4, q)
    x = (yP * p * mQ + yQ * q * mP) % n
    y = (yP * p * mQ - yQ * q * mP) % n
    msgs = [x, n - x, y, n - y]
    for d in msgs:
        if d % 2**32 == h:
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

    (n, k) = genkey(bits, False)

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
