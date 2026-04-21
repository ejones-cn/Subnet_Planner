from ipam_sqlite import IPAMSQLite


def init_ipam():
    return IPAMSQLite()


class IPAMRepository:
    def __init__(self):
        self.ipam = init_ipam()

    def get_all_networks(self):
        return self.ipam.get_all_networks()

    def get_network(self, network_address):
        return self.ipam.get_network(network_address)

    def add_network(self, network_address, description=""):
        return self.ipam.add_network(network_address, description)

    def update_network(self, network_address, description):
        return self.ipam.update_network(network_address, description)

    def delete_network(self, network_address):
        return self.ipam.delete_network(network_address)

    def get_ips_in_network(self, network_address):
        return self.ipam.get_ips_in_network(network_address)

    def add_ip(self, network_address, ip_address, status="available", description=""):
        return self.ipam.add_ip(network_address, ip_address, status, description)

    def update_ip_status(self, ip_id, status, description=None):
        return self.ipam.update_ip_status_by_id(ip_id, status, description)

    def delete_ip(self, ip_id):
        return self.ipam.delete_ip_by_id(ip_id)

    def get_last_backup_time(self):
        return self.ipam.get_last_backup_time()

    def backup_data(self, backup_type='manual', frequency=None):
        return self.ipam.backup_data(backup_type=backup_type, frequency=frequency)

    def restore_data(self, backup_file):
        return self.ipam.restore_data(backup_file)

    def get_all_backups(self):
        return self.ipam.get_all_backups()

    def search_ips(self, keyword, search_mode="contains"):
        return self.ipam.search_ips(keyword, search_mode)

    def get_network_stats(self, network_address):
        return self.ipam.get_network_stats(network_address)

    def get_ip_by_id(self, ip_id):
        return self.ipam.get_ip_record_by_id(ip_id)

    def allocate_ip(self, network_address, ip_address, description="", status="allocated"):
        return self.ipam.allocate_ip(network_address, ip_address, description, status)

    def release_ip(self, ip_id):
        return self.ipam.release_ip_by_id(ip_id)

    def reserve_ip(self, network_address, ip_address, description=""):
        return self.ipam.reserve_ip(network_address, ip_address, description)

    def get_expired_ips(self):
        return self.ipam.get_expired_ips()

    def get_expiring_ips(self, days_ahead=7):
        return self.ipam.get_expiring_ips(days_ahead)

    def set_ip_expiry(self, ip_id, expiry_date):
        return self.ipam.update_ip_expiry_by_id(ip_id, expiry_date)

    def batch_allocate_ips(self, network_address, ip_addresses, description=""):
        return self.ipam.batch_allocate_ips(network_address, ip_addresses, description)

    def batch_release_ips(self, ip_ids):
        return self.ipam.batch_release_ips(ip_ids)

    def check_ip_conflicts(self, network_address=None):
        return self.ipam.check_ip_conflicts(network_address)

    def get_available_ips(self, network_address):
        return self.ipam.get_available_ips(network_address)

    def cleanup_available_ips(self, network_address):
        return self.ipam.cleanup_available_ips(network_address)

    def batch_migrate_ips(self, ip_ids, target_network):
        return self.ipam.batch_migrate_ips(ip_ids, target_network)

    def batch_set_expiry_date(self, ip_ids, expiry_date):
        return self.ipam.batch_update_ip_expiry_by_ids(ip_ids, expiry_date)

    def update_ip_record(self, record_id, hostname, mac_address, description, expiry_date=None):
        return self.ipam.update_ip_record(record_id, hostname, mac_address, description, expiry_date)

    def update_ip_info(self, ip_address, hostname=None, description=None, mac_address=""):
        return self.ipam.update_ip_info(ip_address, hostname, description, mac_address)

    def update_ip_expiry(self, ip_address, expiry_date, record_id=None):
        return self.ipam.update_ip_expiry(ip_address, expiry_date, record_id)

    def batch_update_ip_expiry(self, ip_addresses, expiry_date, record_ids=None):
        return self.ipam.batch_update_ip_expiry(ip_addresses, expiry_date, record_ids)