import logging
import os
import sys
from collections import deque

# 添加项目根目录到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.history_sqlite import HistorySQLite
from i18n import translate as _

logger = logging.getLogger(__name__)


class HistoryRepository:
    def __init__(self):
        self.db = HistorySQLite()

        self.history_states = deque(maxlen=20)
        self.current_history_index = -1
        self.planning_history_records = []

        # 使用与数据库一致的历史记录数量上限
        self.split_parent_networks = deque(maxlen=self.db.MAX_COMBO_HISTORY_ITEMS)
        self.split_networks = deque(maxlen=self.db.MAX_COMBO_HISTORY_ITEMS)
        self.planning_parent_networks = deque(maxlen=self.db.MAX_COMBO_HISTORY_ITEMS)

        self.ipv4_history = []
        self.ipv6_history = []
        self.range_start_history = []
        self.range_end_history = []

        self.history_records = []
        self.deleted_history = []

        self._load_from_db()

    def _load_from_db(self):
        """从数据库加载所有历史数据"""
        try:
            self._load_combo_histories()
            self._load_split_history()
        except Exception as e:
            logger.error(_("load_history_failed").format(error=str(e)))

    def _load_combo_histories(self):
        """从数据库加载所有下拉表历史"""
        # 直接使用数据库中的排序，最新的记录已经排在前面（sort_order ASC）
        # 使用与数据库一致的历史记录数量上限
        self.planning_parent_networks = deque(
            self.db.load_combo_history(HistorySQLite.CATEGORY_PLANNING_PARENT_V4),
            maxlen=self.db.MAX_COMBO_HISTORY_ITEMS
        )
        self.planning_parent_networks_v4 = self.planning_parent_networks
        self.planning_parent_networks_v6 = deque(
            self.db.load_combo_history(HistorySQLite.CATEGORY_PLANNING_PARENT_V6),
            maxlen=self.db.MAX_COMBO_HISTORY_ITEMS
        )

        self.split_parent_networks_v4 = deque(
            self.db.load_combo_history(HistorySQLite.CATEGORY_SPLIT_PARENT_V4),
            maxlen=self.db.MAX_COMBO_HISTORY_ITEMS
        )
        self.split_parent_networks_v6 = deque(
            self.db.load_combo_history(HistorySQLite.CATEGORY_SPLIT_PARENT_V6),
            maxlen=self.db.MAX_COMBO_HISTORY_ITEMS
        )
        self.split_networks_v4 = deque(
            self.db.load_combo_history(HistorySQLite.CATEGORY_SPLIT_NETWORK_V4),
            maxlen=self.db.MAX_COMBO_HISTORY_ITEMS
        )
        self.split_networks_v6 = deque(
            self.db.load_combo_history(HistorySQLite.CATEGORY_SPLIT_NETWORK_V6),
            maxlen=self.db.MAX_COMBO_HISTORY_ITEMS
        )

        self.split_parent_networks = self.split_parent_networks_v4
        self.split_networks = self.split_networks_v4

        self.ipv4_history = self.db.load_combo_history(HistorySQLite.CATEGORY_IPV4_QUERY)
        self.ipv6_history = self.db.load_combo_history(HistorySQLite.CATEGORY_IPV6_QUERY)
        self.range_start_history = self.db.load_combo_history(HistorySQLite.CATEGORY_RANGE_START)
        self.range_end_history = self.db.load_combo_history(HistorySQLite.CATEGORY_RANGE_END)

    def _load_split_history(self):
        """从数据库加载切分历史记录"""
        loaded = self.db.load_split_history()
        logger.info(_("loaded_split_history", count=len(loaded)))
        self.history_records.clear()
        self.history_records.extend(loaded)

    def save_state(self, state):
        """保存规划操作状态到撤销/重做栈"""
        self.history_states.append(state)
        self.current_history_index = len(self.history_states) - 1

    def get_state(self, index):
        """获取指定索引的操作状态"""
        if 0 <= index < len(self.history_states):
            return self.history_states[index]
        return None

    def undo(self):
        """撤销操作，返回上一个状态"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            return self.get_state(self.current_history_index)
        return None

    def can_undo(self):
        """判断是否可以撤销"""
        return self.current_history_index > 0

    def update_history(self, entry, history_list, value=None, max_items=None):
        """更新列表类型的历史记录（如高级工具下拉表）

        Args:
            entry: 输入框控件
            history_list: 历史列表
            value: 新值，为None时从entry获取
            max_items: 最大保留条目数，为None时使用与数据库一致的历史记录数量上限
        """
        # 如果没有指定max_items，使用与数据库一致的历史记录数量上限
        if max_items is None:
            max_items = self.db.MAX_COMBO_HISTORY_ITEMS
            
        if value is None:
            value = entry.get().strip()
        if value:
            # 如果值已存在，先移除它
            if value in history_list:
                history_list.remove(value)
            # 将值添加到列表开头
            history_list.insert(0, value)
            if len(history_list) > max_items:
                history_list.pop()
            if hasattr(entry, 'configure'):
                entry['values'] = history_list
            self._persist_combo_history(history_list)

    def update_history_entry(self, value, history_container, entry_widget):
        """更新deque类型的历史记录（如切分/规划父网段下拉表）

        Args:
            value: 新值
            history_container: deque容器
            entry_widget: 输入框控件
        """
        if value:
            # 如果值已存在，先移除它
            if value in history_container:
                history_container.remove(value)
            # 将值添加到列表开头
            history_container.appendleft(value)
            if len(history_container) > history_container.maxlen:
                history_container.pop()
        if hasattr(entry_widget, 'configure'):
            entry_widget['values'] = list(history_container)
        self._persist_combo_history(history_container)

    def _persist_combo_history(self, history_container):
        """将下拉表历史持久化到数据库

        Args:
            history_container: 历史容器（list或deque）
        """
        try:
            category = self._identify_category(history_container)
            if category:
                self.db.save_combo_history(category, list(history_container))
        except Exception as e:
            logger.error(_("persist_combo_history_failed", error=str(e)))

    def _identify_category(self, history_container):
        """根据容器对象识别其对应的数据库类别

        Args:
            history_container: 历史容器对象

        Returns:
            str: 类别标识，未识别返回None
        """
        container_map = {
            id(self.ipv4_history): HistorySQLite.CATEGORY_IPV4_QUERY,
            id(self.ipv6_history): HistorySQLite.CATEGORY_IPV6_QUERY,
            id(self.range_start_history): HistorySQLite.CATEGORY_RANGE_START,
            id(self.range_end_history): HistorySQLite.CATEGORY_RANGE_END,
            id(self.planning_parent_networks): HistorySQLite.CATEGORY_PLANNING_PARENT_V4,
            id(self.planning_parent_networks_v4): HistorySQLite.CATEGORY_PLANNING_PARENT_V4,
            id(self.planning_parent_networks_v6): HistorySQLite.CATEGORY_PLANNING_PARENT_V6,
            id(self.split_parent_networks): HistorySQLite.CATEGORY_SPLIT_PARENT_V4,
            id(self.split_parent_networks_v4): HistorySQLite.CATEGORY_SPLIT_PARENT_V4,
            id(self.split_parent_networks_v6): HistorySQLite.CATEGORY_SPLIT_PARENT_V6,
            id(self.split_networks): HistorySQLite.CATEGORY_SPLIT_NETWORK_V4,
            id(self.split_networks_v4): HistorySQLite.CATEGORY_SPLIT_NETWORK_V4,
            id(self.split_networks_v6): HistorySQLite.CATEGORY_SPLIT_NETWORK_V6,
        }
        return container_map.get(id(history_container))

    def save_combo_history_by_category(self, category, values):
        """按类别保存下拉表历史到数据库

        Args:
            category: 类别标识
            values: 历史值列表
        """
        if getattr(self.db, '_db_available', True):
            try:
                self.db.save_combo_history(category, values)
            except Exception as e:
                logger.error(_("save_combo_history_failed", category=category, error=str(e)))

    def add_split_record(self, parent, split):
        """添加切分历史记录

        Args:
            parent: 父网段
            split: 切分段

        Returns:
            bool: 是否添加成功
        """
        duplicate_exists = any(
            record['parent'] == parent and record['split'] == split for record in self.history_records
        )
        if getattr(self.db, '_db_available', True):
            try:
                # 先尝试持久化到数据库（会更新已存在记录的时间戳）
                success = self.db.add_split_record(parent, split)
                if success:
                    # 如果记录已存在，先从内存中移除
                    if duplicate_exists:
                        self.history_records[:] = [
                            r for r in self.history_records
                            if not (r['parent'] == parent and r['split'] == split)
                        ]
                    # 将记录添加到内存的开头（最新的记录显示在最前面）
                    split_record = {'parent': parent, 'split': split}
                    self.history_records.insert(0, split_record)
                    return True
            except Exception as e:
                logger.error(_("persist_split_history_failed", error=str(e)))
        return False

    def delete_split_record(self, parent, split):
        """删除切分历史记录

        Args:
            parent: 父网段
            split: 切分段
        """
        if getattr(self.db, '_db_available', True):
            try:
                # 先尝试从数据库删除
                self.db.delete_split_record(parent, split)
                # 数据库操作成功后，再从内存删除
                self.history_records[:] = [
                    r for r in self.history_records
                    if not (r['parent'] == parent and r['split'] == split)
                ]
            except Exception as e:
                logger.error(_("delete_split_history_failed", error=str(e)))

    def clear_split_history(self):
        """清空所有切分历史记录"""
        if getattr(self.db, '_db_available', True):
            try:
                # 先尝试从数据库清空
                self.db.clear_split_history()
                # 数据库操作成功后，再从内存清空
                self.history_records.clear()
            except Exception as e:
                logger.error(_("clear_split_history_failed", error=str(e)))

    def add_deleted_record(self, record):
        """添加已删除记录到撤销栈"""
        self.deleted_history.append(record)

    def pop_deleted_record(self):
        """弹出最近删除的记录"""
        if self.deleted_history:
            return self.deleted_history.pop()
        return None

    def load_requirements_data(self, table_type):
        """从数据库加载子网需求或需求池数据

        Args:
            table_type: 表类型（requirements或pool）

        Returns:
            list[tuple]: (name, hosts) 列表
        """
        try:
            return self.db.load_requirements_data(table_type)
        except Exception as e:
            logger.error(_("load_requirements_failed", table_type=table_type, error=str(e)))
            return []

    def save_requirements_data(self, table_type, data_list):
        """保存子网需求或需求池数据到数据库

        Args:
            table_type: 表类型（requirements或pool）
            data_list: (name, hosts) 列表
        """
        if getattr(self.db, '_db_available', True):
            try:
                self.db.save_requirements_data(table_type, data_list)
            except Exception as e:
                logger.error(_("save_requirements_failed", table_type=table_type, error=str(e)))

    def load_text_data(self, category):
        """从数据库加载文本数据

        Args:
            category: 类别标识

        Returns:
            str: 文本内容
        """
        try:
            return self.db.load_text_data(category)
        except Exception as e:
            logger.error(_("load_text_data_failed", category=category, error=str(e)))
            return ""

    def save_text_data(self, category, content):
        """保存文本数据到数据库

        Args:
            category: 类别标识
            content: 文本内容
        """
        if getattr(self.db, '_db_available', True):
            try:
                self.db.save_text_data(category, content)
            except Exception as e:
                logger.error(_("save_text_data_failed", category=category, error=str(e)))
