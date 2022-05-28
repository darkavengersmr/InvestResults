from database import database
from sqlalchemy import and_
from models import users, investments_items, investments_history, investments_in_out, categories
import schemas

from exeptions import CategoryInUse, CategoryNotFound, InvestmentNotFound


async def get_user(user_id: int | None = None,
                   username: str | None = None,
                   email: str | None = None) -> schemas.UserInDB:
    """Get user by user_id, username or email from DB"""
    result: schemas.UserInDB | None = None
    if user_id:
        result = await database.fetch_one(users.select().where(users.c.id == user_id))
    elif username:
        result = await database.fetch_one(users.select().where(users.c.username == username))
    elif email:
        result = await database.fetch_one(users.select().where(users.c.email == email))
    return result


async def create_user(user: schemas.UserCreate, hashed_password: str) -> schemas.User:
    """Create new user with hashed password in DB"""
    db_user = users.insert().values(username=user.username,
                                    email=user.email,
                                    hashed_password=hashed_password,
                                    is_active=user.is_active)
    user_id = await database.execute(db_user)
    return schemas.User(**user.dict(), id=user_id)


async def create_user_investment_item(investment: schemas.InvestmentCreate, user_id: int) -> schemas.InvestmentInDB:
    """Create new investment in DB"""
    query = investments_items.insert().values(**investment.dict(), owner_id=user_id)
    investment_id = await database.execute(query)
    return schemas.InvestmentInDB(**investment.dict(), id=investment_id, owner_id=user_id)


async def get_user_investment_items(user_id: int) -> schemas.InvestmentUser:
    """Get user investments by user_id from DB"""
    list_investments = await database.fetch_all(investments_items.select()
                                                .where(investments_items.c.owner_id == user_id))
    return schemas.InvestmentUser(**{"investments": [dict(result) for result in list_investments]})


async def update_user_investment_item(investment: schemas.InvestmentOut, user_id: int) -> schemas.Result:
    """Update user investment in DB (description, category_id)"""
    investment_in_db = await database.fetch_one(investments_items.select()
                                                .where(and_(investments_items.c.id == investment.id,
                                                            investments_items.c.owner_id == user_id)))
    if investment_in_db:
        query = investments_items.update().where(and_(investments_items.c.id == investment.id,
                                                      investments_items.c.owner_id == user_id))\
            .values(description=investment.description, category_id=investment.category_id)
        await database.execute(query)
        return schemas.Result(**{"result": "investment updated"})
    else:
        raise InvestmentNotFound


async def delete_user_investment_item(investment_id: int, user_id: int) -> schemas.Result:
    """Delete user investment by id from DB"""
    query = investments_items.select().where(and_(investments_items.c.id == investment_id,
                                                  investments_items.c.owner_id == user_id))
    result = await database.fetch_one(query)
    if result:
        query = investments_items.delete().where(and_(investments_items.c.id == investment_id,
                                                      investments_items.c.owner_id == user_id))
        await database.execute(query)
        return schemas.Result(**{"result": "investments deleted"})
    else:
        raise InvestmentNotFound


async def create_user_category(category: schemas.CategoryCreate, user_id: int) -> schemas.CategoryInDB:
    """Create new category for user in DB"""
    query = categories.insert().values(**category.dict(), owner_id=user_id)
    category_id = await database.execute(query)
    return schemas.CategoryInDB(**category.dict(), id=category_id, owner_id=user_id)


async def get_user_categories(user_id: int) -> schemas.CategoryUser:
    """Get categories for user from DB"""
    list_categories = await database.fetch_all(categories.select().where(categories.c.owner_id == user_id))
    return schemas.CategoryUser(**{"categories": [dict(result) for result in list_categories]})


async def delete_user_category(category_id: int, user_id: int) -> schemas.Result:
    """Delete unused category from DB"""
    query = investments_items.select().where(and_(investments_items.c.category_id == category_id,
                                                  investments_items.c.owner_id == user_id))
    categories_found = await database.fetch_all(query)
    if categories_found:
        raise CategoryInUse
    else:
        query = categories.select().where(and_(categories.c.id == category_id, categories.c.owner_id == user_id))
        result = await database.execute(query)
        if result:
            query = categories.delete().where(and_(categories.c.id == category_id, categories.c.owner_id == user_id))
            await database.execute(query)
            result = schemas.Result(**{"result": "category deleted"})
        else:
            raise CategoryNotFound
    return result

