#!/usr/bin/env python3
"""页面路由系统 - 单元测试（无 curses 依赖）"""

import sys
sys.path.insert(0, '.')

# Mock curses 模块用于测试
class MockWindow:
    def __init__(self):
        self.height, self.width = 24, 80
        self._maxyx = (24, 80)
    def getmaxyx(self): return self._maxyx
    def clear(self): pass
    def refresh(self): pass
    def addstr(self, *args, **kwargs): pass
    def nodelay(self, v): pass
    def timeout(self, v): pass
    def keypad(self, v): pass

class MockCurses:
    has_colors = lambda self: True
    start_color = lambda self: None
    use_default_colors = lambda self: None
    init_pair = lambda *a, **kw: None
    COLOR_WHITE = 7
    COLOR_BLACK = 0
    COLOR_CYAN = 6
    COLOR_YELLOW = 3
    COLOR_GREEN = 2
    COLOR_MAGENTA = 5
    COLOR_BLACK = 0
    A_BOLD = 1
    KEY_UP = 258
    KEY_DOWN = 258
    KEY_ENTER = 343
    error = Exception
    curs_set = lambda *a, **kw: None

sys.modules['curses'] = MockCurses()

# 现在导入
from curses_app import Page, PageRouter, HomePage, ListPage, FormPage, DetailPage

# 测试 PageRouter 基本操作
stdscr = MockWindow()

def test_push():
    """测试 push 操作"""
    router = PageRouter(stdscr)
    assert router.page_count == 0, f"初始栈为空, got {router.page_count}"
    assert router.current_page is None

    router.push(HomePage)
    assert router.page_count == 1, f"push 后栈深度应为 1, got {router.page_count}"
    assert isinstance(router.current_page, HomePage)
    print("✓ push 操作正常")

def test_pop():
    """测试 pop 操作"""
    router = PageRouter(stdscr)
    router.push(HomePage)
    router.push(ListPage, "test data")

    result = router.pop("return data")
    assert router.page_count == 1, f"pop 后栈深度应为 1, got {router.page_count}"
    assert isinstance(router.current_page, HomePage)
    print("✓ pop 操作正常")

def test_replace():
    """测试 replace 操作"""
    router = PageRouter(stdscr)
    router.push(HomePage)
    router.push(ListPage)

    router.replace(DetailPage, "replaced")
    assert router.page_count == 2, f"replace 后栈深度应为 2, got {router.page_count}"
    assert isinstance(router.current_page, DetailPage)
    print("✓ replace 操作正常")

def test_data_pass():
    """测试页面间数据传递"""
    router = PageRouter(stdscr)
    router.push(HomePage)

    # 模拟页面 push 时传递数据
    class TestPage(Page):
        def render(self, stdscr): pass
        def on_enter(self, prev, data):
            self.received_data = data

    router.push(TestPage, "hello world")
    assert router.current_page.received_data == "hello world"
    print("✓ 页面间数据传递正常")

def test_lifecycle():
    """测试生命周期钩子"""
    router = PageRouter(stdscr)
    events = []

    class LifeCyclePage(Page):
        def on_enter(self, prev, data):
            events.append(f"enter({data})")
        def on_leave(self):
            events.append("leave")
        def render(self, stdscr): pass

    router.push(LifeCyclePage, "arg1")
    assert "enter(arg1)" in events
    assert len(events) == 1

    router.push(HomePage)
    # 从 LifeCyclePage 切换到 HomePage
    # 此时 LifeCyclePage.on_leave 应该在 pop 或 replace 时触发
    # 但 push 不触发上一个页面的 on_leave...

    # 简单测试: pop 应该触发 on_leave
    events.clear()
    router.push(LifeCyclePage, "arg2")
    assert "enter(arg2)" in events
    events.clear()

    result = router.pop()
    assert "leave" in events
    print("✓ 生命周期钩子正常")

def test_resize():
    """测试窗口大小变化检测"""
    router = PageRouter(stdscr)
    router.push(HomePage)

    # 模拟窗口变化（修改 mock 的 getmaxyx）
    class ResizePage(Page):
        def render(self, stdscr): pass
        def on_resize(self, h, w):
            self.new_size = (h, w)

    router.replace(ResizePage)
    stdscr._maxyx = (30, 100)  # 更新 mock 的尺寸
    router.height, router.width = 24, 80  # 设为旧值，让 check_resize 检测到变化
    router.check_resize()
    assert router.current_page.new_size == (30, 100), \
        f"on_resize 应收到新尺寸 (30,100), got {router.current_page.new_size}"
    print("✓ 窗口大小变化检测正常")

def test_global_shortcut():
    """测试全局快捷键"""
    router = PageRouter(stdscr)
    router.push(HomePage)

    called = []
    def handler():
        called.append(True)

    router.register_global_shortcut(ord('x'), "Test", handler)
    router.handle_global_key(ord('x'))
    assert called, "快捷键处理器未被调用"
    print("✓ 全局快捷键注册和触发正常")

if __name__ == "__main__":
    print("运行页面路由系统测试...\n")
    test_push()
    test_pop()
    test_replace()
    test_data_pass()
    test_lifecycle()
    test_resize()
    test_global_shortcut()
    print("\n✅ 所有测试通过")
