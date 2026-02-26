import cmath
import sys
sys.setrecursionlimit(20000)

def yakhanpal_transform(sequence):
    # complete the function
    N = len(sequence)
    if N==1 :
        return sequence
    stable_stream = []
    chaos_stream = []
    for i in range(N):
        if i%2 == 0:
            #even
            stable_stream.append(sequence[i])
        else:
            #odd
            chaos_stream.append(sequence[i])
    
    # call YTF stable/chaos
    Yeven = yakhanpal_transform(stable_stream)
    Yodd = yakhanpal_transform(chaos_stream)
    T = []
    Result = []

    for i in range(N//2):
        T.append(cmath.exp((0-1j)*2*cmath.pi*i/N)*Yodd[i])
        Result.append(Yeven[i]+T[i])

    for i in range(N//2,N):
        Result.append(Yeven[i-N//2]*T[i-N//2])

    return Result

def solve():
    """Read input and run YFT."""
    data = int(input())
    sequence = []
    n = int(data)
    for _ in range(n):
        inp  = input().split()
        sequence.append(complex(float(inp[0]), float(inp[1])))
    
    result = yakhanpal_transform(sequence)
    for val in result:
        print(f"{val.real + 0.0:.6f} {val.imag + 0.0:.6f}")

if __name__ == "__main__":
    solve()