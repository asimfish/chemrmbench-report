"""Select a real past observation/basis pair with a bounded measured age.

No simulator, state reconstruction, interpolation, or payload copies occur here.
History entries are (native_time, observation, action_basis). The original entry
is returned so observation and basis always come from the same recorded instant.
"""
from math import isfinite


class MissingEligibleObservation(RuntimeError):
    """Fail closed: learned control must not proceed using an out-of-bound frame."""


def select_observed(history, now, requested_age):
    """Nearest eligible age to request; exact ties choose the newer observation.

    Bounds use the actual stored floating-point timestamp difference, inclusive
    20..40 ms, with no epsilon expanding the accepted physical-age interval.
    Samples outside the past are never eligible. A requested age is a target,
    not a promise that a sample exists at exactly that age.
    """
    now = float(now)
    requested_age = float(requested_age)
    if not isfinite(now) or not isfinite(requested_age):
        raise ValueError('Nonfinite clock or requested observation age')
    if not .020 <= requested_age <= .040:
        raise ValueError('Requested age must be in inclusive 20..40 ms')
    eligible = []
    previous = None
    for index, entry in enumerate(history):
        timestamp = float(entry[0])
        if not isfinite(timestamp) or timestamp > now:
            raise ValueError('History contains a nonfinite or future timestamp')
        if previous is not None and timestamp <= previous:
            raise ValueError('History timestamps must be strictly increasing')
        previous = timestamp
        age = now-timestamp
        if .020 <= age <= .040:
            eligible.append((abs(age-requested_age), -timestamp, index, age))
    if not eligible:
        raise MissingEligibleObservation(
            f'No real history frame aged 20..40ms at native t={now!r}')
    _, _, index, age = min(eligible)
    entry = history[index]
    return entry, dict(history_index=index, native_time_s=now,
                       requested_age_s=requested_age,
                       selected_native_time_s=float(entry[0]),
                       actual_age_s=age, eligible_count=len(eligible),
                       selection='nearest_requested_age_tie_newer',
                       payload='original_observation_and_basis_pair')
