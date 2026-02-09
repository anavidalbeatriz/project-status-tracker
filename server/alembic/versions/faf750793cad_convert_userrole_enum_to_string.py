"""convert userrole enum to string

Revision ID: faf750793cad
Revises: 001
Create Date: 2024-02-07 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'faf750793cad'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert enum column to VARCHAR
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE VARCHAR(20) 
        USING role::text;
    """)
    
    # Drop the enum type (optional, but cleans up)
    op.execute("DROP TYPE IF EXISTS userrole;")


def downgrade() -> None:
    # Recreate enum type
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'tech_lead', 'user');")
    
    # Convert back to enum
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole 
        USING role::userrole;
    """)
