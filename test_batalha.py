import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import batalha
from batalha import POKEMON_LIBRARY
from type_chart import TYPE_CHART, TYPES


def make_battler(
    *,
    attack=10,
    defense=5,
    special_attack=10,
    special_defense=5,
    first_type="Normal",
    second_type="Nenhum",
):
    return {
        "data": {
            "nome": "Teste",
            "tipo 1": first_type,
            "tipo 2": second_type,
            "att": attack,
            "def": defense,
            "sp.att": special_attack,
            "sp.def": special_defense,
        },
        "stages": {"att": 0, "def": 0, "sp.att": 0, "sp.def": 0},
    }


class DamageCalculationTests(unittest.TestCase):
    def setUp(self):
        self.attacker = make_battler()
        self.defender = make_battler()

    def test_uses_custom_formula_and_truncates_final_damage(self):
        move = ("Tapa", ("Normal", "physical", 50, 100, None))

        damage = batalha.calculate_damage(
            self.attacker, self.defender, move[1], random_factor=1
        )

        self.assertEqual(damage, 46)

    def test_special_move_uses_special_attack_and_defense(self):
        self.attacker["data"]["sp.att"] = 15
        self.defender["data"]["sp.def"] = 10
        move_data = ("Normal", "special", 50, 100, None)

        damage = batalha.calculate_damage(
            self.attacker, self.defender, move_data, random_factor=1
        )

        self.assertEqual(damage, 35)

    def test_dual_type_effectiveness_multipliers_are_combined(self):
        self.defender["data"]["tipo 1"] = "Fogo"
        self.defender["data"]["tipo 2"] = "Terra"
        move_data = ("Água", "physical", 50, 100, None)

        damage = batalha.calculate_damage(
            self.attacker, self.defender, move_data, random_factor=1
        )

        self.assertEqual(damage, 184)

    def test_type_immunity_reduces_damage_to_zero(self):
        self.defender["data"]["tipo 1"] = "Voador"
        move_data = ("Terra", "physical", 50, 100, None)

        damage = batalha.calculate_damage(
            self.attacker, self.defender, move_data, random_factor=1
        )

        self.assertEqual(damage, 0)

    def test_random_and_status_modifiers_are_applied_once(self):
        move_data = ("Normal", "physical", 50, 100, None)

        damage = batalha.calculate_damage(
            self.attacker,
            self.defender,
            move_data,
            random_factor=1.05,
            status_modifier=0.5,
        )

        self.assertEqual(damage, 24)

    def test_rejects_zero_defense_and_out_of_range_random_factor(self):
        self.defender["data"]["def"] = 0
        move_data = ("Normal", "physical", 50, 100, None)
        with self.assertRaises(ValueError):
            batalha.calculate_damage(
                self.attacker, self.defender, move_data, random_factor=1
            )

        self.defender["data"]["def"] = 5
        with self.assertRaises(ValueError):
            batalha.calculate_damage(
                self.attacker, self.defender, move_data, random_factor=1.1
            )

    def test_random_factor_is_drawn_once_from_the_configured_interval(self):
        move_data = ("Normal", "physical", 50, 100, None)
        with patch("batalha.random.uniform", return_value=1.05) as random_uniform:
            damage = batalha.calculate_damage(
                self.attacker, self.defender, move_data
            )

        self.assertEqual(damage, 48)
        random_uniform.assert_called_once_with(0.95, 1.05)


class TypeChartTests(unittest.TestCase):
    def test_chart_covers_all_18_types_as_attacker_and_defender(self):
        self.assertEqual(len(TYPE_CHART), 18)
        self.assertEqual(set(TYPE_CHART), set(TYPES))
        self.assertTrue(all(set(row) == set(TYPES) for row in TYPE_CHART.values()))

    def test_current_pokemon_moves_are_registered_and_team_selection_is_limited(self):
        for pokemon in POKEMON_LIBRARY.values():
            self.assertTrue(batalha.get_moves(pokemon))

        psyduck = POKEMON_LIBRARY["Psyduck"]
        with redirect_stdout(StringIO()), patch(
            "builtins.input", side_effect=["1", "1", "1"]
        ):
            selected = batalha.choose_battle_moves(psyduck)

        self.assertEqual(len(selected), 4)
        self.assertEqual(selected[-1][0], "proteção")


