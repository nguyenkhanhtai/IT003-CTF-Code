def chinese_remainder_theorem(remainders, moduli):
    total_sum = 0
    prod = 1
    
    # Tính tích của tất cả các module (M = m1 * m2 * ... * mk)
    for mod in moduli:
        prod *= mod

    # Áp dụng công thức tổng CRT
    for a_i, m_i in zip(remainders, moduli):
        M_i = prod // m_i
        # Tìm nghịch đảo module của M_i theo modulo m_i
        y_i = pow(M_i, -1, m_i) 
        total_sum += a_i * M_i * y_i

    return total_sum % prod

# --- Ví dụ sử dụng ---
# Giả sử chúng ta có hệ phương trình:
# x ≡ 2 (mod 3)
# x ≡ 3 (mod 5)
# x ≡ 2 (mod 7)

a = [2, 3, 5]
m = [5, 11, 17]

x = chinese_remainder_theorem(a, m)
print(f"FLAG={x}")