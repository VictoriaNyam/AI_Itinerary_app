"""Initial migration

Revision ID: bebe2114e797
Revises: 
Create Date: 2025-05-05 14:00:07.204313
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bebe2114e797'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # comment table
    with op.batch_alter_table('comment', schema=None) as batch_op:
        # Commented out to prevent error: No such constraint
        # batch_op.drop_constraint('comment_user_id_fkey', type_='foreignkey')
        # batch_op.drop_constraint('comment_upload_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('comment_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('comment_upload_id_fkey', 'upload', ['upload_id'], ['id'], ondelete='CASCADE')

    # itinerary table
    with op.batch_alter_table('itinerary', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('itinerary_user_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        batch_op.create_foreign_key('itinerary_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()))

    # like table
    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.drop_constraint('like_upload_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('like_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('like_upload_id_fkey', 'upload', ['upload_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('like_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')

    # poi table
    with op.batch_alter_table('poi', schema=None) as batch_op:
        batch_op.alter_column('name',
            existing_type=sa.VARCHAR(length=100),
            type_=sa.String(length=255),
            existing_nullable=False)
        batch_op.alter_column('address',
            existing_type=sa.TEXT(),
            type_=sa.String(length=255),
            existing_nullable=True)
        batch_op.alter_column('latitude',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.Float(),
            existing_nullable=True)
        batch_op.alter_column('longitude',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.Float(),
            existing_nullable=True)
        try:
            batch_op.drop_constraint('poi_itinerary_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        batch_op.create_foreign_key('poi_itinerary_id_fkey', 'itinerary', ['itinerary_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('original_longitude')
        batch_op.drop_column('original_latitude')

    # upload table
    with op.batch_alter_table('upload', schema=None) as batch_op:
        batch_op.alter_column('vlog_title',
            existing_type=sa.TEXT(),
            type_=sa.String(length=120),
            existing_nullable=True)
        try:
            batch_op.drop_constraint('upload_user_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        batch_op.create_foreign_key('upload_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # upload table
    with op.batch_alter_table('upload', schema=None) as batch_op:
        batch_op.drop_constraint('upload_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('upload_user_id_fkey', 'user', ['user_id'], ['id'])
        batch_op.alter_column('vlog_title',
            existing_type=sa.String(length=120),
            type_=sa.TEXT(),
            existing_nullable=True)

    # poi table
    with op.batch_alter_table('poi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('original_latitude', sa.REAL(), nullable=True))
        batch_op.add_column(sa.Column('original_longitude', sa.REAL(), nullable=True))
        try:
            batch_op.drop_constraint('poi_itinerary_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        batch_op.create_foreign_key('poi_itinerary_id_fkey', 'itinerary', ['itinerary_id'], ['id'])
        batch_op.alter_column('longitude',
            existing_type=sa.Float(),
            type_=sa.VARCHAR(length=50),
            existing_nullable=True)
        batch_op.alter_column('latitude',
            existing_type=sa.Float(),
            type_=sa.VARCHAR(length=50),
            existing_nullable=True)
        batch_op.alter_column('address',
            existing_type=sa.String(length=255),
            type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('name',
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False)

    # like table
    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.drop_constraint('like_upload_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('like_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('like_upload_id_fkey', 'upload', ['upload_id'], ['id'])
        batch_op.create_foreign_key('like_user_id_fkey', 'user', ['user_id'], ['id'])

    # itinerary table
    with op.batch_alter_table('itinerary', schema=None) as batch_op:
        batch_op.drop_column('timestamp')
        try:
            batch_op.drop_constraint('itinerary_user_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        batch_op.create_foreign_key('itinerary_user_id_fkey', 'user', ['user_id'], ['id'])

    # comment table
    with op.batch_alter_table('comment', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('comment_user_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        try:
            batch_op.drop_constraint('comment_upload_id_fkey', type_='foreignkey')
        except ValueError:
            pass  # If the constraint does not exist, do nothing
        batch_op.create_foreign_key('comment_upload_id_fkey', 'upload', ['upload_id'], ['id'])
        batch_op.create_foreign_key('comment_user_id_fkey', 'user', ['user_id'], ['id'])
