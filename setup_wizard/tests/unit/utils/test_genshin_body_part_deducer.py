import pytest

from pathlib import Path
from setup_wizard.utils.genshin_body_part_deducer import get_body_part, get_character_type, get_npc_mesh_body_part_name, get_monster_body_part_name
from setup_wizard.domain.character_types import CharacterType


@pytest.mark.parametrize("name, expected_body_part", [
    ("Monster_Hair_Mat", "Hair"),
    ("Monster_Face_Mat", "Face"),
    ("Monster_Body_Mat", "Body"),
    ("Monster_Dress_Mat", "Dress"),
    ("None", "Body"),
    ("Monster_Unknown_Mat", "Body"),  # Fallback case
    ("", "Body"),  # Edge case: empty string
])
def test_get_monster_body_part_name(name, expected_body_part):
    assert get_monster_body_part_name(name) == expected_body_part

@pytest.mark.parametrize("material_name, expected_body_part", [
    # Standard cases
    ("NPC_Hair_Mat", "Hair"),
    ("NPC_Face_Mat", "Face"),
    ("NPC_Body_Mat", "Body"),
    ("NPC_Dress_Mat", "Dress"),
    ("NPC_Item_Mat", "Item"),
    ("NPC_Screw_Mat", "Screw"),
    ("NPC_Hat_Mat", "Hat"),
    ("NPC_Others_Mat", "Others"),
    ("NPC_Cloak_Mat", "Cloak"),
    
    # Special item cases with extraction
    ("NPC_Item_Special_Mat", "Item_Special"),
    ("NPC_Item_Weapon_Mat", "Item_Weapon"),
    
    # Edge cases
    ("", None),  # Empty string
    ("Unknown_Material", None),  # No matching pattern
    ("NPC_Unknown_Mat", None),  # No matching body part
])
def test_get_npc_mesh_body_part_name(material_name, expected_body_part):
    assert get_npc_mesh_body_part_name(material_name) == expected_body_part

@pytest.mark.parametrize("file_name, expected_body_part", [
    ("Monster_Hair_Mat", "Hair"),
    ("Monster_Face_Mat", "Face"),
    ("Monster_Body_Mat", "Body"),
    ("Monster_Dress_Mat", "Dress"),
    ("Monster_None_Mat", "Body"),
    ("NPC_Hair_Mat", "Hair"),
    ("NPC_Face_Mat", "Face"),
    ("NPC_Body_Mat", "Body"),
    ("NPC_Dress_Mat", "Dress"),
    ("NPC_Item_Mat", "Item"),
    ("NPC_Screw_Mat", "Screw"),
    ("NPC_Hat_Mat", "Hat"),
    ("NPC_Others_Mat", "Others"),
    ("NPC_Cloak_Mat", "Cloak"),
    ("Equip_Sword_Mat", "Body"),
    ("Unknown_File_Mat", "Mat"),
])
def test_get_body_part(file_name, expected_body_part):
    file = Path(file_name)
    assert get_body_part(file) == expected_body_part

@pytest.mark.parametrize("file_name, expected_character_type", [
    ("Monster_Hair_Mat", CharacterType.MONSTER),
    ("NPC_Hair_Mat", CharacterType.NPC),
    ("Equip_Sword_Mat", CharacterType.GI_EQUIPMENT),
    ("Unknown_File_Mat", CharacterType.UNKNOWN),
])
def test_get_character_type(file_name, expected_character_type):
    file = Path(file_name)
    assert get_character_type(file) == expected_character_type