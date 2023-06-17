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
