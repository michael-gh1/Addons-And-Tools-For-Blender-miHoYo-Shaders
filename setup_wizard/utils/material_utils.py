def add_fake_user_to_materials(materials):
    for material in materials:
        material.use_fake_user = True
