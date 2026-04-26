from pwn import xor

enc = '0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104'
known = 'crypto{'

key = xor(bytes.fromhex(enc)[:len(known)], known.encode()) + xor(bytes.fromhex(enc)[-1], b'}')
key = key * (len(bytes.fromhex(enc)) // len(key))
print(xor(bytes.fromhex(enc), key).decode())