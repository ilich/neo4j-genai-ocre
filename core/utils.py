from loguru import logger


def parse_year(year_str: str) -> int:
    try:
        parts = year_str.split(" ")
        if len(parts) == 1:
            return int(parts[0])
        else:
            year, era = parts[0], parts[1].lower()
            year_int = int(year)
            if era in ["bc", "bce"]:
                return -year_int
            else:
                return year_int
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse year from string '{year_str}': {e}")
        return 0
