import requests

u = "https://aes.cryptohack.org/ecbcbcwtf"
c = bytes.fromhex(requests.get(f"{u}/encrypt_flag/").json()["ciphertext"])
print(b"".join(bytes(x ^ y for x, y in zip(bytes.fromhex(requests.get(f"{u}/decrypt/{c[i:i+16].hex()}/").json()["plaintext"]), c[i-16:i])) for i in range(16, len(c), 16)).decode())