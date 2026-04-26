def word(x):
    return x % (2 ** 32)

def inv_rotate(x, n):
    # Dịch vòng phải n bit (tương đương dịch trái 32 - n bit)
    return ((x >> n) & 0xffffffff) | ((x << (32 - n)) & 0xffffffff)

def inv_quarter_round(x, a, b, c, d):
    # Đảo ngược bước 4 của quarter_round
    x[b] = inv_rotate(x[b], 7)
    x[b] ^= x[c]
    x[c] = word(x[c] - x[d])

    # Đảo ngược bước 3 của quarter_round
    x[d] = inv_rotate(x[d], 8)
    x[d] ^= x[a]
    x[a] = word(x[a] - x[b])

    # Đảo ngược bước 2 của quarter_round
    x[b] = inv_rotate(x[b], 12)
    x[b] ^= x[c]
    x[c] = word(x[c] - x[d])

    # Đảo ngược bước 1 của quarter_round
    x[d] = inv_rotate(x[d], 16)
    x[d] ^= x[a]
    x[a] = word(x[a] - x[b])

def inv_inner_block(state):
    # Gọi inv_quarter_round theo thứ tự ngược từ dưới lên so với _inner_block
    inv_quarter_round(state, 3, 4, 9, 14)
    inv_quarter_round(state, 2, 7, 8, 13)
    inv_quarter_round(state, 1, 6, 11, 12)
    inv_quarter_round(state, 0, 5, 10, 15)
    inv_quarter_round(state, 3, 7, 11, 15)
    inv_quarter_round(state, 2, 6, 10, 14)
    inv_quarter_round(state, 1, 5, 9, 13)
    inv_quarter_round(state, 0, 4, 8, 12)

# --- PHẦN THỰC THI KIỂM TRA TRÊN DỮ LIỆU ---

def recover_initial_state(msg, msg_enc):
    # 1. Trích xuất 64 byte đầu tiên do state chỉ chứa 16 word (16 * 4 = 64 bytes)
    m_block = msg[:64]
    c_block = msg_enc[:64]
    
    # 2. XOR ngược (bản mã XOR bản rõ) để lấy mảng byte trạng thái ở cuối chu trình
    keystream_bytes = b''.join([bytes([x ^ y]) for x, y in zip(m_block, c_block)])
    
    # 3. Chuyển chuỗi byte thành mảng 16 số nguyên (word)
    state = [int.from_bytes(keystream_bytes[i:i+4], 'little') for i in range(0, 64, 4)]
    
    # 4. Thực hiện nghịch đảo lại 10 vòng inner block
    for _ in range(10):
        inv_inner_block(state)
        
    return state

if __name__ == '__main__':
    # Dữ liệu mẫu giả định từ kết quả in ra của file đề bài
    msg_hex = b'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula.'.hex()
    msg_enc_hex = "f3afbada8237af6e94c7d2065ee0e221a1748b8c7b11105a8cc8a1c74253611c94fe7ea6fa8a9133505772ef619f04b05d2e2b0732cc483df72ccebb09a92c211ef5a52628094f09a30fc692cb25647f" # Chèn hex của msg_enc thu được từ server vào đây
    print(64*2)
    msg = bytes.fromhex(msg_hex)
    msg_enc = bytes.fromhex(msg_enc_hex) # Dữ liệu thực tế khi chạy
    
    # Do tôi không có chuỗi msg_enc thực tế sinh ra từ key ngẫu nhiên của bạn, 
    # hàm này sẽ trả về mảng state nguyên thủy khi bạn nạp đủ đầu vào.
    initial_state = recover_initial_state(msg, msg_enc)
    print([hex(w) for w in initial_state])