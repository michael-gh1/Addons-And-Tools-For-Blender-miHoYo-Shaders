# Author: michael-gh1


from pathlib import Path, Path

from setup_wizard.domain.character_types import CharacterType


def get_monster_body_part_name(name):
        if 'Hair' in name:
            return 'Hair'
        elif 'Face' in name:
            return 'Face'
        elif 'Body' in name:
            return 'Body'
        elif 'Dress' in name:
            return 'Dress'  # TODO: Not sure if all 'Dress' are 'Body'
        elif 'None' in name:
            return 'Body'  # TODO: Current assumption/belief all None are Body-type
        else:
            print(f'"Best Guess" attempt made for retrieving mosnter body part name {name}')
            return 'Body'


def get_npc_mesh_body_part_name(material_name):
    if 'Hair' in material_name:
        return 'Hair'
    elif 'Face' in material_name:
        return 'Face'
    elif 'Body' in material_name:
        return 'Body'
    elif 'Dress' in material_name:  # I don't think this is a valid case, either they use Hair or Body textures
        return 'Dress'
    elif 'Item' in material_name:
        item_name = material_name.replace('NPC_', '').replace('_Mat', '')
        return item_name
    elif 'Screw' in material_name:
        return 'Screw'
    elif 'Hat' in material_name:
        return 'Hat'
    elif 'Others' in material_name:
        return 'Others'
    else:
        return None


# TODO: Refactor out of GenshinImpactMaterialDataImporter
def get_body_part(file):
    if 'Monster' in file.name:
        expected_body_part_name = Path(file.name).stem.split('_')[-2]
        body_part = get_monster_body_part_name(Path(file.name).stem.split('_')[-2]) if expected_body_part_name != 'Mat' else get_monster_body_part_name(Path(file.name).stem.split('_')[-1])
    elif 'NPC' in file.name:
        body_part = get_npc_mesh_body_part_name(Path(file.name).stem)
    elif 'Equip' in file.name:
        body_part = 'Body'
    else:
        body_part = Path(file.name).stem.split('_')[-1]
    return body_part


def get_character_type(file):
    if 'Monster' in file.name:
        return CharacterType.MONSTER
    elif 'NPC' in file.name:
        return CharacterType.NPC
    elif 'Equip' in file.name:
        return CharacterType.GI_EQUIPMENT
    else:
        return CharacterType.UNKNOWN  # catch-all, tries default material applying behavior
