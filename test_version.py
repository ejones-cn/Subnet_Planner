#!/usr/bin/env python3
"""
测试版本信息获取功能
"""

import sys
import os

# 将当前目录添加到Python路径
sys.path.insert(0, os.getcwd())


def test_version_import():
    """测试直接导入version模块"""
    print("=== 测试直接导入version模块 ===")
    try:
        import version
        
        print(f"版本号: {version.__version__}")
        print(f"主版本号: {version.MAJOR_VERSION}")
        print(f"次版本号: {version.MINOR_VERSION}")
        print(f"修订号: {version.PATCH_VERSION}")
        print(f"版本元组: {version.VERSION_TUPLE}")
        print(f"当前版本发布日期: {version.get_release_date()}")
        print(f"2.5.5版本发布日期: {version.get_release_date('2.5.5')}")
        
        print("✅ 直接导入version模块成功")
        return True
    except Exception as e:
        print(f"❌ 直接导入version模块失败: {e}")
        return False


def test_get_version_info():
    """测试build_compile.py中的get_version_info函数"""
    print("\n=== 测试build_compile.py中的get_version_info函数 ===")
    try:
        # 导入build_compile模块
        import build_compile
        
        version = build_compile.get_version_info()
        print(f"get_version_info()返回: {version}")
        
        print("✅ get_version_info函数调用成功")
        return True
    except Exception as e:
        print(f"❌ get_version_info函数调用失败: {e}")
        return False


def test_full_version_access():
    """测试从build_compile中访问完整的版本元数据"""
    print("\n=== 测试从build_compile中访问完整的版本元数据 ===")
    try:
        # 直接导入version模块以访问完整元数据
        import version
        
        # 测试所有可用的版本相关功能
        print(f"版本号: {version.get_version()}")
        print(f"版本元组: {version.get_version_tuple()}")
        print(f"主要版本: {version.VERSION_TUPLE[0]}")
        print(f"次要版本: {version.VERSION_TUPLE[1]}")
        print(f"补丁版本: {version.VERSION_TUPLE[2]}")
        
        print("✅ 完整版本元数据访问成功")
        return True
    except Exception as e:
        print(f"❌ 完整版本元数据访问失败: {e}")
        return False



if __name__ == "__main__":
    print("开始测试版本信息获取功能...")
    
    test1 = test_version_import()
    test2 = test_get_version_info()
    test3 = test_full_version_access()
    
    print("\n=== 测试结果汇总 ===")
    print(f"直接导入version模块: {'通过' if test1 else '失败'}")
    print(f"get_version_info函数: {'通过' if test2 else '失败'}")
    print(f"完整版本元数据访问: {'通过' if test3 else '失败'}")
    
    if test1 and test2 and test3:
        print("\n🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败!")
        sys.exit(1)
