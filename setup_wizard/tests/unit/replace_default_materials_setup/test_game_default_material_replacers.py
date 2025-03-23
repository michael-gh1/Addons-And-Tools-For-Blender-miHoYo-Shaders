import pytest
import sys
from unittest.mock import MagicMock, call, patch, ANY

# Create mock bpy module with all necessary components
def setup_mock_bpy():
    mock_bpy = MagicMock()
    mock_types = MagicMock()
    
    # Create specific classes needed
    mock_types.Context = type('Context', (), {})
    mock_types.Operator = type('Operator', (), {})
    
    # Setup data structures
    mock_data = MagicMock()
    mock_data.materials = MagicMock()
    mock_data.materials.get = MagicMock(return_value=MagicMock())
    
    # Attach to bpy mock
    mock_bpy.types = mock_types
    mock_bpy.data = mock_data
    mock_bpy.context = MagicMock()
    
    # Add to sys.modules to make imports work
    sys.modules['bpy'] = mock_bpy
    sys.modules['bpy.types'] = mock_types

# Run this before any tests execute
setup_mock_bpy()


import bpy

from setup_wizard.texture_import_setup.texture_importer_types import TextureImporterType
from setup_wizard.domain.shader_material_name_keywords import ShaderMaterialNameKeywords
from setup_wizard.replace_default_materials_setup.game_default_material_replacers import GenshinImpactDefaultMaterialReplacer
from setup_wizard.domain.shader_node_names import V4_PrimoToonShaderNodeNames
from setup_wizard.domain.shader_material_names import V4_PrimoToonGenshinImpactMaterialNames
from setup_wizard.domain.star_cloak_types import StarCloakTypes

