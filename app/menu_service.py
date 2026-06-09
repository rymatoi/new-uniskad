"""Session-level access to database-controlled application menus."""

import hashlib
from threading import RLock

from app import app_logger

logger = app_logger.get_logger(__name__)


class MenuService:
    """Load each authorized menu once per session while preserving schema objects.

    Cached menu lists are shallow-copied on return so callers may filter or
    append entries without changing the shared cached list. The menu schema
    objects themselves are intentionally preserved for compatibility with the
    existing action-building code.
    """

    def __init__(self, loader=None, context_provider=None):
        self._loader = loader
        # Injected loaders are primarily used by isolated tests/tools that do
        # not initialize the application's database Session.
        if context_provider is not None:
            self._context_provider = context_provider
        elif loader is not None:
            self._context_provider = lambda: None
        else:
            self._context_provider = self._session_context
        self._cache = {}
        self._authorization_generation = 0
        self._lock = RLock()

    def _load_menu(self, mode, location):
        if self._loader is not None:
            return self._loader(mode, location)

        # Import lazily to avoid a db -> app.menu_service -> db cycle while the
        # process-wide database Session is being initialized.
        from db import sp

        return sp.get_user_menu_(mode, location)

    @staticmethod
    def _session_context():
        # The active database role/grants are changed server-side and do not
        # have a stable local identifier. Those changes call ``clear()``, which
        # advances the generation included in every key. Login and Session
        # identity additionally prevent accidental reuse between sessions.
        from db import session

        return id(session), getattr(session, '_login', None)

    def _authorization_context(self):
        """Return non-secret state that separates authorization contexts."""
        return self._context_provider()

    @staticmethod
    def _context_fingerprint(context):
        """Return a diagnostic-safe identifier without logging login details."""
        return hashlib.sha256(repr(context).encode('utf-8')).hexdigest()[:12]

    def _cache_key(self, mode, location):
        context = self._authorization_context()
        try:
            hash(context)
        except TypeError:
            context = repr(context)
        return self._authorization_generation, context, mode, location

    def _diagnostic_key(self, key):
        generation, context, _mode, _location = key
        return 'auth={}:{}'.format(generation, self._context_fingerprint(context))

    def get_menu(self, mode, location):
        """Return the authorized menu for the current context and location.

        Only valid lists are cached. Database errors, ``None``, and other
        unexpected values are returned unchanged and retried on the next call.
        """
        with self._lock:
            key = self._cache_key(mode, location)
            diagnostic_key = self._diagnostic_key(key)
            cached = self._cache.get(key)
            if cached is not None:
                logger.info(
                    "Menu cache HIT: mode=%s, location=%s, key=%s",
                    mode, location, diagnostic_key,
                )
                return list(cached)

            logger.info(
                "Menu cache MISS: mode=%s, location=%s, key=%s",
                mode, location, diagnostic_key,
            )
            menu = self._load_menu(mode, location)
            if isinstance(menu, list):
                self._cache[key] = list(menu)
                return list(menu)

            logger.warning(
                "Menu result not cached: mode=%s, location=%s, key=%s, result_type=%s",
                mode, location, diagnostic_key, type(menu).__name__,
            )
            return menu

    def clear(self, reason="unspecified"):
        """Discard all cached menus after session authorization state changes."""
        with self._lock:
            entry_count = len(self._cache)
            self._cache.clear()
            self._authorization_generation += 1
        logger.info("Menu cache CLEARED: reason=%s, entries=%s", reason, entry_count)


menu_service = MenuService()


def get_menu(mode, location):
    """Return a menu through the process-wide session menu service."""
    return menu_service.get_menu(mode, location)


def clear_menu_cache(reason="unspecified"):
    """Clear the process-wide session menu cache."""
    menu_service.clear(reason)
