from datetime import datetime, timedelta
from typing import List, Union
from pydantic import BaseModel, BaseSettings, Field


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_NAME: str
    SECRET_KEY: str
    MY_INVITE: str
    DEMO_USER_ID: str
    EXCEPTION_PER_SEC_LIMIT: int
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    invite: str
    is_active: bool = True

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[None, str] = None


class InvestmentBase(BaseModel):
    description: str = 'Прочие инвестиции'
    category_id: Union[None, int] = None


class InvestmentCreate(InvestmentBase):
    class Config:
        orm_mode = True


class InvestmentInDB(InvestmentBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class InvestmentOut(BaseModel):
    id: int
    description: str
    category_id: Union[None, int]

    class Config:
        orm_mode = True


class InvestmentDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class InvestmentUser(BaseModel):
    investments: List[InvestmentOut] = []

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    category: str = 'Прочая категория'


class CategoryCreate(CategoryBase):
    class Config:
        orm_mode = True


class CategoryInDB(CategoryBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    id: int
    category: str

    class Config:
        orm_mode = True


class CategoryDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class CategoryUser(BaseModel):
    categories: List[CategoryOut] = []

    class Config:
        orm_mode = True


class HistoryBase(BaseModel):
    date: datetime = Field(default_factory=lambda: datetime.strptime(f"{datetime.now().timetuple().tm_year}-"
                                                                     f"{datetime.now().timetuple().tm_mon}-01 00:00:00",
                                                                     "%Y-%m-%d %H:%M:%S"))
    sum: int = 0
    investments_id: Union[int, None]


class HistoryCreate(InvestmentBase):
    class Config:
        orm_mode = True


class HistoryInDB(InvestmentBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class HistoryOut(BaseModel):
    id: int
    date: datetime
    sum: int
    investments_id: Union[int, None]

    class Config:
        orm_mode = True


class HistoryDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class HistoryUser(BaseModel):
    history: List[HistoryOut] = []

    class Config:
        orm_mode = True


class InOutBase(BaseModel):
    date: datetime = Field(default_factory=lambda: datetime.strptime(f"{datetime.now().timetuple().tm_year}-"
                                                                     f"{datetime.now().timetuple().tm_mon}-01 00:00:00",
                                                                         "%Y-%m-%d %H:%M:%S"))
    description: str = 'Прочие корректировки'
    sum: int = 0
    investments_id: Union[int, None]


class InOutCreate(InvestmentBase):
    class Config:
        orm_mode = True


class InOutInDB(InvestmentBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class InOutOut(BaseModel):
    id: int
    date: datetime
    description: str
    sum: int
    investments_id: Union[int, None]

    class Config:
        orm_mode = True


class InOutDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class InOutUser(BaseModel):
    history: List[HistoryOut] = []

    class Config:
        orm_mode = True


class Result(BaseModel):
    result: str
