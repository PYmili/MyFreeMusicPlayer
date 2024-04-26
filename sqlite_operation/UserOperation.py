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
        self.DB_NAME = os.getenv("USER_DB_NAME")
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
        if not self.table_exists("user"):
            self.cursor.execute("""
                CREATE TABLE user (
                    user_name TEXT NOT NULL PRIMARY KEY,
                    password TEXT NOT NULL,
                    key TEXT NOT NULL
                )
            """)
            self.conn.commit()
            logger.info("表 user 创建成功")
        # 添加默认用户admin
        self.add_default_user_if_not_exists()
    
    def add_default_user_if_not_exists(self) -> None:
        """
        如果默认用户（如admin）不存在，则插入该用户。
        """
        # 确保也为默认用户指定了密码
        default_user = ("admin", "admin", "1949_10_1")
        query = "SELECT * FROM user WHERE user_name=? AND key=?"
        # 只需要user_name和key来检查用户是否存在
        self.cursor.execute(query, (default_user[0], default_user[2]))
        if not self.cursor.fetchone():
            insert_query = "INSERT INTO user (user_name, password, key) VALUES (?, ?, ?)"
            self.cursor.execute(insert_query, default_user)
            self.conn.commit()
            logger.info("默认用户 'admin' 已成功添加至数据库。")
        else:
            logger.info("默认用户 'admin' 已存在于数据库中。")

    def update_user_info(self, new_username: str, **kwargs) -> bool:
        """
        更新唯一用户的信息，用户名为必填，可额外更新密码、key等信息。
        :param new_username: str 新的用户名
        :param kwargs: dict 其他可更新的字段及其新值，如new_password='newpwd', new_key='newkey'
        :return: bool 更新是否成功
        """
        # 确保提供了至少一项额外的更新信息
        update_fields = kwargs.keys()
        if not update_fields:
            logger.error("除了用户名外，至少需要提供一项其他信息（如密码、key）来更新。")
            return False

        set_clause = ["user_name = ?"]
        values = [new_username]

        # 从kwargs中构建SET子句和VALUES列表
        for field in update_fields:
            if field in ['password', 'key']:  # 确保只允许更新预定义的字段
                set_clause.append(f"{field} = ?")
                values.append(kwargs[field])
            else:
                logger.warning(f"尝试更新未知字段 '{field}'，将被忽略。")

        # 构建完整的SET子句
        set_clause_str = ", ".join(set_clause)
        # 因为只有单个用户，不需要WHERE条件直接更新
        query = f"UPDATE user SET {set_clause_str}"

        try:
            self.cursor.execute(query, tuple(values))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"用户信息（用户名更新为'{new_username}'及其它字段）已成功更新。")
                return True
            else:
                logger.warning("未找到记录进行更新，可能是因为表中无数据。")
                return False
        except sqlite3.Error as e:
            logger.error(f"更新用户信息时发生错误：{str(e)}")
            return False
    
    def get_current_user_info(self) -> Union[Dict[str, str], None]:
        """
        查询并返回当前用户的所有信息。
        :return: dict 当前用户的详细信息，如果无记录则返回None
        """
        query = "SELECT * FROM user"
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            if row:
                user_info = {
                    "user_name": row[0],
                    "password": row[1],
                    "key": row[2]
                }
                logger.info("成功获取当前用户信息。")
                return user_info
            else:
                logger.warning("未找到用户信息，将创建默认用户。")
                self.add_default_user_if_not_exists()
                return self.get_current_user_info()
        except sqlite3.Error as e:
            logger.error(f"查询用户信息时发生错误：{str(e)}")
            return None
        