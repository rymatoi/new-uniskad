"""Session-level access to database-controlled application menus."""

from threading import RLock

from app import app_logger

logger = app_logger.get_logger(__name__)


class MenuService:
    """Load each menu once per session while preserving schema objects.

    Cached menu lists are shallow-copied on return so callers may filter or
    append entries without changing the shared cached list. The menu schema
    objects themselves are intentionally preserved for compatibility with the
    existing action-building code.
    """

    def __init__(self, loader=None):
        self._loader = loader
        self._cache = {}
        self._lock = RLock()

    def _load_menu(self, mode, location):
        if self._loader is not None:
            return self._loader(mode, location)

        # Import lazily to avoid a db -> app.menu_service -> db cycle while the
        # process-wide database Session is being initialized.
        from db import sp

        return sp.get_user_menu_(mode, location)

    def get_menu(self, mode, location):
        """Return the authorized menu for ``(mode, location)``.

        Only valid lists are cached. Database errors, ``None``, and other
        unexpected values are returned unchanged and retried on the next call.
        """
        key = (mode, location)
        with self._lock:
            cached = self._cache.get(key)
            if cached is not None:
                logger.debug("Menu cache hit: mode=%s, location=%s", mode, location)
                return list(cached)

            logger.debug("Menu cache miss: mode=%s, location=%s", mode, location)
            menu = self._load_menu(mode, location)
            if isinstance(menu, list):
                self._cache[key] = list(menu)
                return list(menu)

            logger.warning(
                "Menu result not cached: mode=%s, location=%s, result_type=%s",
                mode,
                location,
                type(menu).__name__,
            )
            return menu

    def clear(self, reason="unspecified"):
        """Discard all cached menus after session authorization state changes."""
        with self._lock:
            entry_count = len(self._cache)
            self._cache.clear()
        logger.info("Menu cache cleared: reason=%s, entries=%s", reason, entry_count)


menu_service = MenuService()


def get_menu(mode, location):
    """Return a menu through the process-wide session menu service."""
    return menu_service.get_menu(mode, location)


def clear_menu_cache(reason="unspecified"):
    """Clear the process-wide session menu cache."""
    menu_service.clear(reason)
