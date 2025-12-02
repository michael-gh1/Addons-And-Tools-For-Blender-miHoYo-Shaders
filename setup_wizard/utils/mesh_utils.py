import bpy


def remove_material_slots(mesh, materials, exclude=False):
    bpy.ops.object.mode_set(mode='OBJECT')
    # Reversing is IMPORTANT in order to avoid index errors while removing during runtime
    for material_slot_material in reversed(mesh.material_slots):
        if (not exclude and material_slot_material.material in materials) or (exclude and material_slot_material.material not in materials):
            mesh.active_material_index = mesh.material_slots.get(material_slot_material.material.name).slot_index
            print(f'Removing material: {material_slot_material.material.name} from {mesh.name}')
            bpy.context.view_layer.objects.active = mesh
            bpy.ops.object.material_slot_remove()
