"""Batalha Pokémon local para dois jogadores no terminal."""

import json
import math
import random
import unicodedata
from pathlib import Path

import pokémon_lib
from golpes_lib import MOVE_DATA
from type_chart import TYPE_CHART, canonical_type

TEAM_SIZE = 3
MAX_ACTIVE_POKEMON = 3
POKEMON_DATA_FILE = Path(__file__).with_name("pokemon_custom.json")
ITEM_DATA_FILE = Path(__file__).with_name("itens.json")
POKEMON_SIZE_FILE = Path(__file__).with_name("pokemon_tamanhos.json")

POKEMON_LIBRARY = {
    name: value
    for name, value in vars(pokémon_lib).items()
    if isinstance(value, dict) and "espécie" in value
}

POKEMON_REQUIRED_FIELDS = {
    "espécie",
    "nome",
    "nível",
    "tipo 1",
    "tipo 2",
    "hp",
    "att",
    "def",
    "sp.att",
    "sp.def",
    "speed",
}


def load_json_file(path, default):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def save_json_file(path, data):
    with path.open("w", encoding="utf-8") as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=2)
        data_file.write("\n")


def load_pokemon_library():
    pokemon = {name: dict(data) for name, data in POKEMON_LIBRARY.items()}
    custom_pokemon = load_json_file(POKEMON_DATA_FILE, [])
    if not isinstance(custom_pokemon, list):
        raise ValueError("pokemon_custom.json deve conter uma lista de Pokémon.")

    existing_species = {data["espécie"].casefold() for data in pokemon.values()}
    for record in custom_pokemon:
        validate_pokemon_record(record)
        species = record["espécie"]
        if species.casefold() in existing_species:
            raise ValueError(f"A espécie '{species}' já está cadastrada.")
        existing_species.add(species.casefold())
        pokemon[species] = record

    size_overrides = load_json_file(POKEMON_SIZE_FILE, {})
    if not isinstance(size_overrides, dict):
        raise ValueError("pokemon_tamanhos.json deve conter um objeto JSON.")
    for data in pokemon.values():
        size = size_overrides.get(data["espécie"], data.get("tamanho", "Médio"))
        if not isinstance(size, str) or not size.strip():
            raise ValueError(f"O tamanho de {data['espécie']} precisa ser um texto.")
        data["tamanho"] = size.strip()
    return pokemon


def validate_pokemon_record(record):
    if not isinstance(record, dict):
        raise ValueError("Cada Pokémon cadastrado precisa ser um objeto JSON.")
    missing_fields = POKEMON_REQUIRED_FIELDS - record.keys()
    if missing_fields:
        raise ValueError(
            "Faltam campos obrigatórios no Pokémon: "
            + ", ".join(sorted(missing_fields))
        )
    if not isinstance(record["espécie"], str) or not record["espécie"].strip():
        raise ValueError("A espécie precisa ser informada como texto.")
    if not isinstance(record["nome"], str) or not record["nome"].strip():
        raise ValueError("O nome do Pokémon precisa ser informado como texto.")
    for stat in ("hp", "att", "def", "sp.att", "sp.def", "speed"):
        value = record[stat]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value <= 0
        ):
            raise ValueError(f"O atributo '{stat}' precisa ser um número positivo.")
    if (
        not isinstance(record["nível"], (str, int))
        or not str(record["nível"]).isdigit()
    ):
        raise ValueError("O nível precisa ser um número inteiro.")
    for key in ("tipo 1", "tipo 2"):
        if not isinstance(record[key], str):
            raise ValueError(f"O campo '{key}' precisa conter um tipo em texto.")
        canonical_type(record[key])

    for key, move_name in record.items():
        if "ataque" not in key and key != "proteção":
            continue
        if not move_name:
            continue
        if not isinstance(move_name, str):
            raise ValueError(f"O golpe no campo '{key}' precisa ser texto.")
        normalized_name = normalize(move_name)
        if normalized_name not in {normalize(name) for name in MOVE_DATA}:
            raise ValueError(
                f"O golpe '{move_name}' não está cadastrado em golpes_lib.py."
            )
    if "tamanho" not in record:
        record["tamanho"] = "Médio"
    if not isinstance(record["tamanho"], str) or not record["tamanho"].strip():
        raise ValueError("O tamanho precisa ser informado como texto.")


