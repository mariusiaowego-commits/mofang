"""
主题系统
支持亮色/暗色主题切换，颜色和样式集中管理
"""

import curses
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ColorPair:
    fg: int
    bg: int
    pair_id: int = 0

    def attrs(self) -> int:
        return curses.color_pair(self.pair_id)


@dataclass
class Style:
    """文本样式"""
    color: Optional[int] = None       # curses.A_BOLD 等，或 None
    pair: Optional[ColorPair] = None
    underline: bool = False


@dataclass
class ThemeColors:
    """主题颜色集"""
    # 基础色
    bg: int = curses.COLOR_BLACK
    fg: int = curses.COLOR_WHITE

    # 组件色
    primary: int = curses.COLOR_CYAN
    secondary: int = curses.COLOR_BLUE
    success: int = curses.COLOR_GREEN
    warning: int = curses.COLOR_YELLOW
    error: int = curses.COLOR_RED
    muted: int = curses.COLOR_WHITE

    # 交互色
    highlight_bg: int = curses.COLOR_CYAN
    highlight_fg: int = curses.COLOR_BLACK
    selected_bg: int = curses.COLOR_BLUE
    selected_fg: int = curses.COLOR_WHITE
    disabled_fg: int = curses.COLOR_WHITE


@dataclass
class Theme:
    """主题定义"""
    name: str
    colors: ThemeColors = field(default_factory=ThemeColors)

    # 边框字符
    border_h: str = "─"
    border_v: str = "│"
    border_tl: str = "┌"
    border_tr: str = "┌"
    border_bl: str = "└"
    border_br: str = "┘"
    border_left_t: str = "├"
    border_right_t: str = "┤"
    border_top_t: str = "┬"
    border_bottom_t: str = "┴"
    border_cross: str = "┼"

    # 圆角（可省略）
    corner_radius: bool = False

    def apply(self):
        """将主题颜色应用到 curses 颜色对"""
        c = self.colors
        curses.start_color()
        curses.use_default_colors()

        # pair_id 约定:
        # 1: bg/fg (背景/默认前景)
        # 2: primary
        # 3: secondary
        # 4: success
        # 5: warning
        # 6: error
        # 7: highlight (选中/焦点)
        # 8: muted

        curses.init_pair(1, c.fg, c.bg)
        curses.init_pair(2, c.primary, c.bg)
        curses.init_pair(3, c.secondary, c.bg)
        curses.init_pair(4, c.success, c.bg)
        curses.init_pair(5, c.warning, c.bg)
        curses.init_pair(6, c.error, c.bg)
        curses.init_pair(7, c.highlight_fg, c.highlight_bg)
        curses.init_pair(8, c.muted, c.bg)

    @property
    def c_default(self) -> int:
        return curses.color_pair(1)

    @property
    def c_primary(self) -> int:
        return curses.color_pair(2)

    @property
    def c_secondary(self) -> int:
        return curses.color_pair(3)

    @property
    def c_success(self) -> int:
        return curses.color_pair(4)

    @property
    def c_warning(self) -> int:
        return curses.color_pair(5)

    @property
    def c_error(self) -> int:
        return curses.color_pair(6)

    @property
    def c_highlight(self) -> int:
        return curses.color_pair(7)

    @property
    def c_muted(self) -> int:
        return curses.color_pair(8)


# 预设主题
DARK_THEME = Theme(
    name="dark",
    colors=ThemeColors(
        bg=curses.COLOR_BLACK,
        fg=curses.COLOR_WHITE,
        primary=curses.COLOR_CYAN,
        secondary=curses.COLOR_BLUE,
        success=curses.COLOR_GREEN,
        warning=curses.COLOR_YELLOW,
        error=curses.COLOR_RED,
        muted=240,  # gray
        highlight_bg=curses.COLOR_CYAN,
        highlight_fg=curses.COLOR_BLACK,
        selected_bg=curses.COLOR_BLUE,
        selected_fg=curses.COLOR_WHITE,
        disabled_fg=240,
    ),
)

LIGHT_THEME = Theme(
    name="light",
    colors=ThemeColors(
        bg=curses.COLOR_WHITE,
        fg=curses.COLOR_BLACK,
        primary=curses.COLOR_BLUE,
        secondary=curses.COLOR_CYAN,
        success=curses.COLOR_GREEN,
        warning=curses.COLOR_YELLOW,
        error=curses.COLOR_RED,
        muted=250,
        highlight_bg=curses.COLOR_BLUE,
        highlight_fg=curses.COLOR_WHITE,
        selected_bg=curses.COLOR_CYAN,
        selected_fg=curses.COLOR_BLACK,
        disabled_fg=250,
    ),
)


class ThemeManager:
    """主题管理器"""

    def __init__(self):
        self._themes: dict[str, Theme] = {
            "dark": DARK_THEME,
            "light": LIGHT_THEME,
        }
        self._current: Theme = DARK_THEME

    @property
    def current(self) -> Theme:
        return self._current

    def apply_theme(self, name: str):
        if name not in self._themes:
            raise ValueError(f"Unknown theme: {name}")
        self._current = self._themes[name]
        self._current.apply()

    def toggle(self):
        """切换主题"""
        if self._current.name == "dark":
            self.apply_theme("light")
        else:
            self.apply_theme("dark")

    def register(self, theme: Theme):
        self._themes[theme.name] = theme


# 全局实例
theme_manager = ThemeManager()
