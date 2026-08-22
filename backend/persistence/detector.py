def calculate_persistence(
    detection_count,
    duration_hours,
    recurrence_frequency
):

    if (
        detection_count >= 5
        and duration_hours >= 24
    ):
        return "PERSISTENT"

    elif (
        detection_count >= 3
        or recurrence_frequency >= 2
    ):
        return "RECURRING"

    else:
        return "TEMPORARY"


def calculate_persistence_score(
    detection_count,
    duration_hours,
    recurrence_frequency
):

    score = 0

    # Detection frequency
    if detection_count >= 5:
        score += 30
    elif detection_count >= 3:
        score += 15

    # Duration
    if duration_hours >= 24:
        score += 40
    elif duration_hours >= 12:
        score += 20

    # Historical recurrence
    if recurrence_frequency >= 5:
        score += 30
    elif recurrence_frequency >= 2:
        score += 15

    return min(score, 100)