import re


def parse_runtime(runtime: str):
    # Parse "2h 08min" into 128
    hours, minutes = re.match(r"(\d+)h (\d+)min", runtime).groups()
    return int(hours) * 60 + int(minutes)
