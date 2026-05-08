"""
通用 curses UI 组件库
七个组件: Button, Card, List, Input, Dialog, ProgressBar, Tabs
全部支持键盘导航、焦点管理、主题切换
"""

import curses
from abc import ABC, abstractmethod
from typing import Callable, Optional, Any

from ui.theme import theme_manager


# ─── 基础组件 ───────────────────────────────────────────────

class Component(ABC):
    """所有组件的基类"""

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.focused = False
        self.visible = True
        self.enabled = True

    def contains(self, x: int, y: int) -> bool:
        """判断坐标是否在组件范围内"""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)

    @abstractmethod
    def render(self, win: curses.window):
        """渲染组件到窗口"""
        pass

    @abstractmethod
    def handle_key(self, key: int) -> Optional[Any]:
        """处理按键，返回事件结果或 None"""
        pass


# ─── Button ──────────────────────────────────────────────────

class Button(Component):
    """按钮组件，支持高亮/禁用状态"""

    def __init__(
        self,
        label: str,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        on_click: Optional[Callable[[], Any]] = None,
        enabled: bool = True,
        **kwargs,
    ):
        super().__init__(x, y, width or len(label) + 4, 1)
        self.label = label
        self.on_click = on_click
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    def render(self, win: curses.window):
        theme = theme_manager.current
        if not self.visible:
            return

        # 选择颜色
        if not self._enabled:
            color = theme.c_muted
        elif self.focused:
            color = theme.c_highlight
        else:
            color = theme.c_primary

        label = f"[{self.label}]"
        try:
            win.addstr(self.y, self.x, label, color | curses.A_BOLD)
        except curses.error:
            pass

    def handle_key(self, key: int) -> Optional[Any]:
        if not self._enabled:
            return None
        if key in (curses.KEY_ENTER, 10, 13, ord(' ')):
            return self.on_click() if self.on_click else True
        return None


# ─── Card ────────────────────────────────────────────────────

class Card(Component):
    """卡片组件，带标题、边框、内容区域"""

    def __init__(
        self,
        title: str = "",
        x: int = 0,
        y: int = 0,
        width: int = 40,
        height: int = 10,
        **kwargs,
    ):
        super().__init__(x, y, width, height)
        self.title = title
        self.content: Optional[Component] = None

    def render(self, win: curses.window):
        theme = theme_manager.current
        t = theme

        # 顶部边框 + 标题
        try:
            # 角落
            win.addstr(self.y, self.x, t.border_tl, t.c_default)
            win.addstr(self.y, self.x + self.width - 1, t.border_tr, t.c_default)
            win.addstr(self.y + self.height - 1, self.x, t.border_bl, t.c_default)
            win.addstr(self.y + self.height - 1, self.x + self.width - 1, t.border_br, t.c_default)

            # 水平边
            for col in range(1, self.width - 1):
                win.addstr(self.y, self.x + col, t.border_h, t.c_default)
                win.addstr(self.y + self.height - 1, self.x + col, t.border_h, t.c_default)

            # 垂直边
            for row in range(1, self.height - 1):
                win.addstr(self.y + row, self.x, t.border_v, t.c_default)
                win.addstr(self.y + row, self.x + self.width - 1, t.border_v, t.c_default)

            # 标题
            if self.title:
                title_line = f" {self.title} "
                title_x = self.x + 1
                win.addstr(self.y, title_x, title_line, t.c_primary | curses.A_BOLD)
        except curses.error:
            pass

        # 渲染内容
        if self.content and self.content.visible:
            self.content.render(win)

    def handle_key(self, key: int) -> Optional[Any]:
        if self.content and self.content.visible and self.content.enabled:
            return self.content.handle_key(key)
        return None


# ─── List ────────────────────────────────────────────────────

