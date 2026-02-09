"""add_clients_table

Revision ID: 00e4b9770b55
Revises: faf750793cad
Create Date: 2026-02-07 10:48:11.545959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00e4b9770b55'
down_revision = 'faf750793cad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    # Step 1: Create clients table (if it doesn't exist)
    if 'clients' not in tables:
        op.create_table(
            'clients',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
        op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=True)
    
    # Check if projects table has client_id column
    projects_columns = [col['name'] for col in inspector.get_columns('projects')]
    has_client_id = 'client_id' in projects_columns
    has_client = 'client' in projects_columns
    
    # Step 2: Migrate existing client data from projects to clients table (if client column exists)
    if has_client and not has_client_id:
        # Get distinct client names from projects and insert them
        result = connection.execute(sa.text("SELECT DISTINCT client FROM projects WHERE client IS NOT NULL"))
        client_names = [row[0] for row in result]
        
        # Insert unique clients (using a set to avoid duplicates)
        seen_clients = set()
        for client_name in client_names:
            if client_name and client_name not in seen_clients:
                # Check if client already exists
                existing = connection.execute(
                    sa.text("SELECT id FROM clients WHERE name = :name"),
                    {"name": client_name}
                ).fetchone()
                if not existing:
                    connection.execute(
                        sa.text("INSERT INTO clients (name) VALUES (:name)"),
                        {"name": client_name}
                    )
                seen_clients.add(client_name)
    
    # Step 3: Add client_id column to projects (if it doesn't exist)
    if not has_client_id:
        op.add_column('projects', sa.Column('client_id', sa.Integer(), nullable=True))
        
        # Step 4: Populate client_id based on client name
        if has_client:
            connection.execute(sa.text("""
                UPDATE projects 
                SET client_id = (
                    SELECT id FROM clients WHERE clients.name = projects.client
                )
                WHERE client IS NOT NULL
            """))
        
        # Step 5: Make client_id NOT NULL
        op.alter_column('projects', 'client_id', nullable=False)
        
        # Step 6: Add foreign key constraint
        op.create_foreign_key('fk_projects_client_id', 'projects', 'clients', ['client_id'], ['id'])
        
        # Step 7: Drop the old client column
        if has_client:
            op.drop_column('projects', 'client')


def downgrade() -> None:
    # Step 1: Add back client column
    op.add_column('projects', sa.Column('client', sa.String(), nullable=True))
    
    # Step 2: Populate client column from clients table
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE projects 
        SET client = (
            SELECT name FROM clients WHERE clients.id = projects.client_id
        )
        WHERE client_id IS NOT NULL
    """))
    
    # Step 3: Make client NOT NULL
    op.alter_column('projects', 'client', nullable=False)
    
    # Step 4: Drop foreign key constraint
    op.drop_constraint('fk_projects_client_id', 'projects', type_='foreignkey')
    
    # Step 5: Drop client_id column
    op.drop_column('projects', 'client_id')
    
    # Step 6: Drop clients table
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_table('clients')