class TestGenshinImpactDefaultMaterialReplacer:
    @pytest.fixture
    def mock_blender_operator(self):
        operator = MagicMock()
        operator.report = MagicMock()
        return operator
    
    @pytest.fixture
    def mock_context(self):
        return MagicMock()
    
    @pytest.fixture
    def material_names(self):
        return V4_PrimoToonGenshinImpactMaterialNames
    
    @pytest.fixture
    def shader_node_names(self):
        return V4_PrimoToonShaderNodeNames
    
    @pytest.fixture
    def replacer(self, mock_blender_operator, mock_context, material_names, shader_node_names):
        return GenshinImpactDefaultMaterialReplacer(mock_blender_operator, mock_context, material_names, shader_node_names)

    @patch('bpy.data.materials.get')  # The order of these patches is important! More specific first
    @patch('bpy.data.materials')
    def test_replace_default_materials(self, mock_materials_list, mock_materials_get, replacer, mock_blender_operator):
        # Setup scene with test meshes and materials
        mesh1 = MagicMock(name="test_mesh1")
        mesh1.type = 'MESH'
        mesh1.name = "Body_Mesh"
        
        material_slot_body = MagicMock()
        material_slot_body.name = "Avatar_Mat_Body"
        
        material_slot_hair = MagicMock()
        material_slot_hair.name = "Avatar_Mat_Hair"

        material_slot_dress = MagicMock()
        material_slot_dress.name = "Avatar_Mat_Dress"

        material_slot_cloak = MagicMock()
        material_slot_cloak.name = "Avatar_Dainsleif_Mat_Cloak"

        material_slot_skillobj = MagicMock()
        material_slot_skillobj.name = "SkillObj_Test_Glass_Mat"
        
        material_slot_npc_hair = MagicMock()
        material_slot_npc_hair.name = "NPC_Hair_Mat"

        material_slot_npc_face = MagicMock()
        material_slot_npc_face.name = "NPC_Face_Mat"

        material_slot_npc_body = MagicMock()
        material_slot_npc_body.name = "NPC_Body_Mat"

        material_slot_npc_item = MagicMock()
        material_slot_npc_item.name = "NPC_Item_Mat"

        material_slot_npc_screw = MagicMock()
        material_slot_npc_screw.name = "NPC_Screw_Mat"

        material_slot_npc_hat = MagicMock()
        material_slot_npc_hat.name = "NPC_Hat_Mat"

        material_slot_npc_others = MagicMock()
        material_slot_npc_others.name = "NPC_Others_Mat"

        material_slot_npc_cloak = MagicMock()
        material_slot_npc_cloak.name = "NPC_Paimon_Cloak_Mat"
        
        material_slot_monster_hair = MagicMock()
        material_slot_monster_hair.name = "Monster_Hair_Mat"

        material_slot_monster_face = MagicMock()
        material_slot_monster_face.name = "Monster_Face_Mat"

        material_slot_monster_body = MagicMock()
        material_slot_monster_body.name = "Monster_Body_Mat"

        material_slot_monster_other = MagicMock()
        material_slot_monster_other.name = "Monster_Other_Mat"
    
        
        material_slot_mihoyo = MagicMock()
        material_slot_mihoyo.name = "miHoYoDiffuse"
        
        mesh1.material_slots = [
            material_slot_body, 
            material_slot_hair, 
            material_slot_dress,
            material_slot_cloak,
            material_slot_skillobj,
            material_slot_npc_body,
            material_slot_npc_face,
            material_slot_npc_hair,
            material_slot_npc_item,
            material_slot_npc_screw,
            material_slot_npc_hat,
            material_slot_npc_others,
            material_slot_npc_cloak,
            material_slot_monster_hair,
            material_slot_monster_face,
            material_slot_monster_body,
            material_slot_monster_other,
            material_slot_mihoyo
        ]
        
        # Directly modify the bpy.context.scene.objects in the mock
        bpy.context.scene = MagicMock()
        bpy.context.scene.objects = [mesh1]

        # Material Node Tree Mocking
        # Create mock for node_tree and the complex path to image.name_full
        mock_node_tree = MagicMock()
        mock_principled_node = MagicMock()
        mock_input = MagicMock()
        mock_link = MagicMock() 
        mock_from_node = MagicMock()
        mock_image = MagicMock()
        
        # Set the image name
        # mock_image.name_full = "Avatar_Lady_Pole_Rosaria_Tex_Body_Diffuse.png"
        mock_image.name_full = "Avatar_Girl_Undefined_Skirk_Tex_Effect_Diffuse.png"
        
        # Build the chain
        mock_from_node.image = mock_image
        mock_link.from_node = mock_from_node
        mock_input.links = [mock_link]
        
        # Setup dictionary-like access for inputs
        def input_getitem(self, key):
            if key == 'Base Color':
                return mock_input
            return MagicMock()
        mock_principled_node.inputs = MagicMock()
        mock_principled_node.inputs.__getitem__ = input_getitem
        
        # Setup dictionary-like access for nodes
        def node_getitem(self, key):
            if key == 'Principled BSDF':
                return mock_principled_node
            return MagicMock()
        mock_node_tree.nodes = MagicMock()
        mock_node_tree.nodes.__getitem__ = node_getitem
        # End Material Node Tree Mocking'

        # Setup material mocks
        mock_body_material = MagicMock(name="body_material")
        mock_face_material = MagicMock(name="face_material")
        mock_hair_material = MagicMock(name="hair_material")
        mock_dress_material = MagicMock(name="dress_material")
        mock_cloak_material = MagicMock(name="cloak_material")
        mock_item_material = MagicMock(name="item_material")
        mock_screw_material = MagicMock(name="screw_material")
        mock_hat_material = MagicMock(name="hat_material")
        mock_others_material = MagicMock(name="others_material")
        mock_cloak_material = MagicMock(name="cloak_material")
        mock_glass_material = MagicMock(name="glass_material")
        mock_vfx_material = MagicMock(name="vfx_material")

        
        # Attach to material
        mock_dress_material.node_tree = mock_node_tree


        # Material.get() returns corresponding materials
        def material_get_side_effect(name):
            material_map = {
                f'{replacer.material_names.MATERIAL_PREFIX}Body': mock_body_material,
                f'{replacer.material_names.MATERIAL_PREFIX}Face': mock_face_material,
                f'{replacer.material_names.MATERIAL_PREFIX}Hair': mock_hair_material,
                f'{replacer.material_names.MATERIAL_PREFIX}{material_slot_npc_item.name}': mock_item_material,
                f'{replacer.material_names.MATERIAL_PREFIX}{material_slot_npc_screw.name}': mock_screw_material,
                f'{replacer.material_names.MATERIAL_PREFIX}{material_slot_npc_hat.name}': mock_hat_material,
                f'{replacer.material_names.MATERIAL_PREFIX}{material_slot_npc_others.name}': mock_others_material,
                f'{replacer.material_names.MATERIAL_PREFIX}{material_slot_npc_cloak.name}': mock_cloak_material,
                f'{replacer.material_names.MATERIAL_PREFIX}Glass': mock_glass_material,
                f'{replacer.material_names.MATERIAL_PREFIX}VFX': mock_vfx_material,
            }
            return material_map.get(name, None)
        mock_materials_get.side_effect = material_get_side_effect

        # Setup mock_materials_list to be properly iterable
        mock_materials_list.__iter__.return_value = iter([
            mock_body_material,
            mock_hair_material,
            mock_glass_material,
            mock_vfx_material,
            mock_dress_material
        ])
        
        # Add .name attribute to each mock material
        mock_body_material.name = material_slot_body.name
        mock_face_material.name = material_slot_npc_face.name
        mock_hair_material.name = material_slot_hair.name
        mock_dress_material.name = material_slot_dress.name
        mock_cloak_material.name = material_slot_cloak.name
        mock_item_material.name = material_slot_npc_item.name
        mock_screw_material.name = material_slot_npc_screw.name
        mock_hat_material.name = material_slot_npc_hat.name
        mock_others_material.name = material_slot_npc_others.name
        mock_cloak_material.name = material_slot_npc_cloak.name
        mock_glass_material.name = material_slot_skillobj.name
        mock_vfx_material.name = material_slot_skillobj.name

        # Mock helper methods
        with patch.object(replacer, '_GenshinImpactDefaultMaterialReplacer__set_glass_star_cloak_toggle') as mock_set_star_cloak_toggle, \
            patch.object(replacer, '_GenshinImpactDefaultMaterialReplacer__set_star_cloak_type') as mock_set_star_cloak_type:
            
            # For Dress material, mock return a VFX material
            mock_vfx_material.name = f'{replacer.material_names.STAR_CLOAK}'
            
            # Execute function being tested
            replacer.replace_default_materials()
            
            # Assertions
            mock_blender_operator.report.assert_any_call({'INFO'}, 'Replaced default materials with Genshin shader materials...')
            
            # Check regular material replacement
            assert material_slot_body.material == mock_body_material
            assert material_slot_hair.material == mock_hair_material
            
            # Check SkillObj material handling
            material_slot_skillobj.material = mock_glass_material
            
            # Check NPC material handling
            assert material_slot_npc_body.material == mock_body_material
            assert material_slot_npc_face.material == mock_face_material
            assert material_slot_npc_hair.material == mock_hair_material
            assert material_slot_npc_item.material == mock_item_material
            assert material_slot_npc_screw.material == mock_screw_material
            assert material_slot_npc_hat.material == mock_hat_material
            assert material_slot_npc_others.material == mock_others_material
            
            # Check Monster material handling
            assert material_slot_monster_hair.material == mock_hair_material
            assert material_slot_monster_face.material == mock_face_material
            assert material_slot_monster_body.material == mock_body_material
            assert material_slot_monster_other.material == mock_body_material
            
            # Check Dress/VFX/StarCloak handling
            assert mock_set_star_cloak_toggle.call_count == 3
            mock_set_star_cloak_toggle.assert_called_with(ANY, True)
            material_arg = mock_set_star_cloak_toggle.call_args[0][0]  # Get the first argument
            assert material_arg.name == replacer.material_names.STAR_CLOAK

            assert mock_set_star_cloak_type.call_count == 3
            expected_calls = [
                call(ANY, 'Avatar_Mat_Dress'),
                call(ANY, 'Avatar_Dainsleif_Mat_Cloak'),
                call(ANY, 'NPC_Paimon_Cloak_Mat'),
            ]
            mock_set_star_cloak_type.assert_has_calls(expected_calls)
            material_arg = mock_set_star_cloak_type.call_args[0][0]  # Get the first argument
            assert material_arg.name == replacer.material_names.STAR_CLOAK
            
            # Check miHoYoDiffuse special case
            assert material_slot_mihoyo.material == mock_body_material

    @patch('setup_wizard.domain.shader_material_name_keywords.ShaderMaterialNameKeywords')
    def test_create_shader_material_if_unique_mesh(self, mock_keywords, replacer):
        """Test creation of materials for unique mesh types"""
        # Setup
        mock_mesh = MagicMock()
        mock_keywords.SKILLOBJ = "SkillObj"
        
        # Test cases for different material types
        with patch.object(replacer, 'create_hair_material') as mock_create_hair, \
             patch.object(replacer, 'create_body_material') as mock_create_body, \
             patch.object(replacer, 'create_glass_material') as mock_create_glass, \
             patch.object(replacer, '_GenshinImpactDefaultMaterialReplacer__set_glass_star_cloak_toggle') as mock_set_toggle:
            
            # Setup mock returns
            mock_hair_material = MagicMock(name="mock_hair_material")
            mock_hair_material.name = "test_hair_material"
            mock_create_hair.return_value = mock_hair_material
            
            mock_body_material = MagicMock(name="mock_body_material")
            mock_body_material.name = "test_body_material"
            mock_create_body.return_value = mock_body_material
            
            mock_glass_material = MagicMock(name="mock_glass_material")
            mock_glass_material.name = "test_glass_material"
            mock_create_glass.return_value = mock_glass_material
            
            # Test 1: EffectHair (hair type)
            result = replacer.create_shader_material_if_unique_mesh(mock_mesh, 'EffectHair', 'original_material')
            mock_create_hair.assert_called_with(replacer.material_names, replacer.material_names.EFFECT_HAIR)
            assert result == "test_hair_material"
            mock_create_hair.reset_mock()
            
            # Test 2: Gauntlet (body type)
            result = replacer.create_shader_material_if_unique_mesh(mock_mesh, 'Gauntlet', 'original_material')
            mock_create_body.assert_called_with(replacer.material_names, replacer.material_names.GAUNTLET)
            assert result == "test_body_material"
            mock_create_body.reset_mock()
            
            # Test 3: Glass_Eff (glass type with special settings)
            result = replacer.create_shader_material_if_unique_mesh(mock_mesh, 'Glass_Eff', 'original_material')
            mock_create_glass.assert_called_with(replacer.material_names, replacer.material_names.GLASS_EFF)
            mock_set_toggle.assert_called_with(mock_glass_material, False)
            assert mock_glass_material.blend_method == 'BLEND'
            assert mock_glass_material.shadow_method == 'NONE'
            assert mock_glass_material.show_transparent_back == False
            assert result == "test_glass_material"
            mock_create_glass.reset_mock()
            mock_set_toggle.reset_mock()
            
            # Test 4: SkillObj (specialized body type with name replacement)
            mock_mesh_body_part_name = 'SkillObj Fugu'
            mock_body_material.name = "SkillObj_Mualani_Fugu_Mat"
            result = replacer.create_shader_material_if_unique_mesh(
                mock_mesh, 
                mock_mesh_body_part_name,
                'original_material'
            )
            mock_create_body.assert_called_with(replacer.material_names, replacer.material_names.SKILLOBJ)
            assert result == "SkillObj Fugu_Mualani_Fugu_Mat"
            mock_create_body.reset_mock()
            
            # Test 5: Default case (no special handling)
            result = replacer.create_shader_material_if_unique_mesh(mock_mesh, 'Regular_Material', 'original_material')
            mock_create_hair.assert_not_called()
            mock_create_body.assert_not_called()
            mock_create_glass.assert_not_called()
            assert result == 'original_material'

    def test_get_npc_mesh_body_part_name(self, replacer):
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Hair_Mat") == "Hair"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Face_Mat") == "Face"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Body_Mat") == "Body"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Dress_Mat") == "Dress"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Item_Mat") == "NPC_Item_Mat"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Screw_Mat") == "NPC_Screw_Mat"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Hat_Mat") == "NPC_Hat_Mat"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Others_Mat") == "NPC_Others_Mat"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Cloak_Mat") == "Cloak"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_npc_mesh_body_part_name("NPC_Unknown_Mat") is None
    
    def test_get_monster_mesh_body_part_name(self, replacer):
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_monster_mesh_body_part_name("Monster_Hair_Mat") == "Hair"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_monster_mesh_body_part_name("Monster_Face_Mat") == "Face"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_monster_mesh_body_part_name("Monster_Body_Mat") == "Body"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_monster_mesh_body_part_name("Monster_Dress_Mat") == "Dress"
        assert replacer._GenshinImpactDefaultMaterialReplacer__get_monster_mesh_body_part_name("Monster_Unknown_Mat") == "Body"  # Default case
    
    @patch('bpy.data.materials.get')
    def test_create_body_material(self, mock_materials_get, replacer, material_names):
        # Setup
        mock_body_material = MagicMock(name="body_material")
        mock_body_copy = MagicMock(name="body_copy")
        mock_body_material.copy.return_value = mock_body_copy
        
        mock_materials_get.side_effect = lambda name: mock_body_material if name == material_names.BODY else None
        
        # Test
        result = replacer.create_body_material(material_names, "test_material_name")
        
        # Assert
        mock_materials_get.assert_called_with(material_names.BODY)
        mock_body_material.copy.assert_called_once()
        assert mock_body_copy.name == "test_material_name"
        assert mock_body_copy.use_fake_user is True
        assert result == mock_body_copy
    
    @patch('bpy.data.materials.get')
    def test_create_hair_material(self, mock_materials_get, replacer, material_names):
        # Setup
        mock_hair_material = MagicMock(name="hair_material")
        mock_hair_copy = MagicMock(name="hair_copy")
        mock_hair_material.copy.return_value = mock_hair_copy
        
        mock_materials_get.side_effect = lambda name: mock_hair_material if name == material_names.HAIR else None
        
        # Test
        result = replacer.create_hair_material(material_names, "test_material_name")
        
        # Assert
        mock_materials_get.assert_called_with(material_names.HAIR)
        mock_hair_material.copy.assert_called_once()
        assert mock_hair_copy.name == "test_material_name"
        assert mock_hair_copy.use_fake_user is True
        assert result == mock_hair_copy
    
    @patch('bpy.data.materials.get')
    def test_create_glass_material(self, mock_materials_get, replacer, material_names):
        # Setup
        mock_vfx_material = MagicMock(name="vfx_material")
        mock_vfx_copy = MagicMock(name="vfx_copy")
        mock_vfx_material.copy.return_value = mock_vfx_copy
        
        mock_materials_get.side_effect = lambda name: mock_vfx_material if name == material_names.VFX else None
        
        # Test
        result = replacer.create_glass_material(material_names, "test_material_name")
        
        # Assert
        mock_materials_get.assert_called_with(material_names.VFX)
        mock_vfx_material.copy.assert_called_once()
        assert mock_vfx_copy.name == "test_material_name"
        assert mock_vfx_copy.use_fake_user is True
        assert result == mock_vfx_copy
    
    @patch('bpy.data.materials.get')
    def test_set_glass_star_cloak_toggle(self, mock_materials_get, replacer):
        # Setup
        mock_material = MagicMock()
        mock_node = MagicMock()
        mock_input = MagicMock()
        
        mock_material.node_tree.nodes.get.return_value = mock_node
        mock_node.inputs.get.return_value = mock_input
        
        # Test
        replacer._GenshinImpactDefaultMaterialReplacer__set_glass_star_cloak_toggle(mock_material, True)
        
        # Assert
        mock_material.node_tree.nodes.get.assert_called_once_with(replacer.shader_node_names.VFX_SHADER)
        mock_node.inputs.get.assert_called_once_with(replacer.shader_node_names.TOGGLE_GLASS_STAR_CLOAK)
        assert mock_input.default_value == True
    
    @patch('bpy.data.materials.get')
    def test_set_star_cloak_type(self, mock_materials_get, replacer):
        # Setup
        mock_material = MagicMock()
        mock_node = MagicMock()
        mock_input = MagicMock()
        
        mock_material.node_tree.nodes.get.return_value = mock_node
        mock_node.inputs.get.return_value = mock_input
        
        # Test with a valid StarCloakType
        with patch.object(StarCloakTypes, '__iter__', return_value=iter(['SKIRK'])):
            replacer._GenshinImpactDefaultMaterialReplacer__set_star_cloak_type(mock_material, "Character_SKIRK_Material")
            
            # Assert
            mock_material.node_tree.nodes.get.assert_called_once_with(replacer.shader_node_names.VFX_SHADER)
            mock_node.inputs.get.assert_called_once_with(replacer.shader_node_names.STAR_CLOAK_TYPE)
            assert mock_input.default_value == 3
