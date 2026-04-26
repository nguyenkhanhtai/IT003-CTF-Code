import requests

BASE_URL = "https://aes.cryptohack.org/symmetry"

print("[*] Bước 1: Gọi API lấy Cờ đã mã hóa (kèm IV) từ server...")
url_flag = f"{BASE_URL}/encrypt_flag/"
res_flag = requests.get(url_flag).json()
full_ciphertext = res_flag["ciphertext"]

print(f"    -> Chuỗi gốc nhận được (Hex): {full_ciphertext}")

print("\n[*] Bước 2: Cắt IV và Ciphertext theo thiết kế của bạn...")
# Cắt 16 byte đầu tiên (32 ký tự hex) làm IV
iv = full_ciphertext[:32]
# Phần còn lại là Ciphertext thực sự
actual_ciphertext = full_ciphertext[32:]

print(f"    -> IV đã cắt ra (Hex): {iv}")
print(f"    -> Ciphertext thực sự (Hex): {actual_ciphertext}")

print("\n[*] Bước 3: Đưa Ciphertext (làm plaintext) và IV vào hàm encrypt để dội ngược...")
# API: /symmetry/encrypt/<plaintext>/<iv>/
url_encrypt = f"{BASE_URL}/encrypt/{actual_ciphertext}/{iv}/"
res_encrypt = requests.get(url_encrypt).json()

# Kết quả trả về nằm trong key 'ciphertext' của JSON
decrypted_hex = res_encrypt["ciphertext"]
print(f"    <- Kết quả server trả về (Hex): {decrypted_hex}")

print("\n[*] Bước 4: Ép kiểu Hex sang văn bản để đọc Cờ...")
try:
    flag = bytes.fromhex(decrypted_hex).decode()
    print(f"\n[+] KẾT QUẢ THU ĐƯỢC: {flag}")
except Exception as e:
    print(f"\n[-] Lỗi ép kiểu chữ: {e}")