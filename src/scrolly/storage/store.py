from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from scrolly.ports import Store
from scrolly.storage.settings import SqlSettings


def make_engine(db_file: Path) -> Engine:
    return create_engine(f"sqlite:///{db_file}")


class SqliteStores:
    """Opens one transaction per request: commit on success, roll back on error."""

    def __init__(self, engine: Engine) -> None:
        self._sessions = sessionmaker(engine, expire_on_commit=False)

    @contextmanager
    def __call__(self) -> Iterator[Store]:
        session: Session = self._sessions()
        try:
            yield Store(settings=SqlSettings(session), commit=session.commit)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
