import glob
import math
from itertools import combinations
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def solve():
    # 1. Đọc tất cả các file .pem trong thư mục
    pem_files = glob.glob("*.pem")
    keys = {}
    
    print(f"[*] Đang đọc {len(pem_files)} file Public Key...")
    for file in pem_files:
        with open(file, 'r') as f:
            key = RSA.import_key(f.read())
            keys[file] = key

    # 2. Tìm cặp Public Key dùng chung số nguyên tố bằng thuật toán GCD
    print("[*] Đang chạy thuật toán Euclid tìm Ước chung lớn nhất (Batch GCD)...")
    
    shared_p = None
    target_file_1 = None
    target_file_2 = None
    
    for file1, file2 in combinations(keys.keys(), 2):
        n1 = keys[file1].n
        n2 = keys[file2].n
        
        g = math.gcd(n1, n2)
        if g > 1:
            print(f"\n[+] BINGO! Tìm thấy sự trùng lặp thừa số!")
            print(f"    - {file1} và {file2} dùng chung số nguyên tố p.")
            shared_p = g
            target_file_1 = file1
            target_file_2 = file2
            break

    if not shared_p:
        print("[-] Không tìm thấy cặp khóa nào dùng chung thừa số. Có thể cần Yafu hoặc thuật toán khác.")
        return

    # 3. Phân tích thừa số và tạo Private Key
    # Chúng ta lấy n1 từ file1 để giải mã file1.ciphertext tương ứng
    n = keys[target_file_1].n
    e = keys[target_file_1].e
    p = shared_p
    q = n // p
    
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    
    print(f"[*] Đang cấu trúc lại Private Key cho {target_file_1}...")
    private_key = RSA.construct((n, e, d, p, q))
    cipher = PKCS1_OAEP.new(private_key)
    
    # 4. Đọc file ciphertext tương ứng và giải mã
    ciphertext_file = target_file_1.replace('.pem', '.ciphertext')
    try:
        with open(ciphertext_file, 'r') as f:
            encrypted_hex = f.read().strip()
        
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        flag = cipher.decrypt(encrypted_bytes)
        
        print("\n" + "="*40)
        print("[+] GIẢI MÃ OAEP THÀNH CÔNG!")
        print(f"[*] FLAG: {flag.decode('utf-8')}")
        print("="*40)
        
    except FileNotFoundError:
        print(f"[-] Không tìm thấy file {ciphertext_file} để giải mã.")
    except Exception as err:
        print(f"[-] Lỗi giải mã: {err}")

if __name__ == "__main__":
    solve()