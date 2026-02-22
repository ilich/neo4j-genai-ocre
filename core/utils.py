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


def record_to_dict(record, selector: str = "c") -> dict[str, str | int]:
    return {
        "record_id": record[selector]["record_id"],
        "title": record[selector]["title"],
        "date_range": record[selector]["date_range"],
        "from_year": record[selector]["from_year"],
        "to_year": record[selector]["to_year"],
        "object_type": record[selector]["object_type"],
        "description": record[selector]["description"],
    }