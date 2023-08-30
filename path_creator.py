import time
import keyboard
import pyperclip
import csv
import re
import csv
import pyautogui


def extract_numbers(input_string):
    pattern = r"-?\d+\.\d+"

    numbers = re.findall(pattern, input_string)

    numbers = [float(num) for num in numbers]

    return numbers


def change():
    print("working")
    input_filename = 'copied_values.csv'
    output_filename = 'output.csv'

    with open(input_filename, 'r') as input_file, open(output_filename, 'w', newline='') as output_file:
        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)

        for row in csv_reader:
            if row:
                line = row[0]  # Assuming each line contains a single string

                line = line[1:-1]
                line = line.replace('"', '')
                numbers = extract_numbers(line)
                formatted_line = ','.join([f'{num}' for num in numbers]) + ',0'
                csv_writer.writerow([formatted_line])

    print(f"Processed data with added ',0' and without quotes written to '{output_filename}'.")


def finale():
    print("last")
    input_filename = 'output.csv'
    output_filename = 'second.csv'

    with open(input_filename, 'r') as input_file, open(output_filename, 'w', newline='') as output_file:
        for line in input_file:
            modified_line = line[1:-2]  # Remove first and last characters
            output_file.write(modified_line + '\n')

    print(f"Processed data written to '{output_filename}'.")



def main():
    # Create a CSV file to store the copied values
    change()
    finale()

if __name__ == "__main__":
    main()
