# SnowNavi Pose Analyzer - 布局优化指南

## 概述

本文档描述了为优化 SnowNavi Pose Analyzer 导出对话框布局所做的改进，主要目标是充分利用预览区域的空间，减少设置区域的空间占用。

## 问题描述

原始布局存在以下问题：

1. **左侧设置区域过宽**：占用了过多的水平空间
2. **预览区域空间不足**：视频预览区域太小，无法有效展示内容
3. **控件间距过大**：不必要的空白浪费了宝贵的空间
4. **分组框内边距过大**：每个分组框都有过多的内边距

## 优化方案

### 1. 调整主要布局比例

**左侧设置区域宽度优化**：
```python
# 优化前
left_widget.setFixedWidth(450)

# 优化后
left_widget.setFixedWidth(350)  # 减少100px宽度
```

**预览区域扩大**：
```python
# 优化前
self.export_preview_widget.setMinimumSize(350, 250)

# 优化后
self.export_preview_widget.setMinimumSize(500, 420)  # 显著增大预览区域
```

### 2. 紧凑化布局设计

**主容器边距和间距优化**：
```python
# 左侧设置区域
left_main_layout.setContentsMargins(8, 8, 8, 8)  # 减少边距
left_main_layout.setSpacing(6)  # 减少间距

# 右侧预览区域
right_layout.setContentsMargins(8, 8, 8, 8)
right_layout.setSpacing(6)
```

**分组框内部布局优化**：
```python
# 主要分组框
video_layout.setContentsMargins(8, 8, 8, 8)
video_layout.setSpacing(4)

# 次要分组框（水印设置等）
text_watermark_layout.setContentsMargins(6, 6, 6, 6)
text_watermark_layout.setSpacing(3)
```

### 3. 字体和控件尺寸优化

**标题字体减小**：
```python
# 优化前
title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
preview_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))

# 优化后
title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
preview_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
```

**按钮文字简化**：
```python
# 优化前
ModernButton("播放预览", "▶️", "#4CAF50")
ModernButton("刷新预览", "🔄", "#2196F3")

# 优化后
ModernButton("播放", "▶️", "#4CAF50")
ModernButton("刷新", "🔄", "#2196F3")
```

### 4. 预览区域拉伸优化

**添加拉伸因子**：
```python
# 让预览区域占据剩余空间
right_layout.addWidget(self.export_preview_widget, 1)  # 拉伸因子为1
```

## 优化效果

### 空间利用率提升

| 区域 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| 左侧设置区域 | 450px | 350px | -22% |
| 预览区域宽度 | ~450px | ~550px | +22% |
| 预览区域高度 | 250px | 420px | +68% |
| 预览区域面积 | 112,500px² | 231,000px² | +105% |

### 视觉体验改善

1. **更大的视频预览**：用户可以更清楚地看到导出效果
2. **更紧凑的设置面板**：减少滚动需求，提高操作效率
3. **更好的空间平衡**：左右区域比例更合理
4. **更清晰的层次结构**：通过间距优化提升可读性

## 技术实现细节

### 布局管理器优化

1. **QVBoxLayout 和 QHBoxLayout**：
   - 统一设置 `setContentsMargins()` 和 `setSpacing()`
   - 根据内容重要性调整间距大小

2. **QGroupBox 内部布局**：
   - 主要功能组：8px 边距，4-6px 间距
   - 次要功能组：6px 边距，3px 间距

3. **拉伸因子应用**：
   - 预览区域使用拉伸因子 1，占据剩余空间
   - 设置区域固定宽度，保持稳定性

### 响应式设计考虑

1. **最小尺寸保证**：
   - 预览区域设置合理的最小尺寸
   - 确保在小屏幕上仍可用

2. **滚动区域优化**：
   - 左侧设置区域支持垂直滚动
   - 避免内容被截断

## 使用建议

### 开发者

1. **新增控件时**：
   - 遵循现有的间距规范
   - 优先考虑空间效率

2. **布局调整时**：
   - 保持左右区域的比例平衡
   - 测试不同屏幕尺寸下的效果

### 用户

1. **更好的预览体验**：
   - 预览区域现在更大，可以更清楚地看到导出效果
   - 支持更好的视频预览质量

2. **更高效的设置操作**：
   - 设置面板更紧凑，减少滚动需求
   - 控件布局更合理，操作更流畅

## 相关文件

- `pose_detection_app_pyside6.py` - 主应用程序文件（已优化）
- `docs/guides/LAYOUT_OPTIMIZATION_GUIDE.md` - 本文档

## 未来改进方向

1. **自适应布局**：
   - 根据窗口大小动态调整左右区域比例
   - 支持更灵活的布局配置

2. **可折叠面板**：
   - 允许用户折叠不常用的设置组
   - 进一步节省空间

3. **预设布局**：
   - 提供不同的布局模式选择
   - 满足不同用户的使用习惯

---

**更新日期**: 2025-07-04  
**版本**: 1.0  
**作者**: SnowNavi 开发团队
