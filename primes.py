#!/usr/bin/env python3
#
# LICENSE GOES HERE.
#
#

from random import randrange as uniform

def is_even(n): return n % 2 == 0

def is_odd(n): return n % 2 == 1

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

def is_prime_MR(n, k):
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n < 4:
        return True
    for _ in range (0, k):
        a = uniform(2, n - 1) # Euler witness (or liar)
        if witness(a, n):
            return False
    return True

# Compute the Jacobi symbol:
#  n
# (-)
#  k

def Jacobi(n, k):
    assert(k > 0 and is_odd(k))
    n = n % k
    t = 1
    while n != 0:
        while is_even(n):
            n = n // 2
            r = k % 8
            t = -t if r == 3 or r == 5 else t
        n, k = k, n
        t = -t if n % 4 == 3 and k % 4 == 3 else t
        n = n % k
    if k == 1:
        return t
    else:
        return 0

def is_prime_SS(n, k):
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n < 4:
        return True
    for _ in range(0, k):
        a = uniform(2, n - 1) # Euler witness (or liar)
        x = Jacobi(a, n)
        if x == 0 or power_mod(a, (n - 1) // 2, n) != x % n:
            return False
    return True

# Default

is_prime = is_prime_SS

if __name__ == '__main__':
    g = 1
    try:
        while g != 0:
            g = int(input("?? "))
            if g == 2 or is_odd(g) and is_prime(g, 100):
                print(f"{g} is probably prime.")
            else:
                print(f"{g} is composite.")
    except:
        print("\nSo long!")

# Routines to generate primes

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

# Euclidean extended greatest common divisor

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


def gen_rabin_key(n_bits, safe=True):
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
