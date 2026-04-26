import math
from Crypto.Util.number import long_to_bytes

# Thông số đề bài cung cấp
N = 0xb12746657c720a434861e9a4828b3c89a6b8d4a1bd921054e48d47124dbcc9cfcdcc39261c5e93817c167db818081613f57729e0039875c72a5ae1f0bc5ef7c933880c2ad528adbc9b1430003a491e460917b34c4590977df47772fab1ee0ab251f94065ab3004893fe1b2958008848b0124f22c4e75f60ed3889fb62e5ef4dcc247a3d6e23072641e62566cd96ee8114b227b8f498f9a578fc6f687d07acdbb523b6029c5bbeecd5efaf4c4d35304e5e6b5b95db0e89299529eb953f52ca3247d4cd03a15939e7d638b168fd00a1cb5b0cc5c2cc98175c1ad0b959c2ab2f17f917c0ccee8c3fe589b4cb441e817f75e575fc96a4fe7bfea897f57692b050d2b
e = 0x9d0637faa46281b533e83cc37e1cf5626bd33f712cc1948622f10ec26f766fb37b9cd6c7a6e4b2c03bce0dd70d5a3a28b6b0c941d8792bc6a870568790ebcd30f40277af59e0fd3141e272c48f8e33592965997c7d93006c27bf3a2b8fb71831dfa939c0ba2c7569dd1b660efc6c8966e674fbe6e051811d92a802c789d895f356ceec9722d5a7b617d21b8aa42dd6a45de721953939a5a81b8dffc9490acd4f60b0c0475883ff7e2ab50b39b2deeedaefefffc52ae2e03f72756d9b4f7b6bd85b1a6764b31312bc375a2298b78b0263d492205d2a5aa7a227abaf41ab4ea8ce0e75728a5177fe90ace36fdc5dba53317bbf90e60a6f2311bb333bf55ba3245f
c = 0xa3bce6e2e677d7855a1a7819eb1879779d1e1eefa21a1a6e205c8b46fdc020a2487fdd07dbae99274204fadda2ba69af73627bdddcb2c403118f507bca03cb0bad7a8cd03f70defc31fa904d71230aab98a10e155bf207da1b1cac1503f48cab3758024cc6e62afe99767e9e4c151b75f60d8f7989c152fdf4ff4b95ceed9a7065f38c68dee4dd0da503650d3246d463f504b36e1d6fafabb35d2390ecf0419b2bb67c4c647fb38511b34eb494d9289c872203fa70f4084d2fa2367a63a8881b74cc38730ad7584328de6a7d92e4ca18098a15119baee91237cea24975bdfc19bdbce7c1559899a88125935584cd37c8dd31f3f2b4517eefae84e7e588344fa5

print("[*] Đang khởi chạy Wiener's Attack...")

def rational_to_contfrac(num, den):
    """Tính các hệ số của Liên phân số"""
    quotients = []
    while den != 0:
        quotient = num // den
        quotients.append(quotient)
        num, den = den, num - quotient * den
    return quotients

def convergents_from_contfrac(frac):
    """Tạo các phân số xấp xỉ (k/d) từ các hệ số Liên phân số"""
    convs = []
    for i in range(len(frac)):
        if i == 0:
            num, den = frac[0], 1
        elif i == 1:
            num, den = frac[1] * frac[0] + 1, frac[1]
        else:
            num = frac[i] * convs[i-1][0] + convs[i-2][0]
            den = frac[i] * convs[i-1][1] + convs[i-2][1]
        convs.append((num, den))
    return convs

def wiener_attack(e, N):
    frac = rational_to_contfrac(e, N)
    convergents = convergents_from_contfrac(frac)
    
    print(f"[*] Đã sinh ra {len(convergents)} phân số xấp xỉ. Đang kiểm tra nghiệm...")
    
    for k, d in convergents:
        # Bỏ qua các trường hợp k = 0 hoặc d là số chẵn (trong RSA d luôn là số lẻ)
        if k == 0 or d % 2 == 0:
            continue
            
        # Kiểm tra điều kiện chia hết: e*d = k*phi(N) + 1
        if (e * d - 1) % k != 0:
            continue
            
        phi = (e * d - 1) // k
        
        # Phương trình bậc 2 tìm p, q: x^2 - (N - phi + 1)x + N = 0
        b = N - phi + 1
        discriminant = b * b - 4 * N
        
        # Kiểm tra Delta có hợp lệ (là số chính phương) không
        if discriminant >= 0:
            s = math.isqrt(discriminant)
            if s * s == discriminant and (b + s) % 2 == 0:
                return d
    return None

# Thực thi tìm khóa d
d_found = wiener_attack(e, N)

if d_found:
    print(f"\n[+] TÌM THẤY KHÓA BÍ MẬT d: {hex(d_found)}")
    print("[*] Đang tiến hành giải mã bản mã...")
    
    # Giải mã: M = c^d mod N
    pt = pow(c, d_found, N)
    flag = long_to_bytes(pt)
    
    print("\n[+] BẺ KHÓA THÀNH CÔNG!")
    print(f"[*] FLAG: {flag.decode('utf-8', errors='ignore')}")
else:
    print("\n[-] Không tìm thấy khóa d bằng Wiener's Attack.")
    print("[-] Rất có thể khóa d đã vượt qua mốc N^0.25. Bạn cần chuyển sang dùng Boneh-Durfee Attack trên SageMath!")