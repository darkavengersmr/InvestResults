from datetime import datetime
from typing import List, Union, Dict
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
    is_active: bool = True


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
    is_active: bool = True

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
    date: datetime = Field(default_factory=datetime.now)
    sum: int = 0
    investment_id: int


class HistoryCreate(HistoryBase):
    class Config:
        orm_mode = True


class HistoryInDB(HistoryBase):
    id: int

    class Config:
        orm_mode = True


class HistoryOut(BaseModel):
    id: int
    date: datetime
    sum: int
    investment_id: int

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
    date: datetime = Field(default_factory=datetime.now)
    description: str = 'Прочие корректировки'
    sum: int = 0
    investment_id: int


class InOutCreate(InOutBase):
    class Config:
        orm_mode = True


class InOutInDB(InOutBase):
    id: int

    class Config:
        orm_mode = True


class InOutOut(BaseModel):
    id: int
    date: datetime
    description: str
    sum: int
    investment_id: int

    class Config:
        orm_mode = True


class InOutDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class InOutUser(BaseModel):
    in_out: List[InOutOut] = []

    class Config:
        orm_mode = True


class KeyRateBase(BaseModel):
    date: datetime = Field(default_factory=datetime.now)
    key_rate: int = 0


class KeyRateCreate(KeyRateBase):
    class Config:
        orm_mode = True


class KeyRateInDB(KeyRateBase):
    id: int

    class Config:
        orm_mode = True


class KeyRateOut(BaseModel):
    id: int
    date: datetime
    key_rate: int

    class Config:
        orm_mode = True


class KeyRateDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class KeyRateUser(BaseModel):
    key_rates: List[KeyRateOut] = []

    class Config:
        orm_mode = True


class Result(BaseModel):
    result: str


class InvestmentReportAsset(BaseModel):
    sum_in: Dict[str, int] = {}
    sum_out: Dict[str, int] = {}
    sum_plan: Dict[str, int] = {}
    sum_fact: Dict[str, int] = {}
    sum_delta_rub: Dict[str, int] = {}
    sum_delta_proc: Dict[str, float] = {}
    sum_delta_proc_avg: Dict[str, float] = {}
    sum_cashflow: Dict[str, int] = {}
    description: str = ""
    category: str = ""
    id: int = 0
    category_id: int = 0


class InvestmentReport(BaseModel):
    investment_report: List[InvestmentReportAsset] = []