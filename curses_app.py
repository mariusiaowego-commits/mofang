#!/usr/bin/env python3
"""
页面路由系统 - MVC 架构
支持页面栈管理、生命周期管理、页面间数据传递、全局快捷键、主题切换
"""

from __future__ import annotations

import sys
import curses
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from theme_manager import ThemeManager
from user_manager import get_user_manager, UserProfile
from user_pages import UserPageRouter


# ─── 颜色初始化 ──────────────────────────────────────────────────────────────

def init_colors(theme_mgr: ThemeManager):
    """使用 ThemeManager 初始化 curses 颜色"""
    return theme_mgr.init_colors()


# ─── 页面基类 ─────────────────────────────────────────────────────────────────

class Page(ABC):
    """页面基类，所有页面继承此类"""

    def __init__(self, router: 'PageRouter', data: Any = None):
        self.router = router
        self.data = data          # 接收从上一个页面传递的数据
        self._result: Any = None   # 返回给上一个页面的数据

    # ── 生命周期钩子 ──────────────────────────────────────────────────────────

    def on_enter(self, prev_page: Optional['Page'] = None, data: Any = None):
        """进入页面时调用（可选重写）"""
        pass

    def on_leave(self) -> Any:
        """离开页面时调用，返回传递给下一个页面的数据（可选重写）"""
        return None

    def on_resize(self, height: int, width: int):
        """窗口大小变化时调用（可选重写）"""
        pass

    def on_key(self, key: int) -> bool:
        """按键处理，返回 False 则退出当前页面（返回上一页）
        
        内置全局快捷键在 PageRouter 中处理，页面只处理业务按键
        """
        return True

    @abstractmethod
    def render(self, stdscr):
        """渲染页面内容（必须重写）"""
        pass

    def set_result(self, data: Any):
        """设置返回给上一个页面的数据"""
        self._result = data

    @property
    def result(self) -> Any:
        """获取上一个页面返回的数据"""
        return self._result


# ─── 页面路由 ─────────────────────────────────────────────────────────────────

class PageRouter:
    """
    页面路由器 - 核心 MVC 组件
    
    职责：
    - 页面栈管理（push/pop/replace）
    - 页面生命周期触发
    - 全局快捷键处理（ESC 返回）
    - 页面间数据传递
    """

    def __init__(self, stdscr: curses.window, app=None):
        self.stdscr = stdscr
        self.app = app  # reference to CursesApp
        self.stack: list[Page] = []       # 页面栈
        self.current_page: Optional[Page] = None
        self.height, self.width = stdscr.getmaxyx()

        # 全局快捷键映射: key -> (description, handler)
        self._global_shortcuts: dict[int, tuple[str, Callable]] = {}

        # 动画状态
        self._animation_enabled = True

    # ── 全局快捷键 ──────────────────────────────────────────────────────────

    def register_global_shortcut(self, key: int, desc: str, handler: Callable):
        """注册全局快捷键（每个 key 只对应一个 handler）"""
        self._global_shortcuts[key] = (desc, handler)

    def handle_global_key(self, key: int) -> bool:
        """处理全局快捷键，返回 True 表示已处理"""
        if key in self._global_shortcuts:
            _, handler = self._global_shortcuts[key]
            handler()
            return True
        return False

    # ── 页面栈操作 ───────────────────────────────────────────────────────────

    def push(self, page_class: type, data: Any = None, **kwargs):
        """
        压入新页面（可传递数据）
        
        Args:
            page_class: Page 子类（不是实例）
            data: 传递给新页面的数据
            **kwargs: 传给 page_class.__init__ 的额外参数
        """
        # 触发当前页面的 on_leave
        if self.current_page:
            result = self.current_page.on_leave()
            if result is not None:
                self.current_page.set_result(result)

        # 创建新页面
        prev_page = self.current_page
        page = page_class(self, data, **kwargs)
        self.stack.append(page)

        # 触发新页面的 on_enter
        self.current_page = page
        page.on_enter(prev_page, data)

        # 渲染新页面
        self._render()

    def pop(self, data: Any = None) -> Optional[Any]:
        """
        弹出当前页面，返回传递给上一个页面的数据
        
        Args:
            data: 传递给上一个页面的数据（可选）
        """
        if len(self.stack) <= 1:
            # 已经是最后一页，不能再 pop
            return None

        page = self.stack.pop()
        self.current_page = self.stack[-1]

        # 触发返回页面的 on_enter
        self.current_page.on_enter(page, data or page._result)

        # 触发弹出页面的 on_leave（设置返回数据）
        page.on_leave()
        if data is not None:
            page.set_result(data)

        self._render()
        return page._result

    def replace(self, page_class: type, data: Any = None, **kwargs):
        """
        替换当前页面（不保留当前页面状态）
        """
        if self.current_page:
            self.current_page.on_leave()

        # 创建新页面，替换栈顶
        prev_page = self.current_page
        page = page_class(self, data, **kwargs)
        if self.stack:
            self.stack[-1] = page
        else:
            self.stack.append(page)

        self.current_page = page
        page.on_enter(prev_page, data)
        self._render()

    def pop_to_root(self):
        """返回根页面"""
        while len(self.stack) > 1:
            self.pop()
        self._render()

    @property
    def page_count(self) -> int:
        """当前栈深度"""
        return len(self.stack)

    # ── 窗口大小 ─────────────────────────────────────────────────────────────

    def check_resize(self):
        """检查窗口大小变化"""
        new_h, new_w = self.stdscr.getmaxyx()
        if new_h != self.height or new_w != self.width:
            self.height, self.width = new_h, new_w
            if self.current_page:
                self.current_page.on_resize(self.height, self.width)
            self._render()

    # ── 渲染 ─────────────────────────────────────────────────────────────────

    def _render(self):
        """内部渲染方法"""
        if self.current_page:
            try:
                self.current_page.render(self.stdscr)
                self.stdscr.refresh()
            except curses.error:
                pass

    def render(self):
        """公开渲染方法"""
        self._render()


