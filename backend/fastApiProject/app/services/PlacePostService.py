from typing import List, Optional
from sqlalchemy.orm import Session
from models.place_note_model import PlaceNote, get_db
from core.MySqlCore import MySqlCore


class PlacePostService:
    """处理地点和笔记之间映射关系的服务"""

    def __init__(self, db: Session = next(get_db())):
        """
        初始化 PlaceNoteService

        Args:
            db: 数据库会话，默认从 get_db 获取
        """
        self.mysql_core = MySqlCore(db, PlaceNote)

    def clear_database(self) -> bool:
        """
        清空 place_notes 表中的所有数据

        Returns:
            bool: 操作是否成功
        """
        return self.mysql_core.clear_table()

    def add_mapping(self, place_id: str, note_id: str) -> Optional[PlaceNote]:
        """
        添加一条 place_id 和 note_id 的映射记录

        Args:
            place_id: 地点ID (Google Place ID)
            note_id: 笔记ID (Post ID)

        Returns:
            Optional[PlaceNote]: 添加的记录，失败则返回None
        """
        item_data = {
            "place_id": place_id,
            "note_id": note_id
        }
        return self.mysql_core.add(item_data)

    def get_notes_by_place_id(self, place_id: str) -> List[str]:
        """
        根据 place_id 查找对应的所有 note_id

        Args:
            place_id: 地点ID (Google Place ID)

        Returns:
            List[str]: 对应的所有笔记ID列表
        """
        mappings = self.mysql_core.get_by_filter(place_id=place_id)
        return [mapping.note_id for mapping in mappings]

    def get_mapping_by_id(self, mapping_id: int) -> Optional[PlaceNote]:
        """
        通过ID查找映射记录

        Args:
            mapping_id: 映射记录ID

        Returns:
            Optional[PlaceNote]: 找到的记录，不存在则返回None
        """
        return self.mysql_core.get_by_id(mapping_id)


# 创建单例实例
place_post_service = PlacePostService()