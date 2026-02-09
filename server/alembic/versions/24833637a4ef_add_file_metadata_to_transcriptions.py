"""add_file_metadata_to_transcriptions

Revision ID: 24833637a4ef
Revises: 00e4b9770b55
Create Date: 2026-02-07 11:00:20.889083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24833637a4ef'
down_revision = '00e4b9770b55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to transcriptions table
    op.add_column('transcriptions', sa.Column('file_name', sa.String(), nullable=True))
    op.add_column('transcriptions', sa.Column('file_type', sa.String(), nullable=True))
    op.add_column('transcriptions', sa.Column('file_size', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove columns from transcriptions table
    op.drop_column('transcriptions', 'file_size')
    op.drop_column('transcriptions', 'file_type')
    op.drop_column('transcriptions', 'file_name')
