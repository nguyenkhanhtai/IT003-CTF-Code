import socket
import json
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime
from sympy.ntheory import factorint, isprime
from sympy.ntheory import discrete_log

class CryptoHackSocket:
    def __init__(self, host, port):
        """Khởi tạo và kết nối đến Server"""
        print(f"[*] Đang móc nối tới {host}:{port}...")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        
        self.f = self.s.makefile('r')
        
        welcome_msg = self.f.readline().strip()
        print(f"[+] Đã vào trong! Server chào: {welcome_msg}")
        self.msg = welcome_msg

    def send_payload(self, payload_dict):
        data_to_send = json.dumps(payload_dict) + "\n"
        self.s.sendall(data_to_send.encode('utf-8'))
        
        response_str = self.f.readline().strip()

        if not response_str:
            print("[-] Server đã ngắt kết nối vô cớ!")
            return None
            
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

    HOST = "socket.cryptohack.org"
    PORT = 13379
    conn = CryptoHackSocket(HOST, PORT)

    message = extract_json(conn.msg)
    list_supported =  ["DH64"]

    payload = { # Alice to Bob
        'supported': list_supported
    }
    response = extract_json(conn.send_payload(payload))
    bob_dh_choice = response["chosen"]

    payload = { # Bob to Alice
        'chosen': "DH64"
    }
    response = extract_json(conn.send_payload(payload))
    p = int(response['p'], 16)
    g = int(response['g'], 16)
    alice_pubkey = int(response['A'], 16)

    payload = { # "Alice to Bob"
        'p': hex(p),
        'g': hex(g),
        'A': hex(alice_pubkey)
    }

    response = extract_json(conn.send_payload(payload))
    bob_pubkey = int(response['B'], 16)

    payload = { # "Bob to Alice"
        'B': hex(bob_pubkey)
    }

    response = extract_json(conn.send_payload(payload))

    # Solve DLP
    a = discrete_log(p, alice_pubkey, g)
    shared_secret = pow(bob_pubkey, a, p)

    iv = response['iv']
    ciphertext = response['encrypted_flag']

    #####
    print("FLAG:", decrypt_flag(shared_secret, iv, ciphertext))
    conn.close()
