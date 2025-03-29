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

from primes import is_prime as is_prime
from primes import gcd as gcd

from random import randrange as uniform

from functools import reduce

def f(x, b, n): return (b + x + x*x) % n

def rho(n):
    """
    Compute Pollard's rho to find a nontrivial factor of n.
    Reinitialize parameters and retry if the computed factor equals n.
    """
    factor = n  # Initialize with the trivial factor
    while factor == n:
        b = uniform(1, max(2, n - 2))
        s = uniform(0, max(2, n))
        slow = s  # Tortoise
        fast = s  # Hare
        factor = 1  # Reset factor for this trial

        while factor == 1:
            slow = f(slow, b, n)
            fast = f(f(fast, b, n), b, n)
            factor = gcd(slow - fast, n)

    return factor

def factor(n):
    if n == 1 or is_prime(n):
        return [n]
    else:
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

if __name__ == '__main__': main()
