from fastapi import HTTPException, status, Depends
from functools import wraps

from app.schemas.current_user import CurrentUser
from app.api.v1.dependencies.get_current_user import get_current_user


ROLE_HEIRARCHY = {
    "superadmin": 4,
    "tenant_admin": 3,
    "manager": 2,
    "operator": 1,
    "integrator": 1,
}


def has_privilege(user_role: str, required_role: str) -> bool:
    # return true if users role >= required role
    if user_role not in ROLE_HEIRARCHY or required_role not in ROLE_HEIRARCHY:
        return False
    return ROLE_HEIRARCHY[user_role] >= ROLE_HEIRARCHY[required_role]


def require_role(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(
            *args, current_user: CurrentUser = Depends(get_current_user), **kwargs
        ):
            if not has_privilege(current_user.role, required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
                )
            return func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


def require_exact_role(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(
            *args, current_user: CurrentUser = Depends(get_current_user), **kwargs
        ):
            if current_user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
                )
            return func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


def require_role_withing(required_role: str, allowed_roles: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(
            *args, current_user: CurrentUser = Depends(get_current_user), **kwargs
        ):
            if not has_privilege(current_user.role, required_role):
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
            if current_user.role not in allowed_roles:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")

            return func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
