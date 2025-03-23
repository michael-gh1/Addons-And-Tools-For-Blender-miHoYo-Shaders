import os
import pathlib

# conftest.py - Configuration for pytest
# Ignore files containing "test_" in their name and "logs" directories

collect_ignore = []

def pytest_configure(config):
    """Add files containing 'test_' and 'logs' directories to the ignore list."""
    
    root_dir = pathlib.Path(__file__).parent
    
    for root, dirs, files in os.walk(root_dir):
        # Add "logs" directories to ignore list
        if "logs" in dirs:
            path = os.path.join(root, "logs")
            relative_path = os.path.relpath(path, start=root_dir)
            collect_ignore.append(relative_path)
            dirs.remove("logs")  # Prevent recursion
        
        # Ignore files containing "test_" except if they are in a "unit" directory
        for file in files:
            if "test_" in file and file.endswith(".py"):
                path = os.path.join(root, file)
                relative_path = os.path.relpath(path, start=root_dir)
                path_parts = pathlib.Path(relative_path).parts
                
                # Only ignore if the file is not in a "unit" directory
                if not any(part == "unit" for part in path_parts):
                    collect_ignore.append(relative_path)
