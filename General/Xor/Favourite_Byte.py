from pwn import xor
ciphertext = '73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d'
for key in range(256):
    plaintext = xor(bytes.fromhex(ciphertext), bytes([key]))
    if all(32 <= b < 127 for b in plaintext) and plaintext.startswith(b'crypto{'):
        print(f'key: {key}, plaintext: {plaintext.decode()}')