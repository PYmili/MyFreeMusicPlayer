import os
import sqlite3
from dotenv import load_dotenv
from loguru import logger
from typing import Union, List, Dict

class DatabaseManager:
    def __init__(self) -> None:
        """
        初始化数据库管理器
        """
        # 从.env文件中加载配置
        load_dotenv("sqlite_operation/.env")

        # 获取数据库文件路径
        self.DB_NAME = os.getenv("MUSIC_LIST_DB_NAME")
        self.DB_DIR = os.getenv("DB_DIR")
        self.db_path = os.path.join(self.DB_DIR, self.DB_NAME)
        self.conn = None
        self.cursor = None

        # 检查并创建数据库目录
        if not os.path.exists(self.DB_DIR):
            os.makedirs(self.DB_DIR)

    def __enter__(self) -> 'DatabaseManager':
        """
        进入上下文管理器
        """
        # 创建数据库连接
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # 检查表是否存在，如果不存在则创建表
        self.create_table_if_not_exists()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        退出上下文管理器
        """
        # 关闭连接
        self.cursor.close()
        self.conn.close()

    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        :param table_name: str 要检查的表名
        :return: bool 存在返回True，否则返回False
        """
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return self.cursor.fetchone() is not None

    def create_table_if_not_exists(self) -> None:
        """
        如果表不存在，则创建表
        """
        if not self.table_exists("music_list"):
            self.cursor.execute("""
                CREATE TABLE music_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    music_name TEXT,
                    music_img TEXT,
                    music_data BLOB,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            logger.info("表 music_list 创建成功")

    def insert_data(self, **kwargs) -> bool:
        """
        插入新数据
        :param kwargs: dict 包含要插入的数据
        :return: bool 插入成功返回True，否则返回False
        """
        # 检查音乐名和音乐数据是否为空
        if not kwargs.get("music_name") or not kwargs.get("music_data"):
            logger.error("用户名和密钥不能为空")
            return False
        
        # 构建SQL语句和参数
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' * len(kwargs))
        sql = f"""
            INSERT INTO music_list ({columns}) VALUES ({placeholders})
        """
        values = tuple(kwargs.values())

        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            logger.info("数据插入成功")
            return True
        except Exception as e:
            logger.error(f"数据插入失败: {e}")
            return False

    def get_records_by_range(
            self,
            start: int = 0,
            end: Union[int, None] = None
        ) -> List[Dict[str, any]]:
        """
        获取指定范围的记录
        :param start: int 范围的起始位置，默认为0
        :param end: int 范围的结束位置，默认为None（即检索所有记录）
        :return: List[Dict[str, any]] 包含记录的列表，每个记录都是一个字典
        """
        # 构建SQL查询语句
        if end is None:
            sql = """SELECT * FROM music_list"""
            # 执行查询
            self.cursor.execute(sql)
        else:
            sql = """
                SELECT * FROM music_list 
                    WHERE LIMIT ? OFFSET ?
            """
            # 执行查询
            self.cursor.execute(sql, (end - start, start))
        
        rows = self.cursor.fetchall()

        # 构建结果列表
        result = []
        for row in rows:
            record = {
                "music_name": row[1],
                "music_img": row[2],
                "music_data": row[3],
                "upload_time": row[4]
            }
            result.append(record)

        return result
    

if __name__ == "__main__":
    # 使用 with 语句创建 DatabaseManager 实例
    with DatabaseManager() as db_manager:
        # 插入新数据示例
        success = db_manager.insert_data(
            music_name="test",
            music_data=b''
        )
        if success:
            logger.info("插入成功")
        else:
            logger.error("插入失败")
        
        # 获取指定用户的记录示例
        records = db_manager.get_records_by_user("PYmili", 0, 10)
        logger.info(f"用户记录: {records}")
