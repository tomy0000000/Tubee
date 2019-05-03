"""empty message

Revision ID: ec78836de0d5
Revises: 
Create Date: 2019-04-25 00:32:08.537406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec78836de0d5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('apscheduler_jobs',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('next_run_time', sa.Float(precision=64), nullable=True),
    sa.Column('job_state', sa.LargeBinary(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apscheduler_jobs_next_run_time'), 'apscheduler_jobs', ['next_run_time'], unique=False)
    op.create_table('callback',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('received_datetime', sa.DateTime(), nullable=False),
    sa.Column('channel_id', sa.String(length=30), nullable=False),
    sa.Column('action', sa.String(length=30), nullable=False),
    sa.Column('details', sa.String(length=20), nullable=False),
    sa.Column('arguments', sa.JSON(), nullable=False),
    sa.Column('data', sa.Text(), nullable=False),
    sa.Column('user_agent', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('initiator', sa.String(length=15), nullable=False),
    sa.Column('sent_datetime', sa.DateTime(), nullable=False),
    sa.Column('message', sa.String(length=2000), nullable=False),
    sa.Column('kwargs', sa.JSON(), nullable=False),
    sa.Column('response', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('request',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('received_datetime', sa.DateTime(), nullable=False),
    sa.Column('method', sa.String(length=10), nullable=False),
    sa.Column('path', sa.String(length=100), nullable=False),
    sa.Column('arguments', sa.JSON(), nullable=False),
    sa.Column('data', sa.Text(), nullable=False),
    sa.Column('user_agent', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscription',
    sa.Column('channel_id', sa.String(length=30), nullable=False),
    sa.Column('channel_name', sa.String(length=100), nullable=False),
    sa.Column('thumbnails_url', sa.String(length=200), nullable=True),
    sa.Column('country', sa.String(length=5), nullable=True),
    sa.Column('language', sa.String(length=5), nullable=True),
    sa.Column('custom_url', sa.String(length=100), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('subscribe_datetime', sa.DateTime(), nullable=False),
    sa.Column('renew_datetime', sa.DateTime(), nullable=False),
    sa.Column('unsubscribe_datetime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('channel_id')
    )
    op.create_table('user',
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('password', sa.String(length=70), nullable=False),
    sa.Column('master', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('pushover_key', sa.String(length=40), server_default='', nullable=True),
    sa.Column('youtube_credentials', sa.JSON(), server_default='{}', nullable=True),
    sa.PrimaryKeyConstraint('username')
    )
    op.create_table('user-subscription',
    sa.Column('subscriber_username', sa.String(length=30), nullable=False),
    sa.Column('subscribing_channel_id', sa.String(length=30), nullable=False),
    sa.Column('tags', sa.PickleType(), nullable=True),
    sa.ForeignKeyConstraint(['subscriber_username'], ['user.username'], ),
    sa.ForeignKeyConstraint(['subscribing_channel_id'], ['subscription.channel_id'], ),
    sa.PrimaryKeyConstraint('subscriber_username', 'subscribing_channel_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user-subscription')
    op.drop_table('user')
    op.drop_table('subscription')
    op.drop_table('request')
    op.drop_table('notification')
    op.drop_table('callback')
    op.drop_index(op.f('ix_apscheduler_jobs_next_run_time'), table_name='apscheduler_jobs')
    op.drop_table('apscheduler_jobs')
    # ### end Alembic commands ###