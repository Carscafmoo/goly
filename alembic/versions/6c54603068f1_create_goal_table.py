"""create goal table

Revision ID: 6c54603068f1
Revises: 8d7360a6b016
Create Date: 2016-01-20 07:16:40.638951

"""

# revision identifiers, used by Alembic.
revision = '6c54603068f1'
down_revision = '8d7360a6b016'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'goal',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user', sa.Integer, sa.ForeignKey("user.id", onupdate="CASCADE"), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, index=True),
        sa.Column('frequency', sa.Enum('day', 'week', 'month', 'quarter', 'year'), nullable=False),
        sa.Column('target', sa.Integer, nullable=False),
        sa.Column('input_type', sa.Enum('binary', 'numeric'), nullable=False),
        sa.Column('active', sa.Boolean, nullable=False, default=True, index=True),
        sa.Column('created', sa.DateTime, nullable=False),
        sa.UniqueConstraint('user', 'name', name='uniq')
    )

def downgrade():
    op.drop_table('goal')
