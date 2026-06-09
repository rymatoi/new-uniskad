import os


def is_feature_enabled(name, environ=None):
    """Return whether an opt-in feature flag has a conventional true value."""
    values = os.environ if environ is None else environ
    return values.get(name, '').lower() in {'1', 'true', 'yes', 'on'}
