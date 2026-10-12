"""Batalha Pokémon local para dois jogadores no terminal."""

import random
import unicodedata

import pokémon_lib


TEAM_SIZE = 3

POKEMON_LIBRARY = {
    name: value
    for name, value in vars(pokémon_lib).items()
    if isinstance(value, dict) and "espécie" in value
}

MOVE_DATA = {
    "cauda d'água": ("Água", "physical", 90, 100, None),
    "hidro bomba": ("Água", "special", 110, 80, None),
    "confusão": ("Psíquico", "special", 50, 100, None),
    "amnésia": (None, "status", 0, 100, ("boost", "sp.def", 2)),
    "mordida": ("Sombrio", "physical", 60, 100, None),
    "roda de fogo": ("Fogo", "physical", 60, 100, None),
    "roda da aura": ("Elétrico", "physical", 110, 100, None),
    "choque do trovão": ("Elétrico", "special", 40, 100, None),
    "ataque de ramo": ("Grama", "physical", 40, 100, None),
    "arranhão": ("Normal", "physical", 40, 100, None),
    "crescimento": (None, "status", 0, 100, ("boost", "both", 1)),
    "tapa de lama": ("Terra", "special", 20, 100, None),
    "investida": ("Normal", "physical", 40, 100, None),
    "pulso d'água": ("Água", "special", 60, 100, None),
    "hipnose": (None, "status", 0, 60, ("sleep",)),
    "ácido": ("Veneno", "special", 40, 100, None),
    "defesa de ferro": (None, "status", 0, 100, ("boost", "def", 2)),
    "cabeçada": ("Normal", "physical", 70, 100, None),
    "brasas": ("Fogo", "special", 40, 100, None),
    "dança da chama": ("Fogo", "physical", 50, 100, None),
    "proteção": (None, "status", 0, 100, ("protect",)),
}

TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2,
        "Rock": 0.5, "Dragon": 0.5, "Steel": 2,
    },
    "Water": {
        "Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2,
        "Rock": 2, "Dragon": 0.5,
    },
    "Electric": {
        "Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0,
        "Flying": 2, "Dragon": 0.5,
    },
    "Grass": {
        "Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5,
        "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2,
        "Dragon": 0.5, "Steel": 0.5,
    },
    "Ice": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5,
        "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5,
    },
    "Fighting": {
        "Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5,
        "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0,
        "Dark": 2, "Steel": 2, "Fairy": 0.5,
    },
    "Poison": {
        "Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5,
        "Ghost": 0.5, "Steel": 0, "Fairy": 2,
    },
    "Ground": {
        "Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2,
        "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2,
    },
    "Psychic": {
        "Fighting": 2, "Poison": 2, "Psychic": 0.5,
        "Steel": 0.5, "Dark": 0,
    },
    "Bug": {
        "Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5,
        "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2,
        "Steel": 0.5, "Fairy": 0.5,
    },
    "Rock": {
        "Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5,
        "Flying": 2, "Bug": 2, "Steel": 0.5,
    },
    "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {
        "Fighting": 0.5, "Psychic": 2, "Ghost": 2,
        "Dark": 0.5, "Fairy": 0.5,
    },
    "Steel": {
        "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2,
        "Rock": 2, "Steel": 0.5, "Fairy": 2,
    },
    "Fairy": {
        "Fire": 0.5, "Fighting": 2, "Poison": 0.5,
        "Dragon": 2, "Dark": 2, "Steel": 0.5,
    },
}

TYPE_NAMES = {
    "Água": "Water",
    "Elétrico": "Electric",
    "Sombrio": "Dark",
    "Grama": "Grass",
    "Veneno": "Poison",
    "Fogo": "Fire",
    "Nenhum": None,
    "Psíquico": "Psychic",
    "Terra": "Ground",
}


def normalize(text):
    """Normaliza acentos para comparar nomes de golpes."""
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text.casefold())
        if unicodedata.category(char) != "Mn"
    )


def get_moves(pokemon):
    moves = []
    move_data_by_name = {
        normalize(name): data for name, data in MOVE_DATA.items()
    }
    for key, value in pokemon.items():
        if value and (
            "ataque" in key
            or key == "proteção"
        ):
            move_key = normalize(value)
            move_data = move_data_by_name.get(move_key)
            if move_data is None:
                category = "special" if key.startswith("sp.") else "physical"
                move_data = ("Normal", category, 40, 100, None)
            moves.append((value, move_data))
    return moves


def create_battler(pokemon):
    return {
        "data": pokemon,
        "hp": pokemon["hp"],
        "max_hp": pokemon["hp"],
        "stages": {"att": 0, "def": 0, "sp.att": 0, "sp.def": 0},
        "sleep": 0,
        "protected": False,
    }


