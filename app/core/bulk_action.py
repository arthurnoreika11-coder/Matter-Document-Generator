import csv

def bulk_action(file_path, action):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            // Perform the specified action on each row
            
