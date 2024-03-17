# Author: michael-gh1


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
        return 'Item'
    elif 'Screw' in material_name:
        return 'Screw'
    elif 'Hat' in material_name:
        return 'Hat'
    else:
        return None
