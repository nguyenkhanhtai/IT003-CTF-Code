import json
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad
from sympy.ntheory import factorint

P = 13322168333598193507807385110954579994440518298037390249219367653433362879385570348589112466639563190026187881314341273227495066439490025867330585397455471
N = 30

def load_matrix(fname):
    data = open(fname, 'r').read().strip()
    rows = [list(map(int, row.split(' '))) for row in data.splitlines()]
    return Matrix(GF(P), rows)

# 1. Load dữ liệu
G = load_matrix("generator.txt")
out_data = json.load(open('output.txt', 'r'))
v = vector(GF(P), out_data['v'])
w = vector(GF(P), out_data['w'])

# print(f"G.dimension = {G.dimensions()}")
# print(f"G = {G[:5,:5]}")
# print(f"v = {v[:5]}")
# print(f"w = {w[:5]}")

# Lấy ma trận Jordan J và P
J, P_mat = G.jordan_form(transformation=True)


P_inv = P_mat.inverse()

v_prime = P_inv * v
w_prime = P_inv * w

SECRET = None
# Duyệt tìm khối Jordan kích thước >= 2 (có số 1 trên đường chéo phụ)
cnt = 0
for i in range(1, N):
    if J[i - 1, i - 1] == J[i, i] and J[i - 1, i] == 1:
        lam = J[i, i]
        
        # Đảm bảo mẫu số khác 0
        if v_prime[i] != 0 and w_prime[i] != 0:
            lam_x = w_prime[i] / v_prime[i]
            x = (w_prime[i - 1] * lam / w_prime[i]) - lam * (v_prime[i - 1] / v_prime[i])
            
            SECRET = int(x)
            print(f"SECRET: {SECRET}")
            break
            
import json
from os import urandom

enc_data = json.load(open('flag.enc', 'r'))
iv = bytes.fromhex(enc_data['iv'])
ciphertext = bytes.fromhex(enc_data['ciphertext'])

KEY_LENGTH = 128
KEY = SHA256.new(data=str(SECRET).encode()).digest()[:KEY_LENGTH]

cipher = AES.new(KEY, AES.MODE_CBC, iv)
flag = unpad(cipher.decrypt(ciphertext), 16)

print(f"FLAG: {flag.decode()}")
