from sympy.ntheory.residue_ntheory import sqrt_mod
from Crypto.Util.number import long_to_bytes

# Dữ liệu từ đề bài

info = {}

with open("broken_rsa.txt", "r") as f:
    data = f.readlines()
    for line in data:
        line = line.strip()
        components = line.split('=')
        key, value = components[0].strip(), components[1].strip()
        info[key] = int(value)

n = info["n"]
ct = info["ct"]


def get_16th_root(c, p):
    current_roots = [c]
    
    # Lặp 4 lần vì 2^4 = 16
    for level in range(1, 5):
        next_roots = []
        for r in current_roots:
            # sqrt_mod dùng Tonelli-Shanks để tìm tất cả các căn bậc 2 của r
            roots_of_r = sqrt_mod(r, p, all_roots=True)
            
            # Nếu r có căn bậc 2 (không bị None), thêm vào mảng của tầng tiếp theo
            if roots_of_r:
                next_roots.extend(roots_of_r)
                
        current_roots = next_roots
        print(f"Level {level}: Tách thành {len(current_roots)} nghiệm.")
        
    return current_roots

final_roots = get_16th_root(ct, n)

# 2. tìm Flag
for m in final_roots:
    try:
        flag = long_to_bytes(m).decode('utf-8')
        if 'crypto{' in flag:
            print(f"FLAG:\n{flag}")
            break
    except UnicodeDecodeError:
        continue