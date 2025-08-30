import os
import sys

# Add the src directory to the path so we can import from main.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the generate_report function from main.py
from main import generate_report

if __name__ == "__main__":
    print("Running report generation test...")
    try:
        generate_report()
        print("Report generation completed successfully!")
    except Exception as e:
        print(f"Error during report generation: {e}")
