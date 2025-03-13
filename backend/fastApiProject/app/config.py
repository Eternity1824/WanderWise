import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 基本设置
    APP_NAME: str = "WanderWise"
    DEBUG: bool = False

    # Mysql
    MYSQL_CONNECTION_STRING: str = "mysql+pymysql://user:123456@localhost:3306/wanderwise"

    # Elasticsearch设置
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "wanderwise_"

    # 外部API
    GOOGLE_MAPS_API_KEY: str = "AIzaSyD4K_0sPAIWmIE8jandYAlaNqMSTu9jAOY"
    DEEP_SEEK_API_KEY: str = "sk-95981642162246b78a24497688378291"


@lru_cache()
def get_settings():
    """创建设置单例，避免重复加载"""
    return Settings()