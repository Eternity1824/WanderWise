from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from config import get_settings

settings = get_settings()

# 创建数据库引擎
engine = create_engine(settings.MYSQL_CONNECTION_STRING)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 获取数据库会话的依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PlacePost(Base):
    __tablename__ = "place_notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    place_id = Column(String(200), index=True)
    note_id = Column(String(50), index=True)