from contextvars import ContextVar

# hold tenant_id for current request
current_tenant: ContextVar[int | None] = ContextVar("current_tenant", default=None)
