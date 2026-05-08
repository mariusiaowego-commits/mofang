#!/usr/bin/env python3
"""
主题系统演示
展示主题切换、颜色显示
"""

import sys
import curses
import locale
import time
from theme_manager import ThemeManager


class ThemeDemoApp:
    """主题演示应用"""

    THEME_KEYS = {
        ord('1'): 'dark',
        ord('2'): 'light',
        ord('3'): 'high_contrast',
        ord('4'): 'solarized_dark',
    }

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.theme_mgr = ThemeManager()
        self.start_time = time.time()
        self.resize_count = 0

        # curses 初始化
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)
        
        # 初始化主题颜色
        self.theme_mgr.init_colors()
        
        # 获取窗口尺寸
        self.height, self.width = self.stdscr.getmaxyx()

    def on_resize(self):
        self.resize_count += 1
        self.height, self.width = self.stdscr.getmaxyx()

    def on_key(self, key):
        if key in (ord('q'), ord('Q'), 27):
            return False
        
        # 主题切换
        if key in self.THEME_KEYS:
            theme_name = self.THEME_KEYS[key]
            if self.theme_mgr.set_theme(theme_name):
                self.stdscr.clear()
        
        # 列出主题
        if key in (ord('l'), ord('L')):
            self._show_theme_list()
        
        return True

    def _show_theme_list(self):
        """显示所有可用主题"""
        themes = self.theme_mgr.list_themes()
        msg = f"可用主题: {', '.join(themes.keys())}"
        # 在底部显示
        try:
            self.stdscr.addstr(self.height - 1, 0, msg[:self.width - 1])
        except curses.error:
            pass
        self.stdscr.refresh()
        time.sleep(1.5)

    def render(self):
        self.stdscr.clear()
        tm = self.theme_mgr
        cp = lambda name: tm.get_color_pair(name)
        theme = tm.active_theme

        # === 标题栏 ===
        title = f"主题演示 - {theme.display_name}"
        try:
            self.stdscr.addstr(0, 0, title.center(self.width - 1), 
                             cp("header") | curses.A_BOLD)
        except curses.error:
            pass

        # === 颜色展示区 ===
        color_names = [
            ("前景", "foreground"),
            ("背景", "background"),
            ("高亮", "highlight"),
            ("标题", "header"),
            ("成功", "success"),
            ("错误", "error"),
            ("暗淡", "dim"),
            ("选中", "selected"),
            ("强调1", "accent1"),
            ("强调2", "accent2"),
        ]

        for i, (label, name) in enumerate(color_names):
            y = 2 + i
            if y >= self.height - 4:
                break
            try:
                # 颜色名称
                self.stdscr.addstr(y, 2, f"{label}: ", cp("foreground"))
                # 颜色块
                color_char = "█" * 8
                self.stdscr.addstr(y, 10, color_char, cp(name))
            except curses.error:
                pass

        # === 主题列表提示 ===
        y = self.height - 6
        hints = [
            "切换主题: 1-暗色 2-浅色 3-高对比 4-Solarized",
            "L: 显示所有主题",
            "Q/ESC: 退出",
        ]
        for i, hint in enumerate(hints):
            try:
                self.stdscr.addstr(y + i, 2, hint, cp("dim"))
            except curses.error:
                pass

        # === 状态栏 ===
        elapsed = time.time() - self.start_time
        status = f"主题: {theme.name} | 窗口: {self.width}x{self.height} | 重设: {self.resize_count} | 耗时: {elapsed:.1f}s"
        try:
            self.stdscr.addstr(self.height - 1, 0, status[:self.width - 1], cp("dim"))
        except curses.error:
            pass

        self.stdscr.refresh()

    def run(self):
        self.render()
        running = True

        while running:
            try:
                key = self.stdscr.getch()
                if key != -1:
                    if not self.on_key(key):
                        running = False

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


def main(stdscr):
    locale.setlocale(locale.LC_ALL, "")
    app = ThemeDemoApp(stdscr)
    app.run()


if __name__ == "__main__":
    start = time.time()
    curses.wrapper(main)
    elapsed = time.time() - start
    print(f"运行时间: {elapsed:.3f}秒", file=sys.stderr)
