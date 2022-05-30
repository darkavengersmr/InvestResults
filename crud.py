import models

from database import database
from sqlalchemy import and_
from models import users, investments_items, investments_history, investments_in_out, categories, Table
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


async def update_user_category(category: schemas.CategoryOut, user_id: int) -> schemas.Result:
    """Delete unused category from DB"""
    query = investments_items.select().where(and_(investments_items.c.category_id == category.id,
                                                  investments_items.c.owner_id == user_id))
    categories_found = await database.fetch_all(query)
    if categories_found:
        query = categories.update().where((categories.c.id == category.id)).values(category=category.category)
        result = await database.execute(query)
        if result:
            return schemas.Result(**{"result": "category updated"})
    else:
        raise CategoryNotFound


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


async def user_investment_exist(investment_id: int, user_id: int) -> bool:
    """Check exist user investment history in DB"""
    return await database.fetch_one(investments_items.select().where(and_(investments_items.c.id == investment_id,
                                                                          investments_items.c.owner_id == user_id)))


async def create_user_investment_history(investment: schemas.HistoryCreate, user_id: int) -> schemas.HistoryInDB:
    """Create new investment history in DB"""
    if await user_investment_exist(investment_id=investment.investment_id, user_id=user_id):
        query = investments_history.insert().values(**investment.dict())
        investment_id = await database.execute(query)
        return schemas.HistoryInDB(**investment.dict(), id=investment_id)
    else:
        raise InvestmentNotFound


async def get_user_investment_history(user_id: int, investment_id: int) -> schemas.HistoryUser:
    """Get user investments history by user_id from DB"""
    if await user_investment_exist(investment_id=investment_id, user_id=user_id):
        list_investment_history = await database.fetch_all(investments_history.select()
                                                           .where(investments_history.c.investment_id == investment_id))
        return schemas.HistoryUser(**{"history": [dict(result) for result in list_investment_history]})
    else:
        raise InvestmentNotFound


async def update_user_investment_history(investment: schemas.HistoryOut, user_id: int) -> schemas.Result:
    """Update user investment history in DB (date, sum)"""
    if await user_investment_exist(investment_id=investment.investment_id, user_id=user_id):
        query = investments_history.update().where((investments_history.c.id == investment.id))\
            .values(date=investment.date, sum=investment.sum)
        await database.execute(query)
        return schemas.Result(**{"result": "investment history updated"})
    else:
        raise InvestmentNotFound


async def delete_user_investment_history(investment_history_id: int, user_id: int) -> schemas.Result:
    """Delete user investment history by id from DB"""
    investment_history_in_db = await database.fetch_one(investments_history
                                             .select().where(investments_history.c.id == investment_history_id))
    if investment_history_in_db and await user_investment_exist(investment_id=investment_history_in_db.investment_id,
                                                                user_id=user_id):
        query = investments_history.delete()\
            .where(and_(investments_history.c.id == investment_history_id,
                        investments_history.c.investment_id == investment_history_in_db.investment_id))
        await database.execute(query)
        return schemas.Result(**{"result": "investments history item deleted"})
    else:
        raise InvestmentNotFound


async def create_user_investment_inout(investment: schemas.InOutCreate, user_id: int) -> schemas.InOutInDB:
    """Create new investment in/out in DB"""
    if await user_investment_exist(investment_id=investment.investment_id, user_id=user_id):
        query = investments_in_out.insert().values(**investment.dict())
        investment_id = await database.execute(query)
        return schemas.InOutInDB(**investment.dict(), id=investment_id)
    else:
        raise InvestmentNotFound


async def get_user_investment_inout(user_id: int, investment_id: int) -> schemas.InOutUser:
    """Get user investments in/out by user_id from DB"""
    if await user_investment_exist(investment_id=investment_id, user_id=user_id):
        list_investment_in_out = await database.fetch_all(investments_in_out.select()
                                                           .where(investments_in_out.c.investment_id == investment_id))
        return schemas.InOutUser(**{"in_out": [dict(result) for result in list_investment_in_out]})
    else:
        raise InvestmentNotFound


async def update_user_investment_inout(investment: schemas.InOutOut, user_id: int) -> schemas.Result:
    """Update user investment in/out in DB (date, sum)"""
    if await user_investment_exist(investment_id=investment.investment_id, user_id=user_id):
        query = investments_in_out.update().where((investments_in_out.c.id == investment.id))\
            .values(date=investment.date, description=investment.description, sum=investment.sum)
        await database.execute(query)
        return schemas.Result(**{"result": "investment in/out updated"})
    else:
        raise InvestmentNotFound


async def delete_user_investment_inout(investment_in_out_id: int, user_id: int) -> schemas.Result:
    """Delete user investment in/out by id from DB"""
    investment_in_out_in_db = await database.fetch_one(investments_in_out
                                             .select().where(investments_in_out.c.id == investment_in_out_id))
    if investment_in_out_in_db and await user_investment_exist(investment_id=investment_in_out_in_db.investment_id,
                                                               user_id=user_id):
        query = investments_in_out.delete()\
            .where(and_(investments_in_out.c.id == investment_in_out_id,
                        investments_in_out.c.investment_id == investment_in_out_in_db.investment_id))
        await database.execute(query)
        return schemas.Result(**{"result": "investments in/out item deleted"})
    else:
        raise InvestmentNotFound
