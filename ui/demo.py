#!/usr/bin/env python3
"""
UI 组件库演示程序
展示所有 7 个组件，支持键盘导航和主题切换
"""

import sys
import curses
import time
import locale

from ui import (
    Theme, theme_manager,
    Button, Card, List, Input, Dialog, ProgressBar, Tabs,
    KeyboardNavigator, FocusManager,
)


class UIDemo:
    """演示应用"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.start_time = time.time()

        # 初始化 curses
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)

        # 初始化主题（默认暗色）
        theme_manager.apply_theme("dark")

        # 获取窗口大小
        self.height, self.width = self.stdscr.getmaxyx()

        # 初始化键盘导航
        self.focus_manager = FocusManager()
        self.navigator = KeyboardNavigator(self.focus_manager)

        # 初始化组件
        self._init_components()

        # 注册全局按键
        self._register_global_keys()

    def _init_components(self):
        """初始化所有组件"""
        h, w = self.height, self.width

        # --- 按钮 ---
        self.btn_demo = Button(
            label="按钮",
            x=3,
            y=3,
            on_click=self._on_btn_click,
            enabled=True,
        )
        self.btn_disabled = Button(
            label="禁用",
            x=15,
            y=3,
            enabled=False,
        )
        self.btn_theme = Button(
            label="切换主题",
            x=3,
            y=5,
            on_click=self._toggle_theme,
        )

        # --- 卡片 ---
        self.card = Card(
            title="卡片标题",
            x=30,
            y=3,
            width=40,
            height=12,
        )

        # --- 列表 ---
        self.list_demo = List(
            items=[f"列表项 {i}" for i in range(1, 21)],
            x=3,
            y=7,
            width=25,
            height=10,
            on_select=self._on_list_select,
        )

        # --- 输入框 ---
        self.input_demo = Input(
            label="用户名",
            x=3,
            y=18,
            width=25,
            on_submit=self._on_input_submit,
        )

        self.input_password = Input(
            label="密码",
            x=3,
            y=20,
            width=25,
            password=True,
        )

        # --- 进度条 ---
        self.progress = ProgressBar(
            x=30,
            y=16,
            width=40,
            value=0.0,
            label="加载中",
        )
        self.progress_timer = 0.0

        # --- 标签页 ---
        self.tabs = Tabs(
            tabs=["标签1", "标签2", "标签3"],
            x=30,
            y=18,
            width=40,
            height=12,
            on_change=self._on_tab_change,
        )

        # --- 对话框（初始隐藏） ---
        self.dialog = Dialog(
            title="提示",
            message="这是一个模态对话框示例。\n按回车或点击按钮关闭。",
            x=h // 2 - 25,
            y=h // 2 - 5,
            width=50,
            height=10,
            modal=True,
            buttons=[("确定", self._close_dialog), ("取消", self._close_dialog)],
        )
        self.dialog.visible = False

        self.btn_open_dialog = Button(
            label="打开对话框",
            x=3,
            y=22,
            on_click=self._open_dialog,
        )

        # 注册焦点组件
        self.focus_manager.register(
            self.btn_demo,
            self.btn_theme,
            self.list_demo,
            self.input_demo,
            self.input_password,
        )
        self.focus_manager.auto_focus_first()

    def _register_global_keys(self):
        """注册全局按键"""
        self.navigator.bind_global(ord('q'), self._quit)
        self.navigator.bind_global(ord('Q'), self._quit)
        self.navigator.bind_global(27, self._quit)  # ESC
        self.navigator.bind_global(ord('t'), self._toggle_theme)
        self.navigator.bind_global(ord('d'), self._open_dialog)
        self.navigator.bind_global(curses.KEY_F5, self._open_dialog)

    # ─── 事件处理 ───────────────────────────────────────────

    def _on_btn_click(self):
        self.status_msg = "按钮被点击！"

    def _toggle_theme(self):
        theme_manager.toggle()
        self.status_msg = f"主题切换为: {theme_manager.current.name}"

    def _on_list_select(self, index):
        self.status_msg = f"选中列表项: {index + 1}"

    def _on_input_submit(self, value):
        self.status_msg = f"输入内容: {value}"

    def _on_tab_change(self, index):
        self.status_msg = f"切换到标签: {index + 1}"

    def _open_dialog(self):
        self.dialog.visible = True
        self.focus_manager.register(self.dialog.buttons[0])
        self.dialog.buttons[0].focused = True

    def _close_dialog(self):
        self.dialog.visible = False
        self.focus_manager.unregister(self.dialog.buttons[0])
        self.focus_manager.unregister(self.dialog.buttons[1])
        self.status_msg = "对话框已关闭"

    def _quit(self):
        self.running = False

    # ─── 渲染 ───────────────────────────────────────────────

    def render(self):
        self.stdscr.clear()
        h, w = self.height, self.width
        theme = theme_manager.current

        # 标题
        title = "Curses UI 组件库演示"
        try:
            self.stdscr.addstr(0, (w - len(title)) // 2, title,
                              theme.c_primary | curses.A_BOLD)
            self.stdscr.addstr(0, w - 20, f"[t]主题", theme.c_muted)
        except curses.error:
            pass

        # 组件列表（左侧）
        comps_label = "组件列表："
        try:
            self.stdscr.addstr(2, 3, comps_label, theme.c_secondary | curses.A_BOLD)
        except curses.error:
            pass

        # 渲染所有组件
        self.btn_demo.render(self.stdscr)
        self.btn_disabled.render(self.stdscr)
        self.btn_theme.render(self.stdscr)
        self.card.render(self.stdscr)
        self.list_demo.render(self.stdscr)
        self.input_demo.render(self.stdscr)
        self.input_password.render(self.stdscr)
        self.progress.render(self.stdscr)
        self.tabs.render(self.stdscr)
        self.btn_open_dialog.render(self.stdscr)

        # 对话框
        if self.dialog.visible:
            self.dialog.render(self.stdscr)

        # 状态栏
        msg = getattr(self, "status_msg", "按 q 退出 | Tab 切换焦点 | t 切换主题 | d 打开对话框")
        try:
            self.stdscr.addstr(h - 1, 0, msg[:w], theme.c_muted)
        except curses.error:
            pass

        # 焦点指示
        focused = self.focus_manager.get_focused()
        if focused:
            hint = f"[{focused.__class__.__name__}]"
            try:
                self.stdscr.addstr(h - 1, w - len(hint) - 1, hint, theme.c_highlight)
            except curses.error:
                pass

        self.stdscr.refresh()

    # ─── 主循环 ─────────────────────────────────────────────

    def on_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.stdscr.clear()

    def run(self):
        self.render()
        last_progress_update = time.time()

        while self.running:
            try:
                key = self.stdscr.getch()
                if key != -1:
                    self.navigator.on_key(key)

                # 更新进度条动画
                now = time.time()
                if now - last_progress_update > 0.1:
                    self.progress_timer += 0.02
                    self.progress.set_value((self.progress_timer % 1.0))
                    last_progress_update = now

                # 窗口大小变化检测
                new_h, new_w = self.stdscr.getmaxyx()
                if new_h != self.height or new_w != self.width:
                    self.height, self.width = new_h, new_w
                    self.on_resize()

                self.render()

            except curses.error:
                pass

        self.cleanup()

    def cleanup(self):
        self.stdscr.keypad(False)
        curses.endwin()
        elapsed = time.time() - self.start_time
        print(f"\n演示结束，运行时长: {elapsed:.1f}秒")


def main(stdscr):
    locale.setlocale(locale.LC_ALL, "")
    demo = UIDemo(stdscr)
    demo.run()


if __name__ == "__main__":
    curses.wrapper(main)
