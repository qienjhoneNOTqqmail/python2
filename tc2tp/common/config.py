from typing import Optional

from pydantic import BaseSettings, validator


class Config(BaseSettings):
    DEBUG: bool = False
    HOST: str = 'localhost'
    DATABASE: str = 'test'
    USER: str = 'root'
    PASSWORD: str = '123456'
    POOL_SIZE: int = 5
    POOL_RECYCLE: int = 60 * 30
    MYSQL_URI: Optional[str] = None
    MONGO_URI: Optional[str] = None

    @validator("MYSQL_URI", pre=True)
    def assemble_sql_uri(cls, v, values):
        if isinstance(v, str):
            return v
        return f"mysql+pymysql://{values.get('USER')}:{values.get('PASSWORD')}@{values.get('HOST')}/{values.get('DATABASE')}"

    @validator("MONGO_URI", pre=True)
    def assemble_mongo_uri(cls, v, values):
        if isinstance(v, str):
            return v
        return f"mongodb://{values.get('HOST')}:27017"

    class Config:
        env_file = ".env"
        env_encoding = "utf8"
        case_sensitive = True


config = Config()
