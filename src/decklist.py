import csv

from src.constants import EVIL_BRIGADES, GOOD_BRIGADES


class Decklist:

    def __init__(self, deck_file_path: str):
        # TODO change this to an ENV variable
        self.card_data_path = (
            "/Applications/LackeyCCG/plugins/Redemption/sets/carddata.txt"
        )
        self.deck_file_path = deck_file_path
        self.main_deck_list = []
        self.reserve_list = []
        self.has_reserve = False
        self._load_file()
        self.card_data = self._load_card_data()
        self.mapped_main_deck_list = self._map_card_metadata(self.main_deck_list)
        self.mapped_reserve_list = self._map_card_metadata(self.reserve_list)
        self._save_json("tbd2.json", self.mapped_reserve_list)
        self._save_json("tbd1.json", self.mapped_main_deck_list)
        self.deck_size = self._get_size_of(self.mapped_main_deck_list)
        self.reserve_size = self._get_size_of(self.mapped_reserve_list)
        if self.deck_size < 50:
            raise AssertionError(
                "Please load a deck_file that contains at least 50 cards in the main deck."
            )
        if self.reserve_size > 10:
            raise AssertionError(
                "Please load a deck_file that contains 10 or less cards in the reserve"
            )

    def _get_size_of(self, card_list: dict) -> int:
        n_cards = 0
        for card in card_list.values():
            n_cards += card["quantity"]
        return n_cards

    @staticmethod
    def normalize_apostrophes(text):
        """Replaces curly apostrophes with straight ones in the provided text."""
        return text.replace("\u2019", "'")

    def _save_json(self, filename: str, dictionary_to_save: dict):
        """Debugging tool used to inspect json file.s"""
        import json

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(dictionary_to_save, file, ensure_ascii=False, indent=4)

    def _load_file(self):
        """Parse the .txt file into internal variables."""
        with open(self.deck_file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("Tokens:"):
                    break
                if line.startswith("Reserve:"):
                    self.has_reserve = True
                    continue

                parts = line.split("\t", 1)
                if len(parts) > 1:
                    card_info = {
                        "quantity": int(parts[0].strip()),
                        "name": self.normalize_apostrophes(parts[1].strip()),
                    }
                    if self.has_reserve:
                        self.reserve_list.append(card_info)
                    else:
                        self.main_deck_list.append(card_info)

        if len(self.main_deck_list) == 0:
            raise AssertionError(
                "Please load a deck_file that contains at least one card in the main deck."
            )

    def _load_card_data(self) -> dict:
        """Take the data found in 'card_data_path' and load it into a csv."""
        card_database = {}
        with open(self.card_data_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter="\t")
            for row in reader:
                # Create a new dictionary with all keys converted to lower case
                row_with_lower_keys = {key.lower(): value for key, value in row.items()}
                normalized_name = self.normalize_apostrophes(
                    row_with_lower_keys["name"]
                )
                card_database[normalized_name] = row_with_lower_keys

        return card_database

    def _map_card_metadata(self, card_list: list[dict]) -> dict:
        """
        Maps the names of each card to the full card data from the loaded card database.

        Parameters:
            cards (list of dict): List of dictionaries where each dict contains the 'quantity' and 'name' of the card.

        Returns:
            dict: Dictionary where keys are card names and values are dictionaries of card data including quantity.
        """
        result = {}
        for card in card_list:
            card_name = card["name"]
            quantity = card["quantity"]
            if card_name in self.card_data:
                # Copy the card data to avoid mutating the original data.
                card_details = self.card_data[card_name].copy()
                card_details["quantity"] = quantity
                # brigade normalization
                card_details["brigade"] = self._normalize_brigade_field(card_details)
                result[card_name] = card_details
            else:
                print(
                    f"Could not find {card['name']}. Skipping loading it. Notify BaboonyTim."
                )

        return result

    def _normalize_brigade_field(self, card_details: dict) -> list:
        """Turn the brigades field into a list, handle good and evil gold."""
        brigade: str = card_details.get("brigade", "")
        alignment = card_details.get("alignment", "")
        card_name = card_details["name"]

        def handle_complex_brigades(brigade: str) -> list:
            if card_name == "Delivered":
                return ["Green", "Teal", "Evil Gold", "Pale Green"]
            elif card_name == "Eternal Judgment":
                return ["Green", "White", "Brown", "Crimson"]
            elif card_name == "Scapegoat (PoC)":
                return ["Teal", "Green", "Crimson"]
            elif card_name == "Zion":
                return ["Purple"]
            elif card_name == "Ashkelon":
                return ["Good Gold"]
            elif card_name == "Raamses":
                return ["White"]
            elif card_name == "Babel":
                return ["Blue"]
            elif card_name == "Sodom & Gomorrah":
                return ["Silver"]
            elif card_name == "City of Enoch":
                return ["Blue"]
            elif card_name == "Hebron":
                return ["Red"]
            elif card_name in ["Damascus (LoC)", "Damascus (Promo)"]:
                return ["Red"]
            elif card_name == "Bethlehem (Promo)":
                return ["White"]
            elif card_name == "Samaria":
                return ["Green"]
            elif card_name == "Ninevah":
                return ["Green"]
            elif card_name == "City of Refuge":
                return ["Teal"]
            elif card_name == "Jerusalem (GoC)":
                return ["Purple", "Good Gold", "White"]
            elif card_name == "Sychar (GoC)":
                return ["Good Gold", "Purple"]

            if "and" in brigade:
                brigade = brigade.split("and")
                return brigade[0].strip().split("/")
            if "(" in brigade:
                main_brigade, sub_brigades = brigade.split(" (")
                sub_brigades = sub_brigades.rstrip(")").split("/")
                if "/" in main_brigade:
                    main_brigade = main_brigade.strip().split("/")
                else:
                    main_brigade = [main_brigade]
                return main_brigade + sub_brigades
            elif "/" in brigade:
                return brigade.split("/")
            else:
                return [brigade]

        brigades_list = handle_complex_brigades(brigade)

        def replace_gold(brigades, replacement):
            return [replacement if b == "Gold" else b for b in brigades]

        def replace_multi(brigades, replacement):
            return [replacement if b == "Multi" else b for b in brigades]

        if "Multi" in brigades_list:
            if card_name == "Saul/Paul":
                brigades_list = ["Gray", "Good Multi"]
            elif alignment == "Good":
                brigades_list = replace_multi(brigades_list, "Good Multi")
            elif alignment == "Evil":
                brigades_list = replace_multi(brigades_list, "Evil Multi")
            # add handling for exceptions
            elif (
                alignment == "Neutral"
                and card_name == "Unified Language"
                or card_name == "Philosophy"
            ):
                brigades_list = ["Good Multi", "Evil Multi"]
            elif alignment == "Neutral":
                brigades_list = replace_multi(brigades_list, "Good Multi")

        if "Gold" in brigades_list:
            if alignment == "Good":
                brigades_list = replace_gold(brigades_list, "Good Gold")
            elif alignment == "Evil":
                brigades_list = replace_gold(brigades_list, "Evil Gold")
            elif alignment == "Neutral":
                if brigades_list[0] == "Gold" or card_name in [
                    "Fire Foxes",
                    "First Bowl of Wrath (RoJ)",
                    "Banks of the Nile/Pharaoh's Court",
                ]:
                    brigades_list = replace_gold(brigades_list, "Good Gold")
                else:
                    brigades_list = replace_gold(brigades_list, "Evil Gold")

        # Add assertions
        allowed_brigades = set(
            GOOD_BRIGADES + EVIL_BRIGADES + ["Good Multi", "Evil Multi", ""]
        )
        for brigade in brigades_list:
            assert (
                brigade in allowed_brigades
            ), f"Card {card_name} has an invalid brigade: {brigade}."

        return brigades_list
