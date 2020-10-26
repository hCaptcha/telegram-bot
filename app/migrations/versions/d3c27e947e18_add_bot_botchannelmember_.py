"""Add bot, botchannelmember, humanchannelmember table

Revision ID: d3c27e947e18
Revises: b4ea7b2c0b57
Create Date: 2020-10-22 01:31:34.220398

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d3c27e947e18"
down_revision = "b4ea7b2c0b57"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "bots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("user_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "bots_channels",
        sa.Column("bot_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bot_id"], ["bots.id"],),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"],),
        sa.PrimaryKeyConstraint("bot_id", "channel_id"),
    )
    op.create_table(
        "humans_channels",
        sa.Column("human_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"],),
        sa.ForeignKeyConstraint(["human_id"], ["humans.id"],),
        sa.PrimaryKeyConstraint("human_id", "channel_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("humans_channels")
    op.drop_table("bots_channels")
    op.drop_table("bots")
    # ### end Alembic commands ###
