#!/usr/bin/env python3
"""
用户选择与切换页面
使用 PageRouter 架构
"""

from __future__ import annotations

import curses
import time
from typing import Optional

from user_manager import UserManager, get_user_manager, UserProfile


# ─── 用户选择页 ────────────────────────────────────────────────────────────

class UserListPage:
    """
    用户列表页
    - 显示所有已创建用户
    - 支持选择用户登录
    - 支持切换/删除用户
    """

    def __init__(self, router: 'UserPageRouter', data=None):
        self.router = router
        self.um: UserManager = get_user_manager()
        self.users = self.um.list_users()
        self.selected = 0
        self._result: Optional[UserProfile] = None

    def on_key(self, key: int) -> bool:
        if key == curses.KEY_UP:
            self.selected = max(0, self.selected - 1)
        elif key == curses.KEY_DOWN:
            self.selected = min(len(self.users) - 1, self.selected + 1)
        elif key in (curses.KEY_ENTER, 10, 13, ord('\n')):
            if self.users:
                user = self.users[self.selected]
                self.um.set_active_user(user.id)
                self._result = user
                # 登录成功，通知关闭
                if self.router.on_user_selected:
                    self.router.on_user_selected(user)
                return False  # 关闭选择页
        elif key == ord('c') or key == ord('C'):
            # 创建新用户
            self.router.push(CreateUserPage)
        elif key == ord('d') or key == ord('D'):
            # 删除用户（需确认）
            if self.users:
                self.router.push(DeleteUserConfirmPage, self.users[self.selected])
        elif key == 27:  # ESC - 取消
            return False
        return True

    def on_enter(self, prev_page, data):
        self.users = self.um.list_users()
        if self.users and self.selected >= len(self.users):
            self.selected = len(self.users) - 1

    def render(self, stdscr):
        stdscr.clear()
        title = "选择用户"
        stdscr.addstr(1, (self.router.width - len(title)) // 2, title,
                      curses.color_pair(2) | curses.A_BOLD)

        if not self.users:
            stdscr.addstr(4, 4, "暂无用户，请按 C 创建新用户", curses.color_pair(5))
        else:
            stdscr.addstr(3, 4, "选择用户登录:", curses.color_pair(3))
            for i, user in enumerate(self.users):
                is_active = (self.um.active_user and 
                            self.um.active_user.id == user.id)
                prefix = "→ " if i == self.selected else "  "
                active_mark = " [当前]" if is_active else ""
                line = f"{prefix}{user.name}{active_mark}"
                attr = (curses.color_pair(3) | curses.A_BOLD 
                        if i == self.selected else curses.color_pair(1))
                try:
                    stdscr.addstr(4 + i, 4, line, attr)
                except curses.error:
                    pass

        # 底部提示
        hints = [
            "↑↓ 选择 | Enter 登录 | C 创建 | D 删除 | ESC 取消"
        ]
        for i, h in enumerate(hints):
            stdscr.addstr(self.router.height - 2, 2, h, curses.color_pair(5))

    @property
    def result(self) -> Optional[UserProfile]:
        return self._result