class List(Component):
    """列表组件，支持选择、滚动、多列"""

    def __init__(
        self,
        items: list[str],
        x: int = 0,
        y: int = 0,
        width: int = 30,
        height: int = 10,
        multi_column: bool = False,
        columns: int = 1,
        on_select: Optional[Callable[[int], Any]] = None,
        **kwargs,
    ):
        super().__init__(x, y, width, height)
        self.items = items
        self.selected = 0
        self.scroll = 0
        self.multi_column = multi_column
        self.columns = max(1, columns)
        self.on_select = on_select
        self._focusable = True

    @property
    def page_size(self) -> int:
        return self.height - 2

    @property
    def item_height(self) -> int:
        return self.height - 2

    def render(self, win: curses.window):
        theme = theme_manager.current
        if not self.visible:
            return

        # 边框
        try:
            win.addstr(self.y, self.x, "┌" + "─" * (self.width - 2) + "┐", theme.c_default)
            for row in range(1, self.height - 1):
                win.addstr(self.y + row, self.x, "│", theme.c_default)
                win.addstr(self.y + row, self.x + self.width - 1, "│", theme.c_default)
            win.addstr(self.y + self.height - 1, self.x, "└" + "─" * (self.width - 2) + "┘", theme.c_default)
        except curses.error:
            pass

        # 计算可见项
        visible_items = self.items[self.scroll: self.scroll + self.page_size]
        col_width = max(1, (self.width - 4) // self.columns)

        for idx, item in enumerate(visible_items):
            row = idx // self.columns
            col = idx % self.columns
            item_y = self.y + 1 + row
            item_x = self.x + 2 + col * col_width

            if item_y >= self.y + self.height - 1:
                break

            is_selected = (self.scroll + idx) == self.selected
            marker = "▶" if is_selected else " "
            color = theme.c_highlight if (is_selected and self.focused) else (
                theme.c_muted if is_selected else theme.c_default)

            try:
                win.addstr(item_y, item_x, marker, color)
                # 截断过长的项
                display_item = item[:col_width - 2]
                win.addstr(item_y, item_x + 1, display_item, color)
            except curses.error:
                pass

        # 滚动条
        if len(self.items) > self.page_size:
            bar_y = self.y + 1 + int(self.scroll / max(1, len(self.items) - self.page_size) * (self.height - 2))
            bar_y = min(bar_y, self.y + self.height - 2)
            try:
                win.addstr(bar_y, self.x + self.width - 1, "▓", theme.c_primary)
            except curses.error:
                pass

    def handle_key(self, key: int) -> Optional[Any]:
        if not self.enabled or not self.visible:
            return None

        old_selected = self.selected
        if key == curses.KEY_UP or key == ord('k'):
            self.selected = max(0, self.selected - 1)
        elif key == curses.KEY_DOWN or key == ord('j'):
            self.selected = min(len(self.items) - 1, self.selected + 1)
        elif key == curses.KEY_PPAGE:
            self.selected = max(0, self.selected - self.page_size)
        elif key == curses.KEY_NPAGE:
            self.selected = min(len(self.items) - 1, self.selected + self.page_size)
        elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
            if self.on_select:
                return self.on_select(self.selected)
            return self.selected
        else:
            return None

        # 更新滚动
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + self.page_size:
            self.scroll = self.selected - self.page_size + 1

        return True if self.selected != old_selected else None


# ─── Input ───────────────────────────────────────────────────

class Input(Component):
    """输入框组件，支持文本/密码输入"""

    def __init__(
        self,
        label: str = "",
        x: int = 0,
        y: int = 0,
        width: int = 20,
        password: bool = False,
        on_submit: Optional[Callable[[str], Any]] = None,
        **kwargs,
    ):
        super().__init__(x, y, width, 1)
        self.label = label
        self.value = ""
        self.password = password
        self.on_submit = on_submit
        self.cursor = 0
        self.scroll_offset = 0

    @property
    def display_width(self) -> int:
        return self.width - 2 - len(self.label)

    def render(self, win: curses.window):
        theme = theme_manager.current
        if not self.visible:
            return

        # 标签
        label_str = f"{self.label}: " if self.label else ""
        try:
            win.addstr(self.y, self.x, label_str, theme.c_default)

            # 输入框区域
            box_x = self.x + len(label_str)
            win.addstr(self.y, box_x, "[", theme.c_default)

            # 显示内容（处理密码隐藏和滚动）
            if self.password:
                display = "*" * len(self.value)
            else:
                display = self.value

            visible = display[self.scroll_offset: self.scroll_offset + self.display_width]
            win.addstr(self.y, box_x + 1, visible.ljust(self.display_width), theme.c_default)

            win.addstr(self.y, box_x + self.display_width + 1, "]", theme.c_default)

            # 光标
            if self.focused:
                cursor_pos = self.cursor - self.scroll_offset
                if 0 <= cursor_pos < self.display_width:
                    curses.curs_set(1)
                    win.move(self.y, box_x + 1 + cursor_pos)
                else:
                    curses.curs_set(0)
        except curses.error:
            pass

    def handle_key(self, key: int) -> Optional[Any]:
        if not self.enabled or not self.visible:
            return None

        if key == curses.KEY_BACKSPACE or key == 127:
            if self.cursor > 0:
                self.value = self.value[:self.cursor - 1] + self.value[self.cursor:]
                self.cursor -= 1
                if self.scroll_offset > 0 and self.cursor < self.scroll_offset:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
            return True

        elif key in (curses.KEY_ENTER, 10, 13):
            if self.on_submit:
                return self.on_submit(self.value)
            return self.value

        elif key == curses.KEY_LEFT:
            self.cursor = max(0, self.cursor - 1)
            if self.cursor < self.scroll_offset:
                self.scroll_offset = self.cursor
            return True

        elif key == curses.KEY_RIGHT:
            self.cursor = min(len(self.value), self.cursor + 1)
            if self.cursor > self.scroll_offset + self.display_width:
                self.scroll_offset = self.cursor - self.display_width
            return True

        elif key == curses.KEY_HOME:
            self.cursor = 0
            self.scroll_offset = 0
            return True

        elif key == curses.KEY_END:
            self.cursor = len(self.value)
            self.scroll_offset = max(0, self.cursor - self.display_width)
            return True

        elif 32 <= key <= 126:
            ch = chr(key)
            self.value = self.value[:self.cursor] + ch + self.value[self.cursor:]
            self.cursor += 1
            if self.cursor > self.scroll_offset + self.display_width:
                self.scroll_offset += 1
            return True

        return None


# ─── Dialog ──────────────────────────────────────────────────

class Dialog(Component):
    """对话框组件，支持模态/非模态"""

    def __init__(
        self,
        title: str = "Dialog",
        message: str = "",
        x: int = 0,
        y: int = 0,
        width: int = 50,
        height: int = 10,
        modal: bool = True,
        buttons: Optional[list[tuple[str, Callable]]] = None,
        **kwargs,
    ):
        super().__init__(x, y, width, height)
        self.title = title
        self.message = message
        self.modal = modal
        self.buttons: list[Button] = []
        self.result: Any = None

        if buttons:
            self._build_buttons(buttons)

    def _build_buttons(self, buttons: list[tuple[str, Callable]]):
        total_w = sum(len(label) + 4 for label, _ in buttons) + len(buttons) - 1
        start_x = self.x + (self.width - total_w) // 2
        cur_x = start_x

        for label, callback in buttons:
            btn = Button(
                label=label,
                x=cur_x,
                y=self.y + self.height - 3,
                on_click=lambda c=callback: self._click(c),
            )
            self.buttons.append(btn)
            cur_x += len(label) + 4 + 1

    def _click(self, callback: Callable):
        self.result = callback() if callback else None

    def render(self, win: curses.window):
        theme = theme_manager.current

        # 半透明遮罩（模态）
        if self.modal:
            for row in range(self.y, self.y + self.height):
                for col in range(self.width):
                    try:
                        win.addstr(row, col, " ", theme.c_default)
                    except curses.error:
                        pass

        # 背景
        try:
            win.addstr(self.y, self.x, "╔" + "═" * (self.width - 2) + "╗", theme.c_secondary)
            for row in range(1, self.height - 1):
                win.addstr(self.y + row, self.x, "║", theme.c_secondary)
                win.addstr(self.y + row, self.x + self.width - 1, "║", theme.c_secondary)
            win.addstr(self.y + self.height - 1, self.x, "╚" + "═" * (self.width - 2) + "╝", theme.c_secondary)
        except curses.error:
            pass

        # 标题
        try:
            title_str = f" {self.title} "
            win.addstr(self.y, self.x + 1, title_str, theme.c_primary | curses.A_BOLD)
        except curses.error:
            pass

        # 消息（自动换行）
        if self.message:
            lines = self._wrap_text(self.message, self.width - 4)
            for i, line in enumerate(lines):
                if self.y + 2 + i < self.y + self.height - 3:
                    try:
                        win.addstr(self.y + 2 + i, self.x + 2, line, theme.c_default)
                    except curses.error:
                        pass

        # 按钮
        for btn in self.buttons:
            btn.render(win)

    def _wrap_text(self, text: str, width: int) -> list[str]:
        words = text.split()
        lines, current = [], ""
        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= width:
                current += " " + word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def handle_key(self, key: int) -> Optional[Any]:
        if self.modal:
            for btn in self.buttons:
                if btn.handle_key(key):
                    return btn.result
        return None


# ─── ProgressBar ─────────────────────────────────────────────

class ProgressBar(Component):
    """进度条组件"""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 30,
        value: float = 0.0,
        label: str = "",
        show_percent: bool = True,
        **kwargs,
    ):
        super().__init__(x, y, width, 1)
        self.value = max(0.0, min(1.0, value))
        self.label = label
        self.show_percent = show_percent

    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))

    def render(self, win: curses.window):
        theme = theme_manager.current
        if not self.visible:
            return

        bar_width = self.width - 2
        if self.label:
            bar_width -= len(self.label) + 1

        filled = int(self.value * bar_width)
        empty = bar_width - filled

        # 构建进度条字符串
        bar = "[" + "█" * filled + "░" * empty + "]"

        if self.label:
            bar += f" {self.label}"

        if self.show_percent:
            pct = f" {int(self.value * 100)}%"
            bar += pct

        try:
            color = theme.c_primary if self.focused else theme.c_default
            win.addstr(self.y, self.x, bar, color)
        except curses.error:
            pass

    def handle_key(self, key: int) -> Optional[Any]:
        # 进度条本身不处理按键
        return None


