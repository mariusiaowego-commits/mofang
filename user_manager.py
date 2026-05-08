#!/usr/bin/env python3
"""
用户管理系统 - JSON 存储
支持多用户账户、数据隔离、快速切换
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


# ─── 目录配置 ──────────────────────────────────────────────────────────────

USER_DATA_DIR = Path("~/.config/mofang/users").expanduser()
USER_DATA_FILE = USER_DATA_DIR / "users.json"
ACTIVE_USER_FILE = USER_DATA_DIR / "active_user.txt"


# ─── 用户数据模型 ──────────────────────────────────────────────────────────

@dataclass
class UserProfile:
    """用户档案"""
    id: str
    name: str
    created_at: float = 0.0
    # 训练统计
    total_solves: int = 0
    best_time: float = 0.0      # 秒，0 表示未记录
    avg_time: float = 0.0      # 秒
    ao5_avg: float = 0.0        # AO5 均值
    ao12_avg: float = 0.0      # AO12 均值
    # 偏好设置
    preferred_theme: str = "dark"
    cube_size: int = 3         # 3=三阶
    # 扩展数据（JSON 自由字段）
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        # 过滤掉未知字段
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


# ─── 用户管理器 ──────────────────────────────────────────────────────────

class UserManager:
    """
    用户管理器
    
    职责：
    - 用户列表管理（增删改查）
    - JSON 持久化存储
    - 当前用户会话
    - 数据隔离
    """

    def __init__(self):
        self.users: dict[str, UserProfile] = {}   # id -> UserProfile
        self.active_user: Optional[UserProfile] = None
        self._data_dir = USER_DATA_DIR
        self._ensure_data_dir()
        self._load()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self._data_dir.mkdir(parents=True, exist_ok=True)

    # ── 持久化 ────────────────────────────────────────────────────────────

    def _load(self):
        """从 JSON 文件加载用户数据"""
        if not USER_DATA_FILE.exists():
            return
        
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for user_data in data.get("users", []):
                user = UserProfile.from_dict(user_data)
                self.users[user.id] = user
            
            # 加载上次活跃用户
            if ACTIVE_USER_FILE.exists():
                active_id = ACTIVE_USER_FILE.read_text().strip()
                self.active_user = self.users.get(active_id)
                
        except (json.JSONDecodeError, IOError) as e:
            # 损坏的文件，使用空状态
            pass

    def save(self):
        """保存用户数据到 JSON 文件"""
        data = {
            "users": [u.to_dict() for u in self.users.values()]
        }
        
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 保存活跃用户
        if self.active_user:
            ACTIVE_USER_FILE.write_text(self.active_user.id)
        elif ACTIVE_USER_FILE.exists():
            ACTIVE_USER_FILE.unlink()

    # ── 用户 CRUD ────────────────────────────────────────────────────────

    def create_user(self, name: str) -> UserProfile:
        """创建新用户，返回用户档案"""
        import time
        import uuid
        
        # 生成唯一 ID
        user_id = uuid.uuid4().hex[:8]
        
        user = UserProfile(
            id=user_id,
            name=name,
            created_at=time.time(),
        )
        self.users[user_id] = user
        self.save()
        return user

    def delete_user(self, user_id: str) -> bool:
        """删除用户，返回是否成功"""
        if user_id not in self.users:
            return False
        
        # 不能删除当前活跃用户
        if self.active_user and self.active_user.id == user_id:
            self.active_user = None
        
        del self.users[user_id]
        self.save()
        return True

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """根据 ID 获取用户"""
        return self.users.get(user_id)

    def list_users(self) -> list[UserProfile]:
        """列出所有用户（按创建时间排序）"""
        return sorted(self.users.values(), key=lambda u: u.created_at)

    def set_active_user(self, user_id: str) -> bool:
        """设置当前活跃用户"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        self.active_user = user
        self.save()
        return True

    def clear_active_user(self):
        """清除当前活跃用户（退出登录）"""
        self.active_user = None
        if ACTIVE_USER_FILE.exists():
            ACTIVE_USER_FILE.unlink()

    # ── 用户统计更新 ──────────────────────────────────────────────────────

    def update_stats(self, user_id: str, 
                     solve_time: float,
                     update_best: bool = True,
                     update_ao5: bool = False,
                     update_ao12: bool = False,
                     ao5_value: Optional[float] = None,
                     ao12_value: Optional[float] = None):
        """更新用户训练统计"""
        user = self.users.get(user_id)
        if not user:
            return
        
        user.total_solves += 1
        
        if update_best and (user.best_time == 0 or solve_time < user.best_time):
            user.best_time = solve_time
        
        # 简单滚动平均
        if user.avg_time == 0:
            user.avg_time = solve_time
        else:
            user.avg_time = (user.avg_time * (user.total_solves - 1) + solve_time) / user.total_solves
        
        if ao5_value is not None:
            user.ao5_avg = ao5_value
        
        if ao12_value is not None:
            user.ao12_avg = ao12_value
        
        self.save()

    def update_preference(self, user_id: str, theme: Optional[str] = None, 
                          cube_size: Optional[int] = None):
        """更新用户偏好"""
        user = self.users.get(user_id)
        if not user:
            return
        
        if theme is not None:
            user.preferred_theme = theme
        
        if cube_size is not None:
            user.cube_size = cube_size
        
        self.save()


# ─── 全局单例 ──────────────────────────────────────────────────────────────

_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
    """获取用户管理器单例"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
