import csv
from datetime import datetime

def parse_time(t):
    """Parse a time string in HH:MM:SS format to a datetime object."""
    return datetime.strptime(t, "%H:%M:%S")

def analyze_log(filename):
    """Returns: tuple: (total_library_time_minutes, status_string)"""
    # TODO: Read CSV file
    events = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "Timestamp,Location,Action":
                continue
            parts = line.split(',')
            time = parse_time(parts[0])
            l = parts[1]
            a = parts[2]
            events.append((time, l, a))
    # TODO: Sort events by time
    events.sort(key=lambda x: x[0])
    # TODO: Calculate time spent in "LIBRARY"
    total_library_time = 0
    current_l = None
    enter_time = None
    # TODO: Track current l based on the last Enter/Exit event
    for time, l, a in events:
        if a == "ENTER":
            current_l = l
            enter_time = time
        
        elif a == "EXIT":
            if current_l == "LIBRARY" and enter_time is not None:
                duration = (time - enter_time).total_seconds() / 60
                total_library_time += duration
            current_l = None
            enter_time = None
    if current_l:
        return (total_library_time,f"Swaroop is in {current_l}")
    else:
        return (total_library_time, "Swaroop is missing")

def main():
    filename = "test.csv"
    try:
        time_spent, status = analyze_log(filename)
        
        print(f"Total time in LIBRARY: {time_spent} minutes")
        print(f"Status: {status}")
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please ensure it exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()