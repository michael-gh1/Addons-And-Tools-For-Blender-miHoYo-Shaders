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
            return None


def get_npc_mesh_body_part_name(material_name):
    if 'Hair' in material_name:
        return 'Hair'
    elif 'Face' in material_name:
        return 'Face'
    elif 'Body' in material_name:
        return 'Body'
    elif 'Dress' in material_name:  # I don't think this is a valid case, either they use Hair or Body textures
        return 'Dress'
    else:
        return None