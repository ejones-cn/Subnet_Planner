from collections import deque


class HistoryRepository:
    def __init__(self):
        self.history_states = deque(maxlen=20)
        self.current_history_index = -1
        self.planning_history_records = []

        self.split_parent_networks = deque(maxlen=100)
        self.split_networks = deque(maxlen=100)
        self.planning_parent_networks = deque(maxlen=100)

        self.ipv4_history = ["192.168.1.1", "10.0.0.1"]
        self.ipv6_history = ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "fe80::1"]
        self.range_start_history = ["192.168.0.1", "10.0.0.1", "2001:db8::1", "fe80::1"]
        self.range_end_history = ["192.168.30.254", "10.0.0.254", "2001:db8::100", "fe80::100"]

        self.history_records = []
        self.deleted_history = []

    def save_state(self, state):
        self.history_states.append(state)
        self.current_history_index = len(self.history_states) - 1

    def get_state(self, index):
        if 0 <= index < len(self.history_states):
            return self.history_states[index]
        return None

    def undo(self):
        if self.current_history_index > 0:
            self.current_history_index -= 1
            return self.get_state(self.current_history_index)
        return None

    def can_undo(self):
        return self.current_history_index > 0

    def update_history(self, entry, history_list, value=None, max_items=10):
        if value is None:
            value = entry.get().strip()
        if value and value not in history_list:
            history_list.insert(0, value)
            if len(history_list) > max_items:
                history_list.pop()
            if hasattr(entry, 'configure'):
                entry['values'] = history_list

    def update_history_entry(self, value, history_container, entry_widget):
        if value and value not in history_container:
            history_container.appendleft(value)
            if len(history_container) > history_container.maxlen:
                history_container.pop()
        if hasattr(entry_widget, 'configure'):
            entry_widget['values'] = list(history_container)

    def add_split_record(self, parent, split):
        duplicate_exists = any(
            record['parent'] == parent and record['split'] == split for record in self.history_records
        )
        if not duplicate_exists:
            split_record = {'parent': parent, 'split': split}
            self.history_records.append(split_record)
            return True
        return False

    def add_deleted_record(self, record):
        self.deleted_history.append(record)

    def pop_deleted_record(self):
        if self.deleted_history:
            return self.deleted_history.pop()
        return None
