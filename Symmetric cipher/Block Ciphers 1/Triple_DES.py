import requests

BASE_URL = "https://aes.cryptohack.org/triple_des"

# Ghép 2 Khóa yếu của DES (mỗi cái 8 byte) thành 1 Khóa 16 byte cho 3DES
# K1 = 0101010101010101
# K2 = FEFEFEFEFEFEFEFE
WEAK_KEY = "0101010101010101FEFEFEFEFEFEFEFE"

print(f"[*] Bước 1: Lừa server mã hóa Cờ bằng Khóa Yếu của chúng ta...")
url_encrypt_flag = f"{BASE_URL}/encrypt_flag/{WEAK_KEY}/"
res_flag = requests.get(url_encrypt_flag).json()
encrypted_flag = res_flag["ciphertext"]

print(f"    -> Cờ bị mã hóa (Hex): {encrypted_flag}")

print("\n[*] Bước 2: Kích hoạt ma thuật! Đem bản mã này đi... MÃ HÓA MỘT LẦN NỮA bằng cùng Khóa đó.")
url_encrypt_again = f"{BASE_URL}/encrypt/{WEAK_KEY}/{encrypted_flag}/"
res_decrypt = requests.get(url_encrypt_again).json()

# Nhờ tính chất của Weak Key: Encrypt(Encrypt(Plaintext)) = Plaintext
decrypted_hex = res_decrypt["ciphertext"]
print(f"    <- Kết quả dội ngược (Hex): {decrypted_hex}")

print("\n[*] Bước 3: Ép kiểu Hex sang văn bản...")
try:
    flag = bytes.fromhex(decrypted_hex).decode()
    print(f"\n[+] BÙM! CỜ CỦA BẠN ĐÂY: {flag}")
except Exception as e:
    print(f"\n[-] Lỗi ép kiểu chữ: {e}")