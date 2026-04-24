import socket
import json
from Crypto.Util.number import long_to_bytes, bytes_to_long
from sympy.ntheory import factorint, isprime
class CryptoHackSocket:
    def __init__(self, host, port):
        """Khởi tạo và kết nối đến Server"""
        print(f"[*] Đang móc nối tới {host}:{port}...")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        
        # Dùng makefile để đọc dữ liệu theo từng dòng (cực kỳ hiệu quả với CryptoHack)
        self.f = self.s.makefile('r')
        
        # Hút cạn câu chào mừng mặc định của CryptoHack để làm sạch bộ đệm
        welcome_msg = self.f.readline().strip()
        print(f"[+] Đã vào trong! Server chào: {welcome_msg}")
        self.msg = welcome_msg

    def send_payload(self, payload_dict):
        """
        Hàm nã đạn: Nhận vào một Dictionary, tự biến thành JSON và gửi đi.
        Sau đó tự động chờ và bóc tách JSON trả về từ Server.
        """
        # 1. Đóng gói Payload thành JSON và thêm \n (bắt buộc với CryptoHack)
        data_to_send = json.dumps(payload_dict) + "\n"
        self.s.sendall(data_to_send.encode('utf-8'))
        
        # 2. Hứng dữ liệu trả về
        response_str = self.f.readline().strip()

        # Nếu server ngắt kết nối đột ngột
        if not response_str:
            print("[-] Server đã ngắt kết nối vô cớ!")
            return None
            

        # 3. Dịch ngược JSON thành Dictionary cho bạn dễ thao tác
        # return json.loads(response_str)
        return response_str

    def close(self):
        """Dọn dẹp chiến trường"""
        self.s.close()
        print("[*] Đã rút êm. Socket đóng!")

import json

def extract_json(intercepted_text):
    json_string = intercepted_text[intercepted_text.find('{'):]
    return json.loads(json_string)




# ###########Decrypt Shared Secret##################################################
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib


def is_pkcs7_padded(message):
    padding = message[-message[-1]:]
    return all(padding[i] == len(padding) for i in range(0, len(padding)))


def decrypt_flag(shared_secret: int, iv: str, ciphertext: str):
    # Derive AES key from shared secret
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    # Decrypt flag
    ciphertext = bytes.fromhex(ciphertext)
    iv = bytes.fromhex(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    if is_pkcs7_padded(plaintext):
        return unpad(plaintext, 16).decode('ascii')
    else:
        return plaintext.decode('ascii')




HOST = "socket.cryptohack.org"
PORT = 13371
conn = CryptoHackSocket(HOST, PORT)
message = extract_json(conn.msg)

p = int(message['p'], 16)
g = int(message['g'], 16)
A = int(message['A'], 16)

print(f"p: {p}")
print(f"g: {g}")
print(f"A: {A}")

payload = {  # Send to Bob
    'p': hex(p),
    'g': hex(g),
    'A': hex(A)
}

response = conn.send_payload(payload)

response_json = extract_json(response)

payload = { # Send to Alice
    'B': hex(p)
}

response = conn.send_payload(payload)
json_response = extract_json(response)

ciphertext = json_response["encrypted_flag"]
iv = json_response["iv"]

shared_secret = 0


print(f"shared_secret: {shared_secret}")
print(f"IV: {iv}")
print(f"CipherText: {ciphertext}")

print("FLAG: ", decrypt_flag(shared_secret, iv, ciphertext))

conn.close()
