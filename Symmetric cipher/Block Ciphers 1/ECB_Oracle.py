import requests
import string
import time

BASE_URL = "http://aes.cryptohack.org/ecb_oracle/encrypt"
# Thêm một vài ký tự đặc biệt phòng hờ
alphabet = string.ascii_letters + string.digits + "_{}?!@#$%&*-+="

flag = "crypto{p3n6u1n5"
print(f"Tiếp tục giải mã từ: {flag}\n")

def get_json_safe(url):
    while True:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 404:
            print("[-] Lỗi 404: Gửi chuỗi rỗng! (Code mới đã fix lỗi này)")
            time.sleep(1)
        else:
            print(f"[-] Bị chặn (Mã {res.status_code}). Đang đợi 2 giây...")
            time.sleep(2)

# Chạy tiếp từ vị trí 15
for i in range(len(flag), 35):
    # ĐIỂM SỬA CHỮA: Dùng 31 thay vì 15 để padding không bao giờ bằng 0
    pad_len = 31 - (i % 16)
    padding = "A" * pad_len
    
    target_url = f"{BASE_URL}/{padding.encode().hex()}/"
    target_ciphertext = get_json_safe(target_url)["ciphertext"]
    
    # ĐIỂM SỬA CHỮA: Vì ta chèn thêm 1 khối (16 byte), ta phải dời điểm so sánh lên 1 khối
    block_idx = (i // 16) + 1
    start = block_idx * 32
    end = start + 32
    target_block = target_ciphertext[start:end]

    found_char = False
    for char in alphabet:
        payload = padding + flag + char
        guess_url = f"{BASE_URL}/{payload.encode().hex()}/"
        
        guess_ciphertext = get_json_safe(guess_url)["ciphertext"]
        guess_block = guess_ciphertext[start:end]
        
        if guess_block == target_block:
            flag += char
            print(f"[*] Tiến độ: {flag}")
            found_char = True
            break
            
    if flag.endswith("}"):
        print("\n[+] HOÀN THÀNH XUẤT SẮC! CỜ CỦA BẠN LÀ: " + flag)
        break
        
    if not found_char:
        print("\n[-] Không tìm thấy ký tự. Dừng vòng lặp.")
        break