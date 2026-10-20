from scrolly.domain.archive import Tables
from scrolly.ports import Store


def current_tables(store: Store) -> Tables:
    """Everything the app holds, as tables, for Backup Scroll."""
    return store.archive.dump()
