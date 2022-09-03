# Blender miHoYo Shaders - Setup Wizard Tool

> You should view this on Github or some other Markdown reader if you aren't!

The goal of this tool is to streamline the character setup process. Whether it's importing the materials, importing the character model, setting up the outlines (geometry nodes) or configuring the outline colors to be game accurate, this tool has got it all! Your one-stop-shop for setting up your characters in Blender!

**Important**: This tool is intended to be used with Festivity's shaders, found here: https://github.com/festivize/Blender-miHoYo-Shaders

## Table of Contents
1. [Tutorials/Screenshots](#demoscreenshots)
2. [Quick Start Guide](#quick-start-guide)
3. [How to Disable Components](#how-to-disable-components-on-the-ui)
4. [Features/Components](#featurescomponents)
5. [Steps (Detailed Guide)](#steps-detailed-guide)
6. [Development Roadmap/Future Features](#development-roadmap--future-features)
7. ["Tested" Character Models](#tested-character-models)
8. [Credits](#credits)

## Demo/Screenshots
### Screenshot of the Tool

![alt text](https://cdn.discordapp.com/attachments/890116796034711595/1014970456572436530/unknown.png)

### Tutorials

Download Tutorials:
- Installation and "One Click" Simplified Setup (First Time Setup, No Cached Data) 
  - https://cdn.discordapp.com/attachments/1015585109639974922/1015585432026763284/SetupWizardUI_v1-0_Installation_and_Simplified_Setup.mp4
- 4 Step Menu: Basic Setup (First Time Setup, No Cached Data)
  - https://cdn.discordapp.com/attachments/1015585109639974922/1015587153058746499/SetupWizardUI_v1-0_Basic_Setup_-_No_Cache.mp4
- 4 Step Menu: Basic Setup (Post-First Time Setup, with Cached Data)
  - https://cdn.discordapp.com/attachments/1015585109639974922/1015587226752659556/SetupWizardUI_v1-0_Basic_Setup_with_Cache.mp4
- Advanced Setup (Post-First Time Setup, with Cached Data)
  - https://cdn.discordapp.com/attachments/1015585109639974922/1015587532362223698/SetupWizardUI_v1-0_Advanced_Setup_with_Cache.mp4





## Quick Start Guide
1. Go to the Releases page and download the latest `Setup_Wizard_UI_Addon.zip`
2. Open Blender (new file or one with no models)
3. Install the Setup Wizard
    * Edit > Preferences > Install > Select `Setup_Wizard_UI_Addon.zip`
4. Open up the N-Panel (Hit the 'N' key)
5. Select the `Genshin` tab
6. Click the `Run Entire Setup` button
    * Outlines are supported for Blender Version >= 3.3 (you can either disable the outline-related components or use the Basic Setup instead)
7. Select the folder with the character model and textures (lightmaps, diffuses, etc.)
8. Select the root/base folder with Festivity's Shaders 
    * **This only needs to be done the first time you run this tool.** This is because the filepath gets cached for future usage (click the clear cache button if you want to reset this value).
    * Double click to navigate inside the folder to select it, do not select a specific file inside!
    * Ex. My shaders are in a folder called `Blender-miHoYo-Shaders`
9. Select the `miHoYo - Outlines.blend` file (located in Festivity's Shaders `experimental-blender-3.3` folder)
    * **This only needs to be done the first time you run this tool.** This is because the filepath gets cached for future usage (click the clear cache button if you want to reset this value).
    * Ex. `Blender-miHoYo-Shaders/experimental-blender-3.3/miHoYo - Outlines.blend`
10. Select the material data JSON files for the outlines
    * Shift+Click or Ctrl+Click the JSON files that you want to use (normally all of them)

> **Do you use BetterFBX? Don't want to use FBX's standard import?** <br>
> No problem! You can run the individual steps for `Set Up Character Menu` under the `Advanced Setup` section.

## How to Disable Components on the UI
This tool is broken up into many different components. The `config_ui.json` file can be used to enable or disable specific steps when running the `Run Entire Setup` or `Basic Setup`.

Example of Disabling Outlines from `Run Entire Setup`:
```
        "GENSHIN_OT_setup_wizard_ui": [
            "IMPORTANT_PLACEHOLDER_VALUE_KEEP_INDEX_ABOVE_0_setup_wizard_ui",
            "import_character_model", 
            "delete_empties",
            "import_materials",
            "replace_default_materials",
            "import_character_textures",
            "fix_transformations",
            "setup_head_driver",
            "set_color_management_to_standard",
            "delete_specific_objects"
        ],
```

In the example above, these were removed from the original `config_ui.json`:
```
            "import_outlines",
            "setup_geometry_nodes",
            "import_outline_lightmaps",
            "import_material_data",
```

You can disable any step (component) in the Setup Wizard UI by removing the step from the list in `config_ui.json`.
* This may be handy in the scenario that you use BetterFBX or are not on a Blender version that works with Outlines/Geometry Nodes.

<br>

You can disable the cache for any step by unchecking the `Cache Enabled` checkbox.
* The cache (`cache.json.tmp`) is used to "save" your previous choice for future usage that uses the same folder/file
    * Character Model Filepath
        * Saves the character model folder file path selected
        * You may want to disable the cache if you are importing textures that are different from the character model (not the usual workflow)
        * Used when importing textures and outline lightmaps
    * Festivity Root/Base Folder File Path
        * Saves the file path to Festivity's shaders folder
        * Used when importing materials from `miHoYo - Genshin Impact.blend`
    * Festivity Outlines File Path
        * Saves the file path to Festivity's Outlines blend file
        * Used when importing outlines from `miHoYo - Outlines.blend`


### Other Notes:
* The `component_name` or names in the `config.json` or `config_ui.json` should NOT be renamed. This is how the Setup Wizard identifies and triggers the next step/component.
* Metadata found in `config.json` is simply there to help provide human readable information and what each component requires (what should be selected on the file explorer window). (`config.json` is used by the Legacy Setup Wizard which is run through the F3 search)

## Features/Components

> Note: Ideally these steps won't change too much between releases! If they do, I will make note of it in the release notes.

0. ~~Setup Wizard~~ (Legacy)
1. Import Character Model
2. Delete Empties
3. Import Materials (`miHoYo - Genshin Impact.blend`)
4. Replace/Re-Assign Default Character Model Materials (and rename)
5. Import Character Textures
6. Import Outlines (`miHoYo - Outlines.blend`)
7. Setup Outlines (Geometry Nodes)
8. Import Lightmaps for Outlines
9. Import Material Data
10. ~~Fix Mouth Outlines~~ - (Legacy, may return in future releases) **[Disabled by Default]** 
11. Fix Transformations on the Character
12. Setup Head Driver
13. Set Color Management to 'Standard'
14. Delete EffectMesh


## Steps (Detailed Guide)
<details>
    <summary>Expand</summary>
    <br>

> Note: Ideally these steps won't change too much between releases! If they do, I will make note of it in the release notes.

0. ~~Setup Wizard~~ (Legacy)
    * This step starts the Setup Wizard process. It also is **very important** for setting up the Python paths so that the scripts can import dependencies and other scripts.
    * If you are running into an error about `invoke_next_step`, this is likely your issue. You only need to run this step for the Setup Wizard and then you can close out of the File Explorer window.
    * Select the root folder that contains Festivity's Shaders
        * Cache not enabled in this step in case you run it only to set up your `sys.path`/Python path)
1. Import Character Model
    * This step will: 
        * Import the character model which should be a .fbx file
        * Hide EffectMesh (gets deleted in a later step) and EyeStar
        * Add 'UV1' UV Map to ALL meshes (I think the important one is just Body though?)
        * Resets the location and rotation bones in pose mode and sets the armature into an A-pose (this is is done because we import with `force_connect_children`)
        * Connects the Normal Map if the texture exists for the character model
    * Select the folder that contains the character model and textures. **It is assumed that the textures for the character are also in this folder.**
2. Delete Empties
    * This step deletes Empty type objects in the scene
    * No selection needed.
3. Import Materials
    * This step imports `miHoYo - Genshin Hair`, `miHoYo - Genshin Face`, `miHoYo - Genshin Body` and `miHoYo - Genshin Outlines`.
    * **This step uses the cache (if enabled)** so you do not need to re-select the `miHoYo - Genshin Impact.blend` after selecting it on first use.
    * Select the root folder that contains Festivity's Shaders.
4. Replace Default Character Model Materials (and rename)
    * This step replaces/re-assigns the default character model materials to the shader's materials.
    * Naming Convention of Genshin Materials (and their Shader nodes): `miHoYo - Genshin {Body Part}` 
        * `{Body Part}` can be `Hair`, `Body`, `Dress`, `Dress1`, `Dress2`, etc.
    * Yes, this tool also handles special exceptions for characters like: `Yelan`, `Collei` and `Rosaria` who may have their `Dress` set to `Hair` instead of the usual `Body`.
    * No selection needed.
5. Import Character Textures
    * This step imports the character textures and assigns them to the materials imported in Step `Import Materials`.
    * Yes, this tool also handles special exceptions for characters like: `Yelan`, `Collei` and `Rosaria` who may have their `Dress` set to `Hair` instead of the usual `Body`.
    * **This step uses the cache (if enabled)** so you do not need to select a folder. It uses what was selected in Step `Import Character Model` (unless you've disabled it).
6. Import `miHoYo - Outlines`
    * This step imports the `miHoYo - Outlines` node group, which is found in the `experimental-blender-3.3` folder.
    * Select the `miHoYo - Outlines.blend` file.
    * **This step uses the cache (if enabled)** so you do not need to re-select the `miHoYo - Outlines.blend` after selecting it on first use.
7. Setup Outlines (Geometry Nodes)
    * This step creates and sets up the Outlines (Geometry Nodes modifier)
    * Naming Convention of Geometry Nodes: `GeometryNodes {Mesh Name}`
        * {Mesh Name} can be `Body`, `Face`, `Face_Eye`, `Brow` (`Face_Eye` and `Brow` don't really get used though and `Face_Eye` has Outline Thickness set to 0.0 by default)
    * Naming Convention of Outline Materials: `miHoYo - Genshin {Body Part} Outlines`
        * `{Body Part}` can be `Hair`, `Body`, `Dress`, `Dress1`, `Dress2`, etc.
    * No selection needed.
8. Import Lightmaps for Outlines
    * This step imports Lightmap textures and assigns them to to materials.
    * Yes, this tool also handles special exceptions for characters like: `Yelan`, `Collei` and `Rosaria` who may have their `Dress` set to `Hair` instead of the usual `Body`.
    * **This step uses the cache (if enabled)** so you do not need to select a folder. It uses what was selected in Step `Import Character Model` or Step `Import Character Textures` (unless you've disabled them).
9. Import Material Data
    * This step imports JSON files containing material data with useful information for shader accuracy, such as specular colors, metalmap scale, metallic colors, outline colors, shininess values, etc.
    * Select the JSON files with the material data (Ctrl + Click or Shift + Click).
10. ~~Fix Mouth Outlines~~ (Legacy, may be return in future releases) - **[Disabled by Default]**
    * This step "fixes" outlines on the mouth (Face) by assigning a Camera to the geometry node and setting Depth Offset. You will likely need to manually change the Depth Offset depending on your scene.
    * This step may not be needed if you use BetterFBX to import your model (not confirmed).
11. Delete Specific Objects
    * This step deletes specific object(s) which is only EffectMesh at this time.
    * No selection needed.
12. Make Character Upright
    * This step will reset the rotation and scale of the character armature and set the character armature to 90 degrees on the x-axis (standing upright).
    * No selection needed.
13. Set Color Management to 'Standard'
    * This step will set the Color Management to Standard (normally Filmic)
    * No selection needed.
14. Setup Head Driver
    * This step will setup the Head Driver constraint so that face shadows work
    * No selection needed.
</details>

<br>

## Development Roadmap / Future Features
### Features
- [X] Head Driver Setup
- [X] Make model upright if not upright (?)
- [X] ~~Scale up x100~~ Reset Scale (scaled to 1.0)
- [X] Character Ramp Type Mapping (automatically plug correct Body Ramp Type from Global Material Properties)
    - Requires knowing all characters who have a different the Body Ramp Type than the default
- [X] BetterFBX Support/Fix UV map imports (only one UV map is imported)
    - Created UV1 UV map which allows for underskirt textures (Zhongli, Lumine, etc.)
    - No BetterFBX support still at this time though... 
- [X] Color Management Filmic -> Standard
- [X] Turn Setup Wizard into an Addon
- [X] UI Setup Wizard Addon
- [ ] Update Configuration from UI (checkboxes that enable/disable steps)
### Refactoring
- [X] Refactor Material Assignment Mapping (externalize/centralize it to one locaiton)
- [ ] Refactor Import Outline Lightmaps component
- [ ] Refactor config.json from a dictionary to a List of dictionaries?
- [ ] Cache Service
- [ ] Invoker Class
- [ ] import_order.py is becoming too big
- [ ] invoke_next_step may not need to cache anymore since we can cache directly in Operators
### Misc.
- [X] Crude design diagram depicting how this tool and the components interact and work
- [ ] A refreshed design diagram with the UI Addon flow

(Legacy Setup Wizard Flow)
![alt text](https://user-images.githubusercontent.com/8632035/183316362-8a47f471-0fa4-4a3d-8e17-ea2c2a9a852e.png)

## "Tested" Character Models
The models below should not throw errors when running the Setup Wizard.
- Amber
- Alhaitham
- Collei
- Dori
- Hu Tao
- Kamisato Ayato
- Keqing
- Lumine
- Nahida
- Nilou
- Rosaria
- Tighnari
- Yelan

#

## Credits

Thanks to all those who helped answer the questions I had while building out this tool and learning about Blender.
<br>
Shoutout to @Festivity, @TheyCallMeSpy, @Sultana, @M4urlcl0 and @Modder4869!

Cheers and Happy Blending,

~Mken
