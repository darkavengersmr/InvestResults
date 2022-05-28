#!/usr/bin/python3

import asyncio
import uvicorn

from datetime import datetime, timedelta
import calendar

from database import database, engine, metadata
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext

import crud
import schemas

from config import SECRET_KEY, MY_INVITE, DEMO_USER_ID, EXCEPTION_PER_SEC_LIMIT, \
    ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from exeptions import DBNoConnection, TooShortPassword, UserPasswordIsInvalid, CategoryInUse, CategoryNotFound, \
    InvestmentNotFound

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Register",
        "description": "Регистрация новых пользователей",
    },
    {
        "name": "Token",
        "description": "Обновление токенов доступа",
    },
    {
        "name": "User",
        "description": "Получение данных из профиля пользователя",
    },
    {
        "name": "Investments",
        "description": "Инвестиции",
    },
    {
        "name": "Categories",
        "description": "Категории инвестиций",
    },
    {
        "name": "Reports",
        "description": "Отчеты",
    },
]

app = FastAPI(
    title="InvestResults Api",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
async def startup() -> None:
    try:
        await database.connect()
    except BaseException:
        raise DBNoConnection


@app.on_event("shutdown")
async def shutdown() -> None:
    try:
        await database.disconnect()
    except BaseException:
        raise DBNoConnection


def get_password_hash(password: str) -> str:
    if len(password) > 5:
        return pwd_context.hash(password)
    else:
        raise TooShortPassword


def verify_password(plain_password: str, hashed_password: str) -> bool:
    #print(get_password_hash(plain_password))
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str) -> schemas.UserInDB:
    user = await crud.get_user(username=username)
    if user and verify_password(password, user.hashed_password):
        return user
    else:
        raise UserPasswordIsInvalid


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await crud.get_user(username=token_data.username)
    if user:
        return user
    else:
        raise credentials_exception


async def get_current_active_user(current_user: schemas.UserInDB = Depends(get_current_user)) -> schemas.UserInDB:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def is_user(user_id: int, email: str) -> schemas.UserInDB:
    db_user = await crud.get_user(user_id=user_id)
    if not db_user:
        await asyncio.sleep(EXCEPTION_PER_SEC_LIMIT)
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.email != email:
        await asyncio.sleep(EXCEPTION_PER_SEC_LIMIT)
        raise HTTPException(status_code=404, detail="Query for other user prohibited")
    return db_user


def month_begin() -> datetime:
    dt = datetime.now()
    return datetime.strptime(f"{dt.timetuple().tm_year}-{dt.timetuple().tm_mon}-01 00:00:00", "%Y-%m-%d %H:%M:%S")


def month_end() -> datetime:
    dt = datetime.now()
    _, num_days = calendar.monthrange(dt.timetuple().tm_year, dt.timetuple().tm_mon)
    return datetime.strptime(f"{dt.timetuple().tm_year}-{dt.timetuple().tm_mon}-{num_days} 23:59:59",
                             "%Y-%m-%d %H:%M:%S")


@app.get("/")
async def redirect_to_index_html():
    return RedirectResponse(url=f"/index.html", status_code=303)


@app.post("/register", response_model=schemas.User, tags=["Register"])
async def create_user(user: schemas.UserCreate) -> schemas.User:
    if not await crud.get_user(email=user.email):
        hashed_password = get_password_hash(user.password)
        if user.invite != MY_INVITE:
            await asyncio.sleep(EXCEPTION_PER_SEC_LIMIT)
            raise HTTPException(status_code=400, detail="Invite is broken")
        return await crud.create_user(user=user, hashed_password=hashed_password)
    else:
        raise HTTPException(status_code=400, detail="Email already registered")


