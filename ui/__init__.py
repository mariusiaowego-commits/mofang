"""
通用 UI 组件库 (curses)
支持键盘导航、主题切换、易于组合使用
"""

from ui.theme import Theme, theme_manager
from ui.components import (
    Button,
    Card,
    List,
    Input,
    Dialog,
    ProgressBar,
    Tabs,
    Component,
)
from ui.keyboard import KeyboardNavigator, FocusManager

__all__ = [
    "Theme",
    "theme_manager",
    "Button",
    "Card",
    "List",
    "Input",
    "Dialog",
    "ProgressBar",
    "Tabs",
    "Component",
    "KeyboardNavigator",
    "FocusManager",
]
