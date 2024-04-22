# Convert times to a readable format
def seconds_to_readable(seconds_to_convert):
    working_seconds = seconds_to_convert

    days, working_seconds = divmod(working_seconds, 86400)
    hours, working_seconds = divmod(working_seconds, 3600)
    minutes, working_seconds = divmod(working_seconds, 60)
    seconds = working_seconds
    if "." in (fractional_seconds := str(seconds_to_convert)):
        milliseconds = int(fractional_seconds.split(".")[-1])
    else:
        milliseconds = 0

    readable = ""
    if days:
        readable += f"{days}d"
    if hours:
        readable += f"{hours}h"
    if minutes:
        readable += f"{minutes}m"
    if seconds:
        readable += f"{seconds}s"
    if milliseconds:
        readable += f"{milliseconds}ms"

    return readable