class PreBattleFeaturesTests(unittest.TestCase):
    def test_custom_pokemon_and_size_overrides_are_loaded_from_json(self):
        source = dict(POKEMON_LIBRARY["Psyduck"])
        source["espécie"] = "PsyduckPersonalizado"
        source["nome"] = "Psyduck Personalizado"

        with TemporaryDirectory() as temp_directory:
            pokemon_file = Path(temp_directory) / "pokemon_custom.json"
            sizes_file = Path(temp_directory) / "pokemon_tamanhos.json"
            batalha.save_json_file(pokemon_file, [source])
            batalha.save_json_file(sizes_file, {"PsyduckPersonalizado": "Colossal"})
            with (
                patch.object(batalha, "POKEMON_DATA_FILE", pokemon_file),
                patch.object(batalha, "POKEMON_SIZE_FILE", sizes_file),
            ):
                library = batalha.load_pokemon_library()

        self.assertEqual(
            library["PsyduckPersonalizado"]["tamanho"], "Colossal"
        )

    def test_fainted_active_pokemon_can_be_replaced_by_a_reserve(self):
        pokemon = dict(POKEMON_LIBRARY["Psyduck"])
        team = [
            {
                "battler": batalha.create_battler(pokemon),
                "moves": batalha.get_moves(pokemon),
            }
            for _ in range(3)
        ]
        team[0]["battler"]["hp"] = 0
        player = {"name": "Treinador", "team": team, "active": [0, 1], "active_limit": 2}

        with redirect_stdout(StringIO()), patch("builtins.input", return_value="1"):
            batalha.replace_fainted(player)

        self.assertEqual(player["active"], [1, 2])

    def test_trainer_can_select_a_target_in_a_multi_pokemon_battle(self):
        first_pokemon = dict(POKEMON_LIBRARY["Psyduck"])
        second_pokemon = dict(POKEMON_LIBRARY["Morpeko"])
        player = {
            "name": "Treinador",
            "team": [
                {
                    "battler": batalha.create_battler(first_pokemon),
                    "moves": batalha.get_moves(first_pokemon),
                }
            ],
            "active": [0],
        }
        opponent = {
            "team": [
                {"battler": batalha.create_battler(second_pokemon)},
                {"battler": batalha.create_battler(second_pokemon)},
            ],
            "active": [0, 1],
        }
        with redirect_stdout(StringIO()), patch(
            "builtins.input", side_effect=["1", "2"]
        ):
            action = batalha.choose_action(player, opponent, 0)

        self.assertEqual(action[0], "move")
        self.assertEqual(action[2], 1)

    def test_item_registration_saves_data_without_adding_battle_effects(self):
        with TemporaryDirectory() as temp_directory:
            items_file = Path(temp_directory) / "itens.json"
            with patch.object(batalha, "ITEM_DATA_FILE", items_file), patch(
                "builtins.input", side_effect=["Poção de teste", "Recupera HP"]
            ), redirect_stdout(StringIO()):
                batalha.register_item()

            items = batalha.load_json_file(items_file, [])

        self.assertEqual(items, [{"nome": "Poção de teste", "descrição": "Recupera HP"}])

    def test_one_two_and_three_active_pokemon_battles_finish(self):
        for active_count in (1, 2, 3):
            with self.subTest(active_count=active_count):
                initial_answers = iter(
                    [str(active_count), "Azul", "Vermelho"]
                )

                def answer_prompt(_prompt=""):
                    return next(initial_answers, "1")

                output = StringIO()
                with redirect_stdout(output), patch(
                    "builtins.input", side_effect=answer_prompt
                ), patch("batalha.random.uniform", return_value=1.05):
                    batalha.battle()

                self.assertIn("venceu a batalha!", output.getvalue())


if __name__ == "__main__":
    unittest.main()