def pokemon_size_overrides():
    overrides = load_json_file(POKEMON_SIZE_FILE, {})
    if not isinstance(overrides, dict):
        raise ValueError("pokemon_tamanhos.json deve conter um objeto JSON.")
    return overrides


def set_pokemon_size(species, size):
    if not size.strip():
        raise ValueError("O tamanho não pode ficar vazio.")
    overrides = pokemon_size_overrides()
    overrides[species] = size.strip()
    save_json_file(POKEMON_SIZE_FILE, overrides)


def load_items():
    items = load_json_file(ITEM_DATA_FILE, [])
    if not isinstance(items, list):
        raise ValueError("itens.json deve conter uma lista de itens.")
    for item in items:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("nome"), str)
            or not isinstance(item.get("descrição"), str)
        ):
            raise ValueError("Cada item deve ter campos de texto 'nome' e 'descrição'.")
    return items


def pokemon_type_label(pokemon):
    first_type = pokemon["tipo 1"]
    second_type = pokemon["tipo 2"]
    if canonical_type(second_type) is None:
        return first_type
    return f"{first_type}/{second_type}"


def normalize(text):
    """Normaliza acentos para comparar nomes de golpes."""
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text.casefold())
        if unicodedata.category(char) != "Mn"
    )


def get_moves(pokemon):
    moves = []
    move_data_by_name = {normalize(name): data for name, data in MOVE_DATA.items()}
    for key, value in pokemon.items():
        if value and ("ataque" in key or key == "proteção"):
            move_key = normalize(value)
            move_data = move_data_by_name.get(move_key)
            if move_data is None:
                raise ValueError(
                    f"O golpe '{value}' de {pokemon['nome']} não está cadastrado "
                    "em golpes_lib.py."
                )
            moves.append((value, move_data))
    protection = move_data_by_name[normalize("proteção")]
    if not any(normalize(name) == normalize("proteção") for name, _ in moves):
        moves.append(("proteção", protection))
    return moves


def choose_battle_moves(pokemon):
    pokemon_moves = get_moves(pokemon)
    protection = next(
        move for move in pokemon_moves if normalize(move[0]) == normalize("proteção")
    )
    available = [
        move for move in pokemon_moves if normalize(move[0]) != normalize("proteção")
    ]
    move_limit = min(3, len(available))
    selected = []

    print(f"\nEscolha até {move_limit} golpes para {pokemon['nome']}:")
    while len(selected) < move_limit:
        for index, (name, move_data) in enumerate(available, start=1):
            print(f"{index} - {name} (poder {move_data[2]})")
        choice = ask_number("Escolha o golpe: ", 1, len(available)) - 1
        selected.append(available.pop(choice))

    selected.append(protection)
    return selected


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
    attacking_type = canonical_type(move_type)
    effectiveness = 1
    for key in ("tipo 1", "tipo 2"):
        raw_defending_type = defender["data"].get(key)
        if not raw_defending_type:
            continue
        defending_type = canonical_type(raw_defending_type)
        if defending_type:
            effectiveness *= TYPE_CHART[attacking_type][defending_type]
    return effectiveness


def stat_value(battler, stat):
    base_stat = battler["data"][stat]
    if (
        isinstance(base_stat, bool)
        or not isinstance(base_stat, (int, float))
        or not math.isfinite(base_stat)
        or base_stat <= 0
    ):
        raise ValueError(f"O atributo '{stat}' precisa ser um número maior que zero.")
    stage = battler["stages"][stat]
    if stage >= 0:
        multiplier = (2 + stage) / 2
    else:
        multiplier = 2 / (2 - stage)
    return max(1, base_stat * multiplier)


