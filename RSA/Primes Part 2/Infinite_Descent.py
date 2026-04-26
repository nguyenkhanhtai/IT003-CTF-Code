import re
import gmpy2
from Crypto.Util.number import long_to_bytes, inverse

# Đường dẫn file output của bạn
FILE_PATH = "output_14f82a67efe7b7edffb810dbb7ab5f27.txt"

def fermat_factorization(n):
    """Thuật toán phân tích thừa số Fermat dành cho Close Primes"""
    # Bắt đầu thử từ phần nguyên căn bậc hai của n
    a = gmpy2.isqrt(n)
    if a*a < n:
        a += 1
    
    print("[*] Đang quét các giá trị xấp xỉ căn bậc hai...")
    count = 0
    while True:
        # Kiểm tra xem a^2 - n có phải là số chính phương (b^2) không
        b2 = a*a - n
        if gmpy2.is_square(b2):
            b = gmpy2.isqrt(b2)
            p = a + b
            q = a - b
            return int(p), int(q)
        
        a += 1
        count += 1
        # In tiến độ mỗi 1 triệu lần thử để bạn đỡ sốt ruột
        if count % 1000000 == 0:
            print(f"    ...Đã thử {count} giá trị...")

def solve():
    # 1. Đọc và bóc tách dữ liệu từ file
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[-] Không tìm thấy file {FILE_PATH}")
        return

    # Tìm n, e, c bằng Regex
    n = int(re.search(r'n\s*=\s*(\d+)', content).group(1))
    e = int(re.search(r'e\s*=\s*(\d+)', content).group(1))
    c = int(re.search(r'c\s*=\s*(\d+)', content).group(1))

    print(f"[*] Đã nhận diện được n (khoảng {n.bit_length()} bits)")

    # 2. Chạy thuật toán Fermat
    p, q = fermat_factorization(n)
    
    if p * q == n:
        print(f"[+] Tìm thấy p: {p}")
        print(f"[+] Tìm thấy q: {q}")
        print(f"[+] Khoảng cách |p-q|: {p - q}")
        
        # 3. Giải mã RSA
        phi = (p - 1) * (q - 1)
        d = inverse(e, phi)
        m = pow(c, d, n)
        
        flag = long_to_bytes(m)
        
        print("\n" + "="*40)
        print("[+] BẺ KHÓA THÀNH CÔNG!")
        print(f"[*] FLAG: {flag.decode('utf-8', errors='ignore')}")
        print("="*40)
    else:
        print("[-] Có gì đó sai sai, tích p*q không khớp với n.")

if __name__ == "__main__":
    solve()