# ─── 演示页面 ─────────────────────────────────────────────────────────────────

class HomePage(Page):
    """首页"""

    def on_enter(self, prev_page, data):
        self.router.register_global_shortcut(27, "返回/退出", self._handle_esc)

    def _handle_esc(self):
        if self.router.page_count > 1:
            self.router.pop()
        else:
            # 最后一页，触发退出
            raise KeyboardInterrupt

    def on_key(self, key: int) -> bool:
        if key in (ord('1'), ):
            self.router.push(ListPage, "来自首页的问候")
        elif key in (ord('2'), ):
            self.router.push(FormPage)
        elif key in (ord('3'), ):
            self.router.push(DetailPage, "初始数据")
        elif key in (ord('u'), ord('U')):
            # 用户切换
            self.router.app.show_user_selector()
        elif key in (ord('q'), ord('Q')):
            raise KeyboardInterrupt
        return True

    def render(self, stdscr):
        stdscr.clear()
        title = "魔方训练助手 - 首页"
        stdscr.addstr(1, (self.width - len(title)) // 2, title,
                      curses.color_pair(2) | curses.A_BOLD)

        # 显示当前用户信息
        um = get_user_manager()
        active = um.active_user
        if active:
            user_info = f"当前用户: {active.name}"
        else:
            user_info = "未登录用户"
        stdscr.addstr(2, 2, user_info, curses.color_pair(3))

        menu = [
            "1. 列表页（页面栈 push）",
            "2. 表单页（页面间数据传递）",
            "3. 详情页（replace 替换）",
            "",
            "U - 切换用户",
            "ESC - 返回上一页（全局）",
            "q - 退出程序",
        ]
        for i, line in enumerate(menu, start=4):
            stdscr.addstr(i, 2, line, curses.color_pair(1))

        hint = f"[ 栈深度: {self.router.page_count} ]"
        stdscr.addstr(self.height - 2, 2, hint, curses.color_pair(3))


