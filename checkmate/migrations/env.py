from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

from blitzdb.backends.sql import Backend as SqlBackend
from checkmate.management.helpers import get_project_config,get_backend,get_project_path

config = context.config
fileConfig(config.config_file_name)

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    project_path = get_project_path()
    project_config = get_project_config(project_path)
    backend = get_backend(project_path,project_config,initialize_db = False)
    url = str(backend.engine.url)
    with backend.transaction():
        context.configure(
            connection=backend.connection,
            url=url, target_metadata=backend.metadata,
            literal_binds=True)

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    print("Running migrations online")

    project_path = get_project_path()
    project_config = get_project_config(project_path)

    backend = get_backend(project_path,project_config,initialize_db = False)

    context.configure(
        connection=backend.connection,
        target_metadata=backend.metadata,
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
