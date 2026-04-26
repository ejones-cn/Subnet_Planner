import os
import sys
import traceback
from PIL import ImageFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from font_config import FontConfig  # noqa: E402
from i18n import _  # noqa: E402


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
                    print(_("font_cleared_pdf"))
        except Exception as e:
            print(_("font_clear_warning", e=str(e)))

        print(_("font_cache_cleared"))

    def __init__(self) -> None:
        self.has_asian_font: bool = False
        self._register_asian_fonts()

    def _register_asian_fonts(self):
        from i18n import get_language
        current_lang = get_language()

        if FontManager._font_path_lang == current_lang and FontManager._font_path_cache:
            print(_("font_using_cached", current_lang=current_lang))
            self.has_asian_font = True
        else:
            print(_("font_will_register", current_lang=current_lang))
            self.has_asian_font = False

    def register_pdf_fonts(self) -> bool:
        from i18n import get_language
        current_lang = get_language()
        print(_("font_pdf_current_lang", current_lang=current_lang))

        if FontManager._font_path_lang == current_lang and FontManager._font_path_cache:
            print(_("font_using_cached_pdf", current_lang=current_lang))
            self.has_asian_font = True
            return True

        print(_("font_need_reregister", old_lang=FontManager._font_path_lang or "None", new_lang=current_lang))

        font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')

        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        font_candidates = FontConfig.get_font_filenames(current_lang)

        font_path = None

        for font_file in font_candidates:
            potential_path = os.path.join(font_dir, font_file)
            if os.path.exists(potential_path):
                font_path = potential_path
                print(_("font_found", font_file=font_file, font_path=font_path))
                break
            else:
                print(_("font_not_found", potential_path=potential_path))

        if font_path:
            try:
                print(_("font_try_register", font_path=font_path))
                print(_("font_current_registered", font_names=str(pdfmetrics.getRegisteredFontNames())))

                font_name = "ChineseFont"
                if font_name in pdfmetrics.getRegisteredFontNames():
                    print(_("font_already_registered", font_name=font_name))
                    try:
                        if hasattr(pdfmetrics, '_fonts') and font_name in pdfmetrics._fonts:  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
                            del pdfmetrics._fonts[font_name]  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
                            print(_("font_old_deleted"))
                    except Exception as del_error:
                        print(_("font_delete_warning", del_error=str(del_error)))

                pdfmetrics.registerFont(TTFont(font_name, font_path))
                self.has_asian_font = True

                FontManager._font_path_cache = font_path
                FontManager._font_path_lang = current_lang

                print(_("font_registered_success", font_file=os.path.basename(font_path), font_name=font_name))
                print(_("font_registered_after", font_names=str(pdfmetrics.getRegisteredFontNames())))

                test_text = FontConfig.get_font_test_text(current_lang)
                try:
                    from reportlab.pdfbase.pdfmetrics import stringWidth
                    width = stringWidth(test_text, font_name, 10)
                    print(_("font_test_passed", test_text=test_text, width=str(width)))
                except Exception as test_error:
                    print(_("font_test_failed", test_error=str(test_error)))

            except Exception as e:
                print(_("font_register_failed", e=str(e)))
                print(_("font_exception_type", exception_type=type(e).__name__))
                traceback.print_exc()

                if "ChineseFont" in pdfmetrics.getRegisteredFontNames():
                    print(_("font_use_previous"))
                    self.has_asian_font = True
                else:
                    print(_("font_use_default"))
                    self.has_asian_font = False
        else:
            print(_("font_no_suitable"))
            self.has_asian_font = False

        print(_("font_using_main", has_asian_font=str(self.has_asian_font)))
        return self.has_asian_font

    def load_system_font(self, font_size=36, bold_offset=4, verbose=False):
        cache_key = (font_size, bold_offset)

        if cache_key in FontManager._font_cache:
            if verbose:
                print(_("font_using_cached_system", font_size=str(font_size), bold_offset=str(bold_offset)))
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
                            print(_("font_loaded_success", font_name=font_name, font_path=font_path))
                        break
                    except (FileNotFoundError, IOError, OSError, ValueError, TypeError) as e:
                        if verbose:
                            print(_("font_load_failed", font_name=font_name, e=str(e)))
                        continue

            if not font_loaded:
                font = ImageFont.load_default()
                bold_font = ImageFont.load_default()
                if verbose:
                    print(_("font_use_default_system"))
        except (IOError, OSError, ValueError, TypeError) as e:
            if verbose:
                print(_("font_load_system_failed", e=str(e)))
            font = ImageFont.load_default()
            bold_font = ImageFont.load_default()

        result = (font, bold_font, font_loaded)
        FontManager._font_cache[cache_key] = result

        return result
