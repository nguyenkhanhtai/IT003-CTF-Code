import requests
from Crypto.Util.number import inverse, long_to_bytes

# Thông số đề bài
n = 984994081290620368062168960884976209711107645166770780785733
e = 65537
ct = 948553474947320504624302879933619818331484350431616834086273

print("[*] Đang truy vấn trực tiếp lên máy chủ FactorDB...")

# Sử dụng API của FactorDB
url = f"http://factordb.com/api?query={n}"
try:
    response = requests.get(url).json()
    
    # Trạng thái 'FF' (Fully Factored) nghĩa là số đã được phân tích hoàn toàn
    if response.get('status') in ['FF', 'CF']:
        factors = response.get('factors')
        
        # factors trả về dạng list chứa [thừa_số, số_mũ]
        p = int(factors[0][0])
        q = int(factors[1][0])
        
        print(f"[+] Tìm thấy p = {p}")
        print(f"[+] Tìm thấy q = {q}")
        
        # Tiến hành giải mã RSA như bình thường
        phi = (p - 1) * (q - 1)
        d = inverse(e, phi)
        pt = pow(ct, d, n)
        flag = long_to_bytes(pt)
        
        print("\n[+] BẺ KHÓA THÀNH CÔNG!")
        print(f"[*] FLAG: {flag.decode('utf-8', errors='ignore')}")
    else:
        print("[-] Số này chưa có trên FactorDB.")
        print("[!] Lời khuyên: Chạy công cụ Yafu trên máy tính để phân tích bằng ngôn ngữ C (siêu nhanh).")

except Exception as err:
    print(f"[-] Đã xảy ra lỗi khi kết nối: {err}")