"""add optimized tenant indexes for group A entities

Revision ID: 90bc8b2887dd
Revises: 5a126fbc9f38
Create Date: 2025-12-08 17:15:28.304181

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "90bc8b2887dd"
down_revision: Union[str, Sequence[str], None] = "5a126fbc9f38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # USERS
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_users_tenant_id_id'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_users_tenant_id_id ON users (tenant_id, id);
        END IF;
    END$$;
    """
    )
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_users_tenant_role'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_users_tenant_role ON users (tenant_id, role);
        END IF;
    END$$;
    """
    )

    # PRODUCTS
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_products_tenant_id_id'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_products_tenant_id_id ON products (tenant_id, id);
        END IF;
    END$$;
    """
    )
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_products_tenant_name'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_products_tenant_name ON products (tenant_id, name);
        END IF;
    END$$;
    """
    )

    # MACHINES
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_machines_tenant_id_id'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_machines_tenant_id_id ON machines (tenant_id, id);
        END IF;
    END$$;
    """
    )
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_machines_tenant_name'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_machines_tenant_name ON machines (tenant_id, name);
        END IF;
    END$$;
    """
    )

    # ROUTINGS
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_routings_tenant_id_id'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_routings_tenant_id_id ON routings (tenant_id, id);
        END IF;
    END$$;
    """
    )
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_routings_tenant_name'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_routings_tenant_name ON routings (tenant_id, name);
        END IF;
    END$$;
    """
    )
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'uq_routings_tenant_product_version'
        ) THEN
            ALTER TABLE routings
            ADD CONSTRAINT uq_routings_tenant_product_version
            UNIQUE (tenant_id, product_id, version);
        END IF;
    END$$;
    """
    )

    # ORDERS
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_orders_tenant_id_id'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_orders_tenant_id_id ON orders (tenant_id, id);
        END IF;
    END$$;
    """
    )
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_orders_tenant_due_date'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_orders_tenant_due_date ON orders (tenant_id, due_date);
        END IF;
    END$$;
    """
    )

    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_orders_tenant_external_id'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_orders_tenant_external_id ON orders (tenant_id, external_id);
        END IF;
    END$$;
    """
    )

    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_orders_tenant_priority'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_orders_tenant_priority ON orders (tenant_id, priority);
        END IF;
    END$$;
    """
    )

    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'idx_orders_tenant_status'
            AND n.nspname = 'public'
        ) THEN
            CREATE INDEX idx_orders_tenant_status ON orders (tenant_id, status);
        END IF;
    END$$;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
