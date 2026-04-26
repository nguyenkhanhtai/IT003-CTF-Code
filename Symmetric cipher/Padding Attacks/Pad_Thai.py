from pwn import *
import json
import os

context.log_level = 'error'

HOST = 'socket.cryptohack.org'
PORT = 13421

def send_req(io, req):
    """Hàm hỗ trợ đóng gói JSON và gửi request, nhận response"""
    io.sendline(json.dumps(req).encode())
    return json.loads(io.recvline().decode().strip())

def decrypt_block(io, target_block, prev_block):
    """
    Hàm giải mã 1 khối 16 byte dựa trên kỹ thuật Padding Oracle.
    target_block: Khối mã cần giải (ví dụ: C1 hoặc C2)
    prev_block: Khối đứng ngay trước nó (ví dụ: IV hoặc C1)
    """
    intermediate = bytearray(16)
    plaintext = bytearray(16)
    
    # Mò ngược từ byte cuối (15) lên byte đầu (0)
    for i in range(15, -1, -1):
        pad_val = 16 - i
        
        # Tạo khối ảo (Crafted Block) với các byte ngẫu nhiên để chống False Positive
        crafted_prev = bytearray(os.urandom(16)) 
        
        # Thiết lập các byte đã giải mã thành công ở đuôi sao cho nó XOR ra đúng pad_val
        for j in range(i + 1, 16):
            crafted_prev[j] = intermediate[j] ^ pad_val
            
        found = False
        # Brute-force 256 giá trị cho byte tại vị trí i
        for guess in range(256):
            crafted_prev[i] = guess
            
            # Gửi lên Oracle: Khối ảo + Khối mục tiêu
            req = {
                "option": "unpad",
                "ct": crafted_prev.hex() + target_block.hex()
            }
            res = send_req(io, req)
            
            # Nếu Oracle báo unpad thành công (Good Padding)
            if res.get("result") == True:
                
                # CHỐNG FALSE POSITIVE (Chỉ cần test khi đang mò byte cuối cùng - padding 0x01)
                if pad_val == 1:
                    # Lật bit của byte liền trước (i-1) để phá vỡ cấu trúc nếu nó lỡ là 02 02
                    crafted_prev[i-1] ^= 1
                    req_check = {
                        "option": "unpad",
                        "ct": crafted_prev.hex() + target_block.hex()
                    }
                    res_check = send_req(io, req_check)
                    
                    # Nếu phá byte trước mà padding hỏng -> False positive (ví dụ nó là 02 02 thật)
                    if res_check.get("result") == False:
                        continue 
                        
                # 1. Lưu lại byte Intermediate State
                intermediate[i] = guess ^ pad_val
                
                # 2. Tính luôn Plaintext thật: P = I ^ Khối_Trước_Nguyên_Thủy
                plaintext[i] = intermediate[i] ^ prev_block[i]
                
                print(f"    [+] Byte {i:02d}: I={hex(intermediate[i])} | P={hex(plaintext[i])} ('{chr(plaintext[i]) if 32 <= plaintext[i] <= 126 else '.'}')")
                found = True
                break
                
        if not found:
            print(f"[-] Lỗi chí mạng tại vị trí {i}: Không tìm được byte hợp lệ.")
            return None
            
    return plaintext

def main():
    print(f"[*] Đang kết nối tới máy chủ Oracle {HOST}:{PORT}...")
    io = remote(HOST, PORT)
    io.recvline() 
    
    # Bước 1: Lấy dữ liệu mục tiêu
    print("[*] Lấy dữ liệu IV và Ciphertext gốc...")
    res_enc = send_req(io, {"option": "encrypt"})
    ct_hex = res_enc["ct"]
    
    # Chia nhỏ dữ liệu thành từng khối 16 byte
    iv = bytes.fromhex(ct_hex[:32])
    c1 = bytes.fromhex(ct_hex[32:64])
    c2 = bytes.fromhex(ct_hex[64:])
    
    # Bước 2: Tấn công khối 1 (Dùng C1 và IV)
    print(f"\n[*] Bắt đầu giải mã Khối 1 (Mục tiêu: C1, Khối trước: IV)...")
    p1 = decrypt_block(io, c1, iv)
    
    # Bước 3: Tấn công khối 2 (Dùng C2 và C1)
    print(f"\n[*] Bắt đầu giải mã Khối 2 (Mục tiêu: C2, Khối trước: C1)...")
    p2 = decrypt_block(io, c2, c1)
    
    # Bước 4: Lắp ráp thông điệp và đổi cờ
    message = (p1 + p2).decode('ascii')
    print(f"\n[*] Hoàn tất giải mã! Thông điệp Hex: {message}")
    print("[*] Đang gửi thông điệp cho Server để chuộc cờ...")
    
    res_flag = send_req(io, {"option": "check", "message": message})
    
    if "flag" in res_flag:
        print("\n" + "="*60)
        print(f"BÙM! LÁ CỜ CỦA BẠN ĐÂY:\n[+] {res_flag['flag']}")
        print("="*60)
    else:
        print(f"[-] Thất bại: {res_flag}")
        
    io.close()

if __name__ == "__main__":
    main()