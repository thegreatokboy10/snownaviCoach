#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一样式 - 验证在不同系统主题下的样式一致性
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout,
    QGroupBox, QCheckBox, QLabel, QComboBox, QLineEdit, QSlider,
    QProgressBar, QPushButton, QTabWidget, QWidget, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class StyleTestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("样式测试对话框")
        self.setFixedSize(600, 500)
        
        # 应用统一样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                color: #2c3e50;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #34495e;
                background: white;
            }
            QCheckBox {
                color: #2c3e50;
                font-size: 11px;
                spacing: 8px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #bdc3c7;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #3498db;
                border: 2px solid #2980b9;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #3498db;
            }
            QLabel {
                color: #2c3e50;
                font-size: 11px;
                background: transparent;
            }
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 6px 12px;
                background: white;
                color: #2c3e50;
                font-size: 11px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox:focus {
                border: 2px solid #2980b9;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px 12px;
                background: white;
                color: #2c3e50;
                font-size: 11px;
                min-height: 20px;
            }
            QLineEdit:hover {
                border: 2px solid #3498db;
            }
            QLineEdit:focus {
                border: 2px solid #2980b9;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 2px solid #2980b9;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 6px;
                background: #ecf0f1;
                text-align: center;
                color: #2c3e50;
                font-size: 11px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 4px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2980b9;
            }
            QTabWidget::pane {
                border: 2px solid #ddd;
                border-radius: 8px;
                background: white;
                color: #2c3e50;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 2px solid #ddd;
                padding: 10px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #2c3e50;
                font-size: 11px;
                font-weight: 500;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid white;
                color: #2980b9;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #e8f4fd;
                color: #2980b9;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("🎨 样式统一性测试")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建标签页
        tabs = QTabWidget()
        
        # 第一个标签页 - 基础控件
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        # 分组框
        group1 = QGroupBox("基础控件测试")
        group1_layout = QVBoxLayout(group1)
        
        # 复选框
        cb1 = QCheckBox("选项1（已选中）")
        cb1.setChecked(True)
        cb2 = QCheckBox("选项2（未选中）")
        group1_layout.addWidget(cb1)
        group1_layout.addWidget(cb2)
        
        # 下拉框
        combo = QComboBox()
        combo.addItems(["选项A", "选项B", "选项C"])
        group1_layout.addWidget(QLabel("下拉选择:"))
        group1_layout.addWidget(combo)
        
        # 输入框
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("请输入文本...")
        group1_layout.addWidget(QLabel("文本输入:"))
        group1_layout.addWidget(line_edit)
        
        tab1_layout.addWidget(group1)
        
        # 第二个标签页 - 高级控件
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        
        group2 = QGroupBox("高级控件测试")
        group2_layout = QVBoxLayout(group2)
        
        # 滑块
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        group2_layout.addWidget(QLabel("滑块控制:"))
        group2_layout.addWidget(slider)
        
        # 进度条
        progress = QProgressBar()
        progress.setValue(75)
        group2_layout.addWidget(QLabel("进度显示:"))
        group2_layout.addWidget(progress)
        
        # 按钮
        button_layout = QHBoxLayout()
        btn1 = QPushButton("确定")
        btn2 = QPushButton("取消")
        btn3 = QPushButton("应用")
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)
        button_layout.addWidget(btn3)
        group2_layout.addLayout(button_layout)
        
        tab2_layout.addWidget(group2)
        
        tabs.addTab(tab1, "基础控件")
        tabs.addTab(tab2, "高级控件")
        layout.addWidget(tabs)
        
        # 说明文字
        info_label = QLabel(
            "此对话框测试统一样式在不同系统主题下的表现。\n"
            "样式应该保持一致，不受系统日间/夜间模式影响。"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)

class StyleTestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SnowNavi Pose Analyzer - 样式测试")
        self.setMinimumSize(800, 600)
        
        # 应用主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                color: #2c3e50;
            }
            QWidget {
                background: transparent;
                color: #2c3e50;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = QLabel("🎨 样式统一性测试工具")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 20px;")
        layout.addWidget(title)
        
        # 说明
        description = QLabel(
            "此工具用于测试应用程序在不同系统主题（日间/夜间模式）下的样式一致性。\n"
            "点击下方按钮打开测试对话框，验证样式是否保持统一。"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 10px;")
        layout.addWidget(description)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        test_btn = QPushButton("🧪 打开样式测试对话框")
        test_btn.clicked.connect(self.open_test_dialog)
        
        export_btn = QPushButton("📤 模拟导出对话框")
        export_btn.clicked.connect(self.open_export_dialog)
        
        config_btn = QPushButton("⚙️ 模拟配置对话框")
        config_btn.clicked.connect(self.open_config_dialog)
        
        button_layout.addWidget(test_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(config_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def open_test_dialog(self):
        dialog = StyleTestDialog(self)
        dialog.exec()
    
    def open_export_dialog(self):
        # 这里可以打开实际的导出对话框进行测试
        print("打开导出对话框测试")
    
    def open_config_dialog(self):
        # 这里可以打开实际的配置对话框进行测试
        print("打开配置对话框测试")

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("SnowNavi Pose Analyzer - Style Test")
    app.setApplicationVersion("1.0")
    
    window = StyleTestMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
