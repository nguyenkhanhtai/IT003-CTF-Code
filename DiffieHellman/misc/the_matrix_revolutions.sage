import json
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

MODULO = 2

def read_binary_matrix(filepath):

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().strip().splitlines()
    
    matrix_data = [[int(bit) for bit in line] for line in lines]
    return Matrix(GF(MODULO), matrix_data)

def compute_gf2n_dlog(base_poly, target_poly, degree):
    field = GF(2**degree)
    poly_ring.<x> = PolynomialRing(field)

    base_root = base_poly(x).roots()[0][0]
    target_root = target_poly(x).roots()[0][0]

    dlog_val = int(pari(target_root).fflog(pari(base_root)))
    return dlog_val

def generate_frobenius_conjugates(base_dlog, degree):
    period = 2**degree - 1
    return [int(base_dlog * pow(2, i, period)) for i in range(degree)]

def solve_private_key(gen_mat, pub_mat):
    g_factors = list(factor(gen_mat.charpoly()))
    a_factors = list(factor(pub_mat.charpoly()))

    g_poly_61 = next(p for p, m in g_factors if p.degree() == 61)
    a_poly_61 = next(p for p, m in a_factors if p.degree() == 61)
    
    g_poly_89 = next(p for p, m in g_factors if p.degree() == 89)
    a_poly_89 = next(p for p, m in a_factors if p.degree() == 89)

    dlog61 = compute_gf2n_dlog(g_poly_61, a_poly_61, 61)
    dlog89 = compute_gf2n_dlog(g_poly_89, a_poly_89, 89)

    candidates_61 = generate_frobenius_conjugates(dlog61, 61)
    candidates_89 = generate_frobenius_conjugates(dlog89, 89)

    period_61, period_89 = 2**61 - 1, 2**89 - 1

    for c61 in candidates_61:
        for c89 in candidates_89:
            priv_candidate = crt([c61, c89], [period_61, period_89])
            
            if is_prime(priv_candidate) and gen_mat^priv_candidate == pub_mat:
                return priv_candidate
    return None

def hash_matrix_to_key(matrix_obj):
    matrix_string = ''.join(str(val) for row in matrix_obj for val in row)
    return SHA256.new(data=matrix_string.encode('utf-8')).digest()

def decrypt_flag(aes_key, enc_filepath='flag.enc'):
    with open(enc_filepath, 'r', encoding='utf-8') as f:
        enc_data = json.load(f)
    
    cipher = AES.new(aes_key, AES.MODE_CBC, bytes.fromhex(enc_data['iv']))
    decrypted_bytes = cipher.decrypt(bytes.fromhex(enc_data['ciphertext']))
    return decrypted_bytes.decode('utf-8', errors='ignore')

if __name__ == "__main__":
    G_matrix = read_binary_matrix('generator.txt')
    Alice_public = read_binary_matrix('alice.pub')
    Bob_public = read_binary_matrix('bob.pub')

    alice_secret_key = solve_private_key(G_matrix, Alice_public)
    print(f"Private Key= {alice_secret_key}")

    shared_matrix = Bob_public^alice_secret_key
    aes_symmetric_key = hash_matrix_to_key(shared_matrix)

    flag = decrypt_flag(aes_symmetric_key)
    print(f"Flag={flag}")