class CreateUserPage:
    """创建新用户页"""

    def __init__(self, router: 'UserPageRouter', data=None):
        self.router = router
        self.name = ""
        self.cursor_pos = 0
        self._result: Optional[UserProfile] = None

    def on_key(self, key: int) -> bool:
        if key == curses.KEY_BACKSPACE or key == 127:
            if self.name and self.cursor_pos > 0:
                self.name = self.name[:self.cursor_pos - 1] + self.name[self.cursor_pos:]
                self.cursor_pos -= 1
        elif key == 27:  # ESC - 取消
            return False  # 关闭，返回列表
        elif key in (curses.KEY_ENTER, 10, 13, ord('\n')):
            # 确认创建
            if self.name.strip():
                um = get_user_manager()
                user = um.create_user(self.name.strip())
                self._result = user
                # 登录新用户
                um.set_active_user(user.id)
                if self.router.on_user_selected:
                    self.router.on_user_selected(user)
                return False  # 关闭创建页
        elif 32 <= key <= 126:  # 可打印 ASCII
            ch = chr(key)
            if len(self.name) < 20:  # 限制名字长度
                self.name = self.name[:self.cursor_pos] + ch + self.name[self.cursor_pos:]
                self.cursor_pos += 1
        elif key == curses.KEY_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == curses.KEY_RIGHT:
            self.cursor_pos = min(len(self.name), self.cursor_pos + 1)
        return True

    def render(self, stdscr):
        stdscr.clear()
        title = "创建新用户"
        stdscr.addstr(1, (self.router.width - len(title)) // 2, title,
                      curses.color_pair(2) | curses.A_BOLD)

        stdscr.addstr(4, 4, "输入用户名:", curses.color_pair(3))
        
        # 显示输入框
        box_y, box_x = 6, 4
        max_w = 30
        stdscr.addstr(box_y, box_x, "+" + "-" * max_w + "+")
        stdscr.addstr(box_y + 1, box_x, "|")
        stdscr.addstr(box_y + 1, box_x + max_w + 1, "|")
        stdscr.addstr(box_y + 2, box_x, "+" + "-" * max_w + "+")
        
        # 显示输入内容（带光标）
        display = self.name.ljust(self.cursor_pos + 1)[:max_w]
        attr = curses.A_REVERSE if True else curses.color_pair(1)  # 光标效果用下划线
        try:
            stdscr.addstr(box_y + 1, box_x + 1, " " * max_w)  # 清空
            stdscr.addstr(box_y + 1, box_x + 1, self.name[:max_w], curses.color_pair(1))
            if self.cursor_pos < len(self.name) and self.cursor_pos < max_w:
                # 光标位置字符高亮
                cur_char = self.name[self.cursor_pos]
                stdscr.addstr(box_y + 1, box_x + 1 + self.cursor_pos, cur_char, 
                             curses.color_pair(3) | curses.A_REVERSE)
        except curses.error:
            pass

        stdscr.addstr(box_y + 3, 4, f"当前: {self.name or '(空)'}", curses.color_pair(5))

        hints = "Enter 确认 | ESC 取消 | ←→ 移动光标 | Backspace 删除"
        stdscr.addstr(self.router.height - 2, 2, hints, curses.color_pair(5))

    @property
    def result(self) -> Optional[UserProfile]:
        return self._result


class DeleteUserConfirmPage:
    """删除用户确认页"""

    def __init__(self, router: 'UserPageRouter', data: UserProfile = None):
        self.router = router
        self.user: UserProfile = data
        self.confirmed = False

    def on_key(self, key: int) -> bool:
        if key in (ord('y'), ord('Y'), curses.KEY_ENTER, 10, 13):
            # 确认删除
            um = get_user_manager()
            if self.user:
                was_active = (um.active_user and um.active_user.id == self.user.id)
                um.delete_user(self.user.id)
                if was_active:
                    um.clear_active_user()
                    if self.router.on_user_logout:
                        self.router.on_user_logout()
            return False  # 关闭确认页
        elif key in (ord('n'), ord('N'), 27):
            return False  # 取消，关闭
        return True

    def render(self, stdscr):
        stdscr.clear()
        title = "确认删除"
        stdscr.addstr(1, (self.router.width - len(title)) // 2, title,
                      curses.color_pair(2) | curses.A_BOLD)

        if self.user:
            msg = f"确定删除用户 '{self.user.name}' 吗？"
            stdscr.addstr(5, 4, msg, curses.color_pair(3))
            stdscr.addstr(7, 4, "此操作不可恢复！", curses.color_pair(5))

        stdscr.addstr(self.router.height - 3, 4, "Y/Enter 确认删除 | N/ESC 取消", 
                      curses.color_pair(5))


# ─── 简单路由（用于用户选择对话框）─────────────────────────────────────────

class UserPageRouter:
    """
    简化版页面路由，用于用户选择流程
    与主 CursesApp 共享窗口但独立管理
    """

    def __init__(self, stdscr,
                 on_user_selected=None,
                 on_user_logout=None):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.stack: list = []
        self.on_user_selected = on_user_selected   # callback(user)
        self.on_user_logout = on_user_logout    # callback()
        self._push_page(UserListPage)

    def _push_page(self, page_class, data=None):
        page = page_class(self, data)
        self.stack.append(page)
        page.on_enter(None, data)
        self.render()

    def push(self, page_class, data=None):
        self._push_page(page_class, data)

    def pop(self):
        if len(self.stack) > 1:
            self.stack.pop()
            self.stack[-1].on_enter(None, None)
            self.render()

    def render(self):
        if self.stack:
            try:
                self.stack[-1].render(self.stdscr)
                self.stdscr.refresh()
            except curses.error:
                pass

    def handle_key(self, key: int) -> bool:
        """处理按键，返回 False 表示关闭用户选择流程"""
        if not self.stack:
            return False
        result = self.stack[-1].on_key(key)
        if result is False:
            # 页面要求关闭
            if len(self.stack) > 1:
                self.pop()
            else:
                # 最后一个页面关闭整个选择流程
                return False
        else:
            self.render()
        return True

    @property
    def current_page(self):
        return self.stack[-1] if self.stack else None
