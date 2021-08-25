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
    for _ in range(0, k):
        a = uniform(2, n - 1)
        x = Jacobi(a, n)
        p = power_mod(a, (n - 1) // 2, n)
        if x == 0 or power_mod(a, (n - 1) // 2, n) != x % n:
            return False
    return True

if __name__ == '__main__':
    g = 1
    try:
        while g != 0:
            g = int(input("?? "))
            if is_odd(g) and is_prime_SS(g, 100):
                print(f"{g} is probably prime.")
            else:
                print(f"{g} is composite.")
    except:
        print("\nSo long!")
