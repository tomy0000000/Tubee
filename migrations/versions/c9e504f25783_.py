"""empty message

Revision ID: c9e504f25783
Revises: 61889220ba8f
Create Date: 2019-05-15 17:06:47.104814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9e504f25783'
down_revision = '61889220ba8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('admin', sa.Boolean(), server_default='0', nullable=True))
        batch_op.drop_column('master')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('master', sa.BOOLEAN(), server_default=sa.text("'0'"), nullable=True))
        batch_op.drop_column('admin')

    # ### end Alembic commands ###
