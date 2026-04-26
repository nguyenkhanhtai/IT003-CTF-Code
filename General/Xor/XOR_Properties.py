key1 = 0xa6c8b6733c9b22de7bc0253266a3867df55acde8635e19c73313
key2_key3 = 0xc1545756687e7573db23aa1c3452a098b71a7fbf0fddddde5fc1
flag_xor_all = 0x04ee9855208a2cd59091d04767ae47963170d1660df7f56f5faf
flag_int = flag_xor_all ^ key1 ^ key2_key3
flag_hex = hex(flag_int)[2:]
flag = bytes.fromhex(flag_hex).decode()

print(flag)