import requests
import time

BASE_URL = "https://aes.cryptohack.org/oh_snap/send_cmd"

# Gửi đúng 1 byte 0x00. Server sẽ trả về: "Unknown command: <Keystream>"
CIPHERTEXT_HEX = "00"

def get_keystream_byte(nonce):
    url = f"{BASE_URL}/{CIPHERTEXT_HEX}/{nonce.hex()}/"
    while True:
        try:
            res = requests.get(url)
            if res.status_code == 429 or "Rate limit" in res.text:
                time.sleep(1.5)
                continue
                
            data = res.json()
            if "error" in data and "Unknown command: " in data["error"]:
                hex_str = data["error"].replace("Unknown command: ", "")
                return int(hex_str[:2], 16)
                
            elif "msg" in data:
                # Nếu lỡ tay XOR ra chữ 'p' (0x70) của lệnh ping
                return 0x70
                
            return None
        except Exception:
            time.sleep(1)

def fms_attack():
    print("="*60)
    print("[*] KHỞI ĐỘNG VŨ KHÍ: FMS ATTACK (WEP CRACKING)")
    print("="*60 + "\n")
    
    flag = b""
    
    # Lặp cho đến khi tìm thấy dấu ngoặc đóng
    while True:
        A = len(flag)      # Vị trí ký tự FLAG đang tìm
        idx = A + 3        # Vị trí của ký tự đó trong mảng Khóa tổng
        votes = [0] * 256  # Mảng thống kê số phiếu bầu cho 256 ký tự ASCII
        
        print(f"[*] Đang tấn công byte thứ {A}...")
        
        # Thử 256 IV yếu (Weak IVs)
        for V in range(256):
            nonce = bytes([idx, 255, V])
            K = get_keystream_byte(nonce)
            
            if K is None:
                continue
                
            # 1. Giả lập lại mảng S (KSA) cho đến ngay trước ký tự mục tiêu
            S = list(range(256))
            j = 0
            key = nonce + flag
            
            for i in range(idx):
                j = (j + S[i] + key[i]) % 256
                S[i], S[j] = S[j], S[i]
                
            # 2. Công thức toán học FMS để giải ngược ra byte Khóa
            guess = (K - j - S[idx]) % 256
            votes[guess] += 1
            
        # 3. Ký tự nào được toán học gọi tên nhiều nhất chính là Flag
        best_guess = votes.index(max(votes))
        flag += bytes([best_guess])
        
        print(f"[+] Lá cờ hiện tại: {flag.decode('ascii', errors='ignore')}")
        
        if flag.endswith(b"}"):
            print("\n" + "="*60)
            print(f"BÙM! ĐÃ PHÁ ĐẢO THÀNH CÔNG:\n[+] {flag.decode('ascii')}")
            print("="*60)
            break

if __name__ == "__main__":
    fms_attack()