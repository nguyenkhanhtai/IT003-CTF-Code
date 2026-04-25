p=29
ints=[14,6,11]
mn = 1e9
for x in ints:
    for y in range(29):
        if ((y * y) % 29 == x):
            print(f"{y} là modular root của {x} modulo {p}")
            mn = min(mn, y)

print("FLAG:", mn)

        