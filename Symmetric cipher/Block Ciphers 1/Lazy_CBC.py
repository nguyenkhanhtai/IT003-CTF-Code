import requests

BASE_URL = "https://aes.cryptohack.org/lazy_cbc"

print("[*] Bước 1: Lấy một khối Ciphertext (C1) bất kỳ...")
# Mã hóa 16 byte 'A' (32 ký tự hex) để lấy một C1 chuẩn 16 byte
r1 = requests.get(f"{BASE_URL}/encrypt/{'41'*16}/")
c1_hex = r1.json()["ciphertext"]

print(f"    -> C1 = {c1_hex}")

print("\n[*] Bước 2: Chế tạo bản mã độc hại (C1 + Khối_0 + C1)...")
zero_block = "00" * 16  # 16 byte 0
malicious_ciphertext = c1_hex + zero_block + c1_hex

print("\n[*] Bước 3: Ép server giải mã và bắt lỗi để lấy Plaintext...")
r2 = requests.get(f"{BASE_URL}/receive/{malicious_ciphertext}/")
error_msg = r2.json()["error"]

# Trích xuất chuỗi hex từ thông báo lỗi
p_hex = error_msg.split("Invalid plaintext: ")[1]
p_bytes = bytes.fromhex(p_hex)

print("\n[*] Bước 4: Thực hiện phép thuật KEY = P1 XOR P3...")
# Cắt lấy P1 (16 byte đầu) và P3 (16 byte từ vị trí 32)
p1 = p_bytes[0:16]
p3 = p_bytes[32:48]

# XOR từng byte của P1 và P3
key_bytes = bytes([a ^ b for a, b in zip(p1, p3)])
key_hex = key_bytes.hex()

print(f"\n[+] TÌM THẤY KEY: {key_hex}")
print(f"[+] KEY DẠNG CHỮ: {key_bytes.decode(errors='ignore')}")

print("\n[*] Bước 5: Lấy Cờ (Flag)...")
# Trong thử thách Lazy CBC thường có API get_flag để nộp key lấy cờ
r3 = requests.get(f"{BASE_URL}/get_flag/{key_hex}/")
print(f"[+] KẾT QUẢ: {r3.json()}")
flag_hex = "63727970746f7b35306d335f703330706c335f64306e375f3768316e6b5f49565f31355f316d70307237346e375f3f7d"
print(bytes.fromhex(flag_hex).decode())