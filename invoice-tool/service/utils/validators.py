from datetime import datetime

def validate_year_and_month(input_str:str)->str:
    """Checks if input string is a valid year and month in format YYYY-MM

    Params
    ----------
    input_str: str
        input string to be validated

    Returns
    -------
    input_str: str
        same input string that is passed in case if it is valid

    Raises
    ------
    ValueError
        If the input_str is not a string or is empty
    """

    if type(input_str) != str or not input_str.strip():
        raise ValueError("must be a valid year and month. Format: YYYY-MM")

    try:
        datetime.strptime(input_str, "%Y-%m")
    except ValueError:
        raise ValueError("must be a valid year and month. Format: YYYY-MM")

    return input_str
