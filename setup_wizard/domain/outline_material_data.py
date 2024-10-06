# Author: michael-gh1

from bpy.types import Material


class OutlineMaterialGroup:
    def __init__(self, material: Material, outlines_material: Material, night_soul_outlines_material: Material = None):
        self.material = material
        self.outlines_material = outlines_material
        self.night_soul_outlines_material = night_soul_outlines_material
