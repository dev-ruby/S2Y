def duration_to_seconds(duration_str: str) -> int:
    """Convert a duration string to total seconds.

    Args:
        duration_str (str): Duration string in the format "HH:MM:SS", "MM:SS", or "SS".

    Returns:
        int: Total duration in seconds.
    """
    parts = duration_str.split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        h, m, s = 0, 0, parts[0]
    return h * 3600 + m * 60 + s


def seconds_to_duration(seconds: int) -> str:
    """Convert total seconds to a duration string.

    Args:
        seconds (int): Total duration in seconds.

    Returns:
        str: Duration string in the format "HH:MM:SS", "MM:SS", or "SS".
    """
    if seconds < 0:
        return "00:00:00"

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    else:
        return f"{m:02}:{s:02}" if m > 0 else f"{s:02}"
