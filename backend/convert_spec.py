# convert_spec.py
import json
import yaml

JSON_FILE_PATH = 'swagger.json' 
YAML_FILE_PATH = 'swagger.yaml' 


print(f"Reading from {JSON_FILE_PATH}...")
try:
    with open(JSON_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)

    print(f"Writing to {YAML_FILE_PATH}...")
    with open(YAML_FILE_PATH, 'w') as yaml_file:
        yaml.dump(data, yaml_file, sort_keys=False) 

    print("Conversion successful!")

except FileNotFoundError:
    print(f"ERROR: Could not find the file '{JSON_FILE_PATH}'. Make sure it's in the same directory as this script.")
except Exception as e:
    print(f"An error occurred: {e}")