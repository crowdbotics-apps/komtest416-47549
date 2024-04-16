def perf_diff_time(start_time, end_time):
    return f"{round(end_time-start_time, 2)}s"


def value_exists(test_string: str) -> bool:
    cleaned_string = (
        test_string.strip() if isinstance(test_string, str) else test_string
    )
    return cleaned_string not in ("", "None", None)
