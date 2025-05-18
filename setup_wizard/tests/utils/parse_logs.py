import json
from collections import defaultdict

'''
This parse logs script is for parsing and comparing different log files and the function parameters and return values.

It was initially generated with Copilot.
'''


def parse_log_file(file_path):
    """
    Parse a log file containing JSON data, extract JSON objects,
    and collect mapping between args and return values.
    """
    json_objects = []
    body_part_mappings = defaultdict(list)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Skip lines that don't contain JSON data
                if ' - INFO - {' not in line:
                    continue

                # Extract JSON part from the line
                json_part = line.split(' - INFO - ', 1)[1].strip()

                try:
                    # Parse the JSON object
                    json_obj = json.loads(json_part)

                    # Store the entire JSON object
                    json_objects.append(json_obj)

                    # Extract data from log_payload
                    log_payload = json_obj.get('log_payload', {})

                    # Check if we have both args and return_value
                    if 'args' in log_payload and log_payload['args'] and 'return_value' in log_payload:
                        # First element in args list
                        body_part = log_payload['args'][0]
                        return_value = log_payload['return_value']

                        # Store the mapping (preserving order and all occurrences)
                        body_part_mappings[body_part].append({
                            'return_value': return_value,
                            'context': {
                                'function': log_payload.get('function', ''),
                                'kwargs': log_payload.get('kwargs', {}),
                                # Add other context fields that might be relevant
                            }
                        })

                except json.JSONDecodeError as e:
                    print(f"JSON parsing error in {file_path}: {e}")
                except Exception as e:
                    print(f"Error processing line in {file_path}: {e}")

        print(f"Successfully processed {file_path}")
        print(f"  - Found {len(json_objects)} JSON objects")
        print(f"  - Found {len(body_part_mappings)} unique body parts")

        return json_objects, body_part_mappings

    except Exception as e:
        print(f"Error opening or reading {file_path}: {e}")
        return [], defaultdict(list)


def process_multiple_log_files(file_paths):
    """Process multiple log files and combine their results."""
    all_json_objects = []
    all_body_part_mappings = defaultdict(list)

    for file_path in file_paths:
        json_objects, body_part_mappings = parse_log_file(file_path)

        all_json_objects.extend(json_objects)

        # Combine mappings from all files
        for body_part, mappings in body_part_mappings.items():
            all_body_part_mappings[body_part].extend(mappings)

    # Get unique return values for each body part
    unique_return_values_by_part = {}
    for body_part, mappings in all_body_part_mappings.items():
        unique_values = set(m['return_value'] for m in mappings)
        unique_return_values_by_part[body_part] = unique_values

    print("\nSummary:")
    print(f"Total JSON objects parsed: {len(all_json_objects)}")
    print(f"Total unique body parts: {len(all_body_part_mappings)}")

    print("\nUnique body parts and their return values:")
    for body_part in sorted(all_body_part_mappings.keys()):
        unique_values = unique_return_values_by_part[body_part]
        print(f"  {body_part}: {len(unique_values)} unique return values")

        # Show the actual values (first 3 to keep output manageable)
        for i, value in enumerate(sorted(unique_values)):
            if i < 3:  # Only show first 3 to avoid excessive output
                print(f"    - {value}")
            elif i == 3:
                print(f"    - ... ({len(unique_values) - 3} more)")
                break

    return all_json_objects, all_body_part_mappings, unique_return_values_by_part


if __name__ == "__main__":
    # List of log files to process
    # TODO: Add your log file paths here
    log_files = [

    ]

    json_objects, body_part_mappings, unique_return_values_by_part = process_multiple_log_files(
        log_files)

    print(body_part_mappings)
    print(unique_return_values_by_part)
