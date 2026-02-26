from swaroop_tracker import analyze_log

def main():
    filename = "swaroop_logs.csv"
    try:
        expected_time = 75
        expected_status = "Swaroop is in LIBRARY"
        
        time_spent, status = analyze_log(filename)
        
        print(f"Total time in LIBRARY: {time_spent} minutes")
        print(f"Status: {status}")
        
        if time_spent == expected_time and status == expected_status:
            print("\nSUCCESS: All checks passed!")
        else:
            print("\nFAIL: Output incorrectly matches expected results.")
            print(f"Expected: Time={expected_time}, Status='{expected_status}'")
            print(f"Got:      Time={time_spent}, Status='{status}'")
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please ensure it exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()