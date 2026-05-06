#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔方训练记录管理系统
支持多用户，记录训练数据，统计分析
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import statistics

# 用纯Python JSON替代PyYAML，减少外部依赖
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / "training" / "users"

def init_user_dir():
    """初始化用户目录"""
    USERS_DIR.mkdir(parents=True, exist_ok=True)

def list_users():
    """列出所有用户"""
    if not USERS_DIR.exists():
        return []
    return [f.stem for f in USERS_DIR.glob("*.json")]

def load_user(username):
    """加载用户数据"""
    user_file = USERS_DIR / f"{username}.json"
    if not user_file.exists():
        # 兼容旧的yaml文件
        old_file = USERS_DIR / f"{username}.yaml"
        if old_file.exists():
            import yaml
            with open(old_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            # 自动迁移到json
            save_user(username, data)
            old_file.unlink()
            return data
        return None
    with open(user_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user(username, data):
    """保存用户数据（用JSON替代YAML）"""
    user_file = USERS_DIR / f"{username}.json"
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_user(username, profile_data):
    """创建新用户"""
    user = {
        "profile": {
            "name": username,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "current_level": profile_data.get("level", "入门"),
            "target_level": profile_data.get("target", "30秒内"),
            "daily_goal": profile_data.get("daily_goal", 20),
            "weekly_goal": profile_data.get("weekly_goal", 5),
        },
        "knowledge": {
            "method": profile_data.get("method", "层先法"),
            "cross_level": profile_data.get("cross_level", "初级"),
            "f2l_level": profile_data.get("f2l_level", "初级"),
            "oll_level": profile_data.get("oll_level", "初级"),
            "pll_level": profile_data.get("pll_level", "初级"),
            "formulas_learned": {
                "f2l": [],
                "oll": [],
                "pll": []
            }
        },
        "personal_bests": {
            "single": 999.99,
            "ao5": 999.99,
            "ao12": 999.99,
            "ao100": 999.99
        },
        "milestones": [],
        "training_log": []
    }
    save_user(username, user)
    return user

def add_training_session(username, session_data):
    """添加训练会话"""
    user = load_user(username)
    if not user:
        return False
    
    session_id = f"S{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    solves = session_data.get("solves", [])
    if solves:
        times = [s["time"] for s in solves if s.get("penalty", "OK") not in ["DNF", "dns"]]
        if times:
            stats = {
                "count": len(times),
                "best": min(times),
                "worst": max(times),
                "mean": round(statistics.mean(times), 2),
            }
            
            if len(times) >= 5:
                sorted_times = sorted(times)
                ao5_times = sorted_times[1:-1]
                stats["ao5"] = round(statistics.mean(ao5_times), 2)
            
            if len(times) >= 12:
                sorted_times = sorted(times)
                ao12_times = sorted_times[1:-1]
                stats["ao12"] = round(statistics.mean(ao12_times), 2)
            
            if len(times) >= 100:
                sorted_times = sorted(times)
                ao100_times = sorted_times[5:-5]
                stats["ao100"] = round(statistics.mean(ao100_times), 2)
            
            if stats.get("best", 999) < user["personal_bests"]["single"]:
                user["personal_bests"]["single"] = stats["best"]
                add_milestone(username, f"PB刷新！单次 {stats['best']}s", stats["best"])
            
            if stats.get("ao5", 999) < user["personal_bests"]["ao5"]:
                user["personal_bests"]["ao5"] = stats["ao5"]
            
            if stats.get("ao12", 999) < user["personal_bests"]["ao12"]:
                user["personal_bests"]["ao12"] = stats["ao12"]
            
            session_data["statistics"] = stats
    
    session = {
        "session_id": session_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": session_data.get("duration", 30),
        "focus_area": session_data.get("focus", []),
        "solves": solves,
        "notes": session_data.get("notes", "")
    }
    
    user["training_log"].append(session)
    save_user(username, user)
    return session

def add_milestone(username, achievement, time=None):
    """添加里程碑"""
    user = load_user(username)
    if not user:
        return False
    
    milestone = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "achievement": achievement,
        "time": time
    }
    user["milestones"].append(milestone)
    save_user(username, user)
    return True

def get_user_stats(username):
    """获取用户统计信息"""
    user = load_user(username)
    if not user:
        return None
    
    total_solves = sum(len(s.get("solves", [])) for s in user["training_log"])
    
    recent_solves = []
    for session in user["training_log"][-10:]:  # 最近10次会话
        for solve in session.get("solves", []):
            if solve.get("penalty", "OK") not in ["DNF", "dns"]:
                recent_solves.append(solve["time"])
    
    stats = {
        "profile": user["profile"],
        "personal_bests": user["personal_bests"],
        "total_sessions": len(user["training_log"]),
        "total_solves": total_solves,
        "milestones": len(user["milestones"]),
    }
    
    if len(recent_solves) >= 5:
        sorted_times = sorted(recent_solves)
        ao5 = statistics.mean(sorted_times[1:-1][:3]) if len(sorted_times) >= 5 else None
        stats["recent_ao5"] = round(ao5, 2) if ao5 else None
    
    return stats

def print_progress_report(username):
    """打印进度报告"""
    user = load_user(username)
    if not user:
        print(f"用户 {username} 不存在")
        return
    
    stats = get_user_stats(username)
    
    print("=" * 50)
    print(f"📊 {username} 的训练进度报告")
    print("=" * 50)
    print(f"🎯 当前水平: {user['profile']['current_level']}")
    print(f"🏆 目标水平: {user['profile']['target_level']}")
    print(f"📅 开始日期: {user['profile']['start_date']}")
    print()
    print(f"⏱️  个人最佳:")
    print(f"   单次: {user['personal_bests']['single']}s")
    print(f"   AO5:  {user['personal_bests']['ao5']}s")
    print(f"   AO12: {user['personal_bests']['ao12']}s")
    print()
    print(f"📈 训练统计:")
    print(f"   训练次数: {stats['total_sessions']} 次")
    print(f"   还原次数: {stats['total_solves']} 次")
    print()
    print(f"🎓 已掌握公式:")
    learned = user['knowledge']['formulas_learned']
    print(f"   F2L: {len(learned['f2l'])}/41")
    print(f"   OLL: {len(learned['oll'])}/57")
    print(f"   PLL: {len(learned['pll'])}/21")
    print()
    print("🏅 里程碑:")
    for m in user["milestones"][-5:]:
        time_str = f" ({m['time']}s)" if m['time'] else ""
        print(f"   [{m['date']}] {m['achievement']}{time_str}")
    print("=" * 50)

def interactive_mode():
    """交互模式"""
    init_user_dir()
    
    while True:
        print("\n" + "=" * 50)
        print("🎲 魔方训练管理系统")
        print("=" * 50)
        print("1. 用户列表")
        print("2. 创建新用户")
        print("3. 查看用户报告")
        print("4. 记录训练")
        print("5. 添加里程碑")
        print("0. 退出")
        print("-" * 50)
        
        choice = input("请选择: ").strip()
        
        if choice == "1":
            users = list_users()
            if users:
                print("\n📋 用户列表:")
                for u in users:
                    print(f"  - {u}")
            else:
                print("\n暂无用户")
        
        elif choice == "2":
            print("\n🆕 创建新用户")
            username = input("用户名: ").strip()
            if not username:
                print("用户名不能为空")
                continue
            
            if load_user(username):
                print(f"用户 {username} 已存在")
                continue
            
            print("\n请回答几个问题以定制你的训练计划:")
            level = input("当前水平 (入门/进阶/熟练/高手): ").strip() or "入门"
            target = input("目标水平 (1分钟/45秒/30秒/20秒/15秒): ").strip() or "30秒"
            method = input("使用方法 (层先法/CFOP): ").strip() or "层先法"
            
            profile = {
                "level": level,
                "target": target,
                "method": method
            }
            
            create_user(username, profile)
            print(f"\n✅ 用户 {username} 创建成功！")
            add_milestone(username, "开始魔方学习之旅！")
        
        elif choice == "3":
            users = list_users()
            if not users:
                print("\n暂无用户，请先创建")
                continue
            
            print("\n👤 选择用户:")
            for i, u in enumerate(users, 1):
                print(f"  {i}. {u}")
            
            idx = int(input("输入编号: ")) - 1
            if 0 <= idx < len(users):
                print_progress_report(users[idx])
        
        elif choice == "4":
            users = list_users()
            if not users:
                print("\n暂无用户，请先创建")
                continue
            
            print("\n👤 选择用户:")
            for i, u in enumerate(users, 1):
                print(f"  {i}. {u}")
            
            idx = int(input("输入编号: ")) - 1
            if 0 <= idx < len(users):
                username = users[idx]
                
                print(f"\n⏱️  记录 {username} 的训练")
                print("输入每次还原的时间（秒），空行结束，输入dnf表示未完成")
                
                solves = []
                count = 1
                while True:
                    time_input = input(f"  #{count}: ").strip()
                    if not time_input:
                        break
                    
                    if time_input.lower() == "dnf":
                        solves.append({"time": 999, "penalty": "DNF"})
                    else:
                        try:
                            time_val = float(time_input)
                            solves.append({"time": time_val, "penalty": "OK"})
                            count += 1
                        except ValueError:
                            print("  无效输入，请输入数字或dnf")
                
                if solves:
                    focus = input("\n训练重点 (用逗号分隔): ").strip().split(",")
                    notes = input("备注: ").strip()
                    
                    session = add_training_session(username, {
                        "solves": solves,
                        "focus": [f.strip() for f in focus if f.strip()],
                        "notes": notes
                    })
                    
                    print(f"\n✅ 训练记录已保存！")
                    if "statistics" in session:
                        stats = session["statistics"]
                        print(f"   还原次数: {stats['count']}")
                        print(f"   最佳单次: {stats['best']}s")
                        print(f"   平均时间: {stats['mean']}s")
                        if "ao5" in stats:
                            print(f"   AO5: {stats['ao5']}s")
                else:
                    print("\n未记录任何数据")
        
        elif choice == "5":
            users = list_users()
            if not users:
                print("\n暂无用户，请先创建")
                continue
            
            print("\n👤 选择用户:")
            for i, u in enumerate(users, 1):
                print(f"  {i}. {u}")
            
            idx = int(input("输入编号: ")) - 1
            if 0 <= idx < len(users):
                username = users[idx]
                achievement = input("\n里程碑内容: ").strip()
                time_input = input("相关时间（可选）: ").strip()
                time_val = float(time_input) if time_input else None
                
                add_milestone(username, achievement, time_val)
                print("✅ 里程碑已添加！")
        
        elif choice == "0":
            print("\n👋 再见！")
            break
        
        else:
            print("\n❌ 无效选择")

if __name__ == "__main__":
    interactive_mode()
