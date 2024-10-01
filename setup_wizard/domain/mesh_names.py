'''
Standardize and document mesh names that come with in each character armature.
'''
class MeshNames:
    BODY = 'Body'
    # HAIR = 'Hair'
    # DRESS = 'Dress'
    # DRESS1 = 'Dress1'
    # DRESS2 = 'Dress2'

    @classmethod
    def get_mesh_names(cls):
        return [value for name, value in cls.__dict__.items() if not name.startswith('__')]
