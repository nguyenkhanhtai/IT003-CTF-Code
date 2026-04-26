import requests

BASE_URL = "https://aes.cryptohack.org/ctrime/encrypt"
known_flag = "crypto{CRIM"

# Chỉ quét các ký tự hợp lệ thường có trong Flag, vứt bỏ dấu cách
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_}@"

print(f"[*] Bắt đầu tấn công CRIME (Phiên bản Vượt Rào Byte-Alignment)...")

while True:
    min_length = 999999
    best_chars = []
    
    print(f"\n[=] Cờ hiện tại: {known_flag}")
    print(f"========== ĐANG DÒ KÝ TỰ TIẾP THEO ==========")
    
    # Bước 1: Quét chiều dài của toàn bộ bảng chữ cái
    for char in CHARSET:
        guess_text = known_flag + char
        guess_hex = guess_text.encode().hex()
        
        try:
            res = requests.get(f"{BASE_URL}/{guess_hex}/").json()
            ct_length = len(res.get("ciphertext", ""))
            
            print(f"\r    -> Thử '{char}' | Chiều dài bản mã: {ct_length}    ", end="", flush=True)
            
            # Gom TẤT CẢ các ký tự có cùng độ dài nhỏ nhất
            if ct_length < min_length:
                min_length = ct_length
                best_chars = [char]
            elif ct_length == min_length:
                best_chars.append(char)
        except Exception:
            continue
            
    print(f"\n[*] Các ký tự lọt vào vòng chung kết (Length = {min_length}): {best_chars}")
    
    final_char = ""
    
    # Bước 2: Lọc kết quả
    if len(best_chars) == 1:
        final_char = best_chars[0]
    else:
        print("[!] Có nhiều ký tự hòa nhau. Khởi động Tie-Breaker (Chèn Padding rác)...")
        tie_min_len = 999999
        
        for char in best_chars:
            # Nhồi thêm byte rác vào đầu để dịch chuyển ranh giới bit của zlib
            pad_text = "123" + known_flag + char 
            pad_hex = pad_text.encode().hex()
            
            try:
                res = requests.get(f"{BASE_URL}/{pad_hex}/").json()
                pad_len = len(res.get("ciphertext", ""))
                
                print(f"    -> Đệm cho '{char}' | Chiều dài mới: {pad_len}")
                if pad_len < tie_min_len:
                    tie_min_len = pad_len
                    final_char = char
            except Exception:
                continue
    
    if not final_char:
        print("[-] Bế tắc! Không tìm được ký tự nào phù hợp. Dừng lại.")
        break
        
    known_flag += final_char
    print(f"[+] BINGO! Chốt ký tự: '{final_char}'")
    
    # Kết thúc nếu tìm thấy dấu đóng ngoặc
    if final_char == '}':
        break

print(f"\n[=+] KẾT QUẢ CUỐI CÙNG: {known_flag}")