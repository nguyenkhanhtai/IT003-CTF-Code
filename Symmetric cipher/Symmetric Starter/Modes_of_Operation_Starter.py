import requests

url = "https://aes.cryptohack.org/block_cipher_starter/"
ciphertext = requests.get(url + "encrypt_flag/").json()["ciphertext"]
plaintext_hex = requests.get(url + "decrypt/" + ciphertext ).json().get("plaintext")

print(bytes.fromhex(plaintext_hex).decode())