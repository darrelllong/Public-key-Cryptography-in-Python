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

"""
Serialization helpers: DER SEQUENCE-of-INTEGERs binary blobs, PEM armor,
and flat-hex XML documents.

Wire formats match the Rust cryptography crate's public_key::io module exactly
so that keys and ciphertexts produced here round-trip with Rust.

Non-RSA field layouts (mirrors Rust io.rs doc comment):
  CocksPublicKey      [n]
  CocksPrivateKey     [pi, q]
  ElGamalPublicKey    [p, exponent_bound, g, b]
  ElGamalPrivateKey   [p, exponent_modulus, a]
  PaillierPublicKey   [n, zeta]
  PaillierPrivateKey  [n, lambda, u]
  RabinPublicKey      [n]
  RabinPrivateKey     [n, p, q]
  SchmidtSamoaPublicKey  [n]
  SchmidtSamoaPrivateKey [d, gamma]

RSA uses PKCS#1 / SPKI / PKCS#8 standard containers (see rsa.py).
"""

import base64

# ── DER low-level primitives ──────────────────────────────────────────────────

def _der_int_bytes(n):
    """Minimal big-endian two's-complement encoding for a DER positive INTEGER."""
    if n < 0:
        raise ValueError("_der_int_bytes: negative not supported")
    if n == 0:
        return bytes([0x00])
    bs = []
    while n > 0:
        bs.append(n & 0xff)
        n >>= 8
    bs.reverse()
    if bs[0] & 0x80:
        bs.insert(0, 0x00)
    return bytes(bs)

def _der_enc_len(length):
    """Return the DER length encoding for `length`."""
    if length < 0x80:
        return bytes([length])
    bs = []
    n = length
    while n > 0:
        bs.append(n & 0xff)
        n >>= 8
    bs.reverse()
    return bytes([0x80 | len(bs)] + list(bs))

def _der_dec_len(data, pos):
    """Decode a DER length at data[pos]. Returns (length, new_pos) or None."""
    if pos >= len(data):
        return None
    first = data[pos]
    if first & 0x80 == 0:
        return (first, pos + 1)
    count = first & 0x7f
    if count == 0 or pos + count >= len(data):
        return None
    length = 0
    for i in range(1, count + 1):
        length = (length << 8) | data[pos + i]
    return (length, pos + 1 + count)

def _der_tlv(tag, content):
    return bytes([tag]) + _der_enc_len(len(content)) + content

def _der_sequence(content):    return _der_tlv(0x30, content)
def _der_octet_string(content): return _der_tlv(0x04, content)
def _der_null():               return _der_tlv(0x05, b'')
def _der_oid(oid):             return _der_tlv(0x06, oid)
def _der_integer(n):           return _der_tlv(0x02, _der_int_bytes(n))
def _der_integer_u8(v):        return _der_tlv(0x02, bytes([v]))
def _der_bit_string(content):  return _der_tlv(0x03, bytes([0x00]) + content)

# ── DER reader ────────────────────────────────────────────────────────────────

class _DerReader:
    def __init__(self, data):
        self.data = data if isinstance(data, (bytes, bytearray)) else bytes(data)
        self.pos = 0

    def done(self):
        return self.pos >= len(self.data)

    def read_tlv(self, expected_tag):
        if self.pos >= len(self.data) or self.data[self.pos] != expected_tag:
            return None
        self.pos += 1
        r = _der_dec_len(self.data, self.pos)
        if r is None:
            return None
        length, self.pos = r
        if self.pos + length > len(self.data):
            return None
        content = self.data[self.pos:self.pos + length]
        self.pos += length
        return content

    def read_bigint(self):
        c = self.read_tlv(0x02)
        if c is None or len(c) == 0:
            return None
        if c[0] & 0x80:
            return None  # negative
        if len(c) > 1 and c[0] == 0x00:
            if not (c[1] & 0x80):
                return None  # non-minimal encoding
            c = c[1:]
        n = 0
        for b in c:
            n = n * 256 + b
        return n

    def read_small_uint(self):
        v = self.read_bigint()
        if v is None or v.bit_length() > 8:
            return None
        return v

# ── RSA OID ───────────────────────────────────────────────────────────────────

_RSA_OID = bytes([0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01])

# ── General public-key blob format ────────────────────────────────────────────

