#!/usr/bin/env python3
"""
颜色主题系统
支持预定义主题、自定义、持久化、动态切换
"""

import curses
import json
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


# 主题配置目录
THEME_DIR = os.path.expanduser("~/.config/mofang/themes")
USER_PREF_FILE = os.path.expanduser("~/.config/mofang/active_theme.json")


@dataclass
class ColorPair:
    """颜色对定义"""
    fg: int      # 前景色 curses.COLOR_*
    bg: int      # 背景色 curses.COLOR_*
    attr: int = 0  # 属性 A_BOLD, A_REVERSE 等


@dataclass
class ThemeColors:
    """主题颜色配置"""
    foreground: Tuple[int, int] = (curses.COLOR_WHITE, curses.COLOR_BLACK)
    background: Tuple[int, int] = (curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight: Tuple[int, int] = (curses.COLOR_YELLOW, curses.COLOR_BLACK)
    header: Tuple[int, int] = (curses.COLOR_CYAN, curses.COLOR_BLACK)
    success: Tuple[int, int] = (curses.COLOR_GREEN, curses.COLOR_BLACK)
    error: Tuple[int, int] = (curses.COLOR_RED, curses.COLOR_BLACK)
    dim: Tuple[int, int] = (curses.COLOR_BLACK, curses.COLOR_WHITE)
    selected: Tuple[int, int] = (curses.COLOR_BLACK, curses.COLOR_CYAN)
    # 可扩展颜色
    accent1: Tuple[int, int] = (curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    accent2: Tuple[int, int] = (curses.COLOR_BLUE, curses.COLOR_BLACK)


@dataclass
class Theme:
    """完整主题定义"""
    name: str
    display_name: str
    description: str = ""
    colors: ThemeColors = field(default_factory=ThemeColors)
    is_dark: bool = True  # 暗色主题标记

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "is_dark": self.is_dark,
            "colors": {
                "foreground": list(self.colors.foreground),
                "background": list(self.colors.background),
                "highlight": list(self.colors.highlight),
                "header": list(self.colors.header),
                "success": list(self.colors.success),
                "error": list(self.colors.error),
                "dim": list(self.colors.dim),
                "selected": list(self.colors.selected),
                "accent1": list(self.colors.accent1),
                "accent2": list(self.colors.accent2),
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        colors_data = data.get("colors", {})
        colors = ThemeColors(
            foreground=tuple(colors_data.get("foreground", [curses.COLOR_WHITE, curses.COLOR_BLACK])),
            background=tuple(colors_data.get("background", [curses.COLOR_BLACK, curses.COLOR_WHITE])),
            highlight=tuple(colors_data.get("highlight", [curses.COLOR_YELLOW, curses.COLOR_BLACK])),
            header=tuple(colors_data.get("header", [curses.COLOR_CYAN, curses.COLOR_BLACK])),
            success=tuple(colors_data.get("success", [curses.COLOR_GREEN, curses.COLOR_BLACK])),
            error=tuple(colors_data.get("error", [curses.COLOR_RED, curses.COLOR_BLACK])),
            dim=tuple(colors_data.get("dim", [curses.COLOR_BLACK, curses.COLOR_WHITE])),
            selected=tuple(colors_data.get("selected", [curses.COLOR_BLACK, curses.COLOR_CYAN])),
            accent1=tuple(colors_data.get("accent1", [curses.COLOR_MAGENTA, curses.COLOR_BLACK])),
            accent2=tuple(colors_data.get("accent2", [curses.COLOR_BLUE, curses.COLOR_BLACK])),
        )
        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            description=data.get("description", ""),
            colors=colors,
            is_dark=data.get("is_dark", True),
        )


# 预定义主题
BUILTIN_THEMES: Dict[str, Theme] = {}


def _init_builtin_themes():
    global BUILTIN_THEMES
    BUILTIN_THEMES = {
        "dark": Theme(
            name="dark",
            display_name="暗色主题",
            description="经典暗色，适合夜间使用",
            colors=ThemeColors(
                foreground=(curses.COLOR_WHITE, curses.COLOR_BLACK),
                background=(curses.COLOR_BLACK, curses.COLOR_WHITE),
                highlight=(curses.COLOR_YELLOW, curses.COLOR_BLACK),
                header=(curses.COLOR_CYAN, curses.COLOR_BLACK),
                success=(curses.COLOR_GREEN, curses.COLOR_BLACK),
                error=(curses.COLOR_RED, curses.COLOR_BLACK),
                dim=(curses.COLOR_BLACK, curses.COLOR_WHITE),
                selected=(curses.COLOR_BLACK, curses.COLOR_CYAN),
            ),
            is_dark=True,
        ),
        "light": Theme(
            name="light",
            display_name="浅色主题",
            description="明亮配色，适合白天使用",
            colors=ThemeColors(
                foreground=(curses.COLOR_BLACK, curses.COLOR_WHITE),
                background=(curses.COLOR_WHITE, curses.COLOR_BLACK),
                highlight=(curses.COLOR_BLUE, curses.COLOR_WHITE),
                header=(curses.COLOR_BLUE, curses.COLOR_WHITE),
                success=(curses.COLOR_GREEN, curses.COLOR_WHITE),
                error=(curses.COLOR_RED, curses.COLOR_WHITE),
                dim=(curses.COLOR_WHITE, curses.COLOR_BLACK),
                selected=(curses.COLOR_WHITE, curses.COLOR_BLUE),
            ),
            is_dark=False,
        ),
        "high_contrast": Theme(
            name="high_contrast",
            display_name="高对比度",
            description="强对比度，适合视力不佳用户",
            colors=ThemeColors(
                foreground=(curses.COLOR_WHITE, curses.COLOR_BLACK),
                background=(curses.COLOR_BLACK, curses.COLOR_WHITE),
                highlight=(curses.COLOR_WHITE, curses.COLOR_BLACK),
                header=(curses.COLOR_CYAN, curses.COLOR_BLACK),
                success=(curses.COLOR_GREEN, curses.COLOR_BLACK),
                error=(curses.COLOR_RED, curses.COLOR_YELLOW),  # 黄底红字
                dim=(curses.COLOR_YELLOW, curses.COLOR_BLACK),
                selected=(curses.COLOR_BLACK, curses.COLOR_YELLOW),
            ),
            is_dark=True,
        ),
        "solarized_dark": Theme(
            name="solarized_dark",
            display_name="Solarized 暗",
            description="Ethans Solarized 暗色方案",
            colors=ThemeColors(
                foreground=(curses.COLOR_BLUE, curses.COLOR_BLACK),        # base01
                background=(curses.COLOR_BLACK, curses.COLOR_BLUE),        # base03
                highlight=(curses.COLOR_YELLOW, curses.COLOR_BLACK),        # yellow
                header=(curses.COLOR_CYAN, curses.COLOR_BLACK),             # cyan
                success=(curses.COLOR_GREEN, curses.COLOR_BLACK),           # green
                error=(curses.COLOR_RED, curses.COLOR_BLACK),               # red
                dim=(curses.COLOR_BLACK, curses.COLOR_BLUE),                # base1
                selected=(curses.COLOR_BLACK, curses.COLOR_CYAN),          # base01
            ),
            is_dark=True,
        ),
    }


_init_builtin_themes()


class ThemeManager:
    """
    主题管理器
    
    职责:
    - 加载/保存主题配置
    - 管理颜色对 (color pairs)
    - 主题切换与持久化
    - 动态主题加载
    """

    # 颜色对 ID 分配
    CP_FOREGROUND = 1
    CP_BACKGROUND = 2
    CP_HIGHLIGHT = 3
    CP_HEADER = 4
    CP_SUCCESS = 5
    CP_ERROR = 6
    CP_DIM = 7
    CP_SELECTED = 8
    CP_ACCENT1 = 9
    CP_ACCENT2 = 10
    CP_COUNT = 10

    def __init__(self):
        self.themes: Dict[str, Theme] = dict(BUILTIN_THEMES)
        self.active_theme: Theme = BUILTIN_THEMES["dark"]
        self.custom_theme_dir = THEME_DIR
        
        # 加载用户偏好
        self._load_user_preference()
        
        # 加载自定义主题
        self._load_custom_themes()

    def _load_user_preference(self):
        """从文件加载用户主题偏好"""
        try:
            if os.path.exists(USER_PREF_FILE):
                with open(USER_PREF_FILE, "r") as f:
                    data = json.load(f)
                    theme_name = data.get("active_theme", "dark")
                    if theme_name in self.themes:
                        self.active_theme = self.themes[theme_name]
        except Exception:
            pass

    def _save_user_preference(self):
        """保存用户主题偏好到文件"""
        try:
            os.makedirs(os.path.dirname(USER_PREF_FILE), exist_ok=True)
            with open(USER_PREF_FILE, "w") as f:
                json.dump({"active_theme": self.active_theme.name}, f)
        except Exception:
            pass

    def _load_custom_themes(self):
        """从配置目录加载自定义主题"""
        if not os.path.exists(self.custom_theme_dir):
            return
        
        try:
            for filename in os.listdir(self.custom_theme_dir):
                if filename.endswith((".json", ".yaml")):
                    path = os.path.join(self.custom_theme_dir, filename)
                    theme = self._load_theme_file(path)
                    if theme:
                        self.themes[theme.name] = theme
        except Exception:
            pass

    def _load_theme_file(self, path: str) -> Optional[Theme]:
        """从文件加载主题"""
        try:
            with open(path, "r") as f:
                if path.endswith(".json"):
                    data = json.load(f)
                else:
                    # 简单 YAML 支持（需要 pyyaml）
                    import yaml
                    data = yaml.safe_load(f)
            
            if "name" in data:
                return Theme.from_dict(data)
        except Exception:
            pass
        return None

    def init_colors(self):
        """初始化 curses 颜色系统"""
        if not curses.has_colors():
            return False
            
        curses.start_color()
        curses.use_default_colors()
        
        # 支持 256 色
        if curses.can_change_color():
            pass  # 可修改颜色时可以做更多事情
        
        self._apply_theme(self.active_theme)
        return True

    def _apply_theme(self, theme: Theme):
        """将主题颜色应用到 curses 颜色对"""
        color_map = [
            (self.CP_FOREGROUND, theme.colors.foreground),
            (self.CP_BACKGROUND, theme.colors.background),
            (self.CP_HIGHLIGHT, theme.colors.highlight),
            (self.CP_HEADER, theme.colors.header),
            (self.CP_SUCCESS, theme.colors.success),
            (self.CP_ERROR, theme.colors.error),
            (self.CP_DIM, theme.colors.dim),
            (self.CP_SELECTED, theme.colors.selected),
            (self.CP_ACCENT1, theme.colors.accent1),
            (self.CP_ACCENT2, theme.colors.accent2),
        ]
        
        for pair_id, (fg, bg) in color_map:
            curses.init_pair(pair_id, fg, bg)

    def set_theme(self, theme_name: str) -> bool:
        """
        切换到指定主题
        返回是否切换成功
        """
        if theme_name not in self.themes:
            return False
        
        self.active_theme = self.themes[theme_name]
        self._apply_theme(self.active_theme)
        self._save_user_preference()
        return True

    def get_color_pair(self, name: str) -> int:
        """获取颜色对 ID"""
        mapping = {
            "foreground": self.CP_FOREGROUND,
            "background": self.CP_BACKGROUND,
            "highlight": self.CP_HIGHLIGHT,
            "header": self.CP_HEADER,
            "success": self.CP_SUCCESS,
            "error": self.CP_ERROR,
            "dim": self.CP_DIM,
            "selected": self.CP_SELECTED,
            "accent1": self.CP_ACCENT1,
            "accent2": self.CP_ACCENT2,
        }
        pair_id = mapping.get(name, self.CP_FOREGROUND)
        return curses.color_pair(pair_id)

    def get_theme(self, name: str) -> Optional[Theme]:
        """获取主题对象"""
        return self.themes.get(name)

    def list_themes(self) -> Dict[str, Theme]:
        """列出所有可用主题"""
        return self.themes

    def add_custom_theme(self, theme: Theme) -> bool:
        """
        添加自定义主题
        保存到用户配置目录
        """
        if theme.name in self.themes:
            return False
        
        self.themes[theme.name] = theme
        
        # 保存到文件
        try:
            os.makedirs(self.custom_theme_dir, exist_ok=True)
            path = os.path.join(self.custom_theme_dir, f"{theme.name}.json")
            with open(path, "w") as f:
                json.dump(theme.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    def export_theme(self, theme_name: str, path: str) -> bool:
        """导出主题到文件"""
        theme = self.themes.get(theme_name)
        if not theme:
            return False
        
        try:
            with open(path, "w") as f:
                json.dump(theme.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    def reload_themes(self):
        """重新加载所有主题（用于热重载）"""
        self.themes = dict(BUILTIN_THEMES)
        self._load_custom_themes()
        
        # 确保当前主题仍然存在
        if self.active_theme.name not in self.themes:
            self.active_theme = BUILTIN_THEMES["dark"]
            self._apply_theme(self.active_theme)
