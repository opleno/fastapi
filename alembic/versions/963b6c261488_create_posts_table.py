"""create posts table

Revision ID: 963b6c261488
Revises: 
Create Date: 2022-10-26 17:31:20.521666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '963b6c261488'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('posts',
                    sa.Column('id', sa.Integer(),
                              nullable=False, primary_key=True),
                    sa.Column('title', sa.String(), nullable=False)
                    )
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
