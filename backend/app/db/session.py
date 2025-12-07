from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.tenant_context import current_tenant
from app.core.config import settings
from app.db import base  # noqa: F401

engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)


# tenant binding sql events
@event.listens_for(engine, "connect")
def set_tenant_on_connect(dbapi_connection, connection_record):
    tenant_id = current_tenant.get()
    cursor = dbapi_connection.cursor()

    if tenant_id is None:
        cursor.execute("RESET app.current_tenant;")
    else:
        cursor.execute("SET app.current_tenant = %s;", (tenant_id,))
    cursor.close()


@event.listens_for(engine, "checkout")
def set_tenant_on_checkout(dbapi_connection, connection_record, connection_proxy):
    tenant_id = current_tenant.get()

    cursor = dbapi_connection.cursor()

    if tenant_id is None:
        cursor.execute("RESET app.current_tenant;")
    else:
        cursor.execute("SET app.current_tenant = %s;", (tenant_id,))

    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
