import pytest

from pathlib import Path
from setup_wizard.utils.genshin_body_part_deducer import get_body_part, get_character_type
from setup_wizard.domain.character_types import CharacterType

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