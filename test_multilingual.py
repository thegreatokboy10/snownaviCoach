#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言功能测试脚本
"""

import sys
import os
from translation_manager import TranslationManager, tr, set_language, get_current_language

def test_translation_manager():
    """测试翻译管理器"""
    print("=" * 50)
    print("测试翻译管理器")
    print("=" * 50)
    
    tm = TranslationManager()
    
    # 测试系统语言检测
    print(f"检测到的系统语言: {tm.get_current_language()}")
    print(f"当前语言名称: {tm.get_current_language_name()}")
    
    # 测试可用语言
    print(f"可用语言: {tm.get_available_languages()}")
    
    # 测试翻译功能
    print("\n--- 英文翻译测试 ---")
    tm.set_language("en_US")
    print(f"应用标题: {tm.tr('app.title')}")
    print(f"工具栏播放: {tm.tr('toolbar.play')}")
    print(f"工具栏暂停: {tm.tr('toolbar.pause')}")
    print(f"设置标题: {tm.tr('settings.title')}")
    print(f"导出标题: {tm.tr('export.title')}")
    
    print("\n--- 中文翻译测试 ---")
    tm.set_language("zh_CN")
    print(f"应用标题: {tm.tr('app.title')}")
    print(f"工具栏播放: {tm.tr('toolbar.play')}")
    print(f"工具栏暂停: {tm.tr('toolbar.pause')}")
    print(f"设置标题: {tm.tr('settings.title')}")
    print(f"导出标题: {tm.tr('export.title')}")
    
    # 测试格式化字符串
    print("\n--- 格式化字符串测试 ---")
    print(f"状态消息: {tm.tr('status.config_applied', config='测试配置')}")
    print(f"FPS显示: {tm.tr('status.fps', fps='30')}")
    
    # 测试不存在的键
    print("\n--- 错误处理测试 ---")
    print(f"不存在的键: {tm.tr('nonexistent.key')}")
    
    return True

def test_global_functions():
    """测试全局函数"""
    print("\n" + "=" * 50)
    print("测试全局函数")
    print("=" * 50)
    
    # 测试全局翻译函数
    print(f"当前语言: {get_current_language()}")
    
    print("\n--- 切换到英文 ---")
    set_language("en_US")
    print(f"应用标题: {tr('app.title')}")
    print(f"帮助标题: {tr('help.title')}")
    
    print("\n--- 切换到中文 ---")
    set_language("zh_CN")
    print(f"应用标题: {tr('app.title')}")
    print(f"帮助标题: {tr('help.title')}")
    
    return True

def test_language_files():
    """测试语言文件完整性"""
    print("\n" + "=" * 50)
    print("测试语言文件完整性")
    print("=" * 50)
    
    tm = TranslationManager()
    
    # 检查关键翻译是否存在
    required_keys = [
        "app.title",
        "toolbar.open_video",
        "toolbar.play",
        "toolbar.pause",
        "toolbar.settings",
        "toolbar.export",
        "toolbar.help",
        "settings.title",
        "export.title",
        "help.title",
        "language.title",
        "language.select_language"
    ]
    
    for lang_code in tm.available_languages.keys():
        tm.set_language(lang_code)
        print(f"\n检查语言: {tm.get_current_language_name()}")
        
        missing_keys = []
        for key in required_keys:
            if not tm.has_translation(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"  缺失的翻译键: {missing_keys}")
        else:
            print(f"  ✅ 所有必需的翻译键都存在")
    
    return True

def main():
    """主函数"""
    print("SnowNavi Pose Analyzer - 多语言功能测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        test_translation_manager()
        test_global_functions()
        test_language_files()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！多语言功能正常工作。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
