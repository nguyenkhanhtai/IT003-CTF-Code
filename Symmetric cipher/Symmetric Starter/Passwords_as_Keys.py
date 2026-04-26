import requests
import hashlib
from Crypto.Cipher import AES
BASE_URL="https://aes.cryptohack.org/passwords_as_keys/"
words = requests.get("https://gist.githubusercontent.com/wchargin/8927565/raw/d9783627c731268fb2935a731a618aa8e95cf465/words").text.splitlines()
response = requests.get(f"{BASE_URL}/encrypt_flag/").json()
def hex_to_ascii(hex_str):return bytes.fromhex(hex_str).decode('ascii', errors='ignore')
ciphertext=response['ciphertext']
ciphertext = bytes.fromhex(ciphertext)
# print(len(words))
for keyword in words:
	key=hashlib.md5(keyword.encode()).digest()
	# key = bytes.fromhex(password_hash)
	cipher = AES.new(key, AES.MODE_ECB)
	decrypted = cipher.decrypt(ciphertext)
	# print(hex_to_ascii(decrypted.hex()))
	text=hex_to_ascii(decrypted.hex())
	if text[0:6]=="crypto":
		print(text)
		break