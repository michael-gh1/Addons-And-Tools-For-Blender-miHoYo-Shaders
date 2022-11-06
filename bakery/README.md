# Bakery (Batch Job Runner)

Welcome to the Bakery!

## Description
The goal of this tool is to execute a set of Operators based on a JSON file configured by the user.

You feed in a recipe and the steps will be executed with your batch of baked items outputted.

## Vision
The user provides a JSON file that contains the Operator to execute and the parameters that need to be supplied.

This is a generic tool and not specific to any particular Blender addon.

Example:

```json
{
    "job": {
        "source_folder": "",
        "output_folder": "",
        "file_extension_search": "fbx",
        "operators": [
            {
                "operator_name": "bpy.ops.abc",
                "parameters": {
                    "file_directory": "a_file_directory"
                }
            },
            {
                "operator_name": "bpy.ops.xyz",
                "parameters": {
                    "filepath": "a_filepath"
                }
            }
        ]
    }
}
```

The goal is for the end user to pass in a JSON file that runs a set of Operators for every folder in a specified directory.
