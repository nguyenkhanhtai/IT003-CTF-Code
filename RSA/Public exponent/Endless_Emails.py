import re
import sympy
from sympy.ntheory.modular import crt
from itertools import combinations
from Crypto.Util.number import long_to_bytes

FILE_PATH = "output_0ef6d6343784e59e2f44f61d2d29896f.txt"

def solve():
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[-] Không tìm thấy file {FILE_PATH}")
        return

    # Bước 1: Tách dữ liệu thành từng khối dựa trên "n ="
    # Cách này đảm bảo n và c luôn đi cùng nhau
    blocks = re.split(r'n\s*=', content)[1:]
    data_pairs = []
    
    for block in blocks:
        n_match = re.search(r'^(\d+)', block.strip())
        c_match = re.search(r'c\s*=\s*(\d+)', block)
        if n_match and c_match:
            data_pairs.append((int(n_match.group(1)), int(c_match.group(1))))

    print(f"[*] Đã trích xuất được {len(data_pairs)} cặp (n, c) hợp lệ.")
    e = 3

    # Bước 2: Thử các tổ hợp 3 cặp (vì e=3 chỉ cần 3 cặp là đủ)
    # Việc thử tổ hợp giúp loại bỏ các "email" bị lỗi hoặc chứa nội dung khác
    print(f"[*] Đang thử các tổ hợp {e} cặp để tìm Flag...")
    
    found = False
    for combo in combinations(data_pairs, e):
        ns = [p[0] for p in combo]
        cs = [p[1] for p in combo]
        
        # Tính CRT
        result = crt(ns, cs)
        if not result: continue
        
        m_exp_e = result[0]
        
        # Lấy căn bậc 3
        m, is_exact = sympy.integer_nthroot(m_exp_e, e)
        
        if is_exact:
            flag = long_to_bytes(m)
            if b"crypto{" in flag:
                print("\n" + "="*40)
                print("[+] BẺ KHÓA THÀNH CÔNG!")
                print(f"[*] FLAG: {flag.decode('utf-8', errors='ignore')}")
                print("="*40)
                found = True
                break
    
    if not found:
        print("[-] Thất bại: Không tìm thấy tổ hợp nào tạo ra lũy thừa bậc 3 hoàn hảo.")
        print("[!] Gợi ý: Kiểm tra xem file output có bị xuống dòng giữa chừng làm mất số không.")

if __name__ == "__main__":
    solve()