def calculate_damage(
    attacker, defender, move_data, random_factor=None, status_modifier=1.0
):
    move_type, category, power, _, _ = move_data
    if category not in ("physical", "special"):
        raise ValueError("Golpes de status não causam dano.")
    if (
        isinstance(power, bool)
        or not isinstance(power, (int, float))
        or not math.isfinite(power)
        or power < 0
    ):
        raise ValueError("O poder do golpe deve ser um número não negativo.")
    if (
        isinstance(status_modifier, bool)
        or not isinstance(status_modifier, (int, float))
        or not math.isfinite(status_modifier)
        or status_modifier < 0
    ):
        raise ValueError(
            "O modificador de status precisa ser um número finito não negativo."
        )
    if random_factor is None:
        random_factor = random.uniform(0.95, 1.05)
    elif (
        isinstance(random_factor, bool)
        or not isinstance(random_factor, (int, float))
        or not math.isfinite(random_factor)
        or not 0.95 <= random_factor <= 1.05
    ):
        raise ValueError("O fator aleatório deve estar entre 0,95 e 1,05.")

    attack_stat = "att" if category == "physical" else "sp.att"
    defense_stat = "def" if category == "physical" else "sp.def"
    attack = stat_value(attacker, attack_stat)
    defense = stat_value(defender, defense_stat)

    base_damage = attack / defense
    base_damage *= power * 22
    base_damage /= 50
    base_damage += 2
    effectiveness = type_effectiveness(move_type, defender)
    if effectiveness == 0:
        return 0
    damage = base_damage * effectiveness
    damage *= random_factor
    damage *= status_modifier
    return int(damage)


def ask_number(prompt, minimum, maximum):
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and minimum <= int(answer) <= maximum:
            return int(answer)
        print(f"Digite um número entre {minimum} e {maximum}.")


def show_title():
    print("\033[95m")
    print("+------------------------------------------------------+")
    print("|                                                      |")
    print("|                  POKÉMON: O RPG                      |")
    print("|                                                      |")
    print("+------------------------------------------------------+")
    print("\033[0m")


def register_pokemon():
    print(
        "\nCole os dados de um Pokémon em JSON. "
        "Quando terminar, pressione Enter numa linha vazia."
    )
    print("Use os campos da ficha-exemplo descrita no README.")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    try:
        pasted_data = json.loads("\n".join(lines))
        records = pasted_data if isinstance(pasted_data, list) else [pasted_data]
        if not records:
            raise ValueError("A lista colada não contém nenhum Pokémon.")
        library = load_pokemon_library()
        existing_species = {name.casefold() for name in library}
        for record in records:
            validate_pokemon_record(record)
            species = record["espécie"].strip()
            if species.casefold() in existing_species:
                raise ValueError(f"A espécie '{species}' já está cadastrada.")
            existing_species.add(species.casefold())
            record["espécie"] = species
            record["nome"] = record["nome"].strip()
            record.setdefault("tamanho", "Médio")
        custom_data = load_json_file(POKEMON_DATA_FILE, [])
        if not isinstance(custom_data, list):
            raise ValueError("pokemon_custom.json deve conter uma lista de Pokémon.")
        save_json_file(POKEMON_DATA_FILE, custom_data + records)
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as error:
        print(f"Não foi possível cadastrar o Pokémon: {error}")
        return
    print(f"{len(records)} Pokémon cadastrado(s) com sucesso.")


def show_pokemon(pokemon_library=None):
    pokemon_library = pokemon_library or load_pokemon_library()
    print("\nPokémon cadastrados:")
    for pokemon in pokemon_library.values():
        print(
            f"- {pokemon['nome']} ({pokemon_type_label(pokemon)}) — "
            f"HP {pokemon['hp']} — tamanho {pokemon.get('tamanho', 'Médio')}"
        )


def register_item():
    name = input("Nome do item: ").strip()
    if not name:
        print("O nome do item não pode ficar vazio.")
        return
    description = input("Descrição/efeito planejado: ").strip()
    try:
        items = load_items()
        if any(item["nome"].casefold() == name.casefold() for item in items):
            print(f"O item '{name}' já está cadastrado.")
            return
        items.append({"nome": name, "descrição": description})
        save_json_file(ITEM_DATA_FILE, items)
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Não foi possível cadastrar o item: {error}")
        return
    print(f"Item '{name}' cadastrado. Seus efeitos ainda não são aplicados na batalha.")


