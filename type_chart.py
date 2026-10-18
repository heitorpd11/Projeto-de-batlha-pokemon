"""Tabela de efetividade dos tipos e nomes aceitos pelo simulador."""

import unicodedata

TYPES = (
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy",
)

_NON_NEUTRAL_EFFECTIVENESS = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 2,
        "Ice": 2,
        "Bug": 2,
        "Rock": 0.5,
        "Dragon": 0.5,
        "Steel": 2,
    },
    "Water": {
        "Fire": 2,
        "Water": 0.5,
        "Grass": 0.5,
        "Ground": 2,
        "Rock": 2,
        "Dragon": 0.5,
    },
    "Electric": {
        "Water": 2,
        "Electric": 0.5,
        "Grass": 0.5,
        "Ground": 0,
        "Flying": 2,
        "Dragon": 0.5,
    },
    "Grass": {
        "Fire": 0.5,
        "Water": 2,
        "Grass": 0.5,
        "Poison": 0.5,
        "Ground": 2,
        "Flying": 0.5,
        "Bug": 0.5,
        "Rock": 2,
        "Dragon": 0.5,
        "Steel": 0.5,
    },
    "Ice": {
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 2,
        "Ice": 0.5,
        "Ground": 2,
        "Flying": 2,
        "Dragon": 2,
        "Steel": 0.5,
    },
    "Fighting": {
        "Normal": 2,
        "Ice": 2,
        "Poison": 0.5,
        "Flying": 0.5,
        "Psychic": 0.5,
        "Bug": 0.5,
        "Rock": 2,
        "Ghost": 0,
        "Dark": 2,
        "Steel": 2,
        "Fairy": 0.5,
    },
    "Poison": {
        "Grass": 2,
        "Poison": 0.5,
        "Ground": 0.5,
        "Rock": 0.5,
        "Ghost": 0.5,
        "Steel": 0,
        "Fairy": 2,
    },
    "Ground": {
        "Fire": 2,
        "Electric": 2,
        "Grass": 0.5,
        "Poison": 2,
        "Flying": 0,
        "Bug": 0.5,
        "Rock": 2,
        "Steel": 2,
    },
    "Flying": {
        "Electric": 0.5,
        "Grass": 2,
        "Fighting": 2,
        "Bug": 2,
        "Rock": 0.5,
        "Steel": 0.5,
    },
    "Psychic": {
        "Fighting": 2,
        "Poison": 2,
        "Psychic": 0.5,
        "Steel": 0.5,
        "Dark": 0,
    },
    "Bug": {
        "Fire": 0.5,
        "Grass": 2,
        "Fighting": 0.5,
        "Poison": 0.5,
        "Flying": 0.5,
        "Psychic": 2,
        "Ghost": 0.5,
        "Dark": 2,
        "Steel": 0.5,
        "Fairy": 0.5,
    },
    "Rock": {
        "Fire": 2,
        "Ice": 2,
        "Fighting": 0.5,
        "Ground": 0.5,
        "Flying": 2,
        "Bug": 2,
        "Steel": 0.5,
    },
    "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {
        "Fighting": 0.5,
        "Psychic": 2,
        "Ghost": 2,
        "Dark": 0.5,
        "Fairy": 0.5,
    },
    "Steel": {
        "Fire": 0.5,
        "Water": 0.5,
        "Electric": 0.5,
        "Ice": 2,
        "Rock": 2,
        "Steel": 0.5,
        "Fairy": 2,
    },
    "Fairy": {
        "Fire": 0.5,
        "Fighting": 2,
        "Poison": 0.5,
        "Dragon": 2,
        "Dark": 2,
        "Steel": 0.5,
    },
}

TYPE_CHART = {
    attacking_type: {
        defending_type: _NON_NEUTRAL_EFFECTIVENESS.get(attacking_type, {}).get(
            defending_type, 1
        )
        for defending_type in TYPES
    }
    for attacking_type in TYPES
}

_TYPE_ALIASES = {
    "normal": "Normal",
    "fogo": "Fire",
    "fire": "Fire",
    "agua": "Water",
    "water": "Water",
    "eletrico": "Electric",
    "electric": "Electric",
    "grama": "Grass",
    "grass": "Grass",
    "gelo": "Ice",
    "ice": "Ice",
    "lutador": "Fighting",
    "fighting": "Fighting",
    "veneno": "Poison",
    "poison": "Poison",
    "terra": "Ground",
    "ground": "Ground",
    "voador": "Flying",
    "flying": "Flying",
    "psiquico": "Psychic",
    "psychic": "Psychic",
    "inseto": "Bug",
    "bug": "Bug",
    "pedra": "Rock",
    "rock": "Rock",
    "fantasma": "Ghost",
    "ghost": "Ghost",
    "dragao": "Dragon",
    "dragon": "Dragon",
    "sombrio": "Dark",
    "dark": "Dark",
    "aco": "Steel",
    "steel": "Steel",
    "fada": "Fairy",
    "fairy": "Fairy",
    "nenhum": None,
    "none": None,
}


def _normalize(text):
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text.casefold())
        if unicodedata.category(char) != "Mn"
    )


TYPE_NAMES = {name: _TYPE_ALIASES[name] for name in _TYPE_ALIASES}


def canonical_type(type_name):
    """Retorna o nome canônico em inglês ou informa que o tipo é inválido."""
    canonical = _TYPE_ALIASES.get(_normalize(type_name))
    if canonical is None and _normalize(type_name) not in ("nenhum", "none"):
        raise ValueError(f"Tipo desconhecido: {type_name}")
    return canonical
