
"""remove legacy remainder sent column

Revision ID: b3c8d9e1f2a4
Revises: 74a906532a04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3c8d9e1f2a4"
down_revision: Union[str, Sequence[str], None] = "74a906532a04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Preserve reminder state and remove the legacy column."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)

    columns = {
        column["name"]
        for column in inspector.get_columns("tasks")
    }

    # Existing databases may still contain the legacy column.
    # Fresh databases created from the initial migration won't.
    if "remainder_sent" in columns:

        # Preserve previously sent reminder information.
        connection.execute(
            sa.text("""
                UPDATE tasks
                SET reminder_sent = 1
                WHERE remainder_sent = 1
                  AND reminder_sent = 0
            """)
        )

        # SQLite uses batch mode to safely alter existing tables.
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.drop_column("remainder_sent")


def downgrade() -> None:
    """Restore the legacy column if rolling back."""

    connection = op.get_bind()
    inspector = sa.inspect(connection)

    columns = {
        column["name"]
        for column in inspector.get_columns("tasks")
    }

    if "remainder_sent" not in columns:

        with op.batch_alter_table("tasks") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "remainder_sent",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("0"),
                )
            )

        # Restore the merged reminder state into the legacy column.
        connection.execute(
            sa.text("""
                UPDATE tasks
                SET remainder_sent = reminder_sent
            """)
        )
