#!/usr/bin/env python3
"""
Per-iteration timing driver for the Python cryptosystems.

Usage: py_bench.py <algorithm> <op> <bits> <iterations>

Algorithms: rsa, elgamal, rabin, paillier, ss, cocks
Ops:        keygen, encrypt, decrypt
Output:     one duration in microseconds per line on stdout, no header.
            Times the *operation only* — key generation cost is excluded
            from encrypt/decrypt timings (key is generated once and reused).
"""

import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import primes, rsa, elgamal, rabin, paillier, ss, cocks
import random
random.seed(20260506)

ALGOS = {
    "rsa": {
        "keygen":  lambda b: rsa.generate_keys(b, False),
        "setup":   lambda b: rsa.generate_keys(b, False),
        "encrypt": lambda key, m: rsa.encrypt(m, key[0], key[2]),
        "decrypt": lambda key, c: rsa.decrypt(c, key[1], key[2]),
        "encrypt_pub":  lambda k: k,
        "decrypt_priv": lambda k: k,
        "encrypt_args": lambda k, m: (m, k[0], k[2]),
        "decrypt_args": lambda k, c: (c, k[1], k[2]),
    },
    "elgamal": {
        "keygen":  lambda b: elgamal.generate_keys(b, False),
        "setup":   lambda b: elgamal.generate_keys(b, False),
        "encrypt": lambda kp, m: elgamal.encrypt(m, kp[1]),
        "decrypt": lambda kp, c: elgamal.decrypt(c, kp[0]),
    },
    "rabin": {
        "keygen":  lambda b: rabin.generate_keys(b, False),
        "setup":   lambda b: rabin.generate_keys(b, False),
        "encrypt": lambda nk, m: rabin.encrypt(m, nk[0]),
        "decrypt": lambda nk, c: rabin.decrypt(c, nk[1]),
    },
    "paillier": {
        "keygen":  lambda b: paillier.generate_keys(b, False),
        "setup":   lambda b: paillier.generate_keys(b, False),
        "encrypt": lambda kp, m: paillier.encrypt(m, kp[1]),
        "decrypt": lambda kp, c: paillier.decrypt(c, kp[0]),
    },
    "ss": {
        "keygen":  lambda b: ss.generate_keys(b, False),
        "setup":   lambda b: ss.generate_keys(b, False),
        "encrypt": lambda kp, m: ss.encrypt(m, kp[0]),
        "decrypt": lambda kp, c: ss.decrypt(c, kp[1]),
    },
    "cocks": {
        "keygen":  lambda b: cocks.generate_keys(b, False),
        "setup":   lambda b: cocks.generate_keys(b, False),
        "encrypt": lambda kp, m: cocks.encrypt(m, kp[0]),
        "decrypt": lambda kp, c: cocks.decrypt(c, kp[1]),
    },
}

def time_op(fn):
    """Returns (elapsed_us, return_value)."""
    t0 = time.perf_counter_ns()
    v = fn()
    t1 = time.perf_counter_ns()
    return (t1 - t0) / 1000.0, v

def main():
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr); sys.exit(2)
    alg, op, bits, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    a = ALGOS[alg]
    msg = primes.encode("benchmark")

    if op == "keygen":
        # warmup
        a["keygen"](bits)
        for _ in range(n):
            us, _ = time_op(lambda: a["keygen"](bits))
            print(f"{us:.3f}")
    elif op == "encrypt":
        key = a["setup"](bits)
        # warmup
        a["encrypt"](key, msg)
        for _ in range(n):
            us, _ = time_op(lambda: a["encrypt"](key, msg))
            print(f"{us:.3f}")
    elif op == "decrypt":
        key = a["setup"](bits)
        # For Rabin we need to ensure the message is small enough; encode is fine.
        c = a["encrypt"](key, msg)
        # warmup
        a["decrypt"](key, c)
        for _ in range(n):
            us, _ = time_op(lambda: a["decrypt"](key, c))
            print(f"{us:.3f}")
    else:
        print(f"Unknown op: {op}", file=sys.stderr); sys.exit(2)

if __name__ == "__main__":
    main()
