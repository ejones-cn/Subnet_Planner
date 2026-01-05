import json

with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查所有可能的翻译键
keys_to_check = [
    'parent_network_info',
    'parent_cidr',
    'network_address',
    'subnet_mask',
    'broadcast_address',
    'prefix_length',
    'available_addresses',
    'host_address_range',
    'split_segment_info',
    'split_segment',
    'wildcard_mask',
    'start_address',
    'end_address',
    'total_addresses',
    'usable_addresses',
    'remaining_segment_info',
    'cidr',
    'usable_address_count'
]

missing_keys = []
for key in keys_to_check:
    if key not in data:
        missing_keys.append(key)

print(f'缺失的翻译键: {missing_keys}')
