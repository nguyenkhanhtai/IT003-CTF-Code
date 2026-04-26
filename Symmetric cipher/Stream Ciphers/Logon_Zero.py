from pwn import *
import json

# Tắt log mặc định của pwntools cho console sạch sẽ
context.log_level = 'error'

print("[*] Khởi động chiến dịch tấn công CFB-8 dựa trên idea đóng băng thanh ghi...")

while True:
    try:
        # Mở kết nối
        io = remote('socket.cryptohack.org', 13399)
        io.recvline() # Bỏ qua dòng chào mừng ban đầu

        # 1. Gửi token 28 byte giống hệt nhau (0x00)
        token_hex = "00" * 28
        print("[*] Đang nạp token 28 byte 0x00 để reset_password...")
        
        req_reset = {"option": "reset_password", "token": token_hex}
        io.sendline(json.dumps(req_reset).encode())
        io.recvline()

        print("[*] Thanh ghi đã bị đóng băng! Đang brute-force 128 ký tự ASCII...")
        flag_found = False
        
        # 2. Brute-force mật khẩu (chắc chắn là 8 ký tự giống hệt nhau)
        for i in range(128):
            guess_char = chr(i)
            guess_password = guess_char * 8
            
            req_auth = {"option": "authenticate", "password": guess_password}
            io.sendline(json.dumps(req_auth).encode())
            
            # Đọc phản hồi từ server
            res_raw = io.recvline().decode()
            response = json.loads(res_raw)
            
            if "Welcome admin" in response.get('msg', ''):
                print(f"\n[+] BINGO! Mật khẩu bị ép thành 8 ký tự: '{guess_char}'")
                print(f"[+] KẾT QUẢ: {response['msg']}\n")
                flag_found = True
                break
                
        if flag_found:
            io.close()
            break
        else:
            print("[-] Xui xẻo! Byte bí mật sinh ra lớn hơn 127. Đang reset lại Key...")
            io.close() # Đóng và kết nối lại vòng lặp while để lấy Key mới
            
    except Exception as e:
        print(f"Lỗi: {e}")
        break