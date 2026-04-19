import os
import sys
import traceback
from PIL import ImageFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from font_config import FontConfig  # noqa: E402


class FontManager:
    _font_cache: dict[tuple[int, int], tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont | None, ImageFont.FreeTypeFont | ImageFont.ImageFont | None, bool]] = {}
    _font_path_cache: str | None = None
    _font_path_lang: str | None = None

    @classmethod
    def clear_font_cache(cls) -> None:
        cls._font_cache.clear()
        cls._font_path_cache = None
        cls._font_path_lang = None

        try:
            from reportlab.pdfbase import pdfmetrics
            if "ChineseFont" in pdfmetrics.getRegisteredFontNames():
                if hasattr(pdfmetrics, '_fonts') and "ChineseFont" in pdfmetrics._fonts:  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
                    del pdfmetrics._fonts["ChineseFont"]  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
                    print("🧹 已清除 ReportLab PDF 字体注册")
        except Exception as e:
            print(f"⚠️ 清除 PDF 字体注册时出现警告: {e}")

        print("🧹 已清除字体缓存")

    def __init__(self) -> None:
        self.has_asian_font: bool = False
        self._register_asian_fonts()

    def _register_asian_fonts(self):
        from i18n import get_language
        current_lang = get_language()

        if FontManager._font_path_lang == current_lang and FontManager._font_path_cache:
            print(f"🔍 [init] 使用已注册的字体缓存 (语言: {current_lang})")
            self.has_asian_font = True
        else:
            print(f"[init] 字体将在导出PDF时注册 (语言: {current_lang})")
            self.has_asian_font = False

    def register_pdf_fonts(self) -> bool:
        from i18n import get_language
        current_lang = get_language()
        print(f"🔍 导出PDF时当前语言: {current_lang}")

        if FontManager._font_path_lang == current_lang and FontManager._font_path_cache:
            print(f"🔍 使用已注册的PDF字体缓存 (语言: {current_lang})")
            self.has_asian_font = True
            return True

        print(f"🔍 语言已切换或无缓存，需要重新注册字体 (旧语言: {FontManager._font_path_lang}, 新语言: {current_lang})")

        font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')

        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        font_candidates = FontConfig.get_font_filenames(current_lang)

        font_path = None

        for font_file in font_candidates:
            potential_path = os.path.join(font_dir, font_file)
            if os.path.exists(potential_path):
                font_path = potential_path
                print(f"🔍 找到可用字体: {font_file} 在 {font_path}")
                break
            else:
                print(f"⚠️ 字体文件不存在: {potential_path}")

        if font_path:
            try:
                print(f"🔍 尝试注册字体: {font_path}")
                print(f"🔍 当前已注册字体: {pdfmetrics.getRegisteredFontNames()}")

                font_name = "ChineseFont"
                if font_name in pdfmetrics.getRegisteredFontNames():
                    print(f"🔍 字体 '{font_name}' 已注册,先删除再重新注册")
                    try:
                        if hasattr(pdfmetrics, '_fonts') and font_name in pdfmetrics._fonts:  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
                            del pdfmetrics._fonts[font_name]  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
                            print("🔍 已删除旧的字体注册")
                    except Exception as del_error:
                        print(f"⚠️ 删除旧字体时出现警告: {del_error}")

                pdfmetrics.registerFont(TTFont(font_name, font_path))
                self.has_asian_font = True

                FontManager._font_path_cache = font_path
                FontManager._font_path_lang = current_lang

                print(f"✅ 成功注册字体: {os.path.basename(font_path)} 作为 {font_name}")
                print(f"🔍 注册后已注册字体: {pdfmetrics.getRegisteredFontNames()}")

                test_text = FontConfig.get_font_test_text(current_lang)
                try:
                    from reportlab.pdfbase.pdfmetrics import stringWidth
                    width = stringWidth(test_text, font_name, 10)
                    print(f"✅ 字体测试通过: '{test_text}' 宽度={width}")
                except Exception as test_error:
                    print(f"⚠️ 字体测试失败: {test_error}")

            except Exception as e:
                print(f"❌ 注册字体失败: {e}")
                print(f"❌ 异常类型: {type(e).__name__}")
                traceback.print_exc()

                if "ChineseFont" in pdfmetrics.getRegisteredFontNames():
                    print("🔍 使用之前注册的 ChineseFont 字体(可能不支持当前语言)")
                    self.has_asian_font = True
                else:
                    print("🔍 无可用字体,将使用默认字体(Helvetica)")
                    self.has_asian_font = False
        else:
            print("🔍 未找到合适字体，将使用默认字体")
            self.has_asian_font = False

        print(f"🔍 使用的主要字体: ChineseFont, has_asian_font={self.has_asian_font}")
        return self.has_asian_font

    def load_system_font(self, font_size=36, bold_offset=4, verbose=False):
        cache_key = (font_size, bold_offset)

        if cache_key in FontManager._font_cache:
            if verbose:
                print(f"使用缓存的字体 (size={font_size}, bold_offset={bold_offset})")
            return FontManager._font_cache[cache_key]

        font = None
        bold_font = None
        font_loaded = False
        try:
            from i18n import get_language
            current_lang = get_language()

            system_font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')

            font_candidates_tuples = FontConfig.get_font_candidates(current_lang)
            font_candidates = [(font_file, font_size, font_name) for font_file, font_name in font_candidates_tuples]

            for font_file, size, font_name in font_candidates:
                font_path = os.path.join(system_font_dir, font_file)
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        bold_font = ImageFont.truetype(font_path, size + bold_offset)
                        font_loaded = True
                        if verbose:
                            print(f"成功加载{font_name}字体: {font_path}")
                        break
                    except (FileNotFoundError, IOError, OSError, ValueError, TypeError) as e:
                        if verbose:
                            print(f"尝试加载{font_name}失败: {e}")
                        continue

            if not font_loaded:
                font = ImageFont.load_default()
                bold_font = ImageFont.load_default()
                if verbose:
                    print("使用默认字体")
        except (IOError, OSError, ValueError, TypeError) as e:
            if verbose:
                print(f"加载系统字体失败: {e}")
            font = ImageFont.load_default()
            bold_font = ImageFont.load_default()

        result = (font, bold_font, font_loaded)
        FontManager._font_cache[cache_key] = result

        return result
