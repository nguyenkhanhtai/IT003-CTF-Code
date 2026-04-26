import requests

BASE_URL = "https://aes.cryptohack.org/bean_counter"

print("[*] Đang tải bản mã (ciphertext) từ server...")
res = requests.get(f"{BASE_URL}/encrypt/").json()
ciphertext_hex = res["encrypted"]
ciphertext_bytes = bytes.fromhex(ciphertext_hex)

# 16 byte bản rõ cố định của mọi file PNG (Signature + IHDR length + "IHDR")
# 89504E470D0A1A0A: PNG Signature
# 0000000D: Độ dài chunk IHDR (13 bytes)
# 49484452: Chữ "IHDR" trong mã ASCII
png_header_hex = "89504e470d0a1a0a0000000d49484452"
png_header_bytes = bytes.fromhex(png_header_hex)

print("[*] Đang trích xuất 16 byte Keystream bí mật...")
first_16_bytes_ct = ciphertext_bytes[:16]

# KPA: Keystream = Ciphertext XOR Plaintext
keystream = bytearray()
for b1, b2 in zip(first_16_bytes_ct, png_header_bytes):
    keystream.append(b1 ^ b2)

print(f"    -> Keystream xịn thu được (Hex): {keystream.hex()}")

print("[*] Đang tiến hành giải mã toàn bộ bức ảnh...")
out_bytes = bytearray()

# Do lỗi của lập trình viên (IV không bao giờ tăng), Keystream này lặp lại cho TẤT CẢ các block
for i in range(0, len(ciphertext_bytes), 16):
    block = ciphertext_bytes[i:i+16]
    
    decrypted_block = bytearray()
    for b1, b2 in zip(block, keystream):
        decrypted_block.append(b1 ^ b2)
        
    out_bytes.extend(decrypted_block)

# Lưu kết quả thành file ảnh nhị phân
output_filename = "final_flag.png"
with open(output_filename, "wb") as f:
    f.write(out_bytes)

print(f"\n[+] BÙM! Giải mã hoàn tất. Dữ liệu đã được ghi ra file: {output_filename}")