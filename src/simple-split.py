#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BSD 2-Clause License
#
# Copyright (c) 2022, Darrell Long
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

# Cryptographic random numbers would be ideal, but this is just a simple example.

from random import randrange as uniform

def encode(s):
    """
    Trivial secret splitting: choose k pseudo-random numbers (in this case 2) and return those
    numbers along with them exclusive or'd with your message.
    """
    b = int.from_bytes(s.encode('utf-8'), 'little')
    l = b.bit_length()
    r = uniform(2**l, 2**(l + 1))
    s = uniform(2**l, 2**(l + 1))
    return (r, s, r ^ s ^ b)

def decode(r, s, t):
    """
    Decoding in this trivial secret splitting scheme is simplying the exclusive or of the three
    pseudo-random numbers.
    """
    m = r ^ s ^ t
    n = int.to_bytes(m, length=m.bit_length() // 8 + 1, byteorder='little')
    return n.decode('utf-8')

def main():
    m = ""
    try:
        while not m in ["Quit", "quit", "Q", "q", "Exit", "exit"]:
            m = input("?? ")
            (a,b,c) = encode(m)
            print(f"a = {a}\nb = {b}\nc = {c}")
            print(f"msg = {decode(a, b, c)}")
    except:
        print("\nSo long!")

if __name__ == '__main__':
    main()
