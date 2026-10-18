from alembic import context
from sqlalchemy import create_engine

from scrolly.storage.tables import Base

config = context.config
url = config.get_main_option("sqlalchemy.url")
assert url is not None

engine = create_engine(url)
with engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()
engine.dispose()
