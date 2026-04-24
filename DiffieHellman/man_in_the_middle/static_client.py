import socket
import json
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime
from sympy.ntheory import factorint, isprime
from sympy.ntheory import discrete_log
import sys

# sys.stdout = "staticlient.txt"
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


if (__name__ == "__main__"):
    # Giữ lại iv và ciphertext của lần 1,
    # Nhận xét là trong lượt 2 nó vẫn sử dụng p và g, chỉ giữ nguyên b0,
    # Nên ta sẽ biến g thành A để nó trả về A^b0 là shared secret của lần 1.
    HOST = "socket.cryptohack.org"
    PORT = 13373
    conn = CryptoHackSocket(HOST, PORT)

    message = extract_json(conn.msg)

    p = int(message['p'], 16)
    g = int(message['g'], 16)
    alice_pubkey = int(message['A'], 16)

    ##1. Gửi Public Key từ Alice đến Bob, đổi giá trị payload để lừa Bob.
    payload = {
        'p': hex(p),
        'g': hex(alice_pubkey),
        'A': hex(g)
    }
    response = extract_json(conn.send_payload(payload))
    print(f"From Bob to Alice: {response} \n\n")
    
    ##2. Gửi Public key từ Bob đến Alice, bước này Bob vẫn gửi như bình thường
    
    bob_pubkey = int(response['B'], 16)

    payload = { #Bob to Alice
        'B': hex(bob_pubkey)
    }
    response = extract_json(conn.send_payload(payload))
    print(f"From Alice to Bob: {response}\n\n")
    iv = response["iv"]
    ciphertext = response["encrypted"]

    first_iv = iv
    first_ciphertext = ciphertext
    
    ##3. Gửi encrypted ciphertext và iv đến cho Bob, lúc này Bob sẽ sử dụng payload đã
    ##   bị chỉnh sửa trước đó.
    payload = { ## Alice to Bob
        'iv': iv,
        'encrypted': ciphertext
    }
    response = extract_json(conn.send_payload(payload))
    bob_pubkey = int(response['B'], 16)
    print(f"From Bob to Alice: {response} \n\n")
    
    #####
    shared_secret = bob_pubkey
    try:
        print("FLAG:",decrypt_flag(shared_secret, first_iv, first_ciphertext))
    except Exception as error:
        print(f"Error: {error}")
    conn.close()
