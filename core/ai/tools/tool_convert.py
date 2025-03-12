from core.ai.tools.base import ToolBaseClass, ToolError

class ConvertTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "convert",
                "description": "Convert given amount from one unit to the other",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount":    {"type": "float",  "description": "the amount to be converted" },
                        "unit_from": {"type": "string", "description": "the unit of the amount to be converted" },
                        "unit1_to":  {"type": "string", "description": "the destination unit" },
                    },
                    "required": ["amount", "unit_from", "unit_to"],
                },
            }
        }
        super().__init__(cfg, *args, pre_match=r"^convert", **kwargs)

        self._type_map = [[ "ounce", "pound", "gram", "kilo" ],
                          [ "milimeter", "centimeter", "decimeter", "meter", "kilometer", "inch", "yard", "mile" ],
                          [ "mililiter", "centiliter", "deciliter", "liter", "teaspoon", "tablespoon", "cup", "ounce" ] 
                         ]

        self._conv_map = {  "gram":  1,         # grams
                            "kilo":  1000,      # grams
                            "pound": 453.5924,  # grams
                            "ounce": 28.34952,  # grams

                            "milimeter":  1,        # milimeters
                            "centimeter": 10,       # milimeters
                            "decimeter":  100,      # milimeters
                            "meter":      1000,     # milimeters
                            "kilometer":  1000000,  # milimeters
                            "inch":       25.4,     # milimeters
                            "yard":       914.4,    # milimeters
                            "mile":       1609344,  # milimeters

                            "mililiter":  1,        # mililiters
                            "centiliter": 10,       # mililiters
                            "deciliter":  100,      # mililiters
                            "liter":      1000,     # mililiters
                            "teaspoon":   4.928906, # mililiters
                            "tablespoon": 14.78672, # mililiters
                            "cup":        236.5875, # mililiters
                            "ounce":      29.57344, # mililiters
                        }

        self._precision = 2

    def to_metric(self, u: str, n: float):
        """ Convert given amount to metric unit.
            Eg: mass to grams,
                length to mm,
                ...
                """
        for unit, amount in self._conv_map.items():
            if unit in u:
                return n * amount

    def metric_to_unit(self, n_metric: float, unit_to: str):
        """ Take result from to_metric() and convert it to destination unit """
        for unit, amount in self._conv_map.items():
            if unit in unit_to:
                return n_metric / amount

    def check_compatible(self, unit_from: str, unit_to: str):
        """ Check in type map if units are compatible. Eg: ounces to grams is ok but ounces to kilometers is not """
        for units in self._type_map:
            res_from = next((u for u in units if u in unit_from), None)
            res_to   = next((u for u in units if u in unit_to), None)
            if res_from and res_to:
                return True

    def call(self, amount: str, unit_from: str, unit_to: str) -> str:
        if not self.check_compatible(unit_from, unit_to):
            raise ToolError(f"I'm affraid I can't do that, {unit_from} and {unit_to} are incompatible units")

        amount_from = float(amount)
        amount_metric = self.to_metric(unit_from, amount_from)
        amount_dest = self.metric_to_unit(amount_metric, unit_to)

        return f"{amount} {unit_from} is {round(amount_dest, self._precision)} {unit_to}"
