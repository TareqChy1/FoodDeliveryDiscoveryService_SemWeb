import subprocess
import sys

# Base directory where the scripts are located
base_path = "C:/Users/nushr/Desktop/Semantic_Web/Project/"

# Mapping of steps to file names and descriptions
steps = {
    1: (base_path + 'collect.py', 'Collect information from CoopCycle'),
    2: (base_path + 'query1.py', 'Query restaurants open at a specific date and time'),
    3: (base_path + 'query2.py', 'Query restaurants by location and opening times'),
    4: (base_path + 'query3.py', 'Query restaurants by delivery price'),
    5: (base_path + 'query4.py', 'Rank restaurants by distance or price'),
    6: (base_path + 'query5.py', 'Query restaurants with preferences from RDF URI'),
    7: (base_path + 'query6.py', 'Query with different sets of preferences on LDP'),
    8: (base_path + 'collectShapeValidation.py', 'Collect data with SHACL shape validation'),
    9: (base_path + 'describe.py', 'Set user preferences and publish on LDP')
}

def main():
    while True:  # This will keep the process running until the user decides to exit
        print("Which step do you want to run?")
        for step, (file, desc) in steps.items():
            print(f"{step}: {desc}")

        try:
            choice = int(input("Enter the step number: "))
            if choice in steps:
                file_name = steps[choice][0]
                subprocess.run([sys.executable, file_name], check=True)

                # Ask the user if they want to run another script
                repeat = input("Do you want to run another step? (yes/no): ").strip().lower()
                if repeat != 'yes':
                    break  # Exit the loop if the user does not want to continue
            else:
                print("Invalid step number.")
        except ValueError:
            print("Please enter a valid integer.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the script: {e}")

# Rest of your script remains the same


if __name__ == "__main__":
    main()
