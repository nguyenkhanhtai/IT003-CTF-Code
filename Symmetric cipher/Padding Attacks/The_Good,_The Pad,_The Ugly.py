#!/usr/bin/env python3
from pwn import *
import json
import os
import time

# Tắt log rác của pwntools để màn hình gọn gàng
context.log_level = 'error'

# Cập nhật PORT theo source code bài toán (13422 thay vì 13421 như Pad Thai)
HOST = 'socket.cryptohack.org'
PORT = 13422  

def send_req(io, req):
    """Hỗ trợ đóng gói JSON và gửi request, nhận response"""
    io.sendline(json.dumps(req).encode())
    res = io.recvline().decode().strip()
    
    # pwntools trả về chuỗi rỗng khi server ngắt kết nối đột ngột
    if not res:
        raise EOFError("Server ngắt kết nối (Có thể do quá 12.000 queries).")
        
    return json.loads(res)

def decrypt_block(io, target_block, prev_block):
    """Giải mã 1 khối bằng kỹ thuật Elimination để chống Oracle nói dối"""
    intermediate = bytearray(16)
    plaintext = bytearray(16)
    
    for i in range(15, -1, -1):
        pad_val = 16 - i
        
        # Khởi tạo khối ảo với các byte ngẫu nhiên (chỉ sinh 1 lần mỗi vị trí)
        crafted_prev = bytearray(os.urandom(16)) 
        
        # Gắn các byte đã giải mã thành công ở đuôi
        for j in range(i + 1, 16):
            crafted_prev[j] = intermediate[j] ^ pad_val
            
        # Chỉ tính toán 16 giá trị sinh ra ký tự Hex
        candidates = []
        for char in b"0123456789abcdef":
            guess = char ^ pad_val ^ prev_block[i]
            candidates.append(guess)
        
        print(f"    [*] Đang giải mã Byte {i:02d}...", end="", flush=True)
        
        # Lặp loại trừ: Rút gọn tập A cho đến khi chỉ còn 1 ứng viên duy nhất
        while len(candidates) > 1:
            next_candidates = []
            
            for guess in candidates:
                crafted_prev[i] = guess
                
                # CHỐNG FALSE POSITIVE: Chỉ cần khi test byte cuối cùng (pad 0x01)
                # Lật bit byte i-1 để hỏng cấu trúc nếu bản rõ vô tình là 0x02 0x02
                if pad_val == 1 and i > 0:
                    crafted_prev[i-1] ^= 0xFF
                    
                req = {
                    "option": "unpad",
                    "ct": crafted_prev.hex() + target_block.hex()
                }
                res = send_req(io, req)
                
                # Trả lại giá trị cũ ngay lập tức
                if pad_val == 1 and i > 0:
                    crafted_prev[i-1] ^= 0xFF
                
                # Nếu Oracle trả về True (do đệm đúng 100% HOẶC nhiễu 60%), giữ lại vòng sau
                # Nếu trả False (chắc chắn sai), loại bỏ luôn.
                if res.get("result") == True:
                    next_candidates.append(guess)
                    
            # Cập nhật lại mảng sau 1 vòng lọc
            candidates = next_candidates
            print(".", end="", flush=True) # In dấu chấm hiển thị tiến độ lọc nhiễu
            
            if len(candidates) == 0:
                raise ValueError(f" Mất toàn bộ ứng viên tại byte {i}! (Có thể do lỗi mạng)")
        
        # Mảng chỉ còn 1 phần tử duy nhất, đó chính là byte đúng
        correct_guess = candidates[0]
        
        # Tính toán Intermediate State và Plaintext thực
        intermediate[i] = correct_guess ^ pad_val
        plaintext[i] = intermediate[i] ^ prev_block[i]
        
        # Hiển thị ký tự nếu nó nằm trong dải in được của ASCII
        char_repr = chr(plaintext[i]) if 32 <= plaintext[i] <= 126 else '.'
        print(f" Xong! I={hex(intermediate[i])} | P={hex(plaintext[i])} ('{char_repr}')")
            
    return plaintext

def exploit():
    """Luồng khai thác chính cho 1 phiên kết nối"""
    print(f"[*] Đang kết nối tới máy chủ Oracle {HOST}:{PORT}...")
    io = remote(HOST, PORT)
    io.recvline() 
    
    print("[*] Lấy dữ liệu IV và Ciphertext gốc...")
    res_enc = send_req(io, {"option": "encrypt"})
    if "ct" not in res_enc:
        raise ValueError("Không lấy được Ciphertext từ server.")
        
    ct_hex = res_enc["ct"]
    
    # Cắt khối 16 byte
    iv = bytes.fromhex(ct_hex[:32])
    c1 = bytes.fromhex(ct_hex[32:64])
    c2 = bytes.fromhex(ct_hex[64:])
    
    print(f"\n[*] Bắt đầu giải mã Khối 1 (Mục tiêu: C1, Khối trước: IV)...")
    p1 = decrypt_block(io, c1, iv)
    
    print(f"\n[*] Bắt đầu giải mã Khối 2 (Mục tiêu: C2, Khối trước: C1)...")
    p2 = decrypt_block(io, c2, c1)
    
    message = (p1 + p2).decode('ascii')
    print(f"\n[*] Hoàn tất giải mã! Thông điệp Hex: {message}")
    print("[*] Đang gửi thông điệp cho Server để chuộc cờ...")
    
    res_flag = send_req(io, {"option": "check", "message": message})
    io.close()
    
    if "flag" in res_flag:
        print("\n" + "="*60)
        print(f"BÙM! LÁ CỜ CỦA BẠN ĐÂY:\n[+] {res_flag['flag']}")
        print("="*60)
        return True
    else:
        print(f"[-] Thất bại: {res_flag}")
        return False

def main():
    """Hệ thống tự động Reset nếu chạm mốc 12.000 queries"""
    attempt = 1
    while True:
        try:
            print(f"\n{'='*50}")
            print(f"[*] KHỞI CHẠY LẦN THỬ THỨ {attempt}")
            print(f"{'='*50}")
            
            is_success = exploit()
            if is_success:
                break
                
        except EOFError:
            print("\n[-] Server đóng cửa do cạn kiệt 12.000 queries. Tự động Retry từ đầu...\n")
            attempt += 1
            time.sleep(1)
        except Exception as e:
            print(f"\n[-] Đứt gánh giữa đường do lỗi: {e}. Đang thử lại...\n")
            attempt += 1
            time.sleep(1)

if __name__ == "__main__":
    main()