from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, TypeVar, Generic, Type, Dict, Any
from sqlalchemy.ext.declarative import DeclarativeMeta

# 泛型类型定义
T = TypeVar('T', bound=DeclarativeMeta)


class MySqlCore(Generic[T]):
    """MySQL Core 服务，提供基础的数据库操作"""

    def __init__(self, db: Session, model: Type[T]):
        """
        初始化 MySQL 服务

        Args:
            db: 数据库会话
            model: 数据模型类
        """
        self.db = db
        self.model = model

    def clear_table(self) -> bool:
        """
        清空表中的所有数据

        Returns:
            bool: 操作是否成功
        """
        try:
            self.db.query(self.model).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"清空表失败: {str(e)}")
            return False

    def add(self, item_data: Dict[str, Any]) -> Optional[T]:
        """
        添加一条记录

        Args:
            item_data: 记录数据字典

        Returns:
            Optional[T]: 添加的记录，失败则返回None
        """
        try:
            item = self.model(**item_data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except IntegrityError:
            self.db.rollback()
            print(f"添加记录失败: 可能违反唯一约束")
            return None
        except Exception as e:
            self.db.rollback()
            print(f"添加记录失败: {str(e)}")
            return None

    def get_by_id(self, item_id: Any) -> Optional[T]:
        """
        通过ID查找记录

        Args:
            item_id: 记录ID

        Returns:
            Optional[T]: 找到的记录，不存在则返回None
        """
        try:
            return self.db.query(self.model).filter(self.model.id == item_id).first()
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return None

    def get_by_filter(self, **filters) -> List[T]:
        """
        根据过滤条件查找记录

        Args:
            **filters: 过滤条件

        Returns:
            List[T]: 满足条件的记录列表
        """
        try:
            query = self.db.query(self.model)
            for attr, value in filters.items():
                query = query.filter(getattr(self.model, attr) == value)
            return query.all()
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return []