# ─── Tabs ────────────────────────────────────────────────────

class Tabs(Component):
    """标签页组件"""

    def __init__(
        self,
        tabs: list[str],
        x: int = 0,
        y: int = 0,
        width: int = 60,
        height: int = 20,
        on_change: Optional[Callable[[int], Any]] = None,
        **kwargs,
    ):
        super().__init__(x, y, width, height)
        self.tabs = tabs
        self.active = 0
        self.on_change = on_change
        self._content: Optional[Component] = None

    @property
    def tab_height(self) -> int:
        return 3  # 标签栏高度

    def set_content(self, index: int, content: Component):
        """设置标签页内容"""
        self._content = content

    def render(self, win: curses.window):
        theme = theme_manager.current
        if not self.visible:
            return

        # 标签行
        tab_width = self.width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_x = self.x + i * tab_width
            is_active = (i == self.active)

            # 标签边框
            try:
                if is_active:
                    win.addstr(self.y, tab_x, "┌", theme.c_primary)
                    win.addstr(self.y, tab_x + tab_width - 1, "┐", theme.c_primary)
                    for col in range(1, tab_width - 1):
                        win.addstr(self.y, tab_x + col, "─", theme.c_primary)
                    # 标签名
                    label = f" {tab} "
                    win.addstr(self.y, tab_x + (tab_width - len(label)) // 2,
                               label, theme.c_highlight | curses.A_BOLD)
                else:
                    win.addstr(self.y, tab_x, "├", theme.c_default)
                    win.addstr(self.y, tab_x + tab_width - 1, "┤", theme.c_default)
                    for col in range(1, tab_width - 1):
                        win.addstr(self.y, tab_x + col, "─", theme.c_default)
                    label = f" {tab} "
                    win.addstr(self.y, tab_x + (tab_width - len(label)) // 2,
                               label, theme.c_muted)
            except curses.error:
                pass

        # 底部线
        try:
            win.addstr(self.y + 1, self.x, "├", theme.c_default)
            win.addstr(self.y + 1, self.x + self.width - 1, "┤", theme.c_default)
            for col in range(1, self.width - 1):
                win.addstr(self.y + 1, self.x + col, "─", theme.c_default)
        except curses.error:
            pass

        # 内容区域
        if self._content:
            self._content.x = self.x
            self._content.y = self.y + 2
            self._content.width = self.width
            self._content.height = self.height - 2
            self._content.render(win)

    def handle_key(self, key: int) -> Optional[Any]:
        if not self.enabled or not self.visible:
            return None

        old = self.active
        if key in (curses.KEY_LEFT, ord('h')):
            self.active = max(0, self.active - 1)
        elif key in (curses.KEY_RIGHT, ord('l')):
            self.active = min(len(self.tabs) - 1, self.active + 1)
        else:
            # 转发给内容
            if self._content:
                return self._content.handle_key(key)
            return None

        if self.active != old:
            if self.on_change:
                return self.on_change(self.active)
            return True

        return None