def show_items():
    items = load_items()
    if not items:
        print("\nAinda não há itens cadastrados.")
        return
    print("\nItens cadastrados:")
    for item in items:
        description = item["descrição"] or "Sem descrição."
        print(f"- {item['nome']}: {description}")


def customize_pokemon_size():
    pokemon = load_pokemon_library()
    pokemon_names = list(pokemon)
    print("\nEscolha um Pokémon para ajustar o tamanho:")
    for index, species in enumerate(pokemon_names, start=1):
        data = pokemon[species]
        print(f"{index} - {data['nome']} " f"(atual: {data.get('tamanho', 'Médio')})")
    selected = ask_number("Pokémon: ", 1, len(pokemon_names)) - 1
    species = pokemon_names[selected]
    size = input("Tamanho (Pequeno, Médio, Grande, Gigante ou outro nome): ").strip()
    if not size:
        print("O tamanho não pode ficar vazio.")
        return
    set_pokemon_size(species, size)
    print(f"Tamanho de {pokemon[species]['nome']} atualizado para {size}.")


def main_menu():
    while True:
        show_title()
        print("1 - Iniciar batalha")
        print("2 - Cadastrar Pokémon (colar JSON)")
        print("3 - Ver Pokémon cadastrados")
        print("4 - Cadastrar item")
        print("5 - Ver itens")
        print("6 - Ajustar tamanho de um Pokémon")
        print("7 - Sair")
        option = ask_number("Escolha uma opção: ", 1, 7)

        if option == 7:
            print("Até a próxima!")
            return
        try:
            if option == 1:
                battle()
            elif option == 2:
                register_pokemon()
            elif option == 3:
                show_pokemon()
            elif option == 4:
                register_item()
            elif option == 5:
                show_items()
            elif option == 6:
                customize_pokemon_size()
        except (OSError, ValueError) as error:
            print(f"Não foi possível completar essa opção: {error}")
        input("\nPressione Enter para voltar ao menu.")


def choose_team(player_name, pokemon_library=None):
    pokemon_library = pokemon_library or load_pokemon_library()
    available = list(pokemon_library.items())
    team = []
    print(f"\n{player_name}, escolha {TEAM_SIZE} Pokémon para sua equipe:")
    while len(team) < TEAM_SIZE:
        for index, (name, pokemon) in enumerate(available, start=1):
            print(
                f"{index} - {pokemon['nome']} "
                f"({pokemon_type_label(pokemon)}, HP {pokemon['hp']}, "
                f"tamanho {pokemon.get('tamanho', 'Médio')})"
            )
        choice = ask_number("Escolha: ", 1, len(available)) - 1
        name, pokemon = available.pop(choice)
        selected_moves = choose_battle_moves(pokemon)
        team.append(
            {
                "name": name,
                "battler": create_battler(pokemon),
                "moves": selected_moves,
            }
        )
        print(f"{pokemon['nome']} entrou para a equipe de {player_name}.\n")
    return team


def choose_target(opponent):
    targets = [
        index
        for index in opponent["active"]
        if opponent["team"][index]["battler"]["hp"] > 0
    ]
    for option, index in enumerate(targets, start=1):
        battler = opponent["team"][index]["battler"]
        pokemon = battler["data"]
        print(
            f"{option} - {pokemon['nome']} " f"(HP {battler['hp']}/{battler['max_hp']})"
        )
    selected = ask_number("Alvo: ", 1, len(targets)) - 1
    return targets[selected]


