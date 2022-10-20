# Automated End-To-End Tests

An automated test which will spawn ONE blender instance to drive the tests (technically unnecessary). The initial blender instance will then:
1. Create a new blender instance
2. Run the Setup Wizard on a character
3. Close the blender instance. 

It will repeat that for all characters found in the `characters_folder_file_path` in `config.json`.

Please review `config.json.sample` for the configuration values that need to be supplied to run the automated tests.


## Run Tests in Foreground:
```
"blender.exe" --python setup_wizard/tests/test_driver.py
```


## Run Tests in Background:
```
"blender.exe" -b --python setup_wizard/tests/test_driver.py
```

## How To Exit/Kill Test Process
```
Ctrl + C
```
(do this twice)