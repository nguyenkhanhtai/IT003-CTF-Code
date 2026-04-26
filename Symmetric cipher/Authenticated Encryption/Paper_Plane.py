import requests
import time

BASE_URL = "https://aes.cryptohack.org/paper_plane"

def send_oracle(ct, m0, c0):
    """Gửi payload lên Web API và kiểm tra Padding"""
    url = f"{BASE_URL}/send_msg/{ct.hex()}/{m0.hex()}/{c0.hex()}/"
    while True:
        try:
            res = requests.get(url).json()
            
            # Xử lý Rate Limit của CryptoHack
            if "error" in res and "Rate limit" in res["error"]:
                time.sleep(1.5)
                continue
                
            return "Message received" in res.get("msg", "")
        except Exception as e:
            print(f"[-] Lỗi mạng: {e}. Đang thử lại...")
            time.sleep(1)

def decrypt_block(target_ct, m0_param, c_prev):
    """
    target_ct: Khối mã cần giải
    m0_param: m0 gốc (nếu là khối 1) hoặc Plaintext khối trước (nếu là khối 2+)
    c_prev: c0 gốc (nếu là khối 1) hoặc Ciphertext khối trước (nếu là khối 2+)
    """
    intermediate = bytearray(16)
    plaintext = bytearray(16)
    
    for i in range(15, -1, -1):
        pad_val = 16 - i
        c0_fake = bytearray(16)
        
        # Đệm các byte đã biết
        for j in range(i + 1, 16):
            c0_fake[j] = intermediate[j] ^ pad_val
            
        found = False
        for guess in range(256):
            c0_fake[i] = guess
            
            if send_oracle(target_ct, m0_param, c0_fake):
                # CHỐNG FALSE POSITIVE (Chỉ cần khi tìm padding 0x01)
                if pad_val == 1 and i > 0:
                    c0_fake[i-1] ^= 0xFF
                    is_still_good = send_oracle(target_ct, m0_param, c0_fake)
                    c0_fake[i-1] ^= 0xFF # Trả lại giá trị cũ
                    
                    if not is_still_good:
                        continue # Là False Positive, bỏ qua guess này
                
                # Tính toán Intermediate và Plaintext thực sự
                intermediate[i] = guess ^ pad_val
                plaintext[i] = intermediate[i] ^ c_prev[i]
                
                char_repr = chr(plaintext[i]) if 32 <= plaintext[i] <= 126 else '.'
                print(f"    [+] Byte {i:02d}: P={hex(plaintext[i])} ('{char_repr}')")
                
                found = True
                break
                
        if not found:
            print(f"[-] Lỗi chí mạng tại vị trí {i}: Không tìm được byte hợp lệ.")
            return None
            
    return plaintext

def exploit():
    print("[*] Lấy dữ liệu Ciphertext, m0 và c0 gốc từ máy chủ...")
    res = requests.get(f"{BASE_URL}/encrypt_flag/").json()
    
    ct = bytes.fromhex(res["ciphertext"])
    m0_goc = bytes.fromhex(res["m0"])
    c0_goc = bytes.fromhex(res["c0"])
    
    # Chia nhỏ Ciphertext thành các khối 16 byte
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    flag = b""
    
    # 1. Giải mã khối đầu tiên (Sử dụng m0 và c0 gốc)
    print(f"\n[*] Bắt đầu giải mã Khối 1...")
    p1 = decrypt_block(blocks[0], m0_goc, c0_goc)
    if not p1: return
    flag += p1
    
    # 2. Giải mã các khối tiếp theo (Cập nhật tham số nạp chéo liên tục)
    prev_p = p1
    prev_c = blocks[0]
    
    for idx in range(1, len(blocks)):
        print(f"\n[*] Bắt đầu giải mã Khối {idx+1}...")
        
        # NẠP CHÉO: m0_param = Plaintext trước, c_prev = Ciphertext trước
        p_next = decrypt_block(blocks[idx], prev_p, prev_c)
        if not p_next: return
        flag += p_next
        
        # Cập nhật lại cho vòng lặp sau
        prev_p = p_next
        prev_c = blocks[idx]
        
    print("\n" + "="*60)
    print(f"[+] GIẢI MÃ HOÀN TẤT:\n{flag.decode('ascii', errors='ignore')}")
    print("="*60)

if __name__ == "__main__":
    exploit()