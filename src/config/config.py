from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    #I have used db credentials as environment variables for security reasons and also becuase we may have different database credentials for different environments
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property # This is a synchronous database URL for SQLAlchemy for reflecting tables only, all the Db operations are async with above Db url
    def sync_database_url(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()