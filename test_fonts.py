# -*- coding: utf-8 -*-
"""
字体验证脚本
验证所有语言的字体配置是否正确
"""

from font_config import FontConfig

def test_all_fonts():
    """测试所有语言的字体配置"""
    
    languages = ["zh", "zh_tw", "ja", "ko", "en"]
    
    print("=" * 60)
    print("字体配置验证")
    print("=" * 60)
    
    for lang in languages:
        # 获取UI字体设置
        font_family, font_size = FontConfig.get_ui_font_settings(lang)
        
        # 获取标签宽度
        tab_width = FontConfig.get_ui_font_settings(lang)[1] if hasattr(FontConfig, 'get_tab_width') else 10
        
        # 获取字体候选列表
        font_candidates = FontConfig.get_font_candidates(lang)
        
        # 打印结果
        print(f"\n语言: {lang}")
        print(f"  UI字体: {font_family}")
        print(f"  字体大小: {font_size}")
        print(f"  字体候选数量: {len(font_candidates)}")
        print(f"  前3个字体:")
        for i, (font_file, font_name) in enumerate(font_candidates[:3]):
            print(f"    {i+1}. {font_name} ({font_file})")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_all_fonts()
