import sqlite3
import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from i18n import translate as _
from window_utils import get_app_directory

logger = logging.getLogger(__name__)


class HistorySQLite:
    """历史数据持久化数据库访问类"""

    # 历史记录数量上限设定
    # 下拉表历史记录数量上限（数据库和内存）
    MAX_COMBO_HISTORY_ITEMS = 10
    # 切分历史记录数量上限（数据库）
    MAX_SPLIT_HISTORY_ITEMS = 20

    CATEGORY_PLANNING_PARENT_V4 = "planning_parent_v4"
    CATEGORY_PLANNING_PARENT_V6 = "planning_parent_v6"
    CATEGORY_SPLIT_PARENT_V4 = "split_parent_v4"
    CATEGORY_SPLIT_PARENT_V6 = "split_parent_v6"
    CATEGORY_SPLIT_NETWORK_V4 = "split_network_v4"
    CATEGORY_SPLIT_NETWORK_V6 = "split_network_v6"
    CATEGORY_IPV4_QUERY = "ipv4_query"
    CATEGORY_IPV6_QUERY = "ipv6_query"
    CATEGORY_RANGE_START = "range_start"
    CATEGORY_RANGE_END = "range_end"

    CATEGORY_SUBNET_MERGE = "subnet_merge"
    CATEGORY_OVERLAP_DETECTION = "overlap_detection"

    TABLE_REQUIREMENTS = "requirements"
    TABLE_POOL = "pool"

    SAMPLE_COMBO_HISTORY = {
        CATEGORY_PLANNING_PARENT_V4: ["10.21.48.0/20", "192.168.0.0/16"],
        CATEGORY_PLANNING_PARENT_V6: ["2001:0db8::/32", "fe80::/10"],
        CATEGORY_SPLIT_PARENT_V4: ["10.0.0.0/8", "172.16.0.0/12"],
        CATEGORY_SPLIT_PARENT_V6: ["2001:0db8::/32", "fe80::/10"],
        CATEGORY_SPLIT_NETWORK_V4: ["10.21.50.0/23", "172.20.180.0/24"],
        CATEGORY_SPLIT_NETWORK_V6: ["2001:0db8::/64", "fe80::1/128"],
        CATEGORY_IPV4_QUERY: ["192.168.1.1", "10.0.0.1"],
        CATEGORY_IPV6_QUERY: ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "fe80::1"],
        CATEGORY_RANGE_START: ["192.168.0.1", "10.0.0.1", "2001:db8::1", "fe80::1"],
        CATEGORY_RANGE_END: ["192.168.30.254", "10.0.0.254", "2001:db8::100", "fe80::100"],
    }

    SAMPLE_REQUIREMENTS_DATA = {
        TABLE_REQUIREMENTS: [
            ("office", 20), ("hr_department", 10), ("finance_department", 10),
            ("planning_department", 30), ("legal", 10), ("procurement", 10),
            ("security", 10), ("party", 20), ("discipline", 10), ("it_department", 20),
        ],
        TABLE_POOL: [
            ("engineering", 20), ("sales", 20), ("rd", 15),
            ("production", 100), ("transportation", 20),
        ],
    }

    SAMPLE_TEXT_DATA = {
        CATEGORY_SUBNET_MERGE: (
            "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24\n"
            "10.21.16.0/24\n10.21.17.0/24\n10.21.18.0/24\n"
            "10.21.19.128/26\n10.21.19.192/26\n"
            "2001:0db8::/127\n2001:0db8::2/127\n"
            "2001:0db8::4/127\n2001:0db8::6/127\n"
            "2001:0db8:1::/64\n2001:0db8:2::/64\n2001:0db8:3::/64"
        ),
        CATEGORY_OVERLAP_DETECTION: (
            "192.168.0.0/24\n192.168.0.128/25\n"
            "10.0.0.0/16\n10.0.0.128/25\n10.0.10.0/20\n10.10.0.0/23\n"
            "2001:0db8::/64\n2001:0db8::1000/120\n"
            "2001:0db8:1::/64\n2001:0db8:2::/64\n"
            "2001:0db8:1:0::/66\n2001:0db8:1:1000::/66"
        ),
    }

    def __init__(self, db_file=None):
        """初始化历史数据库

        Args:
            db_file: 数据库文件路径，为None时自动使用程序所在目录
        """
        self.app_dir = get_app_directory()
        if db_file is None:
            db_file = os.path.join(self.app_dir, "SubnetPlanner_data.db")
        self.db_file = db_file
        self._db_available = True
        try:
            self.init_db()
        except Exception as e:
            self._db_available = False
            logger.error(_("history_db_init_failed", error=str(e)))

    def _get_connection(self):
        """获取数据库连接

        Returns:
            sqlite3.Connection: 数据库连接，数据库不可用时返回None
        """
        if not self._db_available:
            return None
        return sqlite3.connect(self.db_file)

    def init_db(self):
        """初始化数据库，创建表并插入样例数据"""
        conn = self._get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            self._create_tables(cursor)
            self._insert_sample_data(cursor)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("history_db_init_failed_general", error=str(e)))
            raise
        finally:
            conn.close()

    def _create_tables(self, cursor):
        """创建所有历史数据表"""
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS combo_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            value TEXT NOT NULL,
            sort_order INTEGER NOT NULL,
            UNIQUE(category, value)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requirements_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_type TEXT NOT NULL,
            name TEXT NOT NULL,
            hosts INTEGER NOT NULL,
            sort_order INTEGER NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS split_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent TEXT NOT NULL,
            split TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(parent, split)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS text_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            updated_at TEXT,
            UNIQUE(category)
        )
        ''')

    def _insert_sample_data(self, cursor):
        """检查表是否为空，如果为空则插入样例数据"""
        cursor.execute("SELECT COUNT(*) FROM combo_history")
        if cursor.fetchone()[0] == 0:
            for category, values in self.SAMPLE_COMBO_HISTORY.items():
                for order, value in enumerate(values):
                    cursor.execute(
                        "INSERT OR IGNORE INTO combo_history (category, value, sort_order) VALUES (?, ?, ?)",
                        (category, value, order)
                    )

        cursor.execute("SELECT COUNT(*) FROM requirements_data")
        if cursor.fetchone()[0] == 0:
            for table_type, items in self.SAMPLE_REQUIREMENTS_DATA.items():
                for order, (name, hosts) in enumerate(items):
                    translated_name = _(name)
                    cursor.execute(
                        "INSERT INTO requirements_data (table_type, name, hosts, sort_order) VALUES (?, ?, ?, ?)",
                        (table_type, translated_name, hosts, order)
                    )

        cursor.execute("SELECT COUNT(*) FROM text_data")
        if cursor.fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for category, content in self.SAMPLE_TEXT_DATA.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO text_data (category, content, updated_at) VALUES (?, ?, ?)",
                    (category, content, now)
                )

    def load_combo_history(self, category):
        """加载指定类别的下拉表历史

        Args:
            category: 类别标识

        Returns:
            list[str]: 历史值列表，按sort_order排序
        """
        conn = self._get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM combo_history WHERE category = ? ORDER BY sort_order ASC",
                (category,)
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(_("load_combo_history_failed", category=category, error=str(e)))
            return []
        finally:
            conn.close()

    def save_combo_history(self, category, values):
        """保存指定类别的下拉表历史（全量替换）

        Args:
            category: 类别标识
            values: 历史值列表
        """
        conn = self._get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM combo_history WHERE category = ?", (category,))
            for order, value in enumerate(values):
                cursor.execute(
                    "INSERT OR IGNORE INTO combo_history (category, value, sort_order) VALUES (?, ?, ?)",
                    (category, value, order)
                )
            self._enforce_combo_history_limit(cursor, category)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("save_combo_history_failed", category=category, error=str(e)))
        finally:
            conn.close()

    def add_combo_history_item(self, category, value):
        """添加单条下拉表历史记录

        Args:
            category: 类别标识
            value: 历史值
        """
        conn = self._get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sort_order FROM combo_history WHERE category = ? AND value = ?",
                (category, value)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute("DELETE FROM combo_history WHERE category = ? AND value = ?", (category, value))

            # 将新记录的 sort_order 设置为 0，使其排在最前面
            # 同时将其他记录的 sort_order 加 1
            cursor.execute("UPDATE combo_history SET sort_order = sort_order + 1 WHERE category = ?", (category,))
            
            cursor.execute(
                "INSERT OR IGNORE INTO combo_history (category, value, sort_order) VALUES (?, ?, ?)",
                (category, value, 0)
            )
            self._enforce_combo_history_limit(cursor, category)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("save_combo_history_item_failed", category=category, error=str(e)))
        finally:
            conn.close()

    def _enforce_combo_history_limit(self, cursor, category):
        """执行下拉表历史数量上限

        Args:
            cursor: 数据库游标
            category: 类别标识
        """
        cursor.execute(
            "SELECT COUNT(*) FROM combo_history WHERE category = ?",
            (category,)
        )
        count = cursor.fetchone()[0]
        if count > self.MAX_COMBO_HISTORY_ITEMS:
            cursor.execute(
                """DELETE FROM combo_history WHERE category = ? AND id IN (
                    SELECT id FROM combo_history WHERE category = ?
                    ORDER BY sort_order ASC LIMIT ?
                )""",
                (category, category, count - self.MAX_COMBO_HISTORY_ITEMS)
            )

    def load_requirements_data(self, table_type):
        """加载子网需求或需求池数据

        Args:
            table_type: 表类型（requirements或pool）

        Returns:
            list[tuple]: (name, hosts) 列表
        """
        conn = self._get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, hosts FROM requirements_data WHERE table_type = ? ORDER BY sort_order ASC",
                (table_type,)
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(_("load_requirements_failed", table_type=table_type, error=str(e)))
            return []
        finally:
            conn.close()

    def save_requirements_data(self, table_type, data_list):
        """保存子网需求或需求池数据（全量替换）

        Args:
            table_type: 表类型（requirements或pool）
            data_list: (name, hosts) 列表
        """
        conn = self._get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requirements_data WHERE table_type = ?", (table_type,))
            for order, (name, hosts) in enumerate(data_list):
                cursor.execute(
                    "INSERT INTO requirements_data (table_type, name, hosts, sort_order) VALUES (?, ?, ?, ?)",
                    (table_type, name, hosts, order)
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("save_requirements_failed", table_type=table_type, error=str(e)))
        finally:
            conn.close()

    def load_split_history(self):
        """加载切分历史记录

        Returns:
            list[dict]: 切分历史记录列表，每条包含parent和split
        """
        conn = self._get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT parent, split FROM split_history ORDER BY created_at DESC"
            )
            return [{"parent": row[0], "split": row[1]} for row in cursor.fetchall()]
        except Exception as e:
            logger.error(_("load_history_failed", error=str(e)))
            return []
        finally:
            conn.close()

    def add_split_record(self, parent, split):
        """添加切分历史记录

        Args:
            parent: 父网段
            split: 切分段

        Returns:
            bool: 是否添加成功
        """
        conn = self._get_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 先尝试更新已存在的记录（更新时间戳）
            cursor.execute(
                "UPDATE split_history SET created_at = ? WHERE parent = ? AND split = ?",
                (now, parent, split)
            )
            # 如果没有更新任何记录（记录不存在），则插入新记录
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT OR IGNORE INTO split_history (parent, split, created_at) VALUES (?, ?, ?)",
                    (parent, split, now)
                )
            self._enforce_split_history_limit(cursor)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(_("add_split_history_failed", error=str(e)))
            return False
        finally:
            conn.close()

    def delete_split_record(self, parent, split):
        """删除切分历史记录

        Args:
            parent: 父网段
            split: 切分段
        """
        conn = self._get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM split_history WHERE parent = ? AND split = ?",
                (parent, split)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("delete_split_history_failed", error=str(e)))
        finally:
            conn.close()

    def clear_split_history(self):
        """清空所有切分历史记录"""
        conn = self._get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM split_history")
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("clear_split_history_failed", error=str(e)))
        finally:
            conn.close()

    def _enforce_split_history_limit(self, cursor):
        """执行切分历史记录数量上限

        Args:
            cursor: 数据库游标
        """
        cursor.execute("SELECT COUNT(*) FROM split_history")
        count = cursor.fetchone()[0]
        if count > self.MAX_SPLIT_HISTORY_ITEMS:
            cursor.execute(
                """DELETE FROM split_history WHERE id IN (
                    SELECT id FROM split_history ORDER BY created_at ASC LIMIT ?
                )""",
                (count - self.MAX_SPLIT_HISTORY_ITEMS,)
            )

    def load_text_data(self, category):
        """加载文本数据

        Args:
            category: 类别标识

        Returns:
            str: 文本内容，不存在时返回空字符串
        """
        conn = self._get_connection()
        if conn is None:
            return ""
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content FROM text_data WHERE category = ?",
                (category,)
            )
            row = cursor.fetchone()
            return row[0] if row else ""
        except Exception as e:
            logger.error(_("load_text_data_failed", category=category, error=str(e)))
            return ""
        finally:
            conn.close()

    def save_text_data(self, category, content):
        """保存文本数据（UPSERT）

        Args:
            category: 类别标识
            content: 文本内容
        """
        conn = self._get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT OR REPLACE INTO text_data (category, content, updated_at)
                VALUES (?, ?, ?)""",
                (category, content, now)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(_("save_text_data_failed", category=category, error=str(e)))
        finally:
            conn.close()
