"""empty message

Revision ID: a75db9cca46a
Revises: e13dbff2119a
Create Date: 2024-10-27 02:06:37.575922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a75db9cca46a'
down_revision = 'e13dbff2119a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cover_image', sa.String(length=255), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_pic', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('profile_pic')

    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.drop_column('cover_image')

    # ### end Alembic commands ###
