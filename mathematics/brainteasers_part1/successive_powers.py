from sympy.ntheory import factorint

x = 209 
arr = [588,665,216,113,642,4,836,114,851,492,819,237]

n = x * arr[0] - arr[1]
print(max(factorint(n)))

