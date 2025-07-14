class StringProcessor:
    """
    Processes strings by cleaning (removing spaces, slashes, question marks, and commas)
    and provides various case conversions. Handles None, empty, and non-string input.
    """

    def __init__(self, input_string=None):
        """
        Initializes the StringProcessor object.

        Args:
            input_string (Any, optional): The input to be processed. Defaults to None.
        """
        self.input_string = "" if input_string is None else str(input_string)
        self.cleaned_string = self._clean(self.input_string)

    @staticmethod
    def _clean(s: str) -> str:
        """
        Cleans the string by removing spaces, slashes, question marks, and commas.

        Args:
            s (str): The string to clean.

        Returns:
            str: The cleaned string.
        """
        if not s:
            return ""
        cleaned = " ".join(s.split())
        for char in ["/", "?", ","]:
            cleaned = cleaned.replace(char, "")
        return cleaned

    @property
    def uppercase(self) -> str:
        """Returns the cleaned string in uppercase."""
        return self.cleaned_string.upper()

    @property
    def lowercase(self) -> str:
        """Returns the cleaned string in lowercase."""
        return self.cleaned_string.lower()

    @property
    def title(self) -> str:
        """Returns the cleaned string in title case."""
        return self.cleaned_string.title()

    @property
    def capitalized(self) -> str:
        """Returns the cleaned string with only the first letter capitalized."""
        return self.cleaned_string.capitalize()

    def __str__(self):
        return self.cleaned_string


def currency_inr(amount):
    if amount is None:
        return "0.00"

    try:
        decimal_amount = float(amount)
        formatted = "{:,.2f}".format(decimal_amount)
        # Convert to Indian format
        parts = formatted.split(".")
        parts[0] = parts[0].replace(",", "")
        parts[0] = "{:,}".format(int(parts[0]))[::-1].replace(",", ",", 1)[::-1]
        return f"{'.'.join(parts)}"
    except:
        return f"{amount}"


def adjust_name(name, length=10):
    """Truncate or pad name to specified length"""
    if len(name) > length:
        return name[:length] + "..."
    return name.ljust(length)