def choose_action(player, opponent, actor_index):
    active = player["team"][actor_index]["battler"]
    pokemon = active["data"]
    moves = player["team"][actor_index]["moves"]

    print(
        f"\nAção de {player['name']} — {pokemon['nome']} "
        f"(HP {active['hp']}/{active['max_hp']})"
    )
    for index, (name, move_data) in enumerate(moves, start=1):
        print(f"{index} - {name} (poder {move_data[2]})")
    switchable = [
        (index, member)
        for index, member in enumerate(player["team"])
        if index not in player["active"] and member["battler"]["hp"] > 0
    ]
    switch_option = len(moves) + 1
    if switchable:
        print(f"{switch_option} - Trocar este Pokémon por um da reserva")
    choice = ask_number(
        "Escolha sua ação: ", 1, switch_option if switchable else len(moves)
    )
    if choice == switch_option and switchable:
        for option, (_, member) in enumerate(switchable, start=1):
            battler = member["battler"]
            print(
                f"{option} - {battler['data']['nome']} "
                f"(HP {battler['hp']}/{battler['max_hp']})"
            )
        selected = ask_number("Quem entra no campo? ", 1, len(switchable))
        return ("switch", switchable[selected - 1][0])

    move = moves[choice - 1]
    effect = move[1][4]
    target = None
    if move[1][1] != "status" or (effect and effect[0] == "sleep"):
        print("Escolha o Pokémon adversário para mirar:")
        target = choose_target(opponent)
    return ("move", move, target)


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
    if category == "status":
        if not effect:
            raise ValueError(f"O golpe de status '{name}' ainda não tem um efeito.")
        if effect[0] == "protect":
            attacker["protected"] = True
            print(f"{attacker_name} se protegeu!")
            return
        if effect[0] == "boost":
            _, stat, stages = effect
            boosted_stats = ("att", "sp.att") if stat == "both" else (stat,)
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
        raise ValueError(
            f"O efeito '{effect[0]}' do golpe '{name}' ainda não foi implementado."
        )
    if effect is not None:
        raise ValueError(
            f"O efeito especial do golpe '{name}' ainda não foi implementado."
        )

    if random.randint(1, 100) > accuracy:
        print(f"{name} errou!")
        return
    if defender["protected"]:
        print(f"{defender_name} bloqueou o golpe com Proteção!")
        return

    damage = calculate_damage(attacker, defender, move_data)
    defender["hp"] = max(0, defender["hp"] - damage)
    effectiveness = type_effectiveness(move_type, defender)
    if effectiveness > 1:
        print("É super eficaz!")
    elif 0 < effectiveness < 1:
        print("Não é muito eficaz...")
    elif effectiveness == 0:
        print("Não teve efeito.")
    print(
        f"{defender_name} perdeu {damage} HP ({defender['hp']}/{defender['max_hp']} HP restantes)."
    )
    if defender["hp"] == 0:
        print(f"{defender_name} desmaiou!")


def living_team_members(team):
    return sum(member["battler"]["hp"] > 0 for member in team)


def replace_fainted(player):
    fainted = [
        index
        for index in player["active"]
        if player["team"][index]["battler"]["hp"] <= 0
    ]
    for index in fainted:
        player["active"].remove(index)
        pokemon = player["team"][index]["battler"]["data"]
        print(f"{pokemon['nome']} não pode mais lutar.")

    while len(player["active"]) < player["active_limit"] and living_team_members(
        player["team"]
    ) > len(player["active"]):
        available = [
            (index, member)
            for index, member in enumerate(player["team"])
            if index not in player["active"] and member["battler"]["hp"] > 0
        ]
        if not available:
            return
        print(f"\n{player['name']}, escolha um Pokémon para entrar no campo:")
        for option, (_, member) in enumerate(available, start=1):
            battler = member["battler"]
            print(
                f"{option} - {battler['data']['nome']} "
                f"(HP {battler['hp']}/{battler['max_hp']})"
            )
        selected = ask_number("Escolha: ", 1, len(available))
        new_index = available[selected - 1][0]
        player["active"].append(new_index)
        pokemon = player["team"][new_index]["battler"]["data"]
        print(f"{player['name']} enviou {pokemon['nome']}!\n")


def show_status(players):
    print("\n" + "=" * 48)
    for player in players:
        print(
            f"{player['name']} — Pokémon em campo "
            f"({sum(player['team'][index]['battler']['hp'] > 0 for index in player['active'])} "
            "ativos; "
            f"{living_team_members(player['team'])} vivos no time):"
        )
        for index, member in enumerate(player["team"]):
            battler = member["battler"]
            pokemon = battler["data"]
            if index in player["active"]:
                position = "Campo"
            elif battler["hp"] > 0:
                position = "Reserva"
            else:
                position = "Desmaiado"
            print(
                f"  {position}: {pokemon['nome']} ({pokemon_type_label(pokemon)}) "
                f"HP {battler['hp']}/{battler['max_hp']} "
                f"| porte {pokemon.get('tamanho', 'Médio')}"
            )
    print("=" * 48)