class ListPage(Page):
    """列表页"""

    def on_enter(self, prev_page, data):
        self.items = [f"项目 {i}" for i in range(1, 8)]
        self.selected = 0
        self.scroll_offset = 0
        self._message = data if data else ""

    def on_key(self, key: int) -> bool:
        if key == curses.KEY_UP:
            self.selected = max(0, self.selected - 1)
        elif key == curses.KEY_DOWN:
            self.selected = min(len(self.items) - 1, self.selected + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            item = self.items[self.selected]
            self.router.push(DetailPage, item)
        elif key == 27:  # ESC
            result = self.router.pop("列表页返回数据")
            # 首页可以通过 page.result 获取
        elif key in (ord('b'), ord('B')):
            self.router.pop()
        return True

    def render(self, stdscr):
        stdscr.clear()
        title = "列表页"
        stdscr.addstr(1, (self.width - len(title)) // 2, title,
                        curses.color_pair(2) | curses.A_BOLD)

        if self._message:
            stdscr.addstr(2, 2, f"收到数据: {self._message}", curses.color_pair(4))

        # 显示列表
        visible_rows = self.height - 6
        for i in range(min(len(self.items), visible_rows)):
            idx = self.scroll_offset + i
            if idx >= len(self.items):
                break
            item = self.items[idx]
            prefix = "→ " if idx == self.selected else "  "
            attr = curses.color_pair(3) | curses.A_BOLD if idx == self.selected else curses.color_pair(1)
            stdscr.addstr(3 + i, 2, f"{prefix}{item}", attr)

        # 底部提示
        stdscr.addstr(self.height - 3, 2, "↑↓ 选择 | Enter 进入 | b/ESC 返回",
                      curses.color_pair(5))
        stdscr.addstr(self.height - 2, 2, f"[ 栈深度: {self.router.page_count} ]",
                      curses.color_pair(3))


class FormPage(Page):
    """表单页（演示页面间数据传递）"""

    def on_enter(self, prev_page, data):
        self._message = data if data else "无数据"

    def on_key(self, key: int) -> bool:
        if key == 27:
            self.router.pop("表单填写取消")
        elif key in (ord('s'), ord('S')):
            # 模拟提交，返回数据给上一个页面
            self.router.pop("表单提交成功!")
        elif key in (ord('f'), ord('F')):
            self.router.replace(HomePage)
        return True

    def render(self, stdscr):
        stdscr.clear()
        title = "表单页"
        stdscr.addstr(1, (self.width - len(title)) // 2, title,
                      curses.color_pair(2) | curses.A_BOLD)

        stdscr.addstr(3, 2, f"收到上一个页面的数据: {self._message}", curses.color_pair(4))

        fields = [
            "字段 1: [____________]",
            "字段 2: [____________]",
            "",
            "s - 提交（返回成功消息）",
            "f - 替换到首页（不保留表单状态）",
            "ESC - 返回（不提交）",
        ]
        for i, line in enumerate(fields, start=5):
            stdscr.addstr(i, 2, line, curses.color_pair(1))

        stdscr.addstr(self.height - 2, 2, f"[ 栈深度: {self.router.page_count} ]",
                      curses.color_pair(3))


class DetailPage(Page):
    """详情页（演示 replace）"""

    def on_enter(self, prev_page, data):
        self._detail_data = data if data else "无数据"

    def on_key(self, key: int) -> bool:
        if key == 27:
            self.router.pop()
        return True

    def render(self, stdscr):
        stdscr.clear()
        title = "详情页"
        stdscr.addstr(1, (self.width - len(title)) // 2, title,
                      curses.color_pair(2) | curses.A_BOLD)

        stdscr.addstr(3, 2, f"当前数据: {self._detail_data}", curses.color_pair(4))

        stdscr.addstr(5, 2, "replace 会替换掉当前页面，不保留历史", curses.color_pair(5))
        stdscr.addstr(6, 2, "所以这里按 ESC 只会返回空白或者错误", curses.color_pair(5))

        stdscr.addstr(self.height - 3, 2, "ESC - 返回列表页", curses.color_pair(1))
        stdscr.addstr(self.height - 2, 2, f"[ 栈深度: {self.router.page_count} ]",
                      curses.color_pair(3))


# ─── 应用主类 ─────────────────────────────────────────────────────────────────

class CursesApp:
    """Curses 应用（整合页面路由 + 主题系统）"""

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.running = True
        self.start_time = time.time()

        # 关闭按键 echo，隐藏光标
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)

        # 初始化主题管理器
        self.theme_mgr = ThemeManager()
        self.theme_mgr.init_colors()

        # 获取初始窗口尺寸
        self.height, self.width = self.stdscr.getmaxyx()

        # 初始化页面路由（默认显示首页）
        self.router = PageRouter(stdscr, app=self)

        # 用户选择器（临时覆盖层）
        self._user_router: Optional[UserPageRouter] = None

        # 检查是否已登录，未登录则显示用户选择器
        um = get_user_manager()
        if not um.active_user:
            self.show_user_selector()
        else:
            self.router.push(HomePage)

    def show_user_selector(self):
        """显示用户选择器（覆盖层）"""
        def on_selected(user: UserProfile):
            self._user_router = None
            # 登录成功后推入首页
            self.router.push(HomePage)

        def on_logout():
            self._user_router = None
            self.router.render()

        self._user_router = UserPageRouter(
            self.stdscr,
            on_user_selected=on_selected,
            on_user_logout=on_logout,
        )

    def on_resize(self):
        """窗口大小变化时调用"""
        self.height, self.width = self.stdscr.getmaxyx()
        self.router.check_resize()

    def run(self):
        """事件循环"""
        self.router.render()

        while self.running:
            try:
                key = self.stdscr.getch()
                if key != -1:
                    # 如果用户选择器活跃，交给它处理
                    if self._user_router is not None:
                        if not self._user_router.handle_key(key):
                            self._user_router = None
                            self.router.render()
                    else:
                        # 先尝试全局快捷键
                        if not self.router.handle_global_key(key):
                            # 交给当前页面处理
                            if not self.router.current_page.on_key(key):
                                # 页面返回 False，弹出当前页
                                self.router.pop()

                # 检查窗口大小变化
                self.on_resize()

            except curses.error:
                pass
            except KeyboardInterrupt:
                self.running = False
                break

        self.cleanup()

    def cleanup(self):
        """优雅退出"""
        self.stdscr.keypad(False)
        curses.endwin()


def main(stdscr):
    app = CursesApp(stdscr)
    app.run()


if __name__ == "__main__":
    import locale
    locale.setlocale(locale.LC_ALL, "")

    start = time.time()
    curses.wrapper(main)
    elapsed = time.time() - start
    if elapsed > 0.5:
        print(f"警告: 启动时间 {elapsed:.3f}秒 > 0.5秒", file=sys.stderr)
        sys.exit(1)