def encode_big_ints(fields):
    """Encode a list of non-negative ints as a DER SEQUENCE of INTEGERs."""
    body = b''
    for f in fields:
        bs = _der_int_bytes(f)
        body += bytes([0x02]) + _der_enc_len(len(bs)) + bs
    return _der_tlv(0x30, body)

def decode_big_ints(blob):
    """Decode a DER SEQUENCE of INTEGERs. Returns list of ints or None."""
    if not blob or blob[0] != 0x30:
        return None
    r = _der_dec_len(blob, 1)
    if r is None:
        return None
    seq_len, pos = r
    if pos + seq_len != len(blob):
        return None
    end_pos = pos + seq_len
    result = []
    while pos < end_pos:
        if pos >= len(blob) or blob[pos] != 0x02:
            return None
        pos += 1
        r2 = _der_dec_len(blob, pos)
        if r2 is None:
            return None
        ilen, pos = r2
        if pos + ilen > len(blob):
            return None
        field = blob[pos:pos + ilen]
        pos += ilen
        if not field or field[0] & 0x80:
            return None
        if len(field) > 1 and field[0] == 0x00:
            if not (field[1] & 0x80):
                return None  # non-minimal
            field = field[1:]
        n = 0
        for b in field:
            n = n * 256 + b
        result.append(n)
    return result

# ── PEM armor ─────────────────────────────────────────────────────────────────

def pem_wrap(label, blob):
    """Wrap binary blob in PEM text armor. Base64 lines are 64 chars wide."""
    b64 = base64.b64encode(blob).decode('ascii')
    out = f'-----BEGIN {label}-----\n'
    for i in range(0, len(b64), 64):
        out += b64[i:i + 64] + '\n'
    out += f'-----END {label}-----\n'
    return out

def pem_unwrap(label, pem):
    """Decode PEM text armor. Returns bytes or None."""
    lines = pem.rstrip('\n').split('\n')
    if not lines or lines[0] != f'-----BEGIN {label}-----':
        return None
    parts = []
    for line in lines[1:]:
        s = line.strip()
        if s == f'-----END {label}-----':
            return base64.b64decode(''.join(parts))
        if s:
            parts.append(s)
    return None

# ── Uppercase hex encode / decode ─────────────────────────────────────────────

_HEX_DIGITS = '0123456789ABCDEF'

def hex_encode_upper(n):
    """Encode a non-negative int as an even-length uppercase hex string (no '0x')."""
    if n == 0:
        return '00'
    bs = []
    while n > 0:
        bs.append(n & 0xff)
        n >>= 8
    bs.reverse()
    return ''.join(_HEX_DIGITS[b >> 4] + _HEX_DIGITS[b & 0x0f] for b in bs)

def hex_decode_bigint(s):
    """Decode an even-length hex string to an int. Returns None on error."""
    s = s.strip()
    if not s:
        return None
    if s == '0':
        return 0
    if len(s) % 2 != 0:
        return None
    try:
        return int(s, 16)
    except ValueError:
        return None

# ── Flat-hex XML ──────────────────────────────────────────────────────────────

def xml_wrap(root, pairs):
    """
    Produce the compact flat-XML format: <Root><field>HEXHEX</field>...</Root>.
    pairs is an iterable of (field_name, int_value).
    """
    out = f'<{root}>'
    for name, val in pairs:
        out += f'<{name}>{hex_encode_upper(val)}</{name}>'
    out += f'</{root}>'
    return out

def xml_unwrap(root, field_names, xml):
    """
    Parse the compact flat-XML format. Returns list of ints or None.
    """
    xml = xml.strip()
    open_root = f'<{root}>'
    close_root = f'</{root}>'
    if not xml.startswith(open_root) or not xml.endswith(close_root):
        return None
    inner = xml[len(open_root):-len(close_root)]
    result = []
    for name in field_names:
        otag = f'<{name}>'
        ctag = f'</{name}>'
        if not inner.startswith(otag):
            return None
        inner = inner[len(otag):]
        cp = inner.find(ctag)
        if cp < 0:
            return None
        v = hex_decode_bigint(inner[:cp])
        if v is None:
            return None
        result.append(v)
        inner = inner[cp + len(ctag):]
    if inner:
        return None
    return result
