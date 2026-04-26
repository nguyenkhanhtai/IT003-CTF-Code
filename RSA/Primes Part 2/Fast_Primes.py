import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def solve():
    # 1. Đọc khóa công khai từ file key.pem
    try:
        with open("key_17a08b7040db46308f8b9a19894f9f95.pem", "rb") as f:
            public_key = RSA.import_key(f.read())
            n = public_key.n
            e = public_key.e
    except FileNotFoundError:
        print("[-] Không tìm thấy file key.pem. Hãy đặt cùng thư mục với script.")
        return

    print(f"[*] Đã đọc Public Key. Độ dài N: {n.bit_length()} bits")

    # 2. Gọi API FactorDB để phân tích N
    print("[*] Đang truy vấn API FactorDB...")
    api_url = f"http://factordb.com/api?query={n}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
    except Exception as err:
        print(f"[-] Lỗi khi kết nối đến FactorDB: {err}")
        return

    # Trạng thái 'FF' (Fully Factored) hoặc 'CF' (Completely Factored)
    if data.get('status') in ['FF', 'CF']:
        factors = data.get('factors')
        # Đảm bảo N được phân tích thành đúng 2 thừa số nguyên tố bậc 1
        if len(factors) == 2 and factors[0][1] == 1 and factors[1][1] == 1:
            p = int(factors[0][0])
            q = int(factors[1][0])
            print(f"[+] FactorDB trả về kết quả thành công!")
            print(f"    p = {p}")
            print(f"    q = {q}")
        else:
            print("[-] FactorDB trả về cấu trúc thừa số không khớp với RSA (p * q).")
            return
    else:
        print("[-] FactorDB chưa có đáp án cho số N này.")
        print("    Bạn sẽ phải dùng Coppersmith Attack để khai thác lỗ hổng trong hàm get_fast_prime().")
        return

    # 3. Tính toán khóa bí mật d
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)

    # 4. Cấu trúc lại Private Key và giải mã OAEP
    print("[*] Đang cấu trúc lại Private Key và giải mã bản mã...")
    # Việc truyền cả p và q vào giúp PyCryptodome tối ưu giải mã bằng CRT
    private_key = RSA.construct((n, e, d, p, q))
    cipher = PKCS1_OAEP.new(private_key)

    try:
        with open("ciphertext_98a448b6bbcd080909d235e5da5e9d56.txt", "r") as f:
            encrypted_hex = f.read().strip()
        
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        flag = cipher.decrypt(encrypted_bytes)
        
        print("\n" + "="*40)
        print("[+] BẺ KHÓA THÀNH CÔNG!")
        print(f"[*] FLAG: {flag.decode('utf-8')}")
        print("="*40)
        
    except FileNotFoundError:
        print("[-] Không tìm thấy file ciphertext.txt.")
    except ValueError as err:
        print(f"[-] Lỗi giải mã OAEP: {err}")

if __name__ == "__main__":
    solve()