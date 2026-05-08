#!/usr/bin/env python3
"""
魔方训练仪表盘首页
P1 仪盘盘开发 - curses TUI 界面
"""

from __future__ import annotations

import curses
import sys
import os
from datetime import date
from typing import Any

# 添加项目路径（支持直接运行和模块导入）
_dashboard_dir = os.path.dirname(os.path.abspath(__file__))
_mofang_dir = os.path.dirname(_dashboard_dir)
if _mofang_dir not in sys.path:
    sys.path.insert(0, _mofang_dir)

from curses_app import Page, PageRouter
from ui.theme import theme_manager
from ui.components import Card, List, Button, ProgressBar


# ─── 数据模型 ────────────────────────────────────────────────

class TrainingStats:
    """今日训练统计数据"""

    def __init__(self):
        self.solves_today = 0
        self.avg_time_today = 0.0
        self.best_time_today = 0.0
        self.total_time_today = 0.0
        self.dnf_count = 0

    @property
    def formatted_avg(self) -> str:
        if self.avg_time_today == 0:
            return "--"
        return f"{self.avg_time_today:.2f}s"

    @property
    def formatted_best(self) -> str:
        if self.best_time_today == 0:
            return "--"
        return f"{self.best_time_today:.2f}s"

    @property
    def formatted_total(self) -> str:
        if self.total_time_today == 0:
            return "0s"
        mins = int(self.total_time_today // 60)
        secs = int(self.total_time_today % 60)
        if mins > 0:
            return f"{mins}分{secs}秒"
        return f"{secs}秒"


class RecentRecord:
    """最近训练记录"""

    def __init__(self, date_str: str, session_id: str, avg_time: float, solve_count: int):
        self.date_str = date_str
        self.session_id = session_id
        self.avg_time = avg_time
        self.solve_count = solve_count

    def __str__(self) -> str:
        return f"{self.date_str}  #{self.session_id}  均: {self.avg_time:.2f}s  {self.solve_count}次"


# ─── 数据获取 ────────────────────────────────────────────────

def get_current_user() -> dict:
    """获取当前用户（演示用硬编码）"""
    return {
        "name": "学员1号",
        "current_level": "L2-L3 进阶过渡",
        "target": "45秒内",
    }


def get_today_stats() -> TrainingStats:
    """获取今日训练统计"""
    # TODO: 后续从实际训练数据读取
    stats = TrainingStats()
    stats.solves_today = 12
    stats.avg_time_today = 95.5
    stats.best_time_today = 82.3
    stats.total_time_today = 1146.0  # 19分06秒
    stats.dnf_count = 0
    return stats


def get_recent_records() -> list[RecentRecord]:
    """获取最近训练记录"""
    # TODO: 后续从实际训练日志读取
    today = date.today()
    records = [
        RecentRecord(today.strftime("%m-%d"), "S001", 95.5, 12),
        RecentRecord((today.replace(day=today.day - 1)).strftime("%m-%d"), "S002", 98.2, 15),
        RecentRecord((today.replace(day=today.day - 2)).strftime("%m-%d"), "S003", 102.1, 10),
        RecentRecord((today.replace(day=today.day - 3)).strftime("%m-%d"), "S004", 99.8, 18),
        RecentRecord((today.replace(day=today.day - 5)).strftime("%m-%d"), "S005", 105.3, 8),
    ]
    return records


def get_learning_progress() -> dict[str, float]:
    """获取公式学习进度"""
    return {
        "CFOP": 35.0,
        "OLL": 12.3,   # 7/57
        "PLL": 14.3,   # 3/21
        "F2L": 0.0,
    }


def get_system_status() -> dict[str, Any]:
    """获取系统状态"""
    return {
        "user_count": 1,
        "total_sessions": 47,
        "total_solves": 1234,
        "last_train_date": date.today().strftime("%Y-%m-%d"),
    }


# ─── 仪表盘首页 ───────────────────────────────────────────────

class DashboardHomePage(Page):
    """
    仪表盘首页

    布局 (高度 25, 宽度 80 终端):
    ┌──────────────────────────────────────────────────────────────────┐
    │  魔方训练仪表盘          [主题: dark]  2026-05-08  星期四         │
    ├──────────────────────────────────────────────────────────────────┤
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
    │  │ 今日还原数  │  │  今日平均   │  │  今日最佳   │              │
    │  │    12次    │  │   95.50s   │  │   82.30s   │              │
    │  └─────────────┘  └─────────────┘  └─────────────┘              │
    ├──────────────────────────────────────────────────────────────────┤
    │  最近训练记录                                                ▲ ▼ │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │ 05-08  #S001  均: 95.50s  12次                             │  │
    │  │ 05-07  #S002  均: 98.20s  15次                             │  │
    │  │ 05-06  #S003  均: 102.10s 10次                             │  │
    │  └──────────────────────────────────────────────────────────┘  │
    ├──────────────────────────────────────────────────────────────────┤
    │  快速操作    [1-训练]  [2-公式]  [3-分析]  [4-设置]             │
    ├──────────────────────────────────────────────────────────────────┤
    │  学习进度                                                    ▲ ▼ │
    │  CFOP: 35.0%  [████████████░░░░░░░░░░░░░░░░░░░░░░░░░]         │
    │  OLL:  12.3%  [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]       │
    │  PLL:  14.3%  [█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]       │
    ├──────────────────────────────────────────────────────────────────┤
    │  系统状态: 用户1  总训练47次  总还原1234次  最后: 2026-05-08   │
    └──────────────────────────────────────────────────────────────────┘
    """

    # 布局常量
    HEADER_Y = 1
    STATS_Y = 3
    RECORDS_Y = 7
    ACTIONS_Y = 14
    PROGRESS_Y = 16
    STATUS_Y = 21

    def on_enter(self, prev_page, data):
        # 注册全局快捷键
        self.router.register_global_shortcut(27, "退出", self._handle_esc)
        self.router.register_global_shortcut(49, "主题切换", self._toggle_theme)  # 1

        # 加载数据
        self.user = get_current_user()
        self.today_stats = get_today_stats()
        self.recent_records = get_recent_records()
        self.learning_progress = get_learning_progress()
        self.system_status = get_system_status()

        # 选中记录索引
        self.selected_record = 0
        self.record_scroll = 0
        self.max_visible_records = 5

        # 当前用户
        self.current_username = "学员1号"

        # 当前主题名称
        self.theme_name = theme_manager.current.name

    def _handle_esc(self):
        raise KeyboardInterrupt

    def _toggle_theme(self):
        theme_manager.toggle()
        self.theme_name = theme_manager.current.name

    def _get_weekday(self) -> str:
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[date.today().weekday()]

    def on_key(self, key: int) -> bool:
        if key in (ord('q'), ord('Q')):
            raise KeyboardInterrupt

        # 主题切换 1-4
        themes = ["dark", "light", "high_contrast", "solarized_dark"]
        if ord('1') <= key <= ord('4'):
            idx = key - ord('1')
            if idx < len(themes):
                try:
                    theme_manager.apply_theme(themes[idx])
                    self.theme_name = theme_manager.current.name
                except ValueError:
                    pass
            return True

        # 记录列表导航
        if key == curses.KEY_UP or key == ord('k'):
            if self.selected_record > 0:
                self.selected_record -= 1
                if self.selected_record < self.record_scroll:
                    self.record_scroll = self.selected_record
        elif key == curses.KEY_DOWN or key == ord('j'):
            if self.selected_record < len(self.recent_records) - 1:
                self.selected_record += 1
                if self.selected_record >= self.record_scroll + self.max_visible_records:
                    self.record_scroll = self.selected_record - self.max_visible_records + 1
        elif key in (curses.KEY_PPAGE,):
            # 上翻页
            self.record_scroll = max(0, self.record_scroll - self.max_visible_records)
            self.selected_record = self.record_scroll
        elif key == curses.KEY_NPAGE:
            # 下翻页
            max_start = len(self.recent_records) - self.max_visible_records
            self.record_scroll = min(max_start, self.record_scroll + self.max_visible_records)
            self.selected_record = self.record_scroll

        # 快捷操作
        elif key == ord('t') or key == ord('T'):
            self._toggle_theme()
        elif key in (ord('r'),):
            # 刷新数据
            self.today_stats = get_today_stats()
            self.recent_records = get_recent_records()
        elif key in (curses.KEY_ENTER, 10, 13, ord(' ')):
            # 进入选中记录详情
            pass  # TODO

        return True

    def _render_header(self, stdscr):
        """渲染标题栏"""
        theme = theme_manager.current
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        weekday = self._get_weekday()

        title = f"魔方训练仪表盘  {self.current_username}  |  {self.user['current_level']}  →  {self.user['target']}"
        try:
            stdscr.addstr(self.HEADER_Y, 1, title[:self.width - 4], theme.c_primary | curses.A_BOLD)
            # 右侧日期
            right_info = f"{date_str}  {weekday}  [主题: {self.theme_name}]  1-4切换"
            stdscr.addstr(self.HEADER_Y, self.width - len(right_info) - 1, right_info, theme.c_muted)
        except curses.error:
            pass

    def _render_stats_cards(self, stdscr):
        """渲染今日统计卡片"""
        theme = theme_manager.current
        y = self.STATS_Y

        # 三张统计卡
        cards_data = [
            ("今日还原数", f"{self.today_stats.solves_today}次"),
            ("今日平均", f"{self.today_stats.formatted_avg}"),
            ("今日最佳", f"{self.today_stats.formatted_best}"),
        ]

        card_width = (self.width - 8) // 3
        start_x = 3

        for i, (label, value) in enumerate(cards_data):
            x = start_x + i * (card_width + 1)

            # 卡片边框
            try:
                # 顶角
                stdscr.addstr(y, x, "┌" + "─" * (card_width - 2) + "┐", theme.c_default)
                # 底角
                stdscr.addstr(y + 3, x, "└" + "─" * (card_width - 2) + "┘", theme.c_default)
                # 左右边
                for row in range(1, 3):
                    stdscr.addstr(y + row, x, "│", theme.c_default)
                    stdscr.addstr(y + row, x + card_width - 1, "│", theme.c_default)
                # 标题
                stdscr.addstr(y + 1, x + 1, label, theme.c_muted)
                # 数值
                stdscr.addstr(y + 2, x + 1, value, theme.c_highlight | curses.A_BOLD)
            except curses.error:
                pass

    def _render_recent_records(self, stdscr):
        """渲染最近训练记录"""
        theme = theme_manager.current
        y = self.RECORDS_Y

        # 标题
        try:
            stdscr.addstr(y, 1, "最近训练记录", theme.c_primary | curses.A_BOLD)
            stdscr.addstr(y, 1 + len("最近训练记录") + 1, "↑↓ 导航  Enter 查看", theme.c_muted)
        except curses.error:
            pass

        # 记录列表
        list_height = self.max_visible_records + 2
        list_width = self.width - 6
        list_x = 3
        list_y = y + 1

        visible_records = self.recent_records[self.record_scroll: self.record_scroll + self.max_visible_records]

        try:
            # 列表边框
            stdscr.addstr(list_y, list_x, "┌" + "─" * (list_width - 2) + "┐", theme.c_default)
            stdscr.addstr(list_y + list_height - 1, list_x, "└" + "─" * (list_width - 2) + "┘", theme.c_default)
            for row in range(1, list_height - 1):
                stdscr.addstr(list_y + row, list_x, "│", theme.c_default)
                stdscr.addstr(list_y + row, list_x + list_width - 1, "│", theme.c_default)

            # 滚动条
            if len(self.recent_records) > self.max_visible_records:
                scroll_ratio = self.record_scroll / max(1, len(self.recent_records) - self.max_visible_records)
                scroll_bar_y = list_y + 1 + int(scroll_ratio * (list_height - 2))
                scroll_bar_y = min(scroll_bar_y, list_y + list_height - 2)
                stdscr.addstr(scroll_bar_y, list_x + list_width - 1, "▓", theme.c_primary)

            # 记录项
            for idx, record in enumerate(visible_records):
                item_y = list_y + 1 + idx
                global_idx = self.record_scroll + idx
                is_selected = global_idx == self.selected_record

                prefix = "▶ " if is_selected else "  "
                color = theme.c_highlight if (is_selected) else theme.c_default

                record_str = str(record)[:list_width - 4]
                stdscr.addstr(item_y, list_x + 2, prefix, color)
                stdscr.addstr(item_y, list_x + 4, record_str, color)

        except curses.error:
            pass

    def _render_quick_actions(self, stdscr):
        """渲染快速操作入口"""
        theme = theme_manager.current
        y = self.ACTIONS_Y

        try:
            stdscr.addstr(y, 1, "快速操作", theme.c_primary | curses.A_BOLD)

            actions = [
                ("[t] 训练", "开始训练计时"),
                ("[f] 公式", "查看/学习公式"),
                ("[a] 分析", "训练数据分析"),
                ("[s] 设置", "系统设置"),
            ]

            x = 3
            for label, desc in actions:
                stdscr.addstr(y + 1, x, label, theme.c_highlight | curses.A_BOLD)
                stdscr.addstr(y + 1, x + 8, desc, theme.c_muted)
                x += 25

        except curses.error:
            pass

    def _render_learning_progress(self, stdscr):
        """渲染公式学习进度"""
        theme = theme_manager.current
        y = self.PROGRESS_Y

        try:
            stdscr.addstr(y, 1, "公式学习进度", theme.c_primary | curses.A_BOLD)
        except curses.error:
            pass

        bar_width = self.width - 20
        bar_x = 14

        items = [
            ("CFOP", self.learning_progress["CFOP"]),
            ("OLL", self.learning_progress["OLL"]),
            ("PLL", self.learning_progress["PLL"]),
            ("F2L", self.learning_progress["F2L"]),
        ]

        for i, (name, percent) in enumerate(items):
            row_y = y + 1 + i
            try:
                stdscr.addstr(row_y, 3, f"{name}:", theme.c_default)
                stdscr.addstr(row_y, 9, f"{percent:.1f}%", theme.c_muted)

                # 进度条背景
                filled = int(bar_width * percent / 100)
                bar_str = "█" * filled + "░" * (bar_width - filled)
                stdscr.addstr(row_y, bar_x, bar_str, theme.c_success)
            except curses.error:
                pass

    def _render_system_status(self, stdscr):
        """渲染系统状态"""
        theme = theme_manager.current
        y = self.STATUS_Y

        status = self.system_status
        status_str = (
            f"系统状态: 用户{status['user_count']}  "
            f"总训练{status['total_sessions']}次  "
            f"总还原{status['total_solves']}次  "
            f"最后: {status['last_train_date']}"
        )

        try:
            stdscr.addstr(y, 1, status_str, theme.c_muted)
            stdscr.addstr(y, self.width - 15, "ESC/q 退出", theme.c_muted)
        except curses.error:
            pass

    def _render_footer_line(self, stdscr):
        """渲染分隔线"""
        theme = theme_manager.current
        try:
            for x in range(1, self.width - 1):
                try:
                    stdscr.addstr(self.STATS_Y - 1, x, "─", theme.c_default)
                    stdscr.addstr(self.RECORDS_Y - 1, x, "─", theme.c_default)
                    stdscr.addstr(self.ACTIONS_Y - 1, x, "─", theme.c_default)
                    stdscr.addstr(self.PROGRESS_Y - 1, x, "─", theme.c_default)
                    stdscr.addstr(self.STATUS_Y - 1, x, "─", theme.c_default)
                except curses.error:
                    pass
        except curses.error:
            pass

    def render(self, stdscr):
        """渲染仪表盘"""
        stdscr.clear()

        self._render_header(stdscr)
        self._render_footer_line(stdscr)
        self._render_stats_cards(stdscr)
        self._render_recent_records(stdscr)
        self._render_quick_actions(stdscr)
        self._render_learning_progress(stdscr)
        self._render_system_status(stdscr)


# ─── 主程序入口 ────────────────────────────────────────────────

def main(stdscr):
    # 初始化
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # 应用主题
    theme_manager.apply_theme("dark")

    # 获取窗口大小
    height, width = stdscr.getmaxyx()

    # 创建应用
    from curses_app import CursesApp

    class DashboardApp(CursesApp):
        def __init__(self, stdscr):
            super().__init__(stdscr)

    app = DashboardApp(stdscr)
    # 替换首页为仪表盘
    app.router.stack[-1] = DashboardHomePage(app.router)
    app.router.current_page = app.router.stack[-1]
    app.router.current_page.on_enter(None, None)
    app.run()


if __name__ == "__main__":
    import locale
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(main)
