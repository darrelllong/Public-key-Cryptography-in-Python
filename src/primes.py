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

def is_even(n): return n & 0x1 == 0

def is_odd(n):  return n & 0x1 == 1

def lg(n):
    """
    Compute log(n), returns -1 (invalid) for log(0)
               2                                2
    """
    k = -1
    n = abs(n)
    while n > 0:
        n //= 2
        k  += 1
    return k

def power(a, d):
    """
     b
    a  using the method of repeated squares.

    Every integer can be written as a sum of powers of 2 including the exponent. By repeated
    squaring a is raised successive powers of 2. Multiplying these partial powers is the same
    as adding the exponents.
    """
    v = 1 # Value
    p = a # Powers of a
    while d > 0:
        if is_odd(d): # 1 bit in the exponent
            v *= p
        p *= p  # Next power of two
        d //= 2 # Shift exponent one bit
    return v

def power_mod(a, b, n):
    """
     b
    a (mod n) using the method of repeated squares.

    Every integer can be written as a sum of powers of 2 including the exponent. By repeated
    squaring a is raised successive powers of 2. Multiplying these partial powers is the same
    as adding the exponents.
    """
    v = 1 # Value
    p = a # Powers of a
    while b > 0:
        if is_odd(b): # 1 bit in the exponent
            v = (v * p) % n
        p = (p * p) % n # Next power of two
        b //= 2         # Shift exponent one bit
    return v

def perfect_power(n):
    """
                           b                                                    2
    Determine whether n = a using binary search, should require O(lg n (lg lg n) ) time.
    """
    logN = lg(n)
    for b in range(2, logN):
        low  = 2
        high = 1 << logN // b + 1
        while low < high - 1:
            middle = (low + high) // 2
            ab = power(middle, b)
            if ab > n:
                high = middle
            elif ab < n:
                low = middle
            else:
                return (middle, b)
    return (None, None)

def is_perfect_power(n): return perfect_power(n) != (None, None)

def get_d_r(n):
    """
    Factors n into the form d * 2 ** r.
    """
    d = n
    r = 0
    while is_even(d):
        d //= 2
        r += 1

    return (d, r)

def witness(a, n):
    """
    The witness loop of the Miller-Rabin probabilistic primality test.
    """
    (d, r) = get_d_r(n - 1) # Factor n into d * 2**r + 1
    x = power_mod(a, d, n)
    for _ in range(0, r):
        y = power_mod(x, 2, n)
        if y == 1 and x != 1 and x != n - 1:
            return True
        x = y
    return x != 1

from random import randrange as uniform

def is_prime_MR(n, k=100):
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

def Jacobi(n, k):
    """
    Compute the Jacobi symbol:
      n    ⎡  0 if n ≡ 0 (mod k)
     (-) = ⎢  1 if n ≢ 0 (mod k) ⋀ (∃x) a ≡ x**2 (mod k)
      k    ⎣ -1 if n ≢ 0 (mod k) ⋀ (∄x) a ≡ x**2 (mod k)
    """
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
    return t if k == 1 else 0

