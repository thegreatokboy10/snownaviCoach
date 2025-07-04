#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译管理器 - 多语言支持模块
负责语言切换、文本获取、系统语言检测等功能
"""

import json
import os
import locale
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class TranslationManager:
    """翻译管理器类"""
    
    def __init__(self):
        """初始化翻译管理器"""
        self.current_language = "en_US"  # 默认英语
        self.translations = {}
        self.available_languages = {
            "zh_CN": "中文",
            "en_US": "English"
        }
        
        # 获取项目根目录
        self.project_root = Path(__file__).parent
        self.locales_dir = self.project_root / "locales"
        
        # 确保locales目录存在
        self.locales_dir.mkdir(exist_ok=True)
        
        # 检测系统语言
        self.detect_system_language()

        # 加载保存的语言偏好（优先级高于系统语言）
        saved_language = self.load_language_preference()
        if saved_language and saved_language in self.available_languages:
            self.current_language = saved_language

        # 加载翻译文件
        self.load_translations()
    
    def detect_system_language(self):
        """检测系统语言"""
        try:
            # 获取系统语言设置
            system_locale = locale.getdefaultlocale()[0]
            
            if system_locale:
                # 处理不同的语言代码格式
                if system_locale.startswith('zh'):
                    # 中文系统
                    if 'CN' in system_locale or 'Hans' in system_locale:
                        self.current_language = "zh_CN"
                    else:
                        self.current_language = "zh_CN"  # 默认简体中文
                elif system_locale.startswith('en'):
                    # 英文系统
                    self.current_language = "en_US"
                else:
                    # 其他语言默认使用英文
                    self.current_language = "en_US"
            else:
                # 无法检测到系统语言，使用默认英文
                self.current_language = "en_US"
                
        except Exception as e:
            print(f"语言检测失败，使用默认语言: {e}")
            self.current_language = "en_US"
    
    def load_translations(self):
        """加载所有翻译文件"""
        self.translations = {}
        
        for lang_code in self.available_languages.keys():
            lang_file = self.locales_dir / f"{lang_code}.json"
            
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    print(f"已加载语言文件: {lang_code}")
                except Exception as e:
                    print(f"加载语言文件失败 {lang_code}: {e}")
            else:
                print(f"语言文件不存在: {lang_file}")
    
    def set_language(self, language_code: str):
        """设置当前语言"""
        if language_code in self.available_languages:
            self.current_language = language_code
            print(f"语言已切换到: {self.available_languages[language_code]}")
        else:
            print(f"不支持的语言代码: {language_code}")
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    def get_current_language_name(self) -> str:
        """获取当前语言名称"""
        return self.available_languages.get(self.current_language, "Unknown")
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表"""
        return self.available_languages.copy()
    
    def tr(self, key: str, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键，支持点号分隔的嵌套键，如 'app.title'
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        # 获取当前语言的翻译数据
        current_translations = self.translations.get(self.current_language, {})
        
        # 如果当前语言没有翻译，尝试使用英文作为后备
        if not current_translations and self.current_language != "en_US":
            current_translations = self.translations.get("en_US", {})
        
        # 解析嵌套键
        keys = key.split('.')
        value = current_translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 如果找不到翻译，返回键本身
                return key
        
        # 如果值不是字符串，返回键
        if not isinstance(value, str):
            return key
        
        # 格式化字符串
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            # 格式化失败，返回原始字符串
            return value
    
    def has_translation(self, key: str) -> bool:
        """检查是否存在指定键的翻译"""
        current_translations = self.translations.get(self.current_language, {})
        
        keys = key.split('.')
        value = current_translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
        
        return isinstance(value, str)
    
    def get_translation_keys(self) -> list:
        """获取所有翻译键"""
        def extract_keys(data, prefix=""):
            keys = []
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.extend(extract_keys(value, full_key))
                else:
                    keys.append(full_key)
            return keys
        
        current_translations = self.translations.get(self.current_language, {})
        return extract_keys(current_translations)
    
    def save_language_preference(self, language_code: str):
        """保存语言偏好设置"""
        try:
            config_file = self.project_root / "config" / "language.json"
            config_file.parent.mkdir(exist_ok=True)
            
            config = {"language": language_code}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存语言偏好失败: {e}")
    
    def load_language_preference(self) -> Optional[str]:
        """加载语言偏好设置"""
        try:
            config_file = self.project_root / "config" / "language.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("language")
                    
        except Exception as e:
            print(f"加载语言偏好失败: {e}")
        
        return None


# 全局翻译管理器实例
_translation_manager = None


def get_translation_manager() -> TranslationManager:
    """获取全局翻译管理器实例"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def tr(key: str, **kwargs) -> str:
    """
    全局翻译函数
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    return get_translation_manager().tr(key, **kwargs)


def set_language(language_code: str):
    """设置全局语言"""
    get_translation_manager().set_language(language_code)


def get_current_language() -> str:
    """获取当前语言代码"""
    return get_translation_manager().get_current_language()


def get_available_languages() -> Dict[str, str]:
    """获取可用语言列表"""
    return get_translation_manager().get_available_languages()


if __name__ == "__main__":
    # 测试翻译管理器
    tm = TranslationManager()
    
    print(f"当前语言: {tm.get_current_language_name()}")
    print(f"应用标题: {tm.tr('app.title')}")
    print(f"工具栏播放按钮: {tm.tr('toolbar.play')}")
    
    # 切换语言测试
    tm.set_language("zh_CN")
    print(f"切换后语言: {tm.get_current_language_name()}")
    print(f"应用标题: {tm.tr('app.title')}")
    print(f"工具栏播放按钮: {tm.tr('toolbar.play')}")
