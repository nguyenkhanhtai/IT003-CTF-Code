from PIL import Image
import numpy as np

def xor_images(img1_path, img2_path, output_path):
    print(f"[*] Đang thực hiện XOR: {img1_path} ^ {img2_path}...")

    try:
        # Bước 1: Mở ảnh và chuyển sang chế độ màu RGB
        # .convert('RGB') giúp đảm bảo ảnh không có kênh Alpha (trong suốt), 
        # chỉ có 3 kênh màu (R, G, B) để phép XOR chính xác.
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')

        # Bước 2: Kiểm tra kích thước ảnh
        # Phép XOR từng pixel yêu cầu hai ảnh phải có cùng chiều rộng và chiều cao.
        if img1.size != img2.size:
            print("[-] Lỗi: Hai ảnh không cùng kích thước! Phép XOR sẽ bị lệch.")
            return

        print(f"[+] Kích thước ảnh: {img1.size}")

        # Bước 3: Chuyển ảnh thành mảng dữ liệu Numpy (list các byte)
        # Mỗi mảng sẽ có cấu trúc (chiều cao, chiều rộng, 3), 
        # trong đó 3 là giá trị của 3 kênh màu R, G, B.
        data1 = np.array(img1)
        data2 = np.array(img2)

        # Bước 4: Thực hiện phép toán bitwise XOR
        # Numpy cực kỳ mạnh mẽ, nó sẽ lấy từng byte R của ảnh 1 XOR với byte R của ảnh 2,
        # tương tự cho G và B, trong chớp mắt.
        result_data = data1 ^ data2

        # Bước 5: Chuyển mảng kết quả ngược lại thành đối tượng ảnh của Pillow
        result_img = Image.fromarray(result_data)

        # Bước 6: Lưu ảnh kết quả
        result_img.save(output_path)
        print(f"[+] Thành công! Ảnh kết quả đã được lưu tại: {output_path}")

        # (Tùy chọn) Hiển thị ảnh trực tiếp ra màn hình
        # result_img.show()

    except FileNotFoundError:
        print(f"[-] Lỗi: Không tìm thấy file ảnh. Hãy đảm bảo bạn đã tải 'lemur.png' và 'flag.png' về cùng thư mục với file code này.")
    except Exception as e:
        print(f"[-] Đã xảy ra lỗi không xác định: {e}")

# --- Cách dùng ---
# Hãy đảm bảo bạn có sẵn 2 file lemur.png và flag.png trong cùng thư mục.
file_1 = "lemur.png"
file_2 = "flag.png"
file_output = "xor_result.png"

xor_images(file_1, file_2, file_output)