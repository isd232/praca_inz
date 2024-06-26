"""added profile pic

Revision ID: 018f57663a3c
Revises: 0518764abce2
Create Date: 2024-05-12 19:11:12.887347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '018f57663a3c'
down_revision = '0518764abce2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_pic', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('profile_pic')

    # ### end Alembic commands ###
