"""empty message

Revision ID: b4a059acf2ef
Revises: f28a243e95f2
Create Date: 2019-11-04 22:46:51.343158

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b4a059acf2ef'
down_revision = 'f28a243e95f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('_password_hash')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_password_hash', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=128), nullable=False))

    # ### end Alembic commands ###
