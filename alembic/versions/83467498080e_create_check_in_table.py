"""Create check-in table

Revision ID: 83467498080e
Revises: 6c54603068f1
Create Date: 2016-02-06 12:36:18.605376

"""

# revision identifiers, used by Alembic.
revision = '83467498080e'
down_revision = '6c54603068f1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('timeframe', 
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('start', sa.DateTime, nullable=False),
        sa.Column('end', sa.DateTime, nullable=False),
        sa.Column('frequency', sa.Integer, sa.ForeignKey("frequency.id", onupdate="CASCADE"), nullable=False, index=True),
        sa.UniqueConstraint('start', 'end', name='uniq_tf'))

    op.create_table(
        'check_in',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('goal', sa.Integer, sa.ForeignKey("goal.id", onupdate="CASCADE"), nullable=False),
        sa.Column('timeframe', sa.Integer, sa.ForeignKey("timeframe.id", onupdate="CASCADE"), nullable=False),
        sa.Column('value', sa.Integer),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.UniqueConstraint('goal', 'timeframe', name='uniq_gi')
    )


def downgrade():
    op.drop_table('check_in')
    op.drop_table('timeframe')
