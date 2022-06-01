from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime
from database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("username", String),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String),
    Column("is_active", Boolean, default=True)
)


investments_items = Table(
    "investments_items",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("description", String, nullable=False, default='unknown'),
    Column("category_id", Integer, nullable=True),
    Column("owner_id", Integer, ForeignKey("users.id")),
    Column("is_active", Boolean, default=True)
)


investments_history = Table(
    "investments_history",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date", DateTime, nullable=False),
    Column("sum", Integer, nullable=False),
    Column("investment_id", Integer, ForeignKey("investments_items.id"))
)


investments_in_out = Table(
    "investments_in_out",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date", DateTime, nullable=False),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("investment_id", Integer, ForeignKey("investments_items.id"))
)


categories = Table(
    "categories",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("category", String, nullable=False, default='unknown'),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


key_rate = Table(
    "key_rate",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date", DateTime, nullable=False),
    Column("key_rate", Integer, nullable=False),
)