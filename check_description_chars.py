import sqlite3
import sys

def check_description_chars(db_path='./SubnetPlanner_data.db'):
    """检查数据库中描述字段的特殊字符"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT network_address, description FROM networks WHERE network_address LIKE "2001:db8%"')
            rows = cursor.fetchall()
            
            print("=== IPv6网段描述字段检查 ===")
            for network, description in rows:
                print(f"\n网段: {network}")
                print(f"描述值: {repr(description)}")
                print(f"描述长度: {len(description) if description else 0}")
                
                if description:
                    print("字符详情:")
                    for i, char in enumerate(description):
                        char_code = ord(char)
                        print(f"  位置{i}: '{char}' (ASCII/Unicode: {char_code})")
                        if char_code < 32 or char_code == 127:
                            print(f"    ⚠️  控制字符!")
                        elif char_code > 127:
                            print(f"    🔤 Unicode字符")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_description_chars()
    input("按回车退出...")