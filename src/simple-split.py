#!/usr/bin/env python3

from random import randrange as uniform

def encode(s):
    b = int.from_bytes(s.encode('utf-8'), 'little')
    l = b.bit_length()
    r = uniform(2**l, 2**(l + 1))
    s = uniform(2**l, 2**(l + 1))
    return (r, s, r ^ s ^ b)

def decode(r, s, t):
    m = r ^ s ^ t
    n = int.to_bytes(m, length=m.bit_length()//8 + 1, byteorder='little')
    return n.decode('utf-8')

def main():
    msg = input("?? ")
    (a,b,c) = encode(msg)
    print(f"a = {a}\nb = {b}\nc = {c}")
    m = decode(a, b, c)
    print(f"msg = {m}")

if __name__ == '__main__':
    main()

