"""Create user table

Revision ID: 8d7360a6b016
Revises: 
Create Date: 2016-01-09 11:57:48.609970

"""

# revision identifiers, used by Alembic.
revision = '8d7360a6b016'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('first_name', sa.String(50)),
        sa.Column('last_name', sa.String(50)),
        sa.Column('password', sa.String(160)),
        sa.Column('registered_on', sa.DateTime)
    )




def downgrade():
    op.drop_table('user')
