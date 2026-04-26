state = [
    [206, 243, 61, 34],
    [171, 11, 93, 31],
    [16, 200, 91, 108],
    [150, 3, 194, 51],
]

round_key = [
    [173, 129, 68, 82],
    [223, 100, 38, 109],
    [32, 189, 53, 8],
    [253, 48, 187, 78],
]

tam=0
def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            state[i][j]=state[i][j]^round_key[i][j]
add_round_key(state, round_key)
for s1 in state:
    for s2 in s1:
        print(chr(s2),end='')