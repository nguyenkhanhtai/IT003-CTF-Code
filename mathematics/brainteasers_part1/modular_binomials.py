import math

info = {}

with open("binomial.txt", "r") as f:
    data = f.readlines()
    for line in data:
        line = line.strip()
        components = line.split('=')
        key, value = components[0].strip(), components[1].strip()
        info[key] = int(value)

N = info["N"]
e1 = info["e1"]
e2 = info["e2"]
c1 = info["c1"]
c2 = info["c2"]

d = (pow(c1, e2, N) * pow(7, (e1 * e2), N) - 
     pow(c2, e1, N) * pow(3, (e1 * e2), N)) % N

# d = k * p1^(e1 * e2)

p = math.gcd(d, N)
q = N // p

print("FLAG=crypto{",p,",",q,"}", sep = "")