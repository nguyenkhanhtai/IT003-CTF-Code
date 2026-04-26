import requests

BASE_URL = "http://aes.cryptohack.org/flipping_cookie"

print("1. Đang lấy cookie nguyên bản từ server...")
r = requests.get(f"{BASE_URL}/get_cookie/")
cookie_hex = r.json()["cookie"]

# Tách riêng IV (16 byte đầu) và Ciphertext (phần còn lại)
iv_hex = cookie_hex[:32]
ciphertext_hex = cookie_hex[32:]

print(f"[-] IV gốc:       {iv_hex}")

iv_bytes = bytearray.fromhex(iv_hex)

# Vị trí chữ 'F' trong "admin=False"
offset = 6
p_orig = b"False"
p_goal = b"True;" 

for i in range(len(p_orig)):
    iv_bytes[offset + i] = iv_bytes[offset + i] ^ p_orig[i] ^ p_goal[i]

new_iv_hex = iv_bytes.hex()
print(f"[+] IV giả mạo:   {new_iv_hex}")

# --- ĐIỂM SỬA LỖI Ở ĐÂY ---
# Ghép URL theo đúng chuẩn: /check_admin/<cookie>/<iv>/
check_url = f"{BASE_URL}/check_admin/{ciphertext_hex}/{new_iv_hex}/"

print("\n2. Đang gửi cookie đã độ lên server để cướp quyền admin...")
r_check = requests.get(check_url)

# In thẳng JSON ra để hái quả ngọt
print(f"\n[+] BÙM! KẾT QUẢ: {r_check.json()}")