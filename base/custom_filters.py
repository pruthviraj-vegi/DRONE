from django import template
import locale
import base64
from num2words import num2words

locale.setlocale(locale.LC_ALL, "en_IN")

register = template.Library()


@register.filter(name="currency_format")
def currency_format(value, arg=None):
    try:
        formate = {
            "grouping": True,  # Enable thousands grouping
            "grouping_threshold": 3,  # Group digits in threes
            "decimal_point": ".",  # Use dot as the decimal separator
            "frac_digits": 2,  # Show 2 digits after the decimal point
        }

        return locale.format_string(
            "%%.%df" % formate["frac_digits"],
            value,
            grouping=formate["grouping"],
            monetary=False,
        )
    except (TypeError, ValueError) as e:
        return value


@register.filter(name="nonDecimal_format")
def currency_nonDecimal(value, arg=None):
    try:
        formate = {
            "grouping": True,  # Enable thousands grouping
            "grouping_threshold": 3,  # Group digits in threes
            "decimal_point": ".",  # Use dot as the decimal separator
            "frac_digits": 2,  # Show 2 digits after the decimal point
        }

        # Cast value to integer to remove decimals
        value_int = int(value)

        return locale.format_string(
            "%d",
            value_int,
            grouping=formate["grouping"],
            monetary=False,
        )
    except (TypeError, ValueError) as e:
        # Log or handle exceptions as needed
        return value


@register.filter(name="numberToWords")
def numberToWords(value, arg=None):
    try:
        amount = float(value)
        return num2words(amount, lang="en_IN", to="currency", currency="INR").title()
    except BaseException as e:
        print(e)
        return value


@register.filter(name="phoneNo")
def phoneNo(value, arg=None):
    if value is None:
        return ""
    try:
        numbers = value.replace(" ", "")
        return f"{numbers[:5]} {numbers[5:]}" if len(numbers) == 10 else numbers
    except (TypeError, ValueError) as e:
        return value


@register.filter
def add_class(path, expected_path):
    return "active" if path == expected_path else ""


@register.filter
def startWith(path, expected_path):
    return "active" if path.startswith(expected_path) else ""


@register.filter(name="b64encode")
def base64_encode(value):
    return base64.b64encode(value).decode("utf-8")


@register.filter(name="trim")
def trim(value):
    """Removes all whitespace from a string"""
    if value:
        return str(value).strip().replace("\n", "").replace("\r", "").replace(" ", "")
    return value


@register.filter(name="has_role")
def has_role(user, roles):
    """
    Template filter to check if a user has one of the specified roles.
    Usage: {% if request.user|has_role:'admin,manager' %}
    """
    if not hasattr(user, "role"):
        return False
    user_roles = [role.strip() for role in roles.split(",")]
    return user.role in user_roles


@register.filter(name="range")
def range_filter(value):
    """Creates a range from 0 to value-1"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter(name="divideby")
def divideby(value, arg=None):
    return round(value / arg, 2)


@register.filter(name="status_badge")
def status_badge(value):
    if str(value).lower() in ["active", "success", "true", "accepted"]:
        return "badge bg-success"
    elif str(value).lower() in ["inactive", "error", "danger", "false", "rejected"]:
        return "badge bg-danger"
    elif str(value).lower() in ["pending", "warning"]:
        return "badge bg-warning"
    else:
        return "badge bg-secondary"
