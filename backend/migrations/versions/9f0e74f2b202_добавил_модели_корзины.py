"""Добавил модели корзины

Revision ID: 9f0e74f2b202
Revises: ff7de271907d
Create Date: 2025-02-27 13:40:08.326055

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9f0e74f2b202'
down_revision = 'ff7de271907d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cart_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cart_id'], ['cart.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('cart_product')
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['user_id'])
        batch_op.drop_constraint('cart_ibfk_1', type_='foreignkey')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.create_foreign_key('cart_ibfk_1', 'user', ['user_id'], ['id'])
        batch_op.drop_constraint(None, type_='unique')

    op.create_table('cart_product',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('cart_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('quantity', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['cart_id'], ['cart.id'], name='cart_product_ibfk_1'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], name='cart_product_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('cart_item')
    # ### end Alembic commands ###
