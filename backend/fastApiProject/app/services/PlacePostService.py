from typing import List, Optional
from sqlalchemy.orm import Session
from models.PlacePost import PlacePost, get_db
from core.MySqlCore import MySqlCore
from typing import List, Optional, Dict, Any

class PlacePostService:
    """处理地点和笔记之间映射关系的服务"""

    def __init__(self, db: Session = next(get_db())):
        """
        初始化 PlaceNoteService

        Args:
            db: 数据库会话，默认从 get_db 获取
        """
        self.mysql_core = MySqlCore(db, PlacePost)

    def clear_database(self) -> bool:
        """
        清空 place_notes 表中的所有数据

        Returns:
            bool: 操作是否成功
        """
        return self.mysql_core.clear_table()

    def add_mapping(self, place_id: str, note_id: str) -> Optional[PlacePost]:
        """
        添加一条 place_id 和 note_id 的映射记录

        Args:
            place_id: 地点ID (Google Place ID)
            note_id: 笔记ID (Post ID)

        Returns:
            Optional[PlacePost]: 添加的记录，失败则返回None
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
    def get_places_by_note_id(self, note_id: str) -> List[str]:
        mappings = self.mysql_core.get_by_filter(note_id=note_id)
        return [mapping.place_id for mapping in mappings]

    def get_mapping_by_id(self, mapping_id: int) -> Optional[PlacePost]:
        """
        通过ID查找映射记录

        Args:
            mapping_id: 映射记录ID

        Returns:
            Optional[PlacePost]: 找到的记录，不存在则返回None
        """
        return self.mysql_core.get_by_id(mapping_id)

    def export_mappings_to_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        将地点和笔记的映射关系导出到JSON文件

        Args:
            json_file_path: 导出的JSON文件路径

        Returns:
            Dict[str, Any]: 包含导出状态信息的字典
        """
        return self.mysql_core.export_to_json(json_file_path)

    def import_mappings_from_json(self, json_file_path: str, clear_existing: bool = False) -> Dict[str, Any]:
        """
        从JSON文件导入地点和笔记的映射关系

        Args:
            json_file_path: JSON文件路径
            clear_existing: 是否在导入前清空现有数据

        Returns:
            Dict[str, Any]: 包含导入状态信息的字典
        """
        return self.mysql_core.import_from_json(json_file_path, clear_existing)

# 创建单例实例
place_post_service = PlacePostService()