def type_effectiveness(move_type, defender):
    if move_type is None:
        return 1
    chart = TYPE_CHART.get(TYPE_NAMES.get(move_type, move_type), {})
    effectiveness = 1
    for key in ("tipo 1", "tipo 2"):
        defending_type = TYPE_NAMES.get(defender["data"][key])
        if defending_type:
            effectiveness *= chart.get(defending_type, 1)
    return effectiveness


def stat_value(battler, stat):
    base_stat = battler["data"][stat]
    stage = battler["stages"][stat]
    if stage >= 0:
        multiplier = (2 + stage) / 2
    else:
        multiplier = 2 / (2 - stage)
    return max(1, base_stat * multiplier)


def calculate_damage(attacker, defender, move_data, critical=False, random_factor=1):
    move_type, category, power, _, _ = move_data
    attack_stat = "att" if category == "physical" else "sp.att"
    defense_stat = "def" if category == "physical" else "sp.def"
    level = int(attacker["data"]["nível"])
    base_damage = (
        ((2 * level / 5 + 2) * power * stat_value(attacker, attack_stat))
        / stat_value(defender, defense_stat)
        / 50
        + 2
    )
    effectiveness = type_effectiveness(move_type, defender)
    if effectiveness == 0:
        return 0
    stab = 1.5 if move_type in (
        attacker["data"]["tipo 1"],
        attacker["data"]["tipo 2"],
    ) else 1
    critical_multiplier = 1.5 if critical else 1
    return max(1, int(base_damage * effectiveness * stab * critical_multiplier * random_factor))


def ask_number(prompt, minimum, maximum):
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and minimum <= int(answer) <= maximum:
            return int(answer)
        print(f"Digite um número entre {minimum} e {maximum}.")


def choose_team(player_name):
    available = list(POKEMON_LIBRARY.items())
    team = []
    print(f"\n{player_name}, escolha {TEAM_SIZE} Pokémon para sua equipe:")
    while len(team) < TEAM_SIZE:
        for index, (name, pokemon) in enumerate(available, start=1):
            print(
                f"{index} - {pokemon['nome']} "
                f"({pokemon['tipo 1']}, HP {pokemon['hp']})"
            )
        choice = ask_number("Escolha: ", 1, len(available)) - 1
        name, pokemon = available.pop(choice)
        team.append({"name": name, "battler": create_battler(pokemon)})
        print(f"{pokemon['nome']} entrou para a equipe de {player_name}.\n")
    return team


def choose_action(player, team):
    active = team[player["active"]]["battler"]
    pokemon = active["data"]
    moves = get_moves(pokemon)

    print(f"\nVez de {player['name']} — {pokemon['nome']} (HP {active['hp']}/{active['max_hp']})")
    for index, (name, move_data) in enumerate(moves, start=1):
        print(f"{index} - {name}")
    switch_option = len(moves) + 1
    print(f"{switch_option} - Trocar Pokémon")
    choice = ask_number("Escolha sua ação: ", 1, switch_option)
    if choice < switch_option:
        return ("move", moves[choice - 1])

    switchable = [
        (index, member)
        for index, member in enumerate(team)
        if index != player["active"] and member["battler"]["hp"] > 0
    ]
    if not switchable:
        print("Não há outro Pokémon disponível; escolha um golpe.")
        return choose_action(player, team)
    for option, (index, member) in enumerate(switchable, start=1):
        print(f"{option} - {member['battler']['data']['nome']}")
    selected = ask_number("Para qual Pokémon deseja trocar? ", 1, len(switchable))
    return ("switch", switchable[selected - 1][0])


def use_move(attacker, defender, move):
    name, move_data = move
    move_type, category, _, accuracy, effect = move_data
    attacker_name = attacker["data"]["nome"]
    defender_name = defender["data"]["nome"]
    print(f"{attacker_name} usou {name}!")

    if attacker["sleep"] > 0:
        attacker["sleep"] -= 1
        print(f"{attacker_name} está dormindo e não conseguiu atacar.")
        return
    if category == "status" and effect:
        if effect[0] == "protect":
            attacker["protected"] = True
            print(f"{attacker_name} se protegeu!")
            return
        if effect[0] == "boost":
            _, stat, stages = effect
            boosted_stats = (
                ("att", "sp.att") if stat == "both" else (stat,)
            )
            for boosted_stat in boosted_stats:
                attacker["stages"][boosted_stat] = min(
                    6, attacker["stages"][boosted_stat] + stages
                )
            print(f"As estatísticas de {attacker_name} aumentaram!")
            return
        if effect[0] == "sleep":
            if random.randint(1, 100) > accuracy:
                print(f"{name} errou!")
                return
            defender["sleep"] = random.randint(1, 3)
            print(f"{defender_name} adormeceu!")
            return

    if random.randint(1, 100) > accuracy:
        print(f"{name} errou!")
        return
    if defender["protected"]:
        print(f"{defender_name} bloqueou o golpe com Proteção!")
        return

    critical = random.randint(1, 16) == 1
    damage = calculate_damage(
        attacker, defender, move_data, critical, random.uniform(0.85, 1)
    )
    defender["hp"] = max(0, defender["hp"] - damage)
    if critical:
        print("Golpe crítico!")
    effectiveness = type_effectiveness(move_type, defender)
    if effectiveness > 1:
        print("É super eficaz!")
    elif 0 < effectiveness < 1:
        print("Não é muito eficaz...")
    elif effectiveness == 0:
        print("Não teve efeito.")
    print(f"{defender_name} perdeu {damage} HP ({defender['hp']}/{defender['max_hp']} HP restantes).")
    if defender["hp"] == 0:
        print(f"{defender_name} desmaiou!")


