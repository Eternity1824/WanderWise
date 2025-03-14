from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from app.config import get_settings

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


class PlaceNote(Base):
    __tablename__ = "place_notes"

    place_id = Column(String(255), primary_key=True, index=True)
    note_id = Column(Integer, index=True, unique=True)

    # 如果需要添加其他限制或索引
    __table_args__ = (
        UniqueConstraint('note_id', name='uq_note_id'),
    )