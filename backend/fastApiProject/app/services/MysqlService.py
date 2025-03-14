from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.place_note_model import PlaceNote


class MySqlService:
    def __init__(self, db: Session):
        self.db = db

    def clear_database(self) -> bool:
        """
        清空 place_notes 表中的所有数据

        Returns:
            bool: 操作是否成功
        """
        try:
            self.db.query(PlaceNote).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"清空数据库失败: {str(e)}")
            return False

    def add_mapping(self, place_id: str, note_id: str) -> Optional[PlaceNote]:
        """
        添加一条 place_id 和 note_id 的映射记录

        Args:
            place_id: 地点ID (Google Place ID)
            note_id: 笔记ID (Post ID)

        Returns:
            Optional[PlaceNote]: 添加的记录，失败则返回None
        """
        try:
            # 模型现在有id字段作为主键，不需要手动指定
            mapping = PlaceNote(place_id=place_id, note_id=note_id)
            self.db.add(mapping)
            self.db.commit()
            self.db.refresh(mapping)
            return mapping
        except IntegrityError:
            # 如果违反唯一约束(place_id或note_id已存在)
            self.db.rollback()
            print(f"添加映射失败: place_id {place_id} 或 note_id {note_id} 已存在")
            return None
        except Exception as e:
            self.db.rollback()
            print(f"添加映射失败: {str(e)}")
            return None

    def get_notes_by_place_id(self, place_id: str) -> List[str]:
        """
        根据 place_id 查找对应的所有 note_id

        Args:
            place_id: 地点ID (Google Place ID)

        Returns:
            List[str]: 对应的所有笔记ID列表
        """
        try:
            mappings = self.db.query(PlaceNote).filter(
                PlaceNote.place_id == place_id
            ).all()

            return [mapping.note_id for mapping in mappings]
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return []

    # 可以添加按ID查询的方法
    def get_mapping_by_id(self, mapping_id: int) -> Optional[PlaceNote]:
        """
        通过ID查找映射记录

        Args:
            mapping_id: 映射记录ID

        Returns:
            Optional[PlaceNote]: 找到的记录，不存在则返回None
        """
        try:
            return self.db.query(PlaceNote).filter(PlaceNote.id == mapping_id).first()
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return None


from models.place_note_model import get_db

# 获取数据库会话
db = next(get_db())

# 创建服务实例
mysql_service = MySqlService(db)