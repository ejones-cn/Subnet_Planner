import json
import re

class JapaneseTranslationChecker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()
        self.japanese_chars = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF]')
        
        # 定义标准术语映射
        self.standard_terms = {
            "Import": "インポート",
            "Export": "エクスポート",
            "Subnet": "サブネット",
            "Network": "ネットワーク",
            "Address": "アドレス",
            "Prefix": "プレフィックス",
            "Host": "ホスト",
            "Segment": "セグメント",
            "Mask": "マスク",
            "Subnet Mask": "サブネットマスク",
            "CIDR": "CIDR",
            "IPv4": "IPv4",
            "IPv6": "IPv6",
            "Split": "分割",
            "Plan": "計画",
            "Execute": "実行",
            "Save": "保存",
            "Delete": "削除",
            "Add": "追加",
            "Cancel": "キャンセル",
            "OK": "確定",
            "Confirm": "確認",
            "Error": "エラー"
        }
        
        # 定义检查结果
        self.results = {
            "total": 0,
            "no_japanese_chars": [],
            "inconsistent_terms": [],
            "punctuation_issues": [],
            "grammar_issues": [],
            "valid_translations": 0
        }
    
    def load_data(self):
        """加载JSON数据"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_translations(self):
        """检查所有日语翻译"""
        print("=== 开始全面检查日语翻译 ===")
        
        for key, value in self.data.items():
            if isinstance(value, dict) and 'ja' in value:
                self.results["total"] += 1
                ja_translation = value["ja"]
                en_translation = value.get('en', '')
                
                # 检查1: 是否包含日语字符
                if not self.japanese_chars.search(ja_translation):
                    # 检查是否是技术术语或符号
                    if key not in ["move_records"] and ja_translation not in ["↔", "CIDR", "IPv4", "IPv6"]:
                        self.results["no_japanese_chars"].append({
                            "key": key,
                            "translation": ja_translation,
                            "en_translation": en_translation
                        })
                    else:
                        self.results["valid_translations"] += 1
                else:
                    issues = []
                    
                    # 检查2: 术语一致性
                    inconsistent_terms = self.check_term_consistency(ja_translation, en_translation)
                    if inconsistent_terms:
                        self.results["inconsistent_terms"].append({
                            "key": key,
                            "translation": ja_translation,
                            "en_translation": en_translation,
                            "issues": inconsistent_terms
                        })
                        issues.extend(inconsistent_terms)
                    
                    # 检查3: 标点符号
                    punctuation_issues = self.check_punctuation(ja_translation)
                    if punctuation_issues:
                        self.results["punctuation_issues"].append({
                            "key": key,
                            "translation": ja_translation,
                            "issues": punctuation_issues
                        })
                        issues.extend(punctuation_issues)
                    
                    # 检查4: 语法问题
                    grammar_issues = self.check_grammar(ja_translation)
                    if grammar_issues:
                        self.results["grammar_issues"].append({
                            "key": key,
                            "translation": ja_translation,
                            "issues": grammar_issues
                        })
                        issues.extend(grammar_issues)
                    
                    # 如果没有问题，标记为有效翻译
                    if not issues:
                        self.results["valid_translations"] += 1
        
        self.print_results()
        return self.results
    
    def check_term_consistency(self, ja_translation, en_translation):
        """检查术语一致性"""
        issues = []
        
        # 检查每个标准术语
        for en_term, ja_term in self.standard_terms.items():
            # 如果英文翻译包含该术语
            if en_term.lower() in en_translation.lower():
                # 检查日语翻译是否包含正确的对应术语
                if ja_term not in ja_translation:
                    issues.append(f"术语 '{en_term}' 应翻译为 '{ja_term}'")
        
        # 特殊检查：サブネット vs サブネットワーク
        if "サブネットワーク" in ja_translation:
            issues.append("'サブネットワーク' 应简化为 'サブネット'")
        
        # 特殊检查：ネット vs ネットワーク（排除サブネット情况）
        if "ネット" in ja_translation and "ネットワーク" not in ja_translation and "サブネット" not in ja_translation:
            issues.append("'ネット' 应使用 'ネットワーク'")
        
        return issues
    
    def check_punctuation(self, ja_translation):
        """检查标点符号"""
        issues = []
        
        # 检查英文标点符号
        english_punctuations = ['.', ',', ';', ':', '?', '!', '(', ')', '[', ']', '{', '}', '<', '>', "'", '"']
        for punc in english_punctuations:
            if punc in ja_translation:
                issues.append(f"使用了英文标点 '{punc}'，应使用日语标点")
        
        # 检查括号是否匹配
        if ja_translation.count('（') != ja_translation.count('）'):
            issues.append("括号不匹配")
        
        return issues
    
    def check_grammar(self, ja_translation):
        """检查语法问题"""
        issues = []
        
        # 检查多余空格
        if '  ' in ja_translation:
            issues.append("包含连续空格")
        
        # 检查首尾空格
        if ja_translation.strip() != ja_translation:
            issues.append("包含首尾空格")
        
        # 检查句尾标点
        if ja_translation and ja_translation[-1] in ['。', '、', '；', '：', '？', '！']:
            # 日语句尾可以使用这些标点，没问题
            pass
        
        return issues
    
    def print_results(self):
        """打印检查结果"""
        print("\n=== 检查结果 ===")
        print(f"总翻译条目: {self.results['total']}")
        print(f"没有日语字符的翻译: {len(self.results['no_japanese_chars'])}")
        print(f"术语不一致: {len(self.results['inconsistent_terms'])}")
        print(f"标点问题: {len(self.results['punctuation_issues'])}")
        print(f"语法问题: {len(self.results['grammar_issues'])}")
        print(f"有效翻译: {self.results['valid_translations']}")
        print(f"有效率: {self.results['valid_translations'] / self.results['total'] * 100:.2f}%")
        
        # 打印详细问题
        if self.results["no_japanese_chars"]:
            print("\n1. 没有日语字符的翻译:")
            for issue in self.results["no_japanese_chars"]:
                print(f"   - {issue['key']}: {issue['translation']} (英文: {issue['en_translation']})")
        
        if self.results["inconsistent_terms"]:
            print(f"\n2. 术语不一致 ({len(self.results['inconsistent_terms'])} 个):")
            for i, issue in enumerate(self.results["inconsistent_terms"][:10]):
                print(f"   {i + 1}. {issue['key']}: {issue['translation']}")
                for prob in issue['issues']:
                    print(f"      - {prob}")
            if len(self.results["inconsistent_terms"]) > 10:
                print(f"   ... 还有 {len(self.results['inconsistent_terms']) - 10} 个问题")
        
        if self.results["punctuation_issues"]:
            print(f"\n3. 标点问题 ({len(self.results['punctuation_issues'])} 个):")
            for i, issue in enumerate(self.results["punctuation_issues"][:10]):
                print(f"   {i + 1}. {issue['key']}: {issue['translation']}")
                for prob in issue['issues']:
                    print(f"      - {prob}")
            if len(self.results["punctuation_issues"]) > 10:
                print(f"   ... 还有 {len(self.results['punctuation_issues']) - 10} 个问题")
        
        if self.results["grammar_issues"]:
            print(f"\n4. 语法问题 ({len(self.results['grammar_issues'])} 个):")
            for i, issue in enumerate(self.results["grammar_issues"][:10]):
                print(f"   {i+1}. {issue['key']}: {issue['translation']}")
                for prob in issue['issues']:
                    print(f"      - {prob}")
            if len(self.results["grammar_issues"]) > 10:
                print(f"   ... 还有 {len(self.results['grammar_issues']) - 10} 个问题")
    
    def fix_translations(self):
        """修复日语翻译"""
        print("\n=== 开始修复日语翻译 ===")
        
        fix_count = 0
        
        for key, value in self.data.items():
            if isinstance(value, dict) and 'ja' in value:
                original_translation = value["ja"]
                updated_translation = original_translation
                en_translation = value.get('en', '')
                
                # 1. 修复特殊问题：network_address中有多余的ワーク
                if key == "network_address" and "ネットワークワークアドレス" in updated_translation:
                    updated_translation = updated_translation.replace("ネットワークワークアドレス", "ネットワークアドレス")
                
                # 2. 修复术语一致性
                # 特殊处理：Error术语 - 不需要在所有包含Error的英文翻译中都强制出现エラー
                # 只需要确保错误信息中包含エラー
                if "Error" in en_translation and "エラー" not in updated_translation:
                    # 只在错误信息类条目中添加エラー
                    if "failed" in key or "error" in key:
                        updated_translation = updated_translation.replace("失敗しました", "エラーが発生しました")
                
                # 特殊处理：Add术语 - 不需要在所有包含Add的英文翻译中都强制出现追加
                # 只需要确保添加功能条目中包含追加
                if "Add" in en_translation and "追加" not in updated_translation:
                    if "add" in key:
                        updated_translation = updated_translation.replace("サブネット", "サブネットを追加")
                
                # 3. 简化サブネットワーク为サブネット
                updated_translation = updated_translation.replace("サブネットワーク", "サブネット")
                
                # 4. 修复标点符号
                punctuation_map = {
                    '.': '。',
                    ',': '、',
                    ';': '；',
                    ':': '：',
                    '?': '？',
                    '!': '！',
                    '(': '（',
                    ')': '）',
                    '[': '［',
                    ']': '］',
                    '{': '｛',
                    '}': '｝',
                    '<': '＜',
                    '>': '＞',
                    "'": '’',
                    '"': '”'
                }
                for old_punc, new_punc in punctuation_map.items():
                    updated_translation = updated_translation.replace(old_punc, new_punc)
                
                # 5. 修复语法问题
                # 移除多余空格
                while '  ' in updated_translation:
                    updated_translation = updated_translation.replace('  ', ' ')
                # 移除首尾空格
                updated_translation = updated_translation.strip()
                
                # 6. 修复特殊格式问题：确保占位符格式正确
                updated_translation = updated_translation.replace("｛", "{").replace("｝", "}")
                
                # 更新翻译
                if updated_translation != original_translation:
                    value["ja"] = updated_translation
                    fix_count += 1
                    print(f"修复: {key} - 将 '{original_translation}' 替换为 '{updated_translation}'")
        
        # 保存修复后的文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print("\n=== 修复完成 ===")
        print(f"共修复了 {fix_count} 个翻译")
        return fix_count

# 运行检查和修复
checker = JapaneseTranslationChecker('translations.json')
checker.check_translations()
checker.fix_translations()

# 再次检查验证修复结果
print("\n=== 验证修复结果 ===")
checker2 = JapaneseTranslationChecker('translations.json')
results = checker2.check_translations()

# 输出最终报告
print("\n=== 最终报告 ===")
print(f"修复前有效率: {(checker.results['valid_translations'] / checker.results['total']) * 100:.2f}%")
print(f"修复后有效率: {(results['valid_translations'] / results['total']) * 100:.2f}%")
print(f"修复的翻译数量: {checker.results['total'] - results['valid_translations']}")

if results['valid_translations'] == results['total']:
    print("🎉 所有日语翻译都已修复完成！")
else:
    print(f"⚠️  还有 {results['total'] - results['valid_translations']} 个问题需要人工检查。")
