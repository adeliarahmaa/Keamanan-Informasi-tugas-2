# crypto_utils.py
import os
import struct
from Crypto.Cipher import AES

KEY_LEN = 32   # 256-bit
NONCE_LEN = 12
TAG_LEN = 16

def encrypt_message(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    if len(key) != KEY_LEN:
        raise ValueError("Key harus 32 byte (256-bit)")
    nonce = os.urandom(NONCE_LEN)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    if aad:
        cipher.update(aad)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    blob = nonce + ct + tag
    return struct.pack(">I", len(blob)) + blob

def decrypt_message(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    if len(key) != KEY_LEN:
        raise ValueError("Key harus 32 byte (256-bit)")
    if len(blob) < NONCE_LEN + TAG_LEN:
        raise ValueError("Blob terlalu pendek")
    nonce = blob[:NONCE_LEN]
    tag = blob[-TAG_LEN:]
    ct = blob[NONCE_LEN:-TAG_LEN]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    if aad:
        cipher.update(aad)
    pt = cipher.decrypt_and_verify(ct, tag)
    return pt
