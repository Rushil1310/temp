from partB.q3.main import yakhanpal_transform

if __name__ == "__main__":
    # Test cases
    print("=== Test Case 1 ===")
    test1 = [-2, 2]
    result1 = yakhanpal_transform(test1)
    for v in result1:
        print(f"{v.real + 0.0:.6f} {v.imag + 0.0:.6f}")
    
    print("\n=== Test Case 2 ===")
    test2 = [complex(-0.177, -0.271), complex(0.056, -0.379),
             complex(-0.096, -0.361), complex(0.161, -0.301)]
    result2 = yakhanpal_transform(test2)
    for v in result2:
        print(f"{v.real + 0.0:.6f} {v.imag + 0.0:.6f}")