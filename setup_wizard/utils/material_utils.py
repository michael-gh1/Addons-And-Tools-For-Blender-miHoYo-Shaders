def add_fake_user_to_materials(materials):
    for material in materials:
        if material:
            material.use_fake_user = True
