#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量替换硬编码文本的脚本
"""

import re
import os

def batch_replace_in_file(file_path, replacements):
    """批量替换文件中的文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_text, new_text in replacements:
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已更新文件: {file_path}")
            return True
        else:
            print(f"文件无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"处理文件时出错 {file_path}: {e}")
        return False

def main():
    """主函数"""
    file_path = "pose_detection_app_pyside6.py"
    
    # 定义需要替换的文本对
    replacements = [
        # 导出对话框相关
        ('title_label = QLabel("💾 导出视频")', 'title_label = QLabel("💾 " + tr("export.title"))'),
        ('preview_title = QLabel("🎬 预览效果")', 'preview_title = QLabel("🎬 " + tr("export.preview_title"))'),
        ('self.export_preview_widget.setText("🎬 点击播放预览\\n查看导出效果")', 'self.export_preview_widget.setText(tr("video_widget.preview_text"))'),
        ('self.preview_play_btn = ModernButton("播放", "▶️", "#4CAF50")', 'self.preview_play_btn = ModernButton(tr("toolbar.play"), "▶️", "#4CAF50")'),
        ('self.preview_refresh_btn = ModernButton("刷新", "🔄", "#2196F3")', 'self.preview_refresh_btn = ModernButton(tr("export.refresh"), "🔄", "#2196F3")'),
        
        # 导出设置组
        ('video_group = QGroupBox("选择要导出的视频")', 'video_group = QGroupBox(tr("export.video_selection"))'),
        ('self.export_video1_cb = QCheckBox("导出视频1（带姿态检测）")', 'self.export_video1_cb = QCheckBox(tr("export.export_video1"))'),
        ('self.export_video2_cb = QCheckBox("导出视频2（带姿态检测）")', 'self.export_video2_cb = QCheckBox(tr("export.export_video2"))'),
        ('settings_group = QGroupBox("导出设置")', 'settings_group = QGroupBox(tr("export.output_settings"))'),
        ('quality_layout.addWidget(QLabel("视频质量:"))', 'quality_layout.addWidget(QLabel(tr("export.quality")))'),
        ('fps_layout.addWidget(QLabel("输出帧率:"))', 'fps_layout.addWidget(QLabel(tr("export.output_fps")))'),
        
        # 旋转设置
        ('rotation_group = QGroupBox("旋转设置")', 'rotation_group = QGroupBox(tr("export.rotation_settings"))'),
        ('video1_rotation_layout.addWidget(QLabel("视频1旋转:"))', 'video1_rotation_layout.addWidget(QLabel(tr("export.video1_rotation")))'),
        ('video2_rotation_layout.addWidget(QLabel("视频2旋转:"))', 'video2_rotation_layout.addWidget(QLabel(tr("export.video2_rotation")))'),
        
        # 水印设置
        ('watermark_group = QGroupBox("水印设置")', 'watermark_group = QGroupBox(tr("export.watermark_settings"))'),
        ('self.watermark_enabled_cb = QCheckBox("启用水印")', 'self.watermark_enabled_cb = QCheckBox(tr("export.enable_watermark"))'),
        ('text_watermark_group = QGroupBox("文字水印")', 'text_watermark_group = QGroupBox(tr("export.text_watermark"))'),
        ('self.text_watermark_enabled_cb = QCheckBox("启用文字水印")', 'self.text_watermark_enabled_cb = QCheckBox(tr("export.text_watermark"))'),
        ('text_layout.addWidget(QLabel("水印文本:"))', 'text_layout.addWidget(QLabel(tr("export.watermark_text")))'),
        ('self.watermark_text_input.setPlaceholderText("输入水印文本...")', 'self.watermark_text_input.setPlaceholderText(tr("export.watermark_text_placeholder"))'),
        ('text_position_layout.addWidget(QLabel("位置:"))', 'text_position_layout.addWidget(QLabel(tr("export.text_position")))'),
        
        # 图片水印
        ('image_watermark_group = QGroupBox("图片水印")', 'image_watermark_group = QGroupBox(tr("export.image_watermark"))'),
        ('self.image_watermark_enabled_cb = QCheckBox("启用图片水印")', 'self.image_watermark_enabled_cb = QCheckBox(tr("export.image_watermark"))'),
        ('image_layout.addWidget(QLabel("水印图片:"))', 'image_layout.addWidget(QLabel(tr("export.watermark_image")))'),
        ('image_position_layout.addWidget(QLabel("位置:"))', 'image_position_layout.addWidget(QLabel(tr("export.image_position")))'),
        
        # 通用设置
        ('common_group = QGroupBox("通用设置")', 'common_group = QGroupBox(tr("export.common_settings"))'),
        ('opacity_layout.addWidget(QLabel("透明度:"))', 'opacity_layout.addWidget(QLabel(tr("export.opacity")))'),
        ('size_layout.addWidget(QLabel("大小:"))', 'size_layout.addWidget(QLabel(tr("export.size")))'),
        
        # 进度显示
        ('progress_group = QGroupBox("导出进度")', 'progress_group = QGroupBox(tr("export.progress"))'),
        ('self.frame_progress_label = QLabel("帧: 0 / 0")', 'self.frame_progress_label = QLabel(tr("export.frame_progress", current=0, total=0))'),
        ('self.eta_label = QLabel("预计剩余: --")', 'self.eta_label = QLabel(tr("export.eta", time="--"))'),
        
        # 按钮
        ('self.export_start_btn = ModernButton("开始导出", "", "#4CAF50")', 'self.export_start_btn = ModernButton(tr("export.start_export"), "", "#4CAF50")'),
        ('self.export_cancel_btn = ModernButton("取消导出", "", "#F44336")', 'self.export_cancel_btn = ModernButton(tr("export.cancel_export"), "", "#F44336")'),
        ('close_btn = ModernButton("关闭", "", "#607D8B")', 'close_btn = ModernButton(tr("settings.close"), "", "#607D8B")'),
        
        # 性能监控对话框
        ('title_label = QLabel("📊 性能监控")', 'title_label = QLabel("📊 " + tr("performance.monitoring"))'),
        ('info_label = QLabel("性能监控功能正在开发中...")', 'info_label = QLabel(tr("performance.developing"))'),
        
        # 帮助对话框
        ('title_label = QLabel("❓ 使用帮助")', 'title_label = QLabel("❓ " + tr("help.usage_help"))'),
        
        # 设置对话框
        ('title_label = QLabel("⚙️ 完整配置管理器")', 'title_label = QLabel("⚙️ " + tr("settings.title"))'),
        
        # 错误消息
        ('print(f"跳转视频1位置时出错: {e}")', 'print(tr("messages.seek_video1_error", error=str(e)))'),
        ('print(f"跳转视频2位置时出错: {e}")', 'print(tr("messages.seek_video2_error", error=str(e)))'),
        ('print(f"保存配置文件时出错: {e}")', 'print(tr("messages.save_config_error", error=str(e)))'),
        ('print(f"加载配置文件时出错: {e}")', 'print(tr("messages.load_config_error", error=str(e)))'),
        ('print(f"应用预设配置时出错: {e}")', 'print(tr("messages.apply_preset_error", error=str(e)))'),
        ('print(f"应用工具栏配置时出错: {e}")', 'print(tr("messages.apply_toolbar_config_error", error=str(e)))'),
        ('print(f"应用完整配置时出错: {e}")', 'print(tr("messages.apply_complete_config_error", error=str(e)))'),
        ('print(f"语言切换失败: {e}")', 'print(tr("messages.language_switch_failed", error=str(e)))'),
    ]
    
    # 执行批量替换
    success = batch_replace_in_file(file_path, replacements)
    
    if success:
        print("批量替换完成！")
    else:
        print("批量替换失败或无需更新。")

if __name__ == "__main__":
    main()
