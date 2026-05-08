"""
键盘导航与焦点管理
支持 Tab/Shift+Tab 焦点切换、方向键导航、焦点链
"""

import curses
from typing import Optional


class FocusManager:
    """管理焦点组件"""

    def __init__(self):
        self._components: list = []
        self._focused_index: int = -1

    def register(self, *components):
        """注册焦点组件"""
        for comp in components:
            if comp not in self._components:
                self._components.append(comp)
        return self

    def unregister(self, component):
        """注销组件"""
        if component in self._components:
            idx = self._components.index(component)
            self._components.remove(component)
            if idx <= self._focused_index:
                self._focused_index = max(0, self._focused_index - 1)
            self._update_focus()

    def focus_next(self):
        """聚焦下一个组件（Tab）"""
        if not self._components:
            return
        self._focused_index = (self._focused_index + 1) % len(self._components)
        self._update_focus()

    def focus_prev(self):
        """聚焦上一个组件（Shift+Tab）"""
        if not self._components:
            return
        self._focused_index = (self._focused_index - 1) % len(self._components)
        self._update_focus()

    def focus_at(self, index: int):
        """聚焦指定索引的组件"""
        if 0 <= index < len(self._components):
            self._focused_index = index
            self._update_focus()

    def get_focused(self):
        """获取当前焦点组件"""
        if 0 <= self._focused_index < len(self._components):
            return self._components[self._focused_index]
        return None

    def _update_focus(self):
        """更新焦点状态"""
        for i, comp in enumerate(self._components):
            comp.focused = (i == self._focused_index)

    def clear(self):
        """清除所有焦点"""
        self._components.clear()
        self._focused_index = -1

    def auto_focus_first(self):
        """自动聚焦第一个组件"""
        if self._components:
            self._focused_index = 0
            self._update_focus()


class KeyboardNavigator:
    """
    键盘导航器
    将按键事件路由到焦点组件或其他全局处理器
    """

    def __init__(self, focus_manager: Optional[FocusManager] = None):
        self.focus_manager = focus_manager or FocusManager()
        self._global_handlers: dict[int, callable] = {}
        self._tab_enabled = True
        self._arrow_enabled = True

    def on_key(self, key: int):
        """处理按键，返回是否已处理"""
        # Tab / Shift+Tab 焦点切换
        if self._tab_enabled and key == curses.KEY_BTAB:
            self.focus_manager.focus_prev()
            return True

        if self._tab_enabled and key == ord('\t'):
            self.focus_manager.focus_next()
            return True

        # 全局按键处理
        if key in self._global_handlers:
            self._global_handlers[key]()
            return True

        # 转发给焦点组件
        focused = self.focus_manager.get_focused()
        if focused and focused.enabled and focused.visible:
            result = focused.handle_key(key)
            return result is not None

        return False

    def bind_global(self, key: int, handler: callable):
        """绑定全局按键（不转发给组件）"""
        self._global_handlers[key] = handler

    def unbind_global(self, key: int):
        """解绑全局按键"""
        self._global_handlers.pop(key, None)

    @property
    def tab_enabled(self) -> bool:
        return self._tab_enabled

    @tab_enabled.setter
    def tab_enabled(self, value: bool):
        self._tab_enabled = value

    @property
    def arrow_enabled(self) -> bool:
        return self._arrow_enabled

    @arrow_enabled.setter
    def arrow_enabled(self, value: bool):
        self._arrow_enabled = value
