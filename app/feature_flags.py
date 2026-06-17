import os


def is_feature_enabled(name, environ=None, default=False):
    """Return whether a feature flag has a conventional true value."""
    values = os.environ if environ is None else environ
    raw_value = values.get(name)
    if raw_value is None:
        return default
    return raw_value.lower() in {'1', 'true', 'yes', 'on'}
