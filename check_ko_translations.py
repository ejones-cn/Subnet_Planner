#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
韩语翻译全面检查和修复脚本
"""

import json
import re
from collections import defaultdict

class KoreanTranslationChecker:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = self.load_json()
        self.ko_translations = self.extract_korean_translations()
        self.issues = []
        self.fixes = {}
    
    def load_json(self):
        """加载JSON文件"""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_korean_translations(self):
        """提取所有韩语翻译"""
        translations = {}
        for key, value in self.data.items():
            if isinstance(value, dict) and 'ko' in value:
                translations[key] = value['ko']
        return translations
    
    def check_translations(self):
        """全面检查韩语翻译"""
        print("=== 韩语翻译全面检查开始 ===")
        print(f"总翻译项数: {len(self.ko_translations)}")
        
        # 1. 检查常见问题
        self.check_common_issues()
        
        # 2. 检查术语一致性
        self.check_term_consistency()
        
        # 3. 检查语法和表达习惯
        self.check_grammar_and_usage()
        
        print("\n=== 检查完成 ===")
        print(f"发现问题数: {len(self.issues)}")
        
        return self.issues
    
    def check_common_issues(self):
        """检查常见的翻译问题"""
        print("\n--- 检查常见问题 ---")
        
        # 定义常见问题模式，使用更精确的匹配
        common_issues = [
            # (精确匹配的键, 当前值, 修复值, 原因)
            ('confirm', '확   인', '확인', '多余空格'),
            ('available_count', '사용 가능', '사용 가능 수', '缺少"수"'),
            ('about', '관련 있는', '소개', '不准确翻译'),
            ('wildcard_mask', '와일드카드 가면', '와일드카드 마스크', '技术术语错误'),
            ('end', '닫기', '끝', '语境不符'),
            ('check_overlap', '검출 중첩', '중첩 검사', '语序问题'),
            ('detection_result', '테스트 결과', '검출 결과', '语境不符'),
            ('unknown', '의문의', '알 수 없는', '不准确翻译'),
            ('valid', '하루 동안 머물러', '유효', '完全错误'),
            ('invalid', '유효없음', '무효', '表达不标准'),
            ('start_address', '폼주소', '시작 주소', '语境不符'),
            ('host_range_start', '폼주소', '시작 주소', '语境不符'),
            ('select_export_directory', '디렉터리 내보내기 선택', '내보내기 디렉터리 선택', '语序问题'),
            ('planning_result', '결과 계획하기', '계획 결과', '语序问题'),
            ('execute_split', '분할 수행', '분할 실행', '不一致'),
        ]
        
        # 处理需要替换特定短语的情况
        phrase_replacements = [
            # (短语, 修复值, 原因)
            ('예약 가능한', '사용 가능한', '术语不一致'),
            ('디렉터리 내보내기', '내보내기 디렉터리', '语序问题'),
        ]
        
        # 处理精确匹配的问题
        for key, current, suggested, reason in common_issues:
            if key in self.ko_translations and self.ko_translations[key] == current:
                self.issues.append({
                    'key': key,
                    'current': current,
                    'suggested': suggested,
                    'reason': reason
                })
                self.fixes[key] = suggested
        
        # 处理短语替换的问题
        for phrase, replacement, reason in phrase_replacements:
            for key, translation in self.ko_translations.items():
                if phrase in translation:
                    # 确保不会替换到已经包含修复值的情况
                    if replacement not in translation:
                        suggested = translation.replace(phrase, replacement)
                        self.issues.append({
                            'key': key,
                            'current': translation,
                            'suggested': suggested,
                            'reason': f'{reason}: {phrase} → {replacement}'
                        })
                        self.fixes[key] = suggested
    
    def check_term_consistency(self):
        """检查术语一致性"""
        print("\n--- 检查术语一致性 ---")
        
        # 检查关键术语的一致性
        term_groups = {
            '规划结果': ['planning_result', 'save_subnet_planning_result', 'save_subnet_split_result'],
            '导出目录': ['select_export_directory', 'one_click_export_success', 'one_click_pdf_success'],
            '可用主机': ['usable_hosts', 'first_host', 'last_host', 'first_usable_host', 'last_usable_host'],
            '子网': ['subnet_planner', 'subnet_requirements', 'add_subnet_requirement'],
            '网络': ['network_address', 'network_configuration', 'network_scale_and_usage'],
        }
        
        for group_name, keys in term_groups.items():
            translations = [self.ko_translations[key] for key in keys if key in self.ko_translations]
            if len(set(translations)) > 1:
                print(f"术语不一致 - {group_name}: {set(translations)}")
    
    def check_grammar_and_usage(self):
        """检查语法和表达习惯"""
        print("\n--- 检查语法和表达习惯 ---")
        
        # 检查"하는 것이 좋습니다"的使用
        for key, translation in self.ko_translations.items():
            if '하는 것이 좋습니다' in translation:
                print(f"建议简化 - {key}: {translation}")
        
        # 检查"입니다."的使用
        for key, translation in self.ko_translations.items():
            if '입니다.' in translation:
                # 技术文档中通常使用更简洁的表达
                pass
    
    def apply_fixes(self):
        """应用修复"""
        print("\n=== 应用修复 ===")
        print(f"准备修复 {len(self.fixes)} 个问题")
        
        # 应用修复到数据中
        for key, fixed_value in self.fixes.items():
            if key in self.data and isinstance(self.data[key], dict) and 'ko' in self.data[key]:
                old_value = self.data[key]['ko']
                if old_value != fixed_value:
                    self.data[key]['ko'] = fixed_value
                    print(f"修复了 {key}: {old_value} → {fixed_value}")
        
        # 保存修复后的数据
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        
        print("\n修复完成，文件已保存")
    
    def generate_report(self, report_file="ko_translation_report.txt"):
        """生成修复报告"""
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== 韩语翻译修复报告 ===\n\n")
            f.write(f"检查时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总翻译项数: {len(self.ko_translations)}\n")
            f.write(f"发现问题数: {len(self.issues)}\n")
            f.write(f"修复问题数: {len(self.fixes)}\n\n")
            
            f.write("--- 修复详情 ---\n\n")
            for issue in self.issues:
                f.write(f"键: {issue['key']}\n")
                f.write(f"当前翻译: {issue['current']}\n")
                f.write(f"建议翻译: {issue['suggested']}\n")
                f.write(f"原因: {issue['reason']}\n\n")
        
        print(f"\n报告已生成: {report_file}")

# 主程序
if __name__ == "__main__":
    checker = KoreanTranslationChecker("translations.json")
    issues = checker.check_translations()
    checker.apply_fixes()
    checker.generate_report()