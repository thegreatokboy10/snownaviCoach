# SnowNavi Pose Analyzer - 样式统一化指南

## 概述

本文档描述了为确保 SnowNavi Pose Analyzer 在不同系统主题（日间/夜间模式）下保持一致外观所做的样式统一化改进。

## 问题描述

在系统自动切换日间/夜间模式时，应用程序的某些对话框和控件可能会出现样式不一致的问题，包括：

- 背景颜色随系统主题变化
- 控件边框和颜色不统一
- 文字颜色在不同主题下可读性差异
- 复选框、下拉框等控件样式不一致

## 解决方案

### 1. 主窗口样式强化

在 `pose_detection_app_pyside6.py` 中为主窗口添加了更强制的样式设置：

```css
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f8f9fa, stop:1 #e9ecef);
    color: #2c3e50;
}
QWidget {
    background: transparent;
    color: #2c3e50;
}
/* 更多统一样式... */
```

### 2. 导出对话框样式统一

为导出对话框添加了完整的样式定义，确保所有控件在不同系统主题下保持一致：

- **QGroupBox**: 统一的分组框样式，白色背景，圆角边框
- **QCheckBox**: 自定义复选框指示器，蓝色选中状态
- **QComboBox**: 统一的下拉框样式，悬停和焦点效果
- **QLineEdit**: 一致的输入框样式
- **QSlider**: 自定义滑块外观
- **QProgressBar**: 统一的进度条样式

### 3. 配置管理器对话框样式

为配置管理器对话框应用了相同的样式规范，包括：

- 标签页（QTabWidget）的统一外观
- 控件间距和颜色的一致性
- 悬停和选中状态的视觉反馈

### 4. 按钮样式修复

移除了不被Qt支持的CSS `transform` 属性，避免控制台警告：

```css
/* 修复前 */
QPushButton:hover {
    transform: translateY(-1px);  /* 不支持 */
}

/* 修复后 */
QPushButton:hover {
    background: qlineargradient(...);  /* 仅使用颜色变化 */
}
```

## 样式规范

### 颜色方案

- **主背景**: 渐变色 `#f8f9fa` 到 `#e9ecef`
- **主文字**: `#2c3e50`
- **次要文字**: `#7f8c8d`
- **强调色**: `#3498db` (蓝色)
- **悬停色**: `#2980b9` (深蓝色)
- **边框色**: `#ddd` (浅灰色)

### 控件规范

1. **分组框 (QGroupBox)**
   - 白色背景
   - 2px 圆角边框
   - 标题左对齐，带内边距

2. **复选框 (QCheckBox)**
   - 16x16px 指示器
   - 3px 圆角
   - 选中时蓝色背景，白色勾选图标

3. **下拉框 (QComboBox)**
   - 白色背景
   - 6px 圆角
   - 悬停时蓝色边框

4. **输入框 (QLineEdit)**
   - 白色背景
   - 6px 圆角
   - 焦点时深蓝色边框

5. **按钮 (QPushButton)**
   - 蓝色渐变背景
   - 8px 圆角
   - 白色文字，中等字重

## 测试工具

创建了 `test_unified_styles.py` 测试工具，用于验证样式在不同系统主题下的一致性：

```bash
# 运行样式测试
source pose_detection_env/bin/activate
python tests/test_unified_styles.py
```

## 使用建议

### 开发者

1. **新增对话框时**，复制现有的样式定义确保一致性
2. **避免使用** Qt 不支持的 CSS 属性
3. **测试不同主题**，确保在日间/夜间模式下都正常显示

### 用户

1. 应用程序现在会**忽略系统主题设置**，保持一致的浅色主题
2. 所有对话框和控件都有**统一的外观**
3. 在系统切换日间/夜间模式时，应用程序外观**保持不变**

## 技术细节

### 样式优先级

通过在对话框级别设置 `setStyleSheet()`，确保样式优先级高于系统默认主题：

```python
self.export_dialog.setStyleSheet("""
    /* 完整的样式定义 */
""")
```

### 兼容性

- **Qt版本**: PySide6 6.9.1+
- **系统**: macOS, Windows, Linux
- **主题**: 独立于系统主题，自定义外观

## 维护说明

1. **样式更新**时，需要同时更新所有对话框的样式定义
2. **新增控件**时，参考现有样式规范
3. **定期测试**不同系统和主题下的显示效果

## 相关文件

- `pose_detection_app_pyside6.py` - 主应用程序文件
- `tests/test_unified_styles.py` - 样式测试工具
- `docs/guides/STYLE_UNIFICATION_GUIDE.md` - 本文档

---

**更新日期**: 2025-07-04  
**版本**: 1.0  
**作者**: SnowNavi 开发团队
