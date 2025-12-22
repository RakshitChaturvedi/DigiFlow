from datetime import datetime, timezone
from typing import Optional, Tuple, List

from sqlalchemy import select, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
)
from app.core.errors import DigiFlowException, ErrorCode
from app.core.security import hash_password


def create_user(db: Session, tenant_id: int, data: UserCreate) -> User:

    new_user = User(
        tenant_id=tenant_id,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        display_name=data.display_name,
        meta=data.meta,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="User email already exists"
        )


def get_user_by_id(db: Session, tenant_id: int, user_id: int) -> User:

    stmt = select(User).where(and_(User.id == user_id, User.tenant_id == tenant_id))

    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise DigiFlowException(code=ErrorCode.NOT_FOUND, message="User not found")

    return result


def list_users(
    db: Session,
    tenant_id: int,
    cursor: Optional[int],
    limit: int,
    search: Optional[str],
    sort: str,
) -> Tuple[List[User], Optional[int]]:

    stmt = select(User).where(User.tenant_id == tenant_id)

    # filtering
    if search:
        stmt = stmt.where(User.display_name.ilike(f"%{search}%"))

    # sorting
    if sort == "name_asc":
        stmt = stmt.order_by(asc(User.display_name))
    elif sort == "name_desc":
        stmt = stmt.order_by(desc(User.display_name))
    else:
        stmt = stmt.order_by(asc(User.id))

    # cursor pagination
    if cursor is not None:
        if sort in ["name_asc", "name_desc"]:
            raise DigiFlowException(
                code=ErrorCode.INVALID_INPUT,
                message="Cursor pagination not supported for name sorting",
            )
        else:
            stmt = stmt.where(User.id > cursor)

    stmt = stmt.limit(limit + 1)

    rows = db.execute(stmt).scalars().all()

    if len(rows) > limit:
        next_cursor = rows[-1].id
        rows = rows[:limit]
    else:
        next_cursor = None

    return rows, next_cursor


def update_user(
    db: Session,
    tenant_id: int,
    user_id: int,
    data: UserUpdate,
    if_unmodified_since: Optional[datetime],
) -> User:

    user = get_user_by_id(db, tenant_id, user_id)

    # optimistic concurrency check
    if if_unmodified_since and user.updated_at > if_unmodified_since:
        raise DigiFlowException(
            code=ErrorCode.CONFLICT, message="Resource was modified by another request"
        )

    if data.display_name is not None:
        user.display_name = data.display_name

    if data.meta is not None:
        user.meta = data.meta

    user.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise DigiFlowException(code=ErrorCode.CONFLICT, message="User update conflict")


def delete_user(db: Session, tenant_id: int, user_id: int) -> None:
    user = get_user_by_id(db, tenant_id, user_id)

    db.delete(user)
    db.commit()
