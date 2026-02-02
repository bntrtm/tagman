def str_tail_after(string, substring, include=True):
    stop_index = string.rfind(substring)
    if stop_index != -1:
        if include:
            result = string[stop_index:]
        else:
            result = string[stop_index + 1 :]
        return result
    else:
        return string

