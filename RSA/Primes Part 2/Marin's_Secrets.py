import re
from Crypto.Util.number import long_to_bytes, inverse

# Đường dẫn file của bạn
FILE_PATH = "output_f194012343666ced1a6699d196c8adc5.txt"

def solve():
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[-] Không tìm thấy file {FILE_PATH}")
        return

    # Regex xử lý cả dấu '=' và dấu ':'
    def extract(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        if not match: return None
        return int(match.group(1), 0)

    n = extract(r'n\s*[:=]\s*(0x[0-9a-fA-F]+|\d+)', content)
    e = extract(r'e\s*[:=]\s*(0x[0-9a-fA-F]+|\d+)', content)
    c = extract(r'c\s*[:=]\s*(0x[0-9a-fA-F]+|\d+)', content)

    if not n or not e or not c:
        print("[-] Lỗi: Không thể bóc tách đủ n, e, c từ file.")
        return

    bit_len = n.bit_length()
    print(f"[*] Đang quét ước số dạng 2^i - 1 (Mersenne)...")

    p = None
    # Duyệt tìm p = 2^i - 1
    for i in range(2, bit_len):
        potential_p = (1 << i) - 1
        if n % potential_p == 0:
            p = potential_p
            print(f"[+] Tìm thấy p tại i = {i}")
            break

    if p:
        q = n // p
        phi = (p - 1) * (q - 1)
        # Tính khóa bí mật d
        d = inverse(e, phi)
        # Giải mã
        m = pow(c, d, n)
        
        flag = long_to_bytes(m)
        print("\n" + "="*40)
        print("[+] GIẢI MÃ THÀNH CÔNG!")
        print(f"[*] FLAG: {flag.decode()}")
        print("="*40)
    else:
        print("[-] Không tìm thấy ước số phù hợp.")

if __name__ == "__main__":
    solve()