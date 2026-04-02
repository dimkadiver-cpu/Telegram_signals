# Alembic env.py – configure as needed after running `alembic init`
# This file is a placeholder; run `alembic init src/db/migrations` to generate full config.
from logging.config import fileConfig
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models here so Alembic can detect changes
# from src.db.models import *  # noqa: F401, F403
target_metadata = None


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # For async engines use a sync wrapper or connectable
    pass
