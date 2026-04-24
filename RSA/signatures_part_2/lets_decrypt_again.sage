import socket
import json
import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
from pkcs1 import emsa_pkcs1_v15
from bitcoin import random_key, privtopub, pubtoaddr
from sage.all import *

class CryptoHackSocket:
    def __init__(self, host, port):
        """Khởi tạo và kết nối đến Server"""
        print(f"[*] Đang móc nối tới {host}:{port}...")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        
        self.f = self.s.makefile('r')
        welcome_msg = self.f.readline().strip()
        print(f"[+] Đã vào trong! Server chào: {welcome_msg}")

    def send_payload(self, payload_dict):
        data_to_send = json.dumps(payload_dict) + "\n"
        self.s.sendall(data_to_send.encode('utf-8'))
        
        response_str = self.f.readline().strip()
        if not response_str:
            print("[-] Server đã ngắt kết nối vô cớ!")
            return None
            
        return json.loads(response_str)

    def close(self):
        self.s.close()
        print("[*] Đã rút êm. Socket đóng!")

# --- Hàm hỗ trợ toán học cho SageMath ---
def B_smooth(total_size, small_factors_size, big_factor_size):
    while True:
        num_small = (total_size - big_factor_size) // small_factors_size
        factors = [random_prime(2**small_factors_size) for _ in range(num_small)]
        big_p = random_prime(2**big_factor_size)
        p = 2 * big_p * prod(factors) + 1
        if p.nbits() >= total_size and is_prime(p):
            return p, factors

def generate_pq(nbits):
    print("[+] Generating smooth p...")
    while True:
        p, _ = B_smooth(nbits + 32, 15, 40)
        if is_prime(p) and p > 2**nbits:
            break

    print("[+] Generating smooth q...")
    while True:
        q, _ = B_smooth(nbits + 32, 15, 40)
        if is_prime(q) and q > 2**nbits and gcd(p-1, q-1) == 2:
            break
    return p, q

# --- Các hàm tạo thông điệp giả mạo ---
alpha = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def get_test_message(suffix):    
    return "This is a test " + ''.join(random.sample(alpha, 32)) + " for a fake signature." + suffix

def get_own_message(suffix):
    return "My name is " + ''.join(random.sample(alpha, 32)) + " and I own CryptoHack.org" + suffix

def get_btc_message(suffix):
    my_private_key = random_key()
    my_public_key = privtopub(my_private_key)
    my_bitcoin_address = pubtoaddr(my_public_key)
    return "Please send all my money to " + my_bitcoin_address + suffix

# --- Luồng thực thi chính ---
if __name__ == "__main__":
    BIT_LENGTH = 768
    conn = CryptoHackSocket('socket.cryptohack.org', 13394)

    # 1. Lấy chữ ký gốc
    received = conn.send_payload({"option": "get_signature"})
    SIG0 = int(received["signature"], 16)
    print(f"[+] Nhận signature: {hex(SIG0)[:30]}...")

    # 2. Sinh N trơn và set pubkey để lấy suffix
    p, q = generate_pq(BIT_LENGTH)
    N_ = p * q
    print(f"[+] p = {p}")
    print(f"[+] q = {q}")
    
    received = conn.send_payload({"option": "set_pubkey", "pubkey": hex(N_)})
    suffix = received["suffix"]
    print(f"[+] Đã set N mới. Nhận suffix: {suffix}")

    # 3. Tính toán dlog cho 3 thông điệp
    messages = []
    for fn in [get_test_message, get_own_message, get_btc_message]:
        while True:
            m = fn(suffix)        
            digest = bytes_to_long(emsa_pkcs1_v15.encode(m.encode(), BIT_LENGTH // 8))
            
            try:            
                x = discrete_log(Zmod(p)(digest), Zmod(p)(SIG0))
                y = discrete_log(Zmod(q)(digest), Zmod(q)(SIG0))
                e = int(crt(x, y, p-1, q-1))
                print(f"[+] Tìm thấy e cho thông điệp: {m[:30]}...")
                messages.append((m, e))
                break
            except Exception:
                continue

    # 4. Gửi lần lượt để nhận shares
    shares = []
    for index, (m, e) in enumerate(messages):
        received = conn.send_payload({
            "option": "claim", 
            "msg": m, 
            "e": hex(e), 
            "index": index
        })
        shares.append(long_to_bytes(int(received["secret"], 16)))
        print(f"[+] Nhận share {index}")

    # 5. Khôi phục Flag
    last_share = bytes(x ^ y for x, y in zip(shares[2], shares[1]))
    flag = bytes(x ^ y for x, y in zip(last_share, shares[0]))
    
    print("\n[!] BINGO: ", flag.decode())
    conn.close()