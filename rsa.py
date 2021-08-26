#!/usr/bin/env python3
from random import randrange as uniform
from base64 import standard_b64encode as b64encode
from base64 import standard_b64decode as b64decode

import primes

# Generate a key (e, d, n) of a specified bit-length with optional safe primes

def generate_keys(bits, safe=False):
    size = bits // 2
    low  = 2**(size - 1) # Assure the primes are each approximately half of the
    high = 2**size - 1   # bits in the modulus.
    f = primes.safe_prime if safe else primes.random_prime
    p = f(low, high)
    q = f(low, high)
    while p == q:
        q = f(low, high)
    𝝺 = primes.lcm(p - 1, q - 1) # Carmichael 𝝺(n) = lcm(𝝺(p), 𝝺(q)) = lcm(p - 1, q - 1)
    k = 16
    e = 2**k + 1        # Default public exponent
    while primes.gcd(e, 𝝺) != 1: # Happens only if we are very unlucky
        k += 1
        e = 2**k + 1
    d = primes.inverse(e, 𝝺) # The private key
    n = p * q         # The modulus
    return (e, d, n)

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

def encrypt(m, e, n): return primes.power_mod(m, e, n)

def decrypt(c, d, n): return primes.power_mod(c, d, n)

# The number of bytes required to hold n.

def byteLength(n: int) -> int:
    return (n.bit_length() // 8) + (1 if n.bit_length() % 8 != 0 else 0)

# Create a public SSH key string from e and n.
#
# The format of an ssh key is:
#     [key-type (always "ssh-rsa" here)] [e] [n]
# Where each field is made up of:
#     a 32-bit integer -- the length n of the field; and
#     n bytes -- the contents of the field.

def publicKeyToStr(e: int, n: int) -> str:
    key_type = b"ssh-rsa"
    key = bytearray()

    key.extend(len(key_type).to_bytes(4, "big") + key_type)
    key.extend(byteLength(e).to_bytes(4, "big") + e.to_bytes(byteLength(e), "big"))
    key.extend(byteLength(n).to_bytes(4, "big") + n.to_bytes(byteLength(n), "big"))

    key_b64 = b64encode(key).decode("utf-8")

    return "ssh-rsa " + key_b64

# Retrieve (e, n) from a public ssh key string.

def publicKeyFromStr(key: str) -> tuple[int, int]:
    assert key.startswith("ssh-rsa")

    # The key-string is a type (i.e., "ssh-rsa") followed by e and n, followed
    # by an optional comment. We only care about e and n.
    key = key.split(" ")[1]
    key = b64decode(bytes(key, "utf-8"))

    # The current index in the key.
    i = 0

    # Read key type.
    length = int.from_bytes(key[i:i + 4], "big")
    key_type = key[i + 4:i + 4 + length]
    assert key_type == b"ssh-rsa"
    i += 4 + length

    # Read e.
    length = int.from_bytes(key[i:i + 4], "big")
    e = int.from_bytes(key[i + 4:i + 4 + length], "big")
    i += 4 + length

    # Read n.
    length = int.from_bytes(key[i:i + 4], "big")
    n = int.from_bytes(key[i + 4:i + 4 + length], "big")

    return (e, n)

if __name__ == '__main__':
    # Interactively encrypt/decrypt

    try:
        bits = int(input("How many bits? "))
    except:
        print("We needed a positive integer!")
        quit()

    (e, d, n) = generate_keys(bits, False)

    print(f"e = {e}")
    print(f"d = {d}")
    print(f"n = {n}")

    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            c = encrypt(encode(m), e, n); print(f"En[{m}] = {c}")
            t = decode(decrypt(c, d, n)); print(f"De[{c}] = {t}")
    except:
        print("\nSo long!")
