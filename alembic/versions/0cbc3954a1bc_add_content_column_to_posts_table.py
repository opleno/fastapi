"""add content column to posts table

Revision ID: 0cbc3954a1bc
Revises: 963b6c261488
Create Date: 2022-10-26 17:47:04.064684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cbc3954a1bc'
down_revision = '963b6c261488'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
