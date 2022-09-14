#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import primes

from random import randrange as uniform

def f(x, b, n): return (b + x + x*x) % n

def rho(n):
    """
    Compute Pollard's ⍴
    """
    b = uniform(1, max(2, n - 2))
    s = uniform(0, max(2, n))
    A, B, g = s, s, 1
    while g == 1:
        A = f(A, b, n)
        B = f(f(B, b, n), b, n)
        g = primes.gcd(A - B, n)
    return g

def factor(n):
    if primes.is_prime(n):
        return [n]
    else:
        f = []
        q = [n]
        while len(q) > 0:
            x = q.pop()
            r = rho(x)
            y = x // r
            if primes.is_prime(r):
                f.append(r)
            elif r > 1:
                q.append(r)
            if primes.is_prime(y):
                f.append(y)
            elif y > 1:
                q.append(y)
        return f

# Interactive test

from functools import reduce

def naim():
    n = 1
    while n != 0:
        n = int(input("?? "))
        f = factor(n)
        f.sort()
        print(f"{n} = {f} = {reduce(lambda x, y: x * y, f)}")

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