def living_team_members(team):
    return sum(member["battler"]["hp"] > 0 for member in team)


def replace_fainted(player, team):
    active = team[player["active"]]["battler"]
    if active["hp"] > 0:
        return
    available = [
        (index, member)
        for index, member in enumerate(team)
        if member["battler"]["hp"] > 0
    ]
    if not available:
        return
    print(f"\n{player['name']}, escolha o próximo Pokémon:")
    for option, (_, member) in enumerate(available, start=1):
        battler = member["battler"]
        print(f"{option} - {battler['data']['nome']} (HP {battler['hp']}/{battler['max_hp']})")
    selected = ask_number("Escolha: ", 1, len(available))
    player["active"] = available[selected - 1][0]
    pokemon = team[player["active"]]["battler"]["data"]
    print(f"{player['name']} enviou {pokemon['nome']}!\n")


def show_status(players):
    print("\n" + "=" * 48)
    for player in players:
        active = player["team"][player["active"]]["battler"]
        pokemon = active["data"]
        print(
            f"{player['name']}: {pokemon['nome']} "
            f"HP {active['hp']}/{active['max_hp']} "
            f"| Pokémon restantes: {living_team_members(player['team'])}"
        )
    print("=" * 48)


def battle():
    print("=== BATALHA POKÉMON: 2 JOGADORES ===")
    first_name = input("Nome do Jogador 1: ").strip() or "Jogador 1"
    second_name = input("Nome do Jogador 2: ").strip() or "Jogador 2"
    players = [
        {"name": first_name, "team": choose_team(first_name), "active": 0},
        {"name": second_name, "team": choose_team(second_name), "active": 0},
    ]

    print("\nA batalha começou!")
    print(f"{first_name} enviou {players[0]['team'][0]['battler']['data']['nome']}!")
    print(f"{second_name} enviou {players[1]['team'][0]['battler']['data']['nome']}!")
    round_number = 1

    while all(living_team_members(player["team"]) for player in players):
        print(f"\n--- Rodada {round_number} ---")
        for player in players:
            replace_fainted(player, player["team"])
        show_status(players)
        actions = [
            choose_action(player, player["team"])
            for player in players
        ]

        def action_order(index):
            action = actions[index]
            if action[0] == "switch":
                return (2, 0)
            battler = players[index]["team"][players[index]["active"]]["battler"]
            move_effect = action[1][1][4]
            priority = 1 if move_effect and move_effect[0] == "protect" else 0
            return (priority, battler["data"]["speed"])

        order = sorted(
            range(len(players)),
            key=lambda index: action_order(index),
            reverse=True,
        )
        if actions[0][0] == actions[1][0] == "move":
            first_speed = action_order(0)[1]
            second_speed = action_order(1)[1]
            if first_speed == second_speed and random.choice((True, False)):
                order.reverse()

        for index in order:
            player = players[index]
            opponent = players[1 - index]
            action = actions[index]
            if action[0] == "switch":
                player["active"] = action[1]
                pokemon = player["team"][player["active"]]["battler"]["data"]
                print(f"{player['name']} trocou para {pokemon['nome']}!")
                continue
            attacker = player["team"][player["active"]]["battler"]
            defender = opponent["team"][opponent["active"]]["battler"]
            if attacker["hp"] > 0 and defender["hp"] > 0:
                use_move(attacker, defender, action[1])

        for player in players:
            for member in player["team"]:
                member["battler"]["protected"] = False
        round_number += 1

    winner = next(
        player for player in players if living_team_members(player["team"]) > 0
    )
    print(f"\n{winner['name']} venceu a batalha!")


if __name__ == "__main__":
    battle()
