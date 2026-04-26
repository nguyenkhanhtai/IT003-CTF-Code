import os

DATA_FILE = "ciphertexts.txt"
ciphertexts = []

# Đọc dữ liệu từ file local
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        for line in f:
            hex_str = line.strip()
            if hex_str:
                ciphertexts.append(bytes.fromhex(hex_str))
else:
    print("[-] Lỗi: Không tìm thấy file dữ liệu 'ciphertexts.txt'.")
    exit()

if len(ciphertexts) <= 9:
    print("[-] Lỗi: File dữ liệu không có đủ số lượng xâu (chưa tới xâu số 09).")
    exit()

TARGET_INDEX = 9
flag_ct = ciphertexts[TARGET_INDEX]
known_flag = bytearray(b"crypto{")

print("="*60)
print(f"[*] VŨ KHÍ BẮN TỈA: KHÓA MỤC TIÊU XÂU [{TARGET_INDEX:02d}]")
print(f"[*] Chiều dài xâu mục tiêu: {len(flag_ct)} bytes")
print("="*60 + "\n")

# Bắt đầu vòng lặp dò từng vị trí, tiếp nối ngay sau chữ "crypto{"
for col in range(len(known_flag), len(flag_ct)):
    best_guess = 0
    best_score = -999999
    
    # Brute-force các ký tự ASCII in được (từ 32 đến 126) cho lá cờ
    for guess in range(32, 127):
        # 1. TÍNH KEYSTREAM GIẢ ĐỊNH: Bản mã (Xâu 09) XOR Ký tự dự đoán
        k = flag_ct[col] ^ guess
        
        score = 0
        
        # Thưởng điểm ưu tiên nhẹ nếu ký tự đoán hợp lệ với định dạng cờ CTF
        if chr(guess) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_}":
            score += 10
            
        # 2. ÁP KEYSTREAM LÊN TẤT CẢ CÁC XÂU KHÁC ĐỂ CHẤM ĐIỂM
        for idx, ct in enumerate(ciphertexts):
            if idx == TARGET_INDEX:
                continue # Bỏ qua chính nó
            
            # Chỉ tính nếu xâu này đủ dài để với tới cột hiện tại
            if col < len(ct):
                # Giải mã: Bản mã XOR Keystream = Bản rõ
                p = ct[col] ^ k
                
                # CHẤM ĐIỂM HEURISTIC (Ngôn ngữ Anh)
                if 32 <= p <= 126:  # Rơi vào vùng chữ gõ được
                    score += 1
                    char_p = chr(p)
                    # Chữ cái và dấu cách rất phổ biến
                    if char_p in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ":
                        score += 5
                    # Các chữ cái có tần suất xuất hiện cao nhất trong tiếng Anh
                    if char_p in "etaoinshrdlcumETAOINSHRDLCUM":
                        score += 5
                else:
                    score -= 50  # Phạt cực nặng nếu đẻ ra ký tự rác (không gõ được)
                    
        # Chốt ký tự mang lại điểm số cao nhất cho cột này
        if score > best_score:
            best_score = score
            best_guess = guess
            
    # 3. GHI NHẬN KẾT QUẢ VÀ IN RA MÀN HÌNH
    known_flag.append(best_guess)
    print(f"\r[+] Đang phá mã: {known_flag.decode('ascii', errors='replace')} ", end="", flush=True)
    
    # Tự động dừng nếu bắt được dấu ngoặc nhọn đóng (kết thúc cờ)
    if chr(best_guess) == '}':
        break

print("\n\n" + "="*60)
print(f"BÙM! LÁ CỜ HOÀN CHỈNH:\n[+] {known_flag.decode('ascii', errors='replace')}")
print("="*60)