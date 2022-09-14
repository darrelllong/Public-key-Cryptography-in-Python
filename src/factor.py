#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def is_even(n): return n & 0x1 == 0

def is_odd(n):  return n & 0x1 == 1

def power_mod(a, d, n):
    """
     b
    a (mod n) using the method of repeated squares.

    Every integer can be written as a sum of powers of 2 including the exponent. By repeated
    squaring a is raised successive powers of 2. Multiplying these partial powers is the same
    as adding the exponents.
    """
    v = 1 # Value
    p = a # Powers of a
    while d > 0:
        if is_odd(d): # 1 bit in the exponent
            v = (v * p) % n
        p = p**2 % n # Next power of two
        d //= 2      # Shuft exponent one bit
    return v

def witness(a, n):
    """
    The witness loop of the Miller-Rabin probabilistic primality test.
    """
    # Factor n into u * 2**t + 1
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

from random import randrange as uniform

def is_prime(n, k=50):
    """
    Miller-Rabin probabilistic primality test of n with confidence k.
    """
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n == 2 or n == 3:
        return True
    for _ in range (0, k):
        a = uniform(2, n - 1) # Euler witness (or liar)
        if witness(a, n):
            return False
    return True

def gcd(a, b):
    """
    Compute the greatest common divisor gcd(a, b) using the Euclidean algorithm.
    """
    while b != 0:
        a, b = b, a % b # The simple version so students see what is happening.
    return a

def f(x, b, n): return (b + x + x*x) % n

def rho(n):
    """
    Compute Pollard's ⍴
    """
    b = uniform(1, n - 2)
    s = uniform(0, n)
    A, B, g = s, s, 1
    while g == 1:
        A = f(A, b, n)
        B = f(f(B, b, n), b, n)
        g = gcd(A - B, n)
    return g

def factor(n):
    f = []
    q = [n]
    while len(q) > 0:
        x = q.pop()
        r = rho(x)
        y = x // r
        if is_prime(r):
            f.append(r)
        elif r > 1:
            q.append(r)
        if is_prime(y):
            f.append(y)
        elif y > 1:
            q.append(y)
    return f

# Interactive test

from functools import reduce

def main():
    n = 1
    try:
        while n != 0:
            n = int(input("?? "))
            f = factor(n)
            f.sort()
            print(f"{n} = {f} = {reduce(lambda x, y: x * y, f)}")
    except Exception as e:
        print(f"\nBye!")

if __name__ == '__main__':
    main()
