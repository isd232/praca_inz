"""remove fav color

Revision ID: 13ed33617346
Revises: 018f57663a3c
Create Date: 2024-05-13 02:42:17.719614

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '13ed33617346'
down_revision = '018f57663a3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('favorite_color')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_color', mysql.VARCHAR(length=120), nullable=True))

    # ### end Alembic commands ###