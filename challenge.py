from Crypto.Cipher import DES, ARC4
from hashlib import md5
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


def gen_challenge(initial_key: bytearray):
    # Challenge structure: challenge text[40 bytes] + rc4 key 1[16 bytes] + rc4 key 2[16 bytes] + initial key[8 bytes] + md5 checksum(Challenge data + session key #1 + session key #2 + initial key)[16 bytes] + padding[8 bytes]
    ctext = get_random_bytes(40)
    rc4_1 = get_random_bytes(16)
    rc4_2 = get_random_bytes(16)
    checksum = md5(bytearray(ctext)+rc4_1+rc4_2+initial_key).digest()
    data = bytearray()
    data += ctext
    data += rc4_1
    data += rc4_2
    data += initial_key
    data += checksum
    data = pad(data, 8)
    enc = DES.new(initial_key, DES.MODE_ECB)
    encdata = enc.encrypt(data)
    rdata = bytearray()
    rdata += get_random_bytes(8)
    rdata += encdata
    return rc4_1, rc4_2, rdata, ctext

def check_challenge(ch: bytes, initial_key: bytes, cr: bytes):
    # Challenge response: DES ECB Encrypted data with wtv-initial-key as key[MD5(first 80 bytes of challenge)+first 80 bytes of challenge]
    if ch[:8] != cr[:8]:
        print(" * Challenge response mismatch, wrong vector.")
        return False
    dec = DES.new(initial_key, DES.MODE_ECB)
    out = dec.decrypt(ch[8:])
    out2 = cr[8:]
    if out[:40] != out2[16:16+40]:
        print(" * Challenge response mismatch, wrong ctext")
        return False
    return True