def battle():
    pokemon_library = load_pokemon_library()
    if len(pokemon_library) < TEAM_SIZE:
        print(f"Cadastre pelo menos {TEAM_SIZE} Pokémon antes de iniciar.")
        return

    print("\nFormato da batalha:")
    for count in range(1, MAX_ACTIVE_POKEMON + 1):
        print(f"{count} - {count}x{count} Pokémon ativos por lado")
    active_count = ask_number(
        "Quantos Pokémon lutam ao mesmo tempo por lado? ",
        1,
        MAX_ACTIVE_POKEMON,
    )
    first_name = input("Nome do Jogador 1: ").strip() or "Jogador 1"
    second_name = input("Nome do Jogador 2: ").strip() or "Jogador 2"
    players = [
        {
            "name": first_name,
            "team": choose_team(first_name, pokemon_library),
            "active": list(range(active_count)),
            "active_limit": active_count,
        },
        {
            "name": second_name,
            "team": choose_team(second_name, pokemon_library),
            "active": list(range(active_count)),
            "active_limit": active_count,
        },
    ]

    print("\nA batalha começou!")
    for player in players:
        pokemon_names = ", ".join(
            player["team"][index]["battler"]["data"]["nome"]
            for index in player["active"]
        )
        print(f"{player['name']} enviou: {pokemon_names}!")
    round_number = 1

    while all(living_team_members(player["team"]) for player in players):
        print(f"\n--- Rodada {round_number} ---")
        for player in players:
            replace_fainted(player)
        show_status(players)
        actions = []
        for index, player in enumerate(players):
            opponent = players[1 - index]
            for actor_index in player["active"]:
                actions.append(
                    (
                        index,
                        actor_index,
                        choose_action(player, opponent, actor_index),
                    )
                )

        def action_order(action_entry):
            player_index, actor_index, action = action_entry
            actor = players[player_index]["team"][actor_index]["battler"]
            if action[0] == "switch":
                return (2, actor["data"]["speed"], random.random())
            move_effect = action[1][1][4]
            priority = 1 if move_effect and move_effect[0] == "protect" else 0
            return (priority, actor["data"]["speed"], random.random())

        for player_index, actor_index, action in sorted(
            actions, key=action_order, reverse=True
        ):
            player = players[player_index]
            opponent = players[1 - player_index]
            if (
                actor_index not in player["active"]
                or player["team"][actor_index]["battler"]["hp"] <= 0
            ):
                continue
            if action[0] == "switch":
                replacement_index = action[1]
                player["active"][
                    player["active"].index(actor_index)
                ] = replacement_index
                pokemon = player["team"][replacement_index]["battler"]["data"]
                print(
                    f"{player['name']} trocou {player['team'][actor_index]['battler']['data']['nome']} "
                    f"por {pokemon['nome']}!"
                )
                continue
            _, move, target_index = action
            move_data = move[1]
            effect = move_data[4]
            if (
                target_index is None
                and move_data[1] == "status"
                and effect
                and effect[0] in ("protect", "boost")
            ):
                defender = player["team"][actor_index]["battler"]
            elif (
                target_index is not None
                and target_index in opponent["active"]
                and opponent["team"][target_index]["battler"]["hp"] > 0
            ):
                defender = opponent["team"][target_index]["battler"]
            else:
                print("O alvo escolhido já não pode lutar; a ação foi perdida.")
                continue
            attacker = player["team"][actor_index]["battler"]
            use_move(attacker, defender, move)
            if living_team_members(opponent["team"]) == 0:
                break

        for player in players:
            for member in player["team"]:
                member["battler"]["protected"] = False
        round_number += 1

    winner = next(
        player for player in players if living_team_members(player["team"]) > 0
    )
    print(f"\n{winner['name']} venceu a batalha!")


if __name__ == "__main__":
    main_menu()