def is_prime_SS(n, k=100):
    """
    Solovay-Strassen probabilistic primality test of n with confidence k.
    """
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n == 2 or n == 3:
        return True
    for _ in range(0, k):
        a = uniform(2, n - 1) # Euler witness (or liar)
        x = Jacobi(a, n)
        if x == 0 or power_mod(a, (n - 1) // 2, n) != (n + x) % n:
            return False
    return True

def choose_Selfridge(n):
    """
    Chooses Selfridge's parameters for the Lucas primality test.
    Returns: (D, P, Q)
    """
    d = 5
    s = 1
    while True:
        D = d * s
        if gcd(D,n) == 1 and Jacobi(D, n) == -1: # This is guaranteed to occur if it is not square.
            return (D, 1, (1 - D) // 4)

        d = d + 2
        s *= -1

def halve(x, n):
    """
    If x is even, x is halved directly. If x is odd, then n is added to x.  n is
    assumed to be odd since it is a candidate prime, so the result will be even
    and can be halved. This does not change the answer mod n.
    """
    if x % 2 == 1:
        x += n
    return x // 2

def compute_UV(i, n, p, d):
    """
    Computes the i-th element of the Lucas sequence with parameters
    p and d, where q = (1 - d) / 4 (mod n).
    """
    if i == 1:
        return (1, p)
    elif i % 2 == 0:
        (U_k, V_k) = compute_UV(i // 2, n, p, d)
        U_2k = U_k * V_k
        V_2k = halve(V_k * V_k + d * U_k * U_k, n)
        return (U_2k % n, V_2k % n)
    else:
        (U_2k, V_2k) = compute_UV(i - 1, n, p, d)
        U_2k1 = halve(p * U_2k + V_2k, n)
        V_2k1 = halve(d * U_2k + p * V_2k, n)
        return (U_2k1 % n, V_2k1 % n)

def is_prime_LS(n):
    """
    Checks if an integer is a strong Lucas probable prime.
    """
    if n < 2 or (n != 2 and n % 2 == 0) or is_perfect_power(n):
        return False
    if n == 2 or n == 3:
        return True

    (d, p, q) = choose_Selfridge(n)
    (u, v) = compute_UV(n + 1, n, p, d)

    return  u == 0 and v == (2 * q) % n

def is_prime_F(n):
    """
    Strong Fermat (Miller-Rabin with fixed base) test with base a = 2.
    """
    if n < 2 or (n != 2 and n % 2 == 0):
        return False
    if n == 2 or n == 3:
        return True

    if witness(2, n):
        return False
    return True

def is_prime_BPSW(n, k=100):
    """
    Runs a Fermat (Miller-Rabin with fixed base) test base 2 and a Lucas-Selfridge test.
    It is conjectured that pseudoprimes under both tests are significantly different so
    if a number passes both it is very likely to be truly prime.
    """
    return is_prime_F(n) and is_prime_LS(n)

# Default is to use Miller-Rabin.

def is_prime(n, k=100): return is_prime_MR(n, k)

# Routines to generate primes

def random_prime(low, high, confidence=100):
    """
    Generate and return a random prime in the range [low, high].
    """
    guess = 0 # Certainly not prime!
    while is_even(guess) or not is_prime(guess, confidence):
        guess = uniform(low, high) # Half will be even, the rest have Pr[prime] ≈ 1/log(N).
    return guess

def safe_prime(low, high, confidence=100):
    """
    Generate and return a safe prime in the range [low, high].

    A safe prime follows a Sophie Germain prime. If prime(p) and prime(2p + 1) then p is a
    Sophie Germain prime and 2p + 1 is a safe prime.
    """
    p = random_prime(low, high)
    while not is_prime(2 * p + 1, confidence):
        p = random_prime(low, high)
    return 2 * p + 1

def rabin_prime(low, high, safe=True):
    """
    Generate a Rabin prime p ≢ 3 (mod 4), low ⩽ p ⩽ high. Default is to use a safe prime.
    """
    f = safe_prime if safe else random_prime
    p = f(low, high)
    while p % 4 != 3:
        p = f(low, high)
    return p

def extended_GCD(a, b):
    """
    The extended Euclidean algorithm computes the greatest common divisor and the Bézout
    coefficients s, t.

    Returns (remainder, (s, t))
    """
    r, rP = a, b
    s, sP = 1, 0
    t, tP = 0, 1
    while rP != 0:
        q = r // rP
        r, rP = rP, r - q * rP
        s, sP = sP, s - q * sP
        t, tP = tP, t - q * tP
    return (r, (s, t))

def gcd(a, b):
    """
    Compute the greatest common divisor gcd(a, b) using the Euclidean algorithm.
    """
    while b != 0:
        a, b = b, a % b # The simple version so students see what is happening.
    return a

def lcm(a, b):
    """
    Compute the least common multiple lcm(a, b).
    """
    return (a * b) // gcd(a, b)

def inverse(a, n):
    """
    Compute the muliplicative inverse of a (mod n) using the Euclidean algorithm and Bézout's
    identity: a×s + b×t = 1.
    """
    (r, (s, t)) = extended_GCD(a, n) # We did the hard part already.
    if r > 1:
        return None
    return s + n if s < 0 else s

def group_generator(n, p):
    """
    Creates a generator in the neighborhood of n for the group defined by p.

    A generator must not be congruent to 1 for any of its powers that are proper divisors
    of p – 1.  Since p is safe prime, there are only two: 2 and (p – 1) / 2. The number of
    such generators is 𝜑(p – 1).
    """
    g = n
    q = (p - 1) // 2
    while power_mod(g, 2, p) == 1 and power_mod(g, q, p) == 1:
        g = g + 1
    return g

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
        s += chr(n % 256)
        n //= 256
    return s

# Interactive test
import time

def main():
    g = encode("Try harder!")
    try:
        while g != 0:
            g = eval(input("?? "))
            t0 = time.time_ns()
            mr   = is_prime_MR(g)
            t1 = time.time_ns()
            ss   = is_prime_SS(g)
            t2 = time.time_ns()
            bpsw = is_prime_BPSW(g)
            t3 = time.time_ns()
            if g == 2 or is_odd(g) and mr and ss and bpsw:
                print(f"{g} is probably prime.")
            else:
                print(f"{g} is composite.")
                if mr:
                    print("Miller-Rabin disagrees")
                if ss:
                    print("Solovay-Strassen disagrees")
                if bpsw:
                    print("BPSW disagrees")
            (a, b) = perfect_power(g)
            if (a, b) != (None, None):
                print(f"{g} = {a}**{b} is a perfect power.")
            print(f"Performance:\n\tMiller-Rabin: {t1 - t0}ns\n\tSolovay-Strassen: {t2 - t1}ns\n\tBPSW: {t3 - t2}ns")
    except Exception as e:
        print("\nSo long!")

if __name__ == '__main__': main()
