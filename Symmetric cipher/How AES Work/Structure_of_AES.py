def matrix2bytes(matrix):
    return bytes(sum(matrix, []))

state_matrix = [
    [99, 114, 121, 112],
    [116, 111, 123, 105],
    [110, 109, 97, 116],
    [114, 105, 120, 125],
]

plaintext = matrix2bytes(state_matrix)
print(plaintext.decode())