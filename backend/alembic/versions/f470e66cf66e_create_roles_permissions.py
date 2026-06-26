"""create roles permissions dummy migration

Revision ID: f470e66cf66e
Revises: a1b2c3d4e5f6
Create Date: 2026-06-24 10:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f470e66cf66e'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Tables already exist in remote database, so this is a dummy migration
    pass

def downgrade() -> None:
    pass
