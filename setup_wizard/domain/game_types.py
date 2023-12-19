from enum import Enum, auto

'''
It's important to separate this out into its own class because import_order uses GameType and 
Setup Wizard uses GameType and import_order.

This would result in a circular dependency if it existed in import_order or a Setup Wizard class.
'''
class GameType(Enum):
    GENSHIN_IMPACT = auto()
    HONKAI_STAR_RAIL = auto()
    PUNISHING_GRAY_RAVEN = auto()
