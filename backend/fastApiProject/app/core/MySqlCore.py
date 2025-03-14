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

    def get_all(self) -> List[T]:
        """
        获取表中的所有记录

        Returns:
            List[T]: 所有记录列表
        """
        try:
            return self.db.query(self.model).all()
        except Exception as e:
            print(f"获取所有记录失败: {str(e)}")
            return []

    def export_to_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        将表中所有数据导出到JSON文件

        Args:
            json_file_path: 导出的JSON文件路径

        Returns:
            Dict[str, Any]: 包含导出状态信息的字典
        """
        import json
        import time
        from sqlalchemy.inspection import inspect

        try:
            start_time = time.time()

            # 获取所有记录
            all_records = self.get_all()

            # 获取模型的列信息
            mapper = inspect(self.model)
            column_names = [column.key for column in mapper.columns]

            # 转换为可序列化的字典列表
            records_data = []
            for record in all_records:
                record_dict = {}
                for column in column_names:
                    record_dict[column] = getattr(record, column)
                records_data.append(record_dict)

            # 写入JSON文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(records_data, f, ensure_ascii=False, indent=4)

            elapsed_time = time.time() - start_time

            return {
                "status": "success",
                "message": f"成功导出 {len(records_data)} 条记录到 {json_file_path}",
                "total_records": len(records_data),
                "elapsed_time": elapsed_time,
                "file_path": json_file_path
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"导出数据失败: {str(e)}",
                "error": str(e)
            }

    def import_from_json(self, json_file_path: str, clear_existing: bool = False) -> Dict[str, Any]:
        """
        从JSON文件导入数据到表中

        Args:
            json_file_path: JSON文件路径
            clear_existing: 是否在导入前清空现有数据

        Returns:
            Dict[str, Any]: 包含导入状态信息的字典
        """
        import json
        import time

        try:
            start_time = time.time()

            # 读取JSON文件
            with open(json_file_path, 'r', encoding='utf-8') as f:
                records_data = json.load(f)

            # 验证数据格式
            if not isinstance(records_data, list):
                return {
                    "status": "error",
                    "message": "导入失败: JSON文件必须包含一个数组",
                    "error": "Invalid format"
                }

            # 如果需要，清空现有数据
            if clear_existing:
                self.clear_table()

            # 导入数据
            success_count = 0
            failed_count = 0
            skipped_count = 0

            for record_data in records_data:
                try:
                    # 如果有ID且存在相同ID的记录，则跳过
                    if "id" in record_data:
                        existing_record = self.get_by_id(record_data["id"])
                        if existing_record:
                            skipped_count += 1
                            continue

                    # 添加记录
                    result = self.add(record_data)
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"导入记录失败: {str(e)}")
                    failed_count += 1

            elapsed_time = time.time() - start_time

            return {
                "status": "success" if failed_count == 0 else "partial",
                "message": f"导入完成: 成功 {success_count}, 跳过 {skipped_count}, 失败 {failed_count}",
                "total_processed": len(records_data),
                "success_count": success_count,
                "skipped_count": skipped_count,
                "failed_count": failed_count,
                "elapsed_time": elapsed_time
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"导入数据失败: {str(e)}",
                "error": str(e)
            }