@app.post("/token", response_model=schemas.Token , tags=["Token"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    try:
        user = await authenticate_user(form_data.username, form_data.password)
    except UserPasswordIsInvalid:
        await asyncio.sleep(EXCEPTION_PER_SEC_LIMIT)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user", response_model=schemas.User, tags=["User"])
async def read_user(current_user: schemas.User = Depends(get_current_active_user)) -> schemas.UserInDB:
    return await is_user(current_user.id, current_user.email)


@app.post("/users/{user_id}/investment_items/", response_model=schemas.InvestmentInDB, tags=["Investments"])
async def create_investment_for_user(user_id: int, investment: schemas.InvestmentCreate,
                                current_user: schemas.User = Depends(get_current_active_user)) -> schemas.InvestmentInDB:
    await is_user(user_id, current_user.email)
    if user_id == DEMO_USER_ID:
        return schemas.InvestmentInDB(**investment.dict(), id=9999999, owner_id=DEMO_USER_ID)
    return await crud.create_user_investment_item(investment=investment, user_id=user_id)


@app.get("/users/{user_id}/investment_items/", response_model=schemas.InvestmentUser, tags=["Investments"])
async def get_investments_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_user_investment_items(user_id=user_id)


@app.put("/users/{user_id}/investment_items/", response_model=schemas.Result, tags=["Investments"])
async def update_investment_for_user(user_id: int, investment: schemas.InvestmentOut,
                                     current_user: schemas.User = Depends(get_current_active_user)) -> schemas.Result:
    await is_user(user_id, current_user.email)
    if user_id == DEMO_USER_ID:
        return schemas.Result(**{"result": "investment updated"})
    try:
        result = await crud.update_user_investment_item(investment=investment, user_id=user_id)
    except InvestmentNotFound:
        raise HTTPException(status_code=400, detail="Investment for update not found")
    return result

@app.delete("/users/{user_id}/investment_items/", response_model=schemas.Result, tags=["Investments"])
async def delete_investment_for_user(user_id: int, investment_id: int,
                                current_user: schemas.User = Depends(get_current_active_user)) -> schemas.Result:
    await is_user(user_id, current_user.email)
    if user_id == DEMO_USER_ID:
        return schemas.Result(**{"result": "investment for demo user conditionally deleted"})
    try:
        result = await crud.delete_user_investment_item(investment_id=investment_id, user_id=user_id)
    except InvestmentNotFound:
        raise HTTPException(status_code=400, detail="Investment for delete not found")
    return result

@app.get("/users/{user_id}/categories/", response_model=schemas.CategoryUser, tags=["Categories"])
async def get_categories_for_user(user_id: int,
                                  current_user: schemas.User = Depends(get_current_active_user)) -> schemas.CategoryUser:
    await is_user(user_id, current_user.email)
    return await crud.get_user_categories(user_id=user_id)


@app.post("/users/{user_id}/categories/", response_model=schemas.CategoryInDB, tags=["Categories"])
async def create_category_for_user(user_id: int, category: schemas.CategoryCreate,
                                   current_user: schemas.User = Depends(get_current_active_user)) -> schemas.CategoryInDB:
    await is_user(user_id, current_user.email)
    if user_id == DEMO_USER_ID:
        return schemas.CategoryInDB(**category.dict(), id=9999999, owner_id=DEMO_USER_ID)
    return await crud.create_user_category(category=category, user_id=user_id)


@app.delete("/users/{user_id}/categories/", tags=["Categories"])
async def delete_category_for_user(user_id: int, category_id: int,
                                   current_user: schemas.User = Depends(get_current_active_user)) -> schemas.Result:
    await is_user(user_id, current_user.email)
    if user_id == DEMO_USER_ID:
        return schemas.Result(**{"result": "category for demo user conditionally deleted"})
    try:
        result =  await crud.delete_user_category(category_id=category_id, user_id=user_id)
    except CategoryInUse:
        raise HTTPException(status_code=400, detail="Category in use, not deleted")
    except CategoryNotFound:
        raise HTTPException(status_code=400, detail="Category for delete not found")
    return result


app.mount("/", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
