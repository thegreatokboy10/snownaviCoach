#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业姿态检测应用 - 基于PySide6
支持智能视频加载、关节点筛选、实时姿态检测等功能
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSlider, QComboBox, QCheckBox,
    QScrollArea, QFrame, QSplitter, QGroupBox, QProgressBar, QTextEdit,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QSpacerItem,
    QSizePolicy, QToolBar, QStatusBar, QTabWidget, QLineEdit
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QSize, QPropertyAnimation, QEasingCurve,
    QRect, QPoint
)
from PySide6.QtGui import (
    QPixmap, QIcon, QFont, QPalette, QColor, QAction, QPainter,
    QBrush, QPen, QLinearGradient, QImage
)

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import threading
import time
import queue

class ModernButton(QPushButton):
    """现代化按钮样式"""
    def __init__(self, text="", icon_text="", color="#2196F3", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text} {text}" if icon_text else text)
        self.setMinimumHeight(40)
        self.setFont(QFont("Arial", 10, QFont.Weight.Medium))
        
        # 设置现代化样式
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self.darken_color(color)});
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.lighten_color(color)}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: {self.darken_color(color)};
            }}
            QPushButton:disabled {{
                background: #CCCCCC;
                color: #666666;
            }}
        """)

    def darken_color(self, hex_color):
        """使颜色变暗"""
        color_map = {
            "#2196F3": "#1976D2",
            "#4CAF50": "#388E3C",
            "#FF9800": "#F57C00",
            "#F44336": "#D32F2F",
            "#9C27B0": "#7B1FA2",
            "#607D8B": "#455A64"
        }
        return color_map.get(hex_color, hex_color)

    def lighten_color(self, hex_color):
        """使颜色变亮"""
        color_map = {
            "#2196F3": "#42A5F5",
            "#4CAF50": "#66BB6A",
            "#FF9800": "#FFB74D",
            "#F44336": "#EF5350",
            "#9C27B0": "#BA68C8",
            "#607D8B": "#78909C"
        }
        return color_map.get(hex_color, hex_color)

class VideoWidget(QLabel):
    """专业视频显示控件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
                border: 2px solid #ddd;
                border-radius: 12px;
                color: #666;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("🎬 点击工具栏打开视频文件\n支持 MP4, AVI, MOV 等格式")
        self.setScaledContents(True)

class PoseDetectionApp(QMainWindow):
    """专业姿态检测应用主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 应用状态
        self.mediapipe_initialized = False
        self.cap1 = None
        self.cap2 = None
        self.video2_loaded = False
        self.is_playing1 = False
        self.is_playing2 = False
        self.current_frame1 = None
        self.current_frame2 = None
        self.current_frame_pos1 = 0
        self.current_frame_pos2 = 0
        self.total_frames1 = 0
        self.total_frames2 = 0
        self.fps1 = 30
        self.fps2 = 30

        # 播放定时器
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.update_frame)
        self.play_timer_interval = 33  # 约30fps
        
        # 姿态检测设置
        self.landmark_color = (0, 255, 0)  # 绿色
        self.connection_color = (0, 0, 255)  # 红色
        self.line_thickness = 2
        self.landmark_size = 8
        self.landmark_shape = "square"
        
        # 悬浮窗引用
        self.landmark_selector_dialog = None
        self.settings_dialog = None
        self.color_settings_dialog = None
        self.export_dialog = None
        self.performance_dialog = None
        self.help_dialog = None
        
        # 初始化界面
        self.init_ui()
        
        # 初始化关节点数据
        self.initialize_landmark_data()

        # 加载保存的完整配置
        self.load_complete_configs_from_file()

        # 延迟初始化MediaPipe
        QTimer.singleShot(1000, self.initialize_mediapipe)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("SnowNavi Pose Analyzer")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 设置应用样式，强制覆盖系统主题
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
            QFrame {
                background: transparent;
                border: none;
            }
            QMenuBar {
                background: #2c3e50;
                color: white;
                border: none;
                padding: 4px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
                color: white;
            }
            QMenuBar::item:selected {
                background: #34495e;
                color: white;
            }
            QStatusBar {
                background: #34495e;
                color: white;
                border: none;
                padding: 4px;
            }
            QLabel {
                color: #2c3e50;
                background: transparent;
            }
            QGroupBox {
                font-weight: bold;
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
        """)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主内容区域
        self.create_main_content(main_layout)
        
        # 创建状态栏
        self.create_status_bar()

    def create_toolbar(self):
        """创建现代化工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(24, 24))
        
        # 工具栏样式
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: none;
                padding: 8px;
                spacing: 8px;
            }
            QToolButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
                padding: 8px 12px;
                margin: 2px;
                font-weight: 500;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QToolButton:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        
        # 工具栏按钮
        actions = [
            ("📁", "打开视频", self.smart_open_video),
            ("⚙️", "显示设置", self.toggle_landmark_selector),
            ("💾", "导出视频", self.toggle_export),
            ("❓", "帮助", self.toggle_help),
        ]
        
        for icon, text, callback in actions:
            action = QAction(f"{icon} {text}", self)
            action.triggered.connect(callback)
            toolbar.addAction(action)
            
        # 添加分隔符和状态显示
        toolbar.addSeparator()
        
        # 快捷配置选择
        toolbar.addSeparator()

        config_label = QLabel("快捷配置:")
        config_label.setStyleSheet("color: white; padding: 8px; font-weight: 500;")
        toolbar.addWidget(config_label)

        self.toolbar_config_combo = QComboBox()
        self.toolbar_config_combo.setMinimumWidth(120)
        self.toolbar_config_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: white;
                padding: 4px 8px;
                font-weight: 500;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #2c3e50;
                color: white;
                selection-background-color: #34495e;
                border: 1px solid #555;
            }
        """)
        self.toolbar_config_combo.currentTextChanged.connect(self.on_toolbar_config_changed)
        toolbar.addWidget(self.toolbar_config_combo)

        # 初始化工具栏配置选项（延迟更新）
        self.toolbar_config_combo.addItem("选择配置...")
        QTimer.singleShot(100, self.update_toolbar_config_combo)

        # 状态标签
        self.toolbar_status = QLabel("就绪")
        self.toolbar_status.setStyleSheet("color: white; padding: 8px; font-weight: 500;")
        toolbar.addWidget(self.toolbar_status)
        
        self.addToolBar(toolbar)

    def create_main_content(self, main_layout):
        """创建主内容区域"""
        # 直接创建视频显示区域，不使用分割器
        self.create_video_area(main_layout)

    def create_video_area(self, parent_layout):
        """创建视频显示区域"""
        # 视频容器
        self.video_container = QWidget()
        self.video_layout = QHBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(10, 10, 10, 10)
        self.video_layout.setSpacing(10)

        # 视频1容器（包含视频和控制）
        self.create_video1_container()

        # 视频2容器（初始隐藏）
        self.create_video2_container()

        parent_layout.addWidget(self.video_container)

    def create_video1_container(self):
        """创建视频1容器"""
        self.video1_container = QWidget()
        video1_layout = QVBoxLayout(self.video1_container)
        video1_layout.setContentsMargins(0, 0, 0, 0)
        video1_layout.setSpacing(5)

        # 视频1显示区域
        self.video1_widget = VideoWidget()
        video1_layout.addWidget(self.video1_widget)

        # 视频1控制面板
        self.create_video_controls(video1_layout, 1)

        self.video_layout.addWidget(self.video1_container)

    def create_video2_container(self):
        """创建视频2容器"""
        self.video2_container = QWidget()
        video2_layout = QVBoxLayout(self.video2_container)
        video2_layout.setContentsMargins(0, 0, 0, 0)
        video2_layout.setSpacing(5)

        # 视频2显示区域
        self.video2_widget = VideoWidget()
        self.video2_widget.setText("🎬 第二个视频\n用于对比分析")
        video2_layout.addWidget(self.video2_widget)

        # 视频2控制面板
        self.create_video_controls(video2_layout, 2)

        # 添加到主布局并初始隐藏
        self.video_layout.addWidget(self.video2_container)
        self.video2_container.hide()

    def create_video_controls(self, parent_layout, video_num):
        """创建视频控制面板"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        control_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                max-height: 60px;
            }
        """)

        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(5, 5, 5, 5)

        # 播放按钮
        play_button = ModernButton("", "▶️", "#4CAF50")
        play_button.setFixedSize(40, 30)
        if video_num == 1:
            self.play_button1 = play_button
            play_button.clicked.connect(self.toggle_playback1)
        else:
            self.play_button2 = play_button
            play_button.clicked.connect(self.toggle_playback2)
        control_layout.addWidget(play_button)

        # 旋转按钮
        rotate_button = ModernButton("", "🔄", "#FF9800")
        rotate_button.setFixedSize(40, 30)
        if video_num == 1:
            self.rotate_button1 = rotate_button
            rotate_button.clicked.connect(self.rotate_video1)
        else:
            self.rotate_button2 = rotate_button
            rotate_button.clicked.connect(self.rotate_video2)
        control_layout.addWidget(rotate_button)

        # 进度条
        progress_slider = QSlider(Qt.Orientation.Horizontal)
        progress_slider.setMinimum(0)
        progress_slider.setMaximum(100)
        progress_slider.setValue(0)
        progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border: 1px solid #777;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #777;
                width: 16px;
                margin-top: -2px;
                margin-bottom: -2px;
                border-radius: 3px;
            }
        """)

        if video_num == 1:
            self.progress_slider1 = progress_slider
            progress_slider.sliderPressed.connect(self.on_slider1_pressed)
            progress_slider.sliderReleased.connect(self.on_slider1_released)
            progress_slider.valueChanged.connect(self.on_slider1_value_changed)
        else:
            self.progress_slider2 = progress_slider
            progress_slider.sliderPressed.connect(self.on_slider2_pressed)
            progress_slider.sliderReleased.connect(self.on_slider2_released)
            progress_slider.valueChanged.connect(self.on_slider2_value_changed)

        control_layout.addWidget(progress_slider, 1)

        # 时间标签
        time_label = QLabel("00:00 / 00:00")
        time_label.setStyleSheet("color: #666; font-weight: 500; font-size: 11px;")
        time_label.setMinimumWidth(100)  # 使用最小宽度而不是固定宽度，确保能显示完整时间
        if video_num == 1:
            self.time_label1 = time_label
        else:
            self.time_label2 = time_label
        control_layout.addWidget(time_label)

        parent_layout.addWidget(control_frame)





    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        
        # 主状态标签
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        
        # FPS标签
        self.fps_label = QLabel("FPS: --")
        status_bar.addPermanentWidget(self.fps_label)
        
        # 内存使用标签
        self.memory_label = QLabel("内存: --")
        status_bar.addPermanentWidget(self.memory_label)
        
        self.setStatusBar(status_bar)

    def initialize_landmark_data(self):
        """初始化关节点数据"""
        # 定义关节点信息
        self.landmark_info = {
            0: "鼻子", 1: "左眼内侧", 2: "左眼", 3: "左眼外侧", 4: "右眼内侧", 5: "右眼", 6: "右眼外侧",
            7: "左耳", 8: "右耳", 9: "嘴左", 10: "嘴右", 11: "左肩", 12: "右肩", 13: "左肘", 14: "右肘",
            15: "左腕", 16: "右腕", 17: "左小指", 18: "右小指", 19: "左食指", 20: "右食指", 21: "左拇指", 22: "右拇指",
            23: "左髋", 24: "右髋", 25: "左膝", 26: "右膝", 27: "左踝", 28: "右踝", 29: "左脚跟", 30: "右脚跟",
            31: "左脚趾", 32: "右脚趾"
        }

        # 关节点分组
        self.landmark_groups = {
            "头部": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "上肢": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
            "躯干": [11, 12, 23, 24],
            "下肢": [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        }

        # 初始化关节点显示状态（默认全部显示）
        self.landmark_visibility = {i: True for i in range(33)}

        # 初始化完整配置系统
        self.complete_configs = {}  # 存储完整配置（关节点+显示+颜色）

        # 初始化水印设置
        self.watermark_enabled = True  # 默认启用水印
        self.text_watermark_enabled = True  # 文字水印启用
        self.image_watermark_enabled = True  # 图片水印启用
        self.watermark_text = "SnowNavi Pose Analyzer"  # 默认文字
        self.watermark_image_path = "assets/snownavi_logo.png"
        self.text_watermark_position = "右下角"  # 文字水印位置
        self.image_watermark_position = "左下角"  # 图片水印位置
        self.watermark_opacity = 70
        self.watermark_size = "中"

        # 预览播放状态
        self.preview_playing = False
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview_frame)

        # 视频旋转状态 (0=0°, 1=90°, 2=180°, 3=270°)
        self.video1_rotation = 0
        self.video2_rotation = 0

        # 导出时的旋转设置（可以与播放时不同）
        self.export_video1_rotation = 0
        self.export_video2_rotation = 0

    def initialize_mediapipe(self):
        """初始化MediaPipe"""
        try:
            self.update_status("正在初始化MediaPipe...")

            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles

            # 创建Pose模型
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

            self.mediapipe_initialized = True
            self.update_status("MediaPipe初始化完成")

        except Exception as e:
            self.update_status(f"MediaPipe初始化失败: {str(e)}")
            self.mediapipe_initialized = False

    def smart_open_video(self):
        """智能打开视频"""
        try:
            # 检查当前视频状态
            video1_loaded = self.cap1 is not None
            video2_loaded = self.cap2 is not None

            if not video1_loaded:
                # 第一次打开 - 加载视频1
                self.load_video1()
            elif not video2_loaded:
                # 第二次打开 - 加载视频2并启用比较模式
                self.load_video2()
            else:
                # 已有两个视频 - 询问替换哪个
                self.show_video_replace_dialog()

        except Exception as e:
            self.update_status(f"打开视频失败: {str(e)}")

    def load_video1(self):
        """加载视频1"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择视频文件",
                "",
                "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;所有文件 (*.*)"
            )

            if file_path:
                # 释放之前的视频
                if self.cap1:
                    self.cap1.release()

                # 打开新视频
                self.cap1 = cv2.VideoCapture(file_path)
                if self.cap1.isOpened():
                    # 存储原始视频路径（用于音频提取）
                    self.video1_path = file_path
                    # 重置旋转设置
                    self.video1_rotation = 0
                    # 获取视频信息
                    self.total_frames1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
                    self.fps1 = self.cap1.get(cv2.CAP_PROP_FPS)

                    # 显示第一帧
                    ret, frame = self.cap1.read()
                    if ret:
                        self.current_frame1 = frame
                        processed_frame = self.process_pose_detection(frame)
                        self.display_frame_in_widget(processed_frame, self.video1_widget)

                        # 重置到开头
                        self.cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    # 重置播放状态
                    self.is_playing1 = False
                    self.current_frame_pos1 = 0

                    # 设置进度条
                    self.progress_slider1.setValue(0)
                    self.progress_slider1.setMaximum(100)

                    # 更新时间显示
                    self.update_time_display1()

                    self.update_status(f"视频1加载成功: {os.path.basename(file_path)} (旋转已重置)")

                    # 更新导出选项状态
                    if hasattr(self, 'export_dialog') and self.export_dialog is not None:
                        self.update_export_video_options()

                    return True
                else:
                    QMessageBox.critical(self, "错误", "无法打开视频文件")
                    return False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载视频时出错: {str(e)}")
            return False

    def load_video2(self):
        """加载视频2"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择第二个视频文件",
                "",
                "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;所有文件 (*.*)"
            )

            if file_path:
                # 释放之前的视频
                if self.cap2:
                    self.cap2.release()

                # 打开新视频
                self.cap2 = cv2.VideoCapture(file_path)
                if self.cap2.isOpened():
                    # 存储原始视频路径（用于音频提取）
                    self.video2_path = file_path
                    # 重置旋转设置
                    self.video2_rotation = 0
                    # 获取视频信息
                    self.total_frames2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))
                    self.fps2 = self.cap2.get(cv2.CAP_PROP_FPS)

                    # 显示第一帧
                    ret, frame = self.cap2.read()
                    if ret:
                        self.current_frame2 = frame
                        processed_frame = self.process_pose_detection(frame)
                        self.display_frame_in_widget(processed_frame, self.video2_widget)

                        # 重置到开头
                        self.cap2.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    # 启用比较模式
                    self.video2_loaded = True
                    self.update_video_layout()

                    # 重置播放状态
                    self.is_playing2 = False
                    self.current_frame_pos2 = 0

                    # 设置进度条
                    self.progress_slider2.setValue(0)
                    self.progress_slider2.setMaximum(100)

                    # 更新时间显示
                    self.update_time_display2()

                    self.update_status(f"视频2加载成功，启用比较模式: {os.path.basename(file_path)} (旋转已重置)")

                    # 更新导出选项状态
                    if hasattr(self, 'export_dialog') and self.export_dialog is not None:
                        self.update_export_video_options()

                    return True
                else:
                    QMessageBox.critical(self, "错误", "无法打开视频文件")
                    return False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载视频时出错: {str(e)}")
            return False

    def show_video_replace_dialog(self):
        """显示视频替换对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("替换视频")
        dialog.setFixedSize(350, 200)

        layout = QVBoxLayout(dialog)

        # 标题
        title_label = QLabel("已有两个视频")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 说明
        desc_label = QLabel("请选择要替换的视频:")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # 按钮
        button_layout = QHBoxLayout()

        btn1 = ModernButton("替换视频1", "", "#FF9800")
        btn1.clicked.connect(lambda: self.replace_video(dialog, 1))
        button_layout.addWidget(btn1)

        btn2 = ModernButton("替换视频2", "", "#FF9800")
        btn2.clicked.connect(lambda: self.replace_video(dialog, 2))
        button_layout.addWidget(btn2)

        layout.addLayout(button_layout)

        # 取消按钮
        cancel_btn = ModernButton("取消", "", "#607D8B")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.exec()

    def replace_video(self, dialog, video_num):
        """替换指定的视频"""
        dialog.accept()

        if video_num == 1:
            self.load_video1()
        else:
            self.load_video2()

    def display_frame_in_widget(self, frame, widget):
        """在控件中显示帧，保持原始比例"""
        try:
            # 获取控件大小
            widget.update()
            widget_width = widget.width()
            widget_height = widget.height()

            # 如果控件还没有大小，使用默认值
            if widget_width <= 1 or widget_height <= 1:
                widget_width = 640
                widget_height = 480

            # 获取原始帧尺寸
            frame_height, frame_width = frame.shape[:2]

            # 计算帧的宽高比
            frame_aspect_ratio = frame_width / frame_height

            # 根据帧的宽高比决定显示方向和缩放策略
            if frame_aspect_ratio > 1.5:  # 横屏视频 (宽高比 > 1.5)
                # 横屏视频，优先适应宽度
                scale = min(widget_width / frame_width, widget_height / frame_height) * 0.95
            elif frame_aspect_ratio < 0.7:  # 竖屏视频 (宽高比 < 0.7)
                # 竖屏视频，优先适应高度
                scale = min(widget_height / frame_height, widget_width / frame_width) * 0.95
            else:  # 接近正方形的视频
                # 正方形视频，按比例缩放
                scale = min(widget_width / frame_width, widget_height / frame_height) * 0.95

            # 计算新尺寸
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)

            # 确保尺寸有效
            if new_width > 0 and new_height > 0:
                resized_frame = cv2.resize(frame, (new_width, new_height))

                # 转换颜色空间
                rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w

                # 创建QImage
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

                # 创建QPixmap
                pixmap = QPixmap.fromImage(qt_image)

                # 设置像素图，保持宽高比
                widget.setPixmap(pixmap)
                widget.setScaledContents(False)  # 不拉伸内容
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中显示

        except Exception as e:
            print(f"显示帧时出错: {e}")
            widget.setText(f"显示错误: {str(e)}")

    def update_video_layout(self):
        """更新视频布局"""
        if self.video2_loaded:
            # 显示双视频布局
            self.video2_container.show()
        else:
            # 隐藏视频2
            self.video2_container.hide()

    def toggle_landmark_selector(self):
        """切换关节点选择器"""
        if self.landmark_selector_dialog is None:
            self.create_landmark_selector_dialog()

        if self.landmark_selector_dialog.isVisible():
            self.landmark_selector_dialog.hide()
        else:
            self.landmark_selector_dialog.show()



    def toggle_export(self):
        """切换导出"""
        if not hasattr(self, 'export_dialog') or self.export_dialog is None:
            self.create_export_dialog()

        if self.export_dialog.isVisible():
            # 停止预览播放
            if hasattr(self, 'preview_playing') and self.preview_playing:
                self.preview_playing = False
                self.preview_timer.stop()
            self.export_dialog.hide()
        else:
            # 更新视频选择选项状态
            self.update_export_video_options()
            self.export_dialog.show()
            # 刷新预览，确保显示当前旋转状态
            if hasattr(self, 'refresh_export_preview'):
                # 稍微延迟刷新，确保对话框完全显示
                QTimer.singleShot(100, self.refresh_export_preview)

    def toggle_performance(self):
        """切换性能监控"""
        if not hasattr(self, 'performance_dialog') or self.performance_dialog is None:
            self.create_performance_dialog()

        if self.performance_dialog.isVisible():
            self.performance_dialog.hide()
        else:
            self.performance_dialog.show()

    def toggle_help(self):
        """切换帮助"""
        if not hasattr(self, 'help_dialog') or self.help_dialog is None:
            self.create_help_dialog()

        if self.help_dialog.isVisible():
            self.help_dialog.hide()
        else:
            self.help_dialog.show()



    def create_export_dialog(self):
        """创建导出对话框"""
        self.export_dialog = QDialog(self)
        self.export_dialog.setWindowTitle("导出视频")
        self.export_dialog.setFixedSize(900, 700)  # 增大窗口以容纳更多内容

        # 设置统一的对话框样式，确保在日间/夜间模式下都保持一致
        self.export_dialog.setStyleSheet("""
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
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #3498db;
            }
            QCheckBox::indicator:disabled {
                background: #ecf0f1;
                border: 2px solid #bdc3c7;
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
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNEw2IDdMOSA0IiBzdHJva2U9IiM3Zjg2OWMiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                width: 12px;
                height: 12px;
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
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
                color: #2c3e50;
                font-size: 10px;
                padding: 8px;
            }
        """)

        # 主布局使用水平分割
        main_layout = QHBoxLayout(self.export_dialog)

        # 左侧：设置区域 - 紧凑布局
        left_widget = QWidget()
        left_main_layout = QVBoxLayout(left_widget)
        left_main_layout.setContentsMargins(8, 8, 8, 8)  # 减少边距
        left_main_layout.setSpacing(6)  # 减少间距
        left_widget.setFixedWidth(350)  # 减少左侧宽度，给预览更多空间

        # 标题 - 更紧凑
        title_label = QLabel("💾 导出视频")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # 减小字体
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 5px;")  # 减少内边距
        left_main_layout.addWidget(title_label)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # 滚动区域内的widget
        scroll_widget = QWidget()
        left_layout = QVBoxLayout(scroll_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)  # 减少内容边距
        left_layout.setSpacing(8)  # 减少控件间距

        scroll_area.setWidget(scroll_widget)
        left_main_layout.addWidget(scroll_area)

        # 右侧：预览区域 - 优化空间利用
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)  # 减少边距
        right_layout.setSpacing(6)  # 减少间距

        # 预览标题 - 更紧凑
        preview_title = QLabel("🎬 预览效果")
        preview_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # 减小字体
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_title.setStyleSheet("color: #2c3e50; padding: 3px;")  # 减少内边距
        right_layout.addWidget(preview_title)

        # 预览视频区域 - 扩大尺寸，充分利用空间
        self.export_preview_widget = VideoWidget()
        self.export_preview_widget.setMinimumSize(500, 420)  # 显著增大预览区域
        self.export_preview_widget.setText("🎬 点击播放预览\n查看导出效果")
        right_layout.addWidget(self.export_preview_widget, 1)  # 添加拉伸因子，让预览区域占据剩余空间

        # 预览控制按钮 - 更紧凑
        preview_control_layout = QHBoxLayout()
        preview_control_layout.setSpacing(6)  # 减少按钮间距

        self.preview_play_btn = ModernButton("播放", "▶️", "#4CAF50")  # 简化文字
        self.preview_play_btn.clicked.connect(self.toggle_export_preview)
        preview_control_layout.addWidget(self.preview_play_btn)

        self.preview_refresh_btn = ModernButton("刷新", "🔄", "#2196F3")  # 简化文字
        self.preview_refresh_btn.clicked.connect(self.refresh_export_preview)
        preview_control_layout.addWidget(self.preview_refresh_btn)

        right_layout.addLayout(preview_control_layout)

        # 添加左右布局
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # 继续使用left_layout作为主要设置布局
        layout = left_layout

        # 视频选择 - 紧凑布局
        video_group = QGroupBox("选择要导出的视频")
        video_layout = QVBoxLayout(video_group)
        video_layout.setContentsMargins(8, 8, 8, 8)  # 减少内边距
        video_layout.setSpacing(4)  # 减少间距

        self.export_video1_cb = QCheckBox("导出视频1（带姿态检测）")
        self.export_video1_cb.setChecked(True)
        video_layout.addWidget(self.export_video1_cb)

        self.export_video2_cb = QCheckBox("导出视频2（带姿态检测）")
        video_layout.addWidget(self.export_video2_cb)

        layout.addWidget(video_group)

        # 导出设置 - 紧凑布局
        settings_group = QGroupBox("导出设置")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(8, 8, 8, 8)  # 减少内边距
        settings_layout.setSpacing(6)  # 减少间距

        # 质量设置
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("视频质量:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["高质量", "中等质量", "压缩质量"])
        self.quality_combo.setCurrentText("高质量")
        quality_layout.addWidget(self.quality_combo)
        settings_layout.addLayout(quality_layout)

        # 帧率设置
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("输出帧率:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["原始帧率", "30 FPS", "25 FPS", "15 FPS"])
        self.fps_combo.setCurrentText("原始帧率")
        fps_layout.addWidget(self.fps_combo)
        settings_layout.addLayout(fps_layout)

        layout.addWidget(settings_group)

        # 旋转设置 - 紧凑布局
        rotation_group = QGroupBox("旋转设置")
        rotation_layout = QVBoxLayout(rotation_group)
        rotation_layout.setContentsMargins(8, 8, 8, 8)
        rotation_layout.setSpacing(4)

        # 视频1旋转
        if hasattr(self, 'cap1') and self.cap1 is not None:
            video1_rotation_layout = QHBoxLayout()
            video1_rotation_layout.addWidget(QLabel("视频1旋转:"))
            self.video1_rotation_combo = QComboBox()
            self.video1_rotation_combo.addItems(["0°", "90°", "180°", "270°"])
            # 初始化为当前播放旋转角度
            self.export_video1_rotation = self.video1_rotation
            self.video1_rotation_combo.setCurrentIndex(self.export_video1_rotation)
            self.video1_rotation_combo.currentIndexChanged.connect(self.on_export_video1_rotation_changed)
            video1_rotation_layout.addWidget(self.video1_rotation_combo)
            rotation_layout.addLayout(video1_rotation_layout)

        # 视频2旋转
        if hasattr(self, 'cap2') and self.cap2 is not None:
            video2_rotation_layout = QHBoxLayout()
            video2_rotation_layout.addWidget(QLabel("视频2旋转:"))
            self.video2_rotation_combo = QComboBox()
            self.video2_rotation_combo.addItems(["0°", "90°", "180°", "270°"])
            # 初始化为当前播放旋转角度
            self.export_video2_rotation = self.video2_rotation
            self.video2_rotation_combo.setCurrentIndex(self.export_video2_rotation)
            self.video2_rotation_combo.currentIndexChanged.connect(self.on_export_video2_rotation_changed)
            video2_rotation_layout.addWidget(self.video2_rotation_combo)
            rotation_layout.addLayout(video2_rotation_layout)

        layout.addWidget(rotation_group)

        # 水印设置 - 紧凑布局
        watermark_group = QGroupBox("水印设置")
        watermark_layout = QVBoxLayout(watermark_group)
        watermark_layout.setContentsMargins(8, 8, 8, 8)
        watermark_layout.setSpacing(4)

        # 启用水印
        self.watermark_enabled_cb = QCheckBox("启用水印")
        self.watermark_enabled_cb.setChecked(self.watermark_enabled)  # 使用默认值
        self.watermark_enabled_cb.stateChanged.connect(self.on_watermark_enabled_changed)
        watermark_layout.addWidget(self.watermark_enabled_cb)

        # 文字水印设置 - 紧凑布局
        text_watermark_group = QGroupBox("文字水印")
        text_watermark_layout = QVBoxLayout(text_watermark_group)
        text_watermark_layout.setContentsMargins(6, 6, 6, 6)
        text_watermark_layout.setSpacing(3)

        # 启用文字水印
        self.text_watermark_enabled_cb = QCheckBox("启用文字水印")
        self.text_watermark_enabled_cb.setChecked(self.text_watermark_enabled)
        self.text_watermark_enabled_cb.stateChanged.connect(self.on_text_watermark_enabled_changed)
        text_watermark_layout.addWidget(self.text_watermark_enabled_cb)

        # 文字水印文本
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("水印文本:"))
        self.watermark_text_input = QLineEdit()
        self.watermark_text_input.setPlaceholderText("输入水印文本...")
        self.watermark_text_input.setText(self.watermark_text)  # 使用默认文字
        self.watermark_text_input.textChanged.connect(self.on_watermark_text_changed)
        text_layout.addWidget(self.watermark_text_input)
        text_watermark_layout.addLayout(text_layout)

        # 文字水印位置
        text_position_layout = QHBoxLayout()
        text_position_layout.addWidget(QLabel("位置:"))
        self.text_watermark_position_combo = QComboBox()
        self.text_watermark_position_combo.addItems(["右下角", "右上角", "左下角", "左上角", "居中"])
        self.text_watermark_position_combo.setCurrentText(self.text_watermark_position)
        self.text_watermark_position_combo.currentTextChanged.connect(self.on_text_watermark_position_changed)
        text_position_layout.addWidget(self.text_watermark_position_combo)
        text_watermark_layout.addLayout(text_position_layout)

        watermark_layout.addWidget(text_watermark_group)

        # 图片水印设置 - 紧凑布局
        image_watermark_group = QGroupBox("图片水印")
        image_watermark_layout = QVBoxLayout(image_watermark_group)
        image_watermark_layout.setContentsMargins(6, 6, 6, 6)
        image_watermark_layout.setSpacing(3)

        # 启用图片水印
        self.image_watermark_enabled_cb = QCheckBox("启用图片水印")
        self.image_watermark_enabled_cb.setChecked(self.image_watermark_enabled)
        self.image_watermark_enabled_cb.stateChanged.connect(self.on_image_watermark_enabled_changed)
        image_watermark_layout.addWidget(self.image_watermark_enabled_cb)

        # 图片选择
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("水印图片:"))
        self.watermark_image_input = QLineEdit()
        self.watermark_image_input.setPlaceholderText("选择水印图片...")
        self.watermark_image_input.setText("assets/snownavi_logo.png")
        self.watermark_image_input.textChanged.connect(self.on_watermark_image_changed)
        image_layout.addWidget(self.watermark_image_input)

        self.watermark_image_browse_btn = ModernButton("浏览", "📁", "#2196F3")
        self.watermark_image_browse_btn.clicked.connect(self.browse_watermark_image)
        image_layout.addWidget(self.watermark_image_browse_btn)
        image_watermark_layout.addLayout(image_layout)

        # 图片水印位置
        image_position_layout = QHBoxLayout()
        image_position_layout.addWidget(QLabel("位置:"))
        self.image_watermark_position_combo = QComboBox()
        self.image_watermark_position_combo.addItems(["右下角", "右上角", "左下角", "左上角", "居中"])
        self.image_watermark_position_combo.setCurrentText(self.image_watermark_position)
        self.image_watermark_position_combo.currentTextChanged.connect(self.on_image_watermark_position_changed)
        image_position_layout.addWidget(self.image_watermark_position_combo)
        image_watermark_layout.addLayout(image_position_layout)

        watermark_layout.addWidget(image_watermark_group)

        # 通用水印设置 - 紧凑布局
        common_group = QGroupBox("通用设置")
        common_layout = QVBoxLayout(common_group)
        common_layout.setContentsMargins(6, 6, 6, 6)
        common_layout.setSpacing(4)

        # 水印透明度
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self.watermark_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.watermark_opacity_slider.setRange(10, 100)
        self.watermark_opacity_slider.setValue(70)
        self.watermark_opacity_slider.valueChanged.connect(self.on_watermark_opacity_changed)
        opacity_layout.addWidget(self.watermark_opacity_slider)
        self.watermark_opacity_label = QLabel("70%")
        opacity_layout.addWidget(self.watermark_opacity_label)
        common_layout.addLayout(opacity_layout)

        # 水印大小
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("大小:"))
        self.watermark_size_combo = QComboBox()
        self.watermark_size_combo.addItems(["小", "中", "大"])
        self.watermark_size_combo.setCurrentText("中")
        self.watermark_size_combo.currentTextChanged.connect(self.on_watermark_size_changed)
        size_layout.addWidget(self.watermark_size_combo)
        common_layout.addLayout(size_layout)

        watermark_layout.addWidget(common_group)

        layout.addWidget(watermark_group)

        # 进度显示区域 - 紧凑布局
        progress_group = QGroupBox("导出进度")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(8, 8, 8, 8)
        progress_layout.setSpacing(4)

        # 总体进度条
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        self.export_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                background: white;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #66BB6A);
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.export_progress)

        # 详细进度信息
        progress_info_layout = QHBoxLayout()

        # 当前帧/总帧数
        self.frame_progress_label = QLabel("帧: 0 / 0")
        self.frame_progress_label.setStyleSheet("font-size: 11px; color: #666;")
        progress_info_layout.addWidget(self.frame_progress_label)

        # 百分比
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
        progress_info_layout.addWidget(self.percentage_label)

        # 预计剩余时间
        self.eta_label = QLabel("预计剩余: --")
        self.eta_label.setStyleSheet("font-size: 11px; color: #666;")
        progress_info_layout.addWidget(self.eta_label)

        progress_layout.addLayout(progress_info_layout)

        # 状态标签
        self.export_status_label = QLabel("")
        self.export_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.export_status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        progress_layout.addWidget(self.export_status_label)

        # 初始隐藏进度组
        progress_group.setVisible(False)
        self.export_progress_group = progress_group
        layout.addWidget(progress_group)

        # 按钮
        button_layout = QHBoxLayout()

        self.export_start_btn = ModernButton("开始导出", "", "#4CAF50")
        self.export_start_btn.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_start_btn)

        # 取消按钮（导出时显示）
        self.export_cancel_btn = ModernButton("取消导出", "", "#F44336")
        self.export_cancel_btn.clicked.connect(self.cancel_export)
        self.export_cancel_btn.setVisible(False)
        button_layout.addWidget(self.export_cancel_btn)

        close_btn = ModernButton("关闭", "", "#607D8B")
        close_btn.clicked.connect(self.export_dialog.hide)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # 导出取消标志
        self.export_cancelled = False

    def update_export_video_options(self):
        """更新导出视频选项的可用状态"""
        if hasattr(self, 'export_video1_cb'):
            # 视频1选项
            if hasattr(self, 'cap1') and self.cap1 is not None:
                self.export_video1_cb.setEnabled(True)
                if not self.export_video1_cb.isChecked():
                    self.export_video1_cb.setChecked(True)
            else:
                self.export_video1_cb.setEnabled(False)
                self.export_video1_cb.setChecked(False)

        if hasattr(self, 'export_video2_cb'):
            # 视频2选项
            if hasattr(self, 'cap2') and self.cap2 is not None:
                self.export_video2_cb.setEnabled(True)
                if not self.export_video2_cb.isChecked():
                    self.export_video2_cb.setChecked(True)
            else:
                self.export_video2_cb.setEnabled(False)
                self.export_video2_cb.setChecked(False)

    def on_watermark_enabled_changed(self, state):
        """水印启用状态改变"""
        self.watermark_enabled = (state == Qt.CheckState.Checked.value)
        # 启用/禁用水印相关控件
        enabled = self.watermark_enabled
        self.text_watermark_enabled_cb.setEnabled(enabled)
        self.image_watermark_enabled_cb.setEnabled(enabled)
        self.watermark_text_input.setEnabled(enabled and self.text_watermark_enabled)
        self.watermark_image_input.setEnabled(enabled and self.image_watermark_enabled)
        self.watermark_image_browse_btn.setEnabled(enabled and self.image_watermark_enabled)
        self.text_watermark_position_combo.setEnabled(enabled and self.text_watermark_enabled)
        self.image_watermark_position_combo.setEnabled(enabled and self.image_watermark_enabled)
        self.watermark_opacity_slider.setEnabled(enabled)
        self.watermark_size_combo.setEnabled(enabled)
        # 刷新预览以显示水印启用/禁用效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_text_watermark_enabled_changed(self, state):
        """文字水印启用状态改变"""
        self.text_watermark_enabled = (state == Qt.CheckState.Checked.value)
        enabled = self.watermark_enabled and self.text_watermark_enabled
        self.watermark_text_input.setEnabled(enabled)
        self.text_watermark_position_combo.setEnabled(enabled)
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_image_watermark_enabled_changed(self, state):
        """图片水印启用状态改变"""
        self.image_watermark_enabled = (state == Qt.CheckState.Checked.value)
        enabled = self.watermark_enabled and self.image_watermark_enabled
        self.watermark_image_input.setEnabled(enabled)
        self.watermark_image_browse_btn.setEnabled(enabled)
        self.image_watermark_position_combo.setEnabled(enabled)
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_watermark_text_changed(self, text):
        """水印文本改变"""
        self.watermark_text = text
        # 刷新预览以显示新的水印效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_text_watermark_position_changed(self, position):
        """文字水印位置改变"""
        self.text_watermark_position = position
        # 刷新预览以显示新的水印效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_image_watermark_position_changed(self, position):
        """图片水印位置改变"""
        self.image_watermark_position = position
        # 刷新预览以显示新的水印效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_watermark_opacity_changed(self, value):
        """水印透明度改变"""
        self.watermark_opacity = value
        self.watermark_opacity_label.setText(f"{value}%")
        # 刷新预览以显示新的水印效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_watermark_size_changed(self, size):
        """水印大小改变"""
        self.watermark_size = size
        # 刷新预览以显示新的水印效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()



    def on_watermark_image_changed(self, image_path):
        """水印图片路径改变"""
        self.watermark_image_path = image_path
        # 刷新预览以显示新的水印效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def browse_watermark_image(self):
        """浏览选择水印图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.export_dialog,
            "选择水印图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )
        if file_path:
            self.watermark_image_input.setText(file_path)
            self.watermark_image_path = file_path
            # 刷新预览以显示新的水印效果
            if hasattr(self, 'export_preview_widget'):
                self.refresh_export_preview()

    def on_export_video1_rotation_changed(self, index):
        """导出时视频1旋转设置改变"""
        # 为导出单独设置旋转，不影响播放显示
        self.export_video1_rotation = index
        self.update_status(f"导出视频1旋转设置: {index * 90}°")
        # 刷新预览以显示新的旋转效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def on_export_video2_rotation_changed(self, index):
        """导出时视频2旋转设置改变"""
        # 为导出单独设置旋转，不影响播放显示
        self.export_video2_rotation = index
        self.update_status(f"导出视频2旋转设置: {index * 90}°")
        # 刷新预览以显示新的旋转效果
        if hasattr(self, 'export_preview_widget'):
            self.refresh_export_preview()

    def toggle_export_preview(self):
        """切换导出预览播放"""
        # 检查是否有可预览的视频
        has_video = False
        if hasattr(self, 'export_video1_cb') and self.export_video1_cb.isChecked() and self.cap1:
            has_video = True
        elif hasattr(self, 'export_video2_cb') and self.export_video2_cb.isChecked() and self.cap2:
            has_video = True
        elif self.cap1 or self.cap2:
            has_video = True

        if not has_video:
            QMessageBox.warning(self.export_dialog, "警告", "请先加载视频")
            return

        if self.preview_playing:
            # 停止预览
            self.preview_playing = False
            self.preview_timer.stop()
            self.preview_play_btn.setText("▶️ 播放预览")
        else:
            # 开始预览
            self.preview_playing = True
            self.preview_timer.start(33)  # 约30fps
            self.preview_play_btn.setText("⏸️ 停止预览")

    def refresh_export_preview(self):
        """刷新导出预览"""
        # 确定预览哪个视频（优先视频1，如果没有则视频2）
        preview_cap = None
        preview_video_num = 1

        if hasattr(self, 'export_video1_cb') and self.export_video1_cb.isChecked() and self.cap1:
            preview_cap = self.cap1
            preview_video_num = 1
        elif hasattr(self, 'export_video2_cb') and self.export_video2_cb.isChecked() and self.cap2:
            preview_cap = self.cap2
            preview_video_num = 2
        elif self.cap1:  # 默认预览视频1
            preview_cap = self.cap1
            preview_video_num = 1
        elif self.cap2:  # 如果视频1不存在，预览视频2
            preview_cap = self.cap2
            preview_video_num = 2

        if preview_cap:
            # 获取当前帧
            current_pos = int(preview_cap.get(cv2.CAP_PROP_POS_FRAMES))
            ret, frame = preview_cap.read()
            if ret:
                # 处理姿态检测和水印
                processed_frame = self.process_frame_for_export(frame, preview_video_num)
                self.display_frame_in_widget(processed_frame, self.export_preview_widget)

                # 恢复视频位置
                preview_cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos)

    def update_preview_frame(self):
        """更新预览帧"""
        try:
            if not self.preview_playing:
                return

            # 确定预览哪个视频（优先视频1，如果没有则视频2）
            preview_cap = None
            preview_video_num = 1

            if hasattr(self, 'export_video1_cb') and self.export_video1_cb.isChecked() and self.cap1:
                preview_cap = self.cap1
                preview_video_num = 1
            elif hasattr(self, 'export_video2_cb') and self.export_video2_cb.isChecked() and self.cap2:
                preview_cap = self.cap2
                preview_video_num = 2
            elif self.cap1:  # 默认预览视频1
                preview_cap = self.cap1
                preview_video_num = 1
            elif self.cap2:  # 如果视频1不存在，预览视频2
                preview_cap = self.cap2
                preview_video_num = 2

            if not preview_cap:
                return

            ret, frame = preview_cap.read()
            if ret:
                # 处理姿态检测和水印
                processed_frame = self.process_frame_for_export(frame, preview_video_num)
                self.display_frame_in_widget(processed_frame, self.export_preview_widget)
            else:
                # 视频播放完毕，重新开始
                preview_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        except Exception as e:
            print(f"更新预览帧时出错: {e}")

    def process_frame_for_export(self, frame, video_num=1):
        """处理用于导出的帧（包含旋转、姿态检测和水印）"""
        try:
            # 首先应用旋转（使用导出旋转设置）
            if video_num == 1:
                rotation = getattr(self, 'export_video1_rotation', self.video1_rotation)
                rotated_frame = self.rotate_frame(frame, rotation)
            else:
                rotation = getattr(self, 'export_video2_rotation', self.video2_rotation)
                rotated_frame = self.rotate_frame(frame, rotation)

            # 然后进行姿态检测
            processed_frame = self.process_pose_detection(rotated_frame)

            # 如果启用水印，添加水印
            if self.watermark_enabled:
                # 添加文字水印
                if self.text_watermark_enabled and self.watermark_text:
                    processed_frame = self.add_text_watermark(processed_frame)
                # 添加图片水印
                if self.image_watermark_enabled and self.watermark_image_path:
                    processed_frame = self.add_image_watermark(processed_frame)

            return processed_frame

        except Exception as e:
            print(f"处理导出帧时出错: {e}")
            return frame

    def add_text_watermark(self, frame):
        """添加文字水印到帧"""
        try:

            # 获取帧尺寸
            height, width = frame.shape[:2]

            # 根据大小设置字体缩放
            size_map = {"小": 0.5, "中": 0.8, "大": 1.2}
            font_scale = size_map.get(self.watermark_size, 0.8)

            # 调整字体大小基于视频分辨率
            base_font_scale = min(width, height) / 1000.0
            font_scale *= base_font_scale

            # 字体设置
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = max(1, int(font_scale * 2))

            # 获取文本尺寸
            (text_width, text_height), _ = cv2.getTextSize(
                self.watermark_text, font, font_scale, thickness
            )

            # 计算位置
            margin = 20
            position = getattr(self, 'text_watermark_position', '右下角')
            if position == "右下角":
                x = width - text_width - margin
                y = height - margin
            elif position == "右上角":
                x = width - text_width - margin
                y = text_height + margin
            elif position == "左下角":
                x = margin
                y = height - margin
            elif position == "左上角":
                x = margin
                y = text_height + margin
            else:  # 居中
                x = (width - text_width) // 2
                y = (height + text_height) // 2

            # 创建水印图层
            overlay = frame.copy()

            # 绘制文本
            cv2.putText(overlay, self.watermark_text, (x, y), font, font_scale,
                       (255, 255, 255), thickness, cv2.LINE_AA)

            # 应用透明度
            alpha = getattr(self, 'watermark_opacity', 80) / 100.0
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            return frame

        except Exception as e:
            print(f"添加文字水印时出错: {e}")
            return frame

    def add_image_watermark(self, frame):
        """添加图片水印到帧"""
        try:
            import os

            # 检查图片文件是否存在
            if not os.path.exists(self.watermark_image_path):
                print(f"水印图片不存在: {self.watermark_image_path}")
                return frame

            # 读取水印图片
            watermark_img = cv2.imread(self.watermark_image_path, cv2.IMREAD_UNCHANGED)
            if watermark_img is None:
                print(f"无法读取水印图片: {self.watermark_image_path}")
                return frame

            # 获取帧和水印图片的尺寸
            frame_height, frame_width = frame.shape[:2]

            # 根据大小设置调整水印尺寸
            size_map = {"小": 0.08, "中": 0.12, "大": 0.18}  # 增大尺寸避免过小
            scale_factor = size_map.get(getattr(self, 'watermark_size', '中'), 0.12)

            # 计算水印大小（基于帧的较小边）
            base_size = min(frame_width, frame_height)
            watermark_width = int(base_size * scale_factor)

            # 保持水印图片的宽高比
            wm_h, wm_w = watermark_img.shape[:2]
            aspect_ratio = wm_h / wm_w
            watermark_height = int(watermark_width * aspect_ratio)

            # 使用高质量插值调整水印图片大小
            watermark_resized = cv2.resize(
                watermark_img,
                (watermark_width, watermark_height),
                interpolation=cv2.INTER_LANCZOS4  # 使用高质量插值
            )

            # 计算水印位置
            margin = 20
            position = getattr(self, 'image_watermark_position', '左下角')
            if position == "右下角":
                x = frame_width - watermark_width - margin
                y = frame_height - watermark_height - margin
            elif position == "右上角":
                x = frame_width - watermark_width - margin
                y = margin
            elif position == "左下角":
                x = margin
                y = frame_height - watermark_height - margin
            elif position == "左上角":
                x = margin
                y = margin
            else:  # 居中
                x = (frame_width - watermark_width) // 2
                y = (frame_height - watermark_height) // 2

            # 确保水印不会超出帧边界
            x = max(0, min(x, frame_width - watermark_width))
            y = max(0, min(y, frame_height - watermark_height))

            # 添加水印到帧
            if watermark_resized.shape[2] == 4:  # 带透明通道的PNG
                self.add_watermark_with_alpha(frame, watermark_resized, x, y)
            else:  # 不带透明通道的图片
                self.add_watermark_without_alpha(frame, watermark_resized, x, y)

            return frame

        except Exception as e:
            print(f"添加图片水印时出错: {e}")
            return frame

    def add_watermark_with_alpha(self, frame, watermark, x, y):
        """添加带透明通道的水印"""
        try:
            h, w = watermark.shape[:2]

            # 确保帧是3通道
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # 提取BGR和Alpha通道
            if len(watermark.shape) == 3 and watermark.shape[2] == 4:
                watermark_bgr = watermark[:, :, :3]
                watermark_alpha = watermark[:, :, 3] / 255.0
            else:
                print(f"警告: 水印图片不是4通道BGRA格式: {watermark.shape}")
                return

            # 应用透明度设置
            alpha_factor = getattr(self, 'watermark_opacity', 80) / 100.0
            watermark_alpha = watermark_alpha * alpha_factor

            # 获取帧的对应区域
            frame_region = frame[y:y+h, x:x+w]

            # 确保尺寸匹配
            if frame_region.shape[:2] != (h, w):
                watermark_bgr = cv2.resize(watermark_bgr, (frame_region.shape[1], frame_region.shape[0]), interpolation=cv2.INTER_LANCZOS4)
                watermark_alpha = cv2.resize(watermark_alpha, (frame_region.shape[1], frame_region.shape[0]), interpolation=cv2.INTER_LANCZOS4)
                h, w = frame_region.shape[:2]

            # 确保frame_region是3通道
            if len(frame_region.shape) == 2:
                frame_region = cv2.cvtColor(frame_region, cv2.COLOR_GRAY2BGR)

            # 使用向量化操作进行alpha混合，提高性能和质量
            alpha_3d = watermark_alpha[:, :, np.newaxis]
            blended = watermark_bgr * alpha_3d + frame_region * (1 - alpha_3d)

            frame[y:y+h, x:x+w] = blended.astype(np.uint8)

        except Exception as e:
            print(f"添加带透明通道水印时出错: {e}")
            print(f"帧形状: {frame.shape}, 水印形状: {watermark.shape}")
            print(f"位置: ({x}, {y}), 尺寸: ({w}, {h})")

    def add_watermark_without_alpha(self, frame, watermark, x, y):
        """添加不带透明通道的水印"""
        try:
            h, w = watermark.shape[:2]

            # 确保水印和帧有相同的通道数
            if len(watermark.shape) == 2:  # 灰度图
                watermark = cv2.cvtColor(watermark, cv2.COLOR_GRAY2BGR)
            elif len(watermark.shape) == 3 and watermark.shape[2] == 4:  # BGRA
                watermark = cv2.cvtColor(watermark, cv2.COLOR_BGRA2BGR)

            # 确保帧也是3通道
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # 应用透明度
            alpha = getattr(self, 'watermark_opacity', 80) / 100.0

            # 获取帧的对应区域
            frame_region = frame[y:y+h, x:x+w]

            # 确保尺寸匹配
            if frame_region.shape[:2] != watermark.shape[:2]:
                watermark = cv2.resize(watermark, (frame_region.shape[1], frame_region.shape[0]))

            # 确保通道数匹配
            if len(frame_region.shape) == 3 and len(watermark.shape) == 3:
                if frame_region.shape[2] != watermark.shape[2]:
                    if watermark.shape[2] == 1:
                        watermark = cv2.cvtColor(watermark, cv2.COLOR_GRAY2BGR)
                    elif watermark.shape[2] == 4:
                        watermark = cv2.cvtColor(watermark, cv2.COLOR_BGRA2BGR)

            # 混合图像
            blended = cv2.addWeighted(watermark, alpha, frame_region, 1 - alpha, 0)
            frame[y:y+h, x:x+w] = blended

        except Exception as e:
            print(f"添加不带透明通道水印时出错: {e}")
            print(f"帧形状: {frame.shape}, 水印形状: {watermark.shape}")
            print(f"位置: ({x}, {y}), 尺寸: ({w}, {h})")

    def create_performance_dialog(self):
        """创建性能监控对话框"""
        self.performance_dialog = QDialog(self)
        self.performance_dialog.setWindowTitle("性能监控")
        self.performance_dialog.setFixedSize(300, 200)

        layout = QVBoxLayout(self.performance_dialog)

        title_label = QLabel("📊 性能监控")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        info_label = QLabel("性能监控功能正在开发中...")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        close_btn = ModernButton("关闭", "", "#607D8B")
        close_btn.clicked.connect(self.performance_dialog.hide)
        layout.addWidget(close_btn)

    def create_help_dialog(self):
        """创建帮助对话框"""
        self.help_dialog = QDialog(self)
        self.help_dialog.setWindowTitle("帮助")
        self.help_dialog.setFixedSize(500, 400)

        layout = QVBoxLayout(self.help_dialog)

        title_label = QLabel("❓ 使用帮助")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText("""
🎯 基本操作指南

📁 视频操作：
• 点击工具栏"📁 打开视频"加载视频文件
• 第一次点击加载视频1（单视频模式）
• 第二次点击加载视频2（双视频比较模式）
• 第三次点击可选择替换已有视频

▶️ 播放控制：
• 点击"▶️ 播放"开始播放视频
• 点击"⏸️ 暂停"暂停播放
• 拖动进度条跳转到指定位置

⚙️ 显示设置：
• 点击"⚙️ 显示设置"打开完整配置管理器
• 包含关节点选择、显示参数、颜色设置三个标签页
• 支持保存和加载完整配置
• 可按身体部位分组选择关节点
• 调整线条粗细、关节点大小和形状
• 自定义关键点和连接线颜色

💡 使用技巧：
• 所有设置实时生效
• 支持多种视频格式
• 可同时播放两个视频进行对比
        """)
        layout.addWidget(help_text)

        close_btn = ModernButton("关闭", "", "#607D8B")
        close_btn.clicked.connect(self.help_dialog.hide)
        layout.addWidget(close_btn)



    def start_export(self):
        """开始导出视频"""
        try:
            # 检查是否有视频可导出
            if not self.export_video1_cb.isChecked() and not self.export_video2_cb.isChecked():
                QMessageBox.warning(self.export_dialog, "警告", "请至少选择一个视频进行导出")
                return

            if self.export_video1_cb.isChecked() and self.cap1 is None:
                QMessageBox.warning(self.export_dialog, "警告", "视频1未加载")
                return

            if self.export_video2_cb.isChecked() and self.cap2 is None:
                QMessageBox.warning(self.export_dialog, "警告", "视频2未加载")
                return

            # 选择保存路径
            if self.export_video1_cb.isChecked() and self.export_video2_cb.isChecked():
                # 导出两个视频，选择文件夹
                save_dir = QFileDialog.getExistingDirectory(
                    self.export_dialog,
                    "选择保存文件夹",
                    ""
                )
                if not save_dir:
                    return

                # 导出多个视频
                export_count = 0
                total_exports = 0
                if self.export_video1_cb.isChecked():
                    total_exports += 1
                if self.export_video2_cb.isChecked():
                    total_exports += 1

                # 显示进度区域
                self.show_export_progress()

                # 导出视频1
                if self.export_video1_cb.isChecked() and not self.export_cancelled:
                    export_count += 1
                    self.export_status_label.setText(f"📹 准备导出第 {export_count}/{total_exports} 个视频...")
                    output_path1 = f"{save_dir}/video1_with_pose.mp4"
                    self.export_video_with_pose(self.cap1, output_path1, 1)

                # 导出视频2
                if self.export_video2_cb.isChecked() and not self.export_cancelled:
                    export_count += 1
                    self.export_status_label.setText(f"📹 准备导出第 {export_count}/{total_exports} 个视频...")
                    output_path2 = f"{save_dir}/video2_with_pose.mp4"
                    self.export_video_with_pose(self.cap2, output_path2, 2)

                # 隐藏进度区域
                self.hide_export_progress()

                # 全部完成
                if total_exports > 1 and not self.export_cancelled:
                    QMessageBox.information(
                        self.export_dialog,
                        "批量导出完成",
                        f"🎉 所有 {total_exports} 个视频已成功导出到:\n{save_dir}"
                    )
                elif self.export_cancelled:
                    QMessageBox.information(
                        self.export_dialog,
                        "导出已取消",
                        "❌ 批量导出已被用户取消"
                    )
            else:
                # 导出单个视频，选择文件名
                output_path, _ = QFileDialog.getSaveFileName(
                    self.export_dialog,
                    "保存导出视频",
                    "exported_video_with_pose.mp4",
                    "视频文件 (*.mp4);;所有文件 (*.*)"
                )
                if not output_path:
                    return

                # 显示进度区域
                self.show_export_progress()

                if self.export_video1_cb.isChecked():
                    self.export_video_with_pose(self.cap1, output_path, 1)
                else:
                    self.export_video_with_pose(self.cap2, output_path, 2)

                # 检查是否被取消
                if self.export_cancelled:
                    QMessageBox.information(
                        self.export_dialog,
                        "导出已取消",
                        "❌ 视频导出已被用户取消"
                    )

                # 隐藏进度区域
                self.hide_export_progress()

        except Exception as e:
            # 隐藏进度区域
            self.hide_export_progress()
            QMessageBox.critical(self.export_dialog, "错误", f"导出失败: {str(e)}")

    def show_export_progress(self):
        """显示导出进度区域"""
        self.export_progress_group.setVisible(True)
        self.export_start_btn.setVisible(False)
        self.export_cancel_btn.setVisible(True)
        self.export_cancelled = False

        # 停止预览播放但保持预览窗口可见
        if hasattr(self, 'preview_playing') and self.preview_playing:
            self.preview_playing = False
            self.preview_timer.stop()
            self.preview_play_btn.setText("▶️ 播放预览")

        # 强制更新UI
        QApplication.processEvents()

    def hide_export_progress(self):
        """隐藏导出进度区域"""
        self.export_progress_group.setVisible(False)
        self.export_start_btn.setVisible(True)
        self.export_cancel_btn.setVisible(False)

    def export_video_with_pose(self, cap, output_path, video_num):
        """导出带姿态检测的视频"""
        import time

        try:
            if not cap or not cap.isOpened():
                QMessageBox.critical(self.export_dialog, "错误", f"视频{video_num}未正确加载")
                return

            # 设置导出状态
            self.export_status_label.setText(f"🎬 正在准备导出视频{video_num}...")

            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 根据旋转角度计算输出视频尺寸
            if video_num == 1:
                rotation = getattr(self, 'export_video1_rotation', self.video1_rotation)
            else:
                rotation = getattr(self, 'export_video2_rotation', self.video2_rotation)

            # 90度和270度旋转会交换宽高
            if rotation == 1 or rotation == 3:  # 90度或270度
                output_width = original_height
                output_height = original_width
            else:  # 0度或180度
                output_width = original_width
                output_height = original_height

            # 根据设置调整参数
            output_fps = self.get_output_fps(fps)

            # 创建视频写入器，使用旋转后的尺寸
            # 尝试使用更兼容的编码器
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            out = cv2.VideoWriter(output_path, fourcc, output_fps, (output_width, output_height))

            # 如果H264失败，尝试使用mp4v
            if not out.isOpened():
                print("H264编码器失败，尝试使用mp4v编码器")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, output_fps, (output_width, output_height))

            if not out.isOpened():
                raise Exception(f"无法创建输出视频文件。尺寸: {output_width}x{output_height}, FPS: {output_fps}")

            # 调试信息
            print(f"导出视频{video_num}: 原始尺寸 {original_width}x{original_height}, 旋转角度 {rotation*90}°, 输出尺寸 {output_width}x{output_height}")

            # 重置视频到开头
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # 初始化进度跟踪
            self.export_progress.setMaximum(total_frames)
            self.export_progress.setValue(0)
            self.export_progress.setVisible(True)

            # 立即更新UI显示进度条
            QApplication.processEvents()

            # 时间跟踪
            start_time = time.time()
            frame_count = 0
            last_update_time = start_time

            # 更新初始状态
            self.frame_progress_label.setText(f"帧: 0 / {total_frames}")
            self.percentage_label.setText("0%")
            self.eta_label.setText("预计剩余: 计算中...")
            self.export_status_label.setText(f"🎬 正在导出视频{video_num}...")

            # 确保对话框保持在前台
            self.export_dialog.raise_()
            self.export_dialog.activateWindow()

            # 立即更新UI
            QApplication.processEvents()

            while True:
                # 检查是否取消导出
                if self.export_cancelled:
                    self.export_status_label.setText("❌ 导出已取消")
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                # 再次检查是否取消（在处理帧之前）
                if self.export_cancelled:
                    break

                # 处理姿态检测和水印
                processed_frame = self.process_frame_for_export(frame, video_num)

                # 验证帧尺寸是否与VideoWriter期望的尺寸一致
                frame_height, frame_width = processed_frame.shape[:2]
                if frame_width != output_width or frame_height != output_height:
                    print(f"警告: 帧尺寸不匹配! 期望: {output_width}x{output_height}, 实际: {frame_width}x{frame_height}")
                    # 调整帧尺寸以匹配VideoWriter
                    processed_frame = cv2.resize(processed_frame, (output_width, output_height))

                # 写入帧
                out.write(processed_frame)

                frame_count += 1
                current_time = time.time()

                # 每处理10帧或每秒更新一次进度（避免过于频繁的UI更新）
                if frame_count % 10 == 0 or (current_time - last_update_time) >= 1.0:
                    # 检查是否取消
                    if self.export_cancelled:
                        break

                    # 更新预览显示当前处理的帧
                    self.display_frame_in_widget(processed_frame, self.export_preview_widget)
                    # 更新进度条
                    self.export_progress.setValue(frame_count)

                    # 计算百分比
                    percentage = (frame_count / total_frames) * 100

                    # 计算预计剩余时间
                    elapsed_time = current_time - start_time
                    if frame_count > 0:
                        avg_time_per_frame = elapsed_time / frame_count
                        remaining_frames = total_frames - frame_count
                        eta_seconds = remaining_frames * avg_time_per_frame
                        eta_text = self.format_eta(eta_seconds)
                    else:
                        eta_text = "计算中..."

                    # 更新显示
                    self.frame_progress_label.setText(f"帧: {frame_count} / {total_frames}")
                    self.percentage_label.setText(f"{percentage:.1f}%")
                    self.eta_label.setText(f"预计剩余: {eta_text}")

                    # 更新状态文本
                    if percentage < 25:
                        status_icon = "🎬"
                    elif percentage < 50:
                        status_icon = "⚡"
                    elif percentage < 75:
                        status_icon = "🚀"
                    else:
                        status_icon = "🎯"

                    self.export_status_label.setText(
                        f"{status_icon} 正在导出视频{video_num}... {percentage:.1f}%"
                    )

                    # 处理GUI事件，保持界面响应
                    QApplication.processEvents()
                    last_update_time = current_time

                # 检查是否需要跳帧（根据帧率设置）
                if self.fps_combo.currentText() != "原始帧率":
                    frame_skip = self.calculate_frame_skip(fps, output_fps)
                    if frame_count % frame_skip != 0:
                        continue

            # 清理
            out.release()

            # 检查是否被取消
            if self.export_cancelled:
                # 删除未完成的文件
                try:
                    import os
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        self.export_status_label.setText("❌ 导出已取消，文件已删除")
                except Exception as e:
                    print(f"删除未完成文件时出错: {e}")
                    self.export_status_label.setText("❌ 导出已取消")
                return  # 直接返回，不执行后续的完成逻辑

            # 计算总耗时
            total_time = time.time() - start_time
            total_time_text = self.format_eta(total_time)

            # 完成状态
            self.export_progress.setValue(total_frames)
            self.frame_progress_label.setText(f"帧: {total_frames} / {total_frames}")
            self.percentage_label.setText("100%")
            self.eta_label.setText(f"总耗时: {total_time_text}")
            self.export_status_label.setText(f"✅ 视频{video_num}导出完成！")

            # 注意：不在这里隐藏进度区域，由调用方控制

            # 添加音频到导出的视频
            self.export_status_label.setText(f"🎵 正在添加音频到视频{video_num}...")
            QApplication.processEvents()

            final_output_path = self.add_audio_to_video(output_path, video_num)

            # 验证导出的文件
            import os
            file_size = os.path.getsize(final_output_path) if os.path.exists(final_output_path) else 0
            file_size_mb = file_size / (1024 * 1024)

            # 显示完成消息
            QMessageBox.information(
                self.export_dialog,
                "导出完成",
                f"🎉 视频{video_num}已成功导出！\n\n"
                f"📁 保存位置: {final_output_path}\n"
                f"⏱️ 总耗时: {total_time_text}\n"
                f"🎬 总帧数: {total_frames} 帧\n"
                f"📊 文件大小: {file_size_mb:.1f} MB\n"
                f"🔄 旋转角度: {rotation * 90}°\n"
                f"📐 输出尺寸: {output_width}x{output_height}\n"
                f"🎵 音频: 已包含原始音频"
            )

        except Exception as e:
            # 错误处理
            self.export_status_label.setText("❌ 导出失败")
            raise e

    def format_eta(self, seconds):
        """格式化时间显示"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分钟"

    def get_output_fps(self, original_fps):
        """获取输出帧率"""
        fps_text = self.fps_combo.currentText()
        if fps_text == "原始帧率":
            return original_fps
        elif fps_text == "30 FPS":
            return 30.0
        elif fps_text == "25 FPS":
            return 25.0
        elif fps_text == "15 FPS":
            return 15.0
        else:
            return original_fps

    def get_quality_settings(self):
        """获取质量设置"""
        quality = self.quality_combo.currentText()
        if quality == "高质量":
            return {"bitrate": "5000k", "crf": 18}
        elif quality == "中等质量":
            return {"bitrate": "2500k", "crf": 23}
        else:  # 压缩质量
            return {"bitrate": "1000k", "crf": 28}

    def calculate_frame_skip(self, original_fps, target_fps):
        """计算帧跳跃间隔"""
        if target_fps >= original_fps:
            return 1
        return int(original_fps / target_fps)

    def rotate_video1(self):
        """旋转视频1"""
        self.video1_rotation = (self.video1_rotation + 1) % 4
        self.update_status(f"视频1已旋转 {self.video1_rotation * 90}°")
        # 立即更新显示
        self.update_current_frame_display()

    def rotate_video2(self):
        """旋转视频2"""
        self.video2_rotation = (self.video2_rotation + 1) % 4
        self.update_status(f"视频2已旋转 {self.video2_rotation * 90}°")
        # 立即更新显示
        self.update_current_frame_display()

    def rotate_frame(self, frame, rotation):
        """旋转帧"""
        if rotation == 0:
            return frame
        elif rotation == 1:  # 90度顺时针
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 2:  # 180度
            return cv2.rotate(frame, cv2.ROTATE_180)
        elif rotation == 3:  # 270度顺时针 (90度逆时针)
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return frame

    def update_current_frame_display(self):
        """更新当前帧显示（用于旋转后立即刷新）"""
        try:
            # 更新视频1
            if self.cap1 is not None:
                current_pos1 = int(self.cap1.get(cv2.CAP_PROP_POS_FRAMES))
                ret1, frame1 = self.cap1.read()
                if ret1:
                    # 应用旋转
                    rotated_frame1 = self.rotate_frame(frame1, self.video1_rotation)
                    # 处理姿态检测
                    processed_frame1 = self.process_pose_detection(rotated_frame1)
                    # 显示帧
                    self.display_frame_in_widget(processed_frame1, self.video1_widget)
                    # 恢复视频位置
                    self.cap1.set(cv2.CAP_PROP_POS_FRAMES, current_pos1)

            # 更新视频2
            if self.cap2 is not None:
                current_pos2 = int(self.cap2.get(cv2.CAP_PROP_POS_FRAMES))
                ret2, frame2 = self.cap2.read()
                if ret2:
                    # 应用旋转
                    rotated_frame2 = self.rotate_frame(frame2, self.video2_rotation)
                    # 处理姿态检测
                    processed_frame2 = self.process_pose_detection(rotated_frame2)
                    # 显示帧
                    self.display_frame_in_widget(processed_frame2, self.video2_widget)
                    # 恢复视频位置
                    self.cap2.set(cv2.CAP_PROP_POS_FRAMES, current_pos2)

        except Exception as e:
            print(f"更新当前帧显示时出错: {e}")

    def add_audio_to_video(self, video_path, video_num):
        """使用FFmpeg将原始音频添加到导出的视频中"""
        import subprocess
        import os

        try:
            # 获取原始视频文件路径
            if video_num == 1:
                original_video_path = getattr(self, 'video1_path', None)
            else:
                original_video_path = getattr(self, 'video2_path', None)

            if not original_video_path or not os.path.exists(original_video_path):
                print(f"原始视频文件不存在，跳过音频添加: {original_video_path}")
                return video_path

            # 检查原始视频是否有音频流
            check_audio_cmd = [
                'ffprobe', '-v', 'quiet', '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name', '-of', 'csv=p=0',
                original_video_path
            ]

            try:
                result = subprocess.run(check_audio_cmd, capture_output=True, text=True, timeout=10)
                if not result.stdout.strip():
                    print(f"原始视频没有音频流，跳过音频添加")
                    return video_path
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                print(f"检查音频流失败，跳过音频添加: {e}")
                return video_path

            # 创建带音频的最终输出文件路径
            base_name = os.path.splitext(video_path)[0]
            final_output_path = f"{base_name}_with_audio.mp4"

            # 使用FFmpeg合并视频和音频
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # -y 覆盖输出文件
                '-i', video_path,  # 输入视频（无音频）
                '-i', original_video_path,  # 原始视频（有音频）
                '-c:v', 'copy',  # 复制视频流（不重新编码）
                '-c:a', 'aac',   # 音频编码为AAC
                '-map', '0:v:0',  # 使用第一个输入的视频流
                '-map', '1:a:0',  # 使用第二个输入的音频流
                '-shortest',      # 以较短的流为准
                final_output_path
            ]

            print(f"执行FFmpeg命令: {' '.join(ffmpeg_cmd)}")

            # 执行FFmpeg命令
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"音频添加成功: {final_output_path}")
                # 删除临时的无音频视频文件
                try:
                    os.remove(video_path)
                    print(f"删除临时文件: {video_path}")
                except:
                    pass
                return final_output_path
            else:
                print(f"FFmpeg执行失败: {result.stderr}")
                return video_path

        except Exception as e:
            print(f"添加音频时出错: {e}")
            return video_path

    def cancel_export(self):
        """取消导出"""
        reply = QMessageBox.question(
            self.export_dialog,
            "确认取消",
            "确定要取消当前的视频导出吗？\n已处理的进度将会丢失。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.export_cancelled = True
            self.export_status_label.setText("⏹️ 正在取消导出...")

            # 强制更新UI显示取消状态
            QApplication.processEvents()

            # 稍等一下让用户看到取消状态
            QTimer.singleShot(1000, self.hide_export_progress)

    def toggle_playback1(self):
        """切换视频1播放状态"""
        if self.cap1 is None:
            self.update_status("请先加载视频1")
            return

        if self.is_playing1:
            # 暂停视频1
            self.is_playing1 = False
            self.play_button1.setText("▶️")
            self.update_status("视频1已暂停")

            # 如果两个视频都暂停了，停止定时器
            if not self.is_playing2:
                self.play_timer.stop()
        else:
            # 开始播放视频1
            self.is_playing1 = True
            self.play_button1.setText("⏸️")
            self.update_status("视频1正在播放")

            # 启动定时器
            if self.fps1 > 0:
                self.play_timer_interval = int(1000 / self.fps1)
            else:
                self.play_timer_interval = 33  # 默认30fps

            if not self.play_timer.isActive():
                self.play_timer.start(self.play_timer_interval)

    def toggle_playback2(self):
        """切换视频2播放状态"""
        if self.cap2 is None:
            self.update_status("请先加载视频2")
            return

        if self.is_playing2:
            # 暂停视频2
            self.is_playing2 = False
            self.play_button2.setText("▶️")
            self.update_status("视频2已暂停")

            # 如果两个视频都暂停了，停止定时器
            if not self.is_playing1:
                self.play_timer.stop()
        else:
            # 开始播放视频2
            self.is_playing2 = True
            self.play_button2.setText("⏸️")
            self.update_status("视频2正在播放")

            # 启动定时器
            if self.fps2 > 0:
                timer_interval = int(1000 / self.fps2)
            else:
                timer_interval = 33  # 默认30fps

            if not self.play_timer.isActive():
                self.play_timer.start(timer_interval)

    def update_frame(self):
        """更新视频帧"""
        try:
            # 检查是否有视频在播放
            if not (self.is_playing1 or self.is_playing2):
                return

            video1_ended = False
            video2_ended = False

            # 处理视频1
            if self.is_playing1 and self.cap1 is not None:
                ret1, frame1 = self.cap1.read()

                if ret1:
                    self.current_frame1 = frame1
                    self.current_frame_pos1 = int(self.cap1.get(cv2.CAP_PROP_POS_FRAMES))

                    # 应用旋转
                    rotated_frame1 = self.rotate_frame(frame1, self.video1_rotation)

                    # 处理姿态检测
                    processed_frame1 = self.process_pose_detection(rotated_frame1)

                    # 显示帧
                    self.display_frame_in_widget(processed_frame1, self.video1_widget)

                    # 更新进度条1
                    if self.total_frames1 > 0:
                        progress = (self.current_frame_pos1 / self.total_frames1) * 100
                        self.progress_slider1.setValue(int(progress))

                    # 更新时间显示1
                    self.update_time_display1()
                else:
                    video1_ended = True

            # 处理视频2
            if self.is_playing2 and self.video2_loaded and self.cap2 is not None:
                ret2, frame2 = self.cap2.read()

                if ret2:
                    self.current_frame2 = frame2
                    self.current_frame_pos2 = int(self.cap2.get(cv2.CAP_PROP_POS_FRAMES))

                    # 应用旋转
                    rotated_frame2 = self.rotate_frame(frame2, self.video2_rotation)

                    # 处理姿态检测
                    processed_frame2 = self.process_pose_detection(rotated_frame2)

                    # 显示帧
                    self.display_frame_in_widget(processed_frame2, self.video2_widget)

                    # 更新进度条2
                    if self.total_frames2 > 0:
                        progress = (self.current_frame_pos2 / self.total_frames2) * 100
                        self.progress_slider2.setValue(int(progress))

                    # 更新时间显示2
                    self.update_time_display2()
                else:
                    video2_ended = True

            # 检查视频1是否播放完毕
            if video1_ended:
                self.is_playing1 = False
                self.play_button1.setText("▶️")
                self.update_status("视频1播放完毕")

                # 重置视频1到开头
                if self.cap1:
                    self.cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame_pos1 = 0
                    self.progress_slider1.setValue(0)

            # 检查视频2是否播放完毕
            if video2_ended:
                self.is_playing2 = False
                self.play_button2.setText("▶️")
                self.update_status("视频2播放完毕")

                # 重置视频2到开头
                if self.cap2:
                    self.cap2.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame_pos2 = 0
                    self.progress_slider2.setValue(0)

            # 如果两个视频都停止了，停止定时器
            if not self.is_playing1 and not self.is_playing2:
                self.play_timer.stop()

        except Exception as e:
            print(f"更新帧时出错: {e}")
            self.update_status(f"播放错误: {str(e)}")

    def process_pose_detection(self, frame):
        """处理姿态检测"""
        try:
            if not self.mediapipe_initialized:
                return frame

            # 转换颜色空间
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 进行姿态检测
            results = self.pose.process(rgb_frame)

            # 绘制姿态关键点
            annotated_frame = frame.copy()
            if results.pose_landmarks:
                self.draw_custom_landmarks(annotated_frame, results.pose_landmarks)

            return annotated_frame

        except Exception as e:
            print(f"姿态检测处理出错: {e}")
            return frame

    def draw_custom_landmarks(self, image, landmarks):
        """绘制自定义关键点"""
        try:
            if not landmarks:
                return

            height, width, _ = image.shape

            # 绘制连接线
            for connection in self.mp_pose.POSE_CONNECTIONS:
                start_idx = connection[0]
                end_idx = connection[1]

                if (start_idx < len(landmarks.landmark) and
                    end_idx < len(landmarks.landmark) and
                    self.landmark_visibility.get(start_idx, True) and
                    self.landmark_visibility.get(end_idx, True)):

                    start_landmark = landmarks.landmark[start_idx]
                    end_landmark = landmarks.landmark[end_idx]

                    if (start_landmark.visibility > 0.5 and end_landmark.visibility > 0.5):
                        start_point = (
                            int(start_landmark.x * width),
                            int(start_landmark.y * height)
                        )
                        end_point = (
                            int(end_landmark.x * width),
                            int(end_landmark.y * height)
                        )

                        # 绘制连接线
                        cv2.line(image, start_point, end_point,
                                self.connection_color, self.line_thickness)

            # 绘制关键点
            for i, landmark in enumerate(landmarks.landmark):
                if (landmark.visibility > 0.5 and
                    self.landmark_visibility.get(i, True)):

                    x = int(landmark.x * width)
                    y = int(landmark.y * height)

                    # 绘制关键点
                    cv2.circle(image, (x, y), self.landmark_size,
                             self.landmark_color, -1)

        except Exception as e:
            print(f"绘制关键点时出错: {e}")

    def update_time_display1(self):
        """更新视频1时间显示"""
        try:
            if self.cap1 and self.fps1 > 0:
                current_seconds = self.current_frame_pos1 / self.fps1
                total_seconds = self.total_frames1 / self.fps1

                current_time = self.format_time(current_seconds)
                total_time = self.format_time(total_seconds)

                self.time_label1.setText(f"{current_time} / {total_time}")

        except Exception as e:
            print(f"更新视频1时间显示时出错: {e}")

    def update_time_display2(self):
        """更新视频2时间显示"""
        try:
            if self.cap2 and self.fps2 > 0:
                current_seconds = self.current_frame_pos2 / self.fps2
                total_seconds = self.total_frames2 / self.fps2

                current_time = self.format_time(current_seconds)
                total_time = self.format_time(total_seconds)

                self.time_label2.setText(f"{current_time} / {total_time}")

        except Exception as e:
            print(f"更新视频2时间显示时出错: {e}")

    def format_time(self, seconds):
        """格式化时间显示"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    # 视频1进度条控制
    def on_slider1_pressed(self):
        """视频1进度条按下事件"""
        self.slider1_dragging = True

    def on_slider1_released(self):
        """视频1进度条释放事件"""
        self.slider1_dragging = False
        self.seek_to_position1()

    def on_slider1_value_changed(self, value):
        """视频1进度条值改变事件"""
        if not hasattr(self, 'slider1_dragging'):
            self.slider1_dragging = False

        if not self.slider1_dragging:
            return

        # 实时更新时间显示
        if self.cap1 and self.total_frames1 > 0:
            target_frame = int((value / 100.0) * self.total_frames1)
            target_seconds = target_frame / self.fps1 if self.fps1 > 0 else 0
            total_seconds = self.total_frames1 / self.fps1 if self.fps1 > 0 else 0

            current_time = self.format_time(target_seconds)
            total_time = self.format_time(total_seconds)
            self.time_label1.setText(f"{current_time} / {total_time}")

    # 视频2进度条控制
    def on_slider2_pressed(self):
        """视频2进度条按下事件"""
        self.slider2_dragging = True

    def on_slider2_released(self):
        """视频2进度条释放事件"""
        self.slider2_dragging = False
        self.seek_to_position2()

    def on_slider2_value_changed(self, value):
        """视频2进度条值改变事件"""
        if not hasattr(self, 'slider2_dragging'):
            self.slider2_dragging = False

        if not self.slider2_dragging:
            return

        # 实时更新时间显示
        if self.cap2 and self.total_frames2 > 0:
            target_frame = int((value / 100.0) * self.total_frames2)
            target_seconds = target_frame / self.fps2 if self.fps2 > 0 else 0
            total_seconds = self.total_frames2 / self.fps2 if self.fps2 > 0 else 0

            current_time = self.format_time(target_seconds)
            total_time = self.format_time(total_seconds)
            self.time_label2.setText(f"{current_time} / {total_time}")

    def seek_to_position1(self):
        """跳转视频1到指定位置"""
        try:
            progress = self.progress_slider1.value() / 100.0

            if self.cap1 and self.total_frames1 > 0:
                target_frame = int(progress * self.total_frames1)

                # 设置视频位置
                self.cap1.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                self.current_frame_pos1 = target_frame

                # 读取并显示当前帧
                ret, frame = self.cap1.read()
                if ret:
                    self.current_frame1 = frame
                    processed_frame = self.process_pose_detection(frame)
                    self.display_frame_in_widget(processed_frame, self.video1_widget)

                    # 回退一帧，因为read()会前进一帧
                    self.cap1.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

                # 更新时间显示
                self.update_time_display1()

        except Exception as e:
            print(f"跳转视频1位置时出错: {e}")

    def seek_to_position2(self):
        """跳转视频2到指定位置"""
        try:
            progress = self.progress_slider2.value() / 100.0

            if self.cap2 and self.total_frames2 > 0:
                target_frame = int(progress * self.total_frames2)

                # 设置视频位置
                self.cap2.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                self.current_frame_pos2 = target_frame

                # 读取并显示当前帧
                ret, frame = self.cap2.read()
                if ret:
                    self.current_frame2 = frame
                    processed_frame = self.process_pose_detection(frame)
                    self.display_frame_in_widget(processed_frame, self.video2_widget)

                    # 回退一帧，因为read()会前进一帧
                    self.cap2.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

                # 更新时间显示
                self.update_time_display2()

        except Exception as e:
            print(f"跳转视频2位置时出错: {e}")

    def create_landmark_selector_dialog(self):
        """创建完整配置管理器对话框"""
        self.landmark_selector_dialog = QDialog(self)
        self.landmark_selector_dialog.setWindowTitle("完整配置管理器")
        self.landmark_selector_dialog.setFixedSize(500, 700)

        # 设置对话框样式，确保在日间/夜间模式下都保持一致
        self.landmark_selector_dialog.setStyleSheet("""
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
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
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
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNEw2IDdMOSA0IiBzdHJva2U9IiM3Zjg2OWMiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                width: 12px;
                height: 12px;
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
        """)

        layout = QVBoxLayout(self.landmark_selector_dialog)

        # 标题
        title_label = QLabel("⚙️ 完整配置管理器")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)

        # 创建标签页
        self.config_tabs = QTabWidget()
        self.config_tabs.setStyleSheet("""
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
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

        # 创建各个标签页
        self.create_landmark_tab()
        self.create_display_tab()
        self.create_color_tab()

        layout.addWidget(self.config_tabs)

    def create_landmark_tab(self):
        """创建关节点选择标签页"""
        landmark_widget = QWidget()
        layout = QVBoxLayout(landmark_widget)

        # 控制按钮
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)

        btn_all = ModernButton("全选", "", "#4CAF50")
        btn_all.clicked.connect(self.select_all_landmarks)
        control_layout.addWidget(btn_all)

        btn_none = ModernButton("全不选", "", "#F44336")
        btn_none.clicked.connect(self.deselect_all_landmarks)
        control_layout.addWidget(btn_none)

        btn_invert = ModernButton("反选", "", "#FF9800")
        btn_invert.clicked.connect(self.invert_landmark_selection)
        control_layout.addWidget(btn_invert)

        layout.addWidget(control_frame)

        # 完整配置管理区域
        config_management_group = QGroupBox("完整配置管理")
        config_management_layout = QVBoxLayout(config_management_group)

        # 保存配置
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel("配置名称:"))

        self.config_name_input = QLineEdit()
        self.config_name_input.setPlaceholderText("输入配置名称...")
        save_layout.addWidget(self.config_name_input)

        save_btn = ModernButton("保存完整配置", "", "#2196F3")
        save_btn.clicked.connect(self.save_complete_config)
        save_layout.addWidget(save_btn)

        config_management_layout.addLayout(save_layout)

        # 快捷选择
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("快捷选择:"))

        self.config_combo = QComboBox()
        self.config_combo.setMinimumWidth(150)
        quick_layout.addWidget(self.config_combo)

        load_btn = ModernButton("应用", "", "#4CAF50")
        load_btn.clicked.connect(self.load_complete_config)
        quick_layout.addWidget(load_btn)

        delete_btn = ModernButton("删除", "", "#F44336")
        delete_btn.clicked.connect(self.delete_complete_config)
        quick_layout.addWidget(delete_btn)

        config_management_layout.addLayout(quick_layout)

        # 预设配置按钮
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设配置:"))

        preset_buttons = [
            ("上半身", self.preset_upper_body),
            ("下半身", self.preset_lower_body),
            ("核心关节", self.preset_core_joints),
            ("面部", self.preset_face_only)
        ]

        for text, callback in preset_buttons:
            btn = ModernButton(text, "", "#9C27B0")
            btn.clicked.connect(callback)
            preset_layout.addWidget(btn)

        config_management_layout.addLayout(preset_layout)

        layout.addWidget(config_management_group)

        # 加载保存的配置
        self.load_saved_complete_configs()

        # 分组按钮
        group_frame = QFrame()
        group_layout = QHBoxLayout(group_frame)

        for group_name in self.landmark_groups.keys():
            btn = ModernButton(f"选择{group_name}", "", "#2196F3")
            btn.clicked.connect(lambda _, g=group_name: self.select_landmark_group(g))
            group_layout.addWidget(btn)

        layout.addWidget(group_frame)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 创建关节点复选框
        self.landmark_checkboxes = {}

        for group_name, landmark_indices in self.landmark_groups.items():
            # 分组标题
            group_label = QLabel(f"{group_name}:")
            group_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            group_label.setStyleSheet("color: #34495e; padding: 10px 0 5px 0;")
            scroll_layout.addWidget(group_label)

            # 该分组的关节点
            for landmark_idx in landmark_indices:
                landmark_name = self.landmark_info[landmark_idx]

                checkbox = QCheckBox(f"{landmark_idx}: {landmark_name}")
                checkbox.setChecked(self.landmark_visibility[landmark_idx])
                checkbox.stateChanged.connect(
                    lambda state, idx=landmark_idx: self.on_landmark_checkbox_changed(idx, state)
                )

                checkbox.setStyleSheet("""
                    QCheckBox {
                        padding: 5px;
                        font-size: 11px;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                    QCheckBox::indicator:unchecked {
                        border: 2px solid #bdc3c7;
                        background: white;
                        border-radius: 3px;
                    }
                    QCheckBox::indicator:checked {
                        border: 2px solid #3498db;
                        background: #3498db;
                        border-radius: 3px;
                    }
                """)

                self.landmark_checkboxes[landmark_idx] = checkbox
                scroll_layout.addWidget(checkbox)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 添加到标签页
        self.config_tabs.addTab(landmark_widget, "👤 关节点选择")

    def create_display_tab(self):
        """创建显示设置标签页"""
        display_widget = QWidget()
        layout = QVBoxLayout(display_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # 线条粗细设置
        thickness_group = QGroupBox("线条粗细")
        thickness_layout = QVBoxLayout(thickness_group)

        thickness_control_layout = QHBoxLayout()
        thickness_control_layout.addWidget(QLabel("粗细:"))

        self.config_thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.config_thickness_slider.setRange(1, 8)
        self.config_thickness_slider.setValue(self.line_thickness)
        self.config_thickness_slider.valueChanged.connect(self.on_config_thickness_changed)
        thickness_control_layout.addWidget(self.config_thickness_slider)

        self.config_thickness_label = QLabel(str(self.line_thickness))
        self.config_thickness_label.setFixedWidth(30)
        thickness_control_layout.addWidget(self.config_thickness_label)

        thickness_layout.addLayout(thickness_control_layout)
        layout.addWidget(thickness_group)

        # 关节点大小设置
        size_group = QGroupBox("关节点大小")
        size_layout = QVBoxLayout(size_group)

        size_control_layout = QHBoxLayout()
        size_control_layout.addWidget(QLabel("大小:"))

        self.config_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.config_size_slider.setRange(3, 15)
        self.config_size_slider.setValue(self.landmark_size)
        self.config_size_slider.valueChanged.connect(self.on_config_size_changed)
        size_control_layout.addWidget(self.config_size_slider)

        self.config_size_label = QLabel(str(self.landmark_size))
        self.config_size_label.setFixedWidth(30)
        size_control_layout.addWidget(self.config_size_label)

        size_layout.addLayout(size_control_layout)
        layout.addWidget(size_group)

        # 关节点形状设置
        shape_group = QGroupBox("关节点形状")
        shape_layout = QVBoxLayout(shape_group)

        self.config_shape_combo = QComboBox()
        self.config_shape_combo.addItems(["圆形", "正方形", "菱形"])
        self.config_shape_combo.setCurrentText("正方形")
        self.config_shape_combo.currentTextChanged.connect(self.on_config_shape_changed)
        shape_layout.addWidget(self.config_shape_combo)

        layout.addWidget(shape_group)

        # 添加弹性空间
        layout.addStretch()

        # 添加到标签页
        self.config_tabs.addTab(display_widget, "⚙️ 显示设置")

    def create_color_tab(self):
        """创建颜色设置标签页"""
        color_widget = QWidget()
        layout = QVBoxLayout(color_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # 关键点颜色设置
        landmark_color_group = QGroupBox("关键点颜色")
        landmark_color_layout = QVBoxLayout(landmark_color_group)

        landmark_color_control_layout = QHBoxLayout()
        landmark_color_control_layout.addWidget(QLabel("颜色:"))

        self.config_landmark_color_combo = QComboBox()
        self.config_landmark_color_combo.addItems(["绿色", "红色", "蓝色", "黄色", "青色", "白色"])
        self.config_landmark_color_combo.setCurrentText("绿色")
        self.config_landmark_color_combo.currentTextChanged.connect(self.on_config_landmark_color_changed)
        landmark_color_control_layout.addWidget(self.config_landmark_color_combo)

        landmark_color_layout.addLayout(landmark_color_control_layout)
        layout.addWidget(landmark_color_group)

        # 连接线颜色设置
        connection_color_group = QGroupBox("连接线颜色")
        connection_color_layout = QVBoxLayout(connection_color_group)

        connection_color_control_layout = QHBoxLayout()
        connection_color_control_layout.addWidget(QLabel("颜色:"))

        self.config_connection_color_combo = QComboBox()
        self.config_connection_color_combo.addItems(["红色", "绿色", "蓝色", "黄色", "青色", "白色"])
        self.config_connection_color_combo.setCurrentText("红色")
        self.config_connection_color_combo.currentTextChanged.connect(self.on_config_connection_color_changed)
        connection_color_control_layout.addWidget(self.config_connection_color_combo)

        connection_color_layout.addLayout(connection_color_control_layout)
        layout.addWidget(connection_color_group)

        # 预设颜色方案
        preset_color_group = QGroupBox("预设颜色方案")
        preset_color_layout = QVBoxLayout(preset_color_group)

        preset_buttons_layout = QHBoxLayout()

        classic_btn = ModernButton("经典", "", "#2196F3")
        classic_btn.clicked.connect(lambda: self.apply_color_preset("经典"))
        preset_buttons_layout.addWidget(classic_btn)

        vibrant_btn = ModernButton("活力", "", "#FF5722")
        vibrant_btn.clicked.connect(lambda: self.apply_color_preset("活力"))
        preset_buttons_layout.addWidget(vibrant_btn)

        soft_btn = ModernButton("柔和", "", "#9C27B0")
        soft_btn.clicked.connect(lambda: self.apply_color_preset("柔和"))
        preset_buttons_layout.addWidget(soft_btn)

        preset_color_layout.addLayout(preset_buttons_layout)
        layout.addWidget(preset_color_group)

        # 添加弹性空间
        layout.addStretch()

        # 添加到标签页
        self.config_tabs.addTab(color_widget, "🎨 颜色设置")

        # 关闭按钮
        close_btn = ModernButton("关闭", "", "#607D8B")
        close_btn.clicked.connect(self.landmark_selector_dialog.hide)
        layout.addWidget(close_btn)

    def select_all_landmarks(self):
        """选择所有关节点"""
        for i in range(33):
            self.landmark_visibility[i] = True
            if i in self.landmark_checkboxes:
                self.landmark_checkboxes[i].setChecked(True)

    def deselect_all_landmarks(self):
        """取消选择所有关节点"""
        for i in range(33):
            self.landmark_visibility[i] = False
            if i in self.landmark_checkboxes:
                self.landmark_checkboxes[i].setChecked(False)

    def invert_landmark_selection(self):
        """反选关节点"""
        for i in range(33):
            self.landmark_visibility[i] = not self.landmark_visibility[i]
            if i in self.landmark_checkboxes:
                self.landmark_checkboxes[i].setChecked(self.landmark_visibility[i])

    def select_landmark_group(self, group_name):
        """选择特定分组的关节点"""
        # 先取消所有选择
        self.deselect_all_landmarks()

        # 选择指定分组
        if group_name in self.landmark_groups:
            for landmark_idx in self.landmark_groups[group_name]:
                self.landmark_visibility[landmark_idx] = True
                if landmark_idx in self.landmark_checkboxes:
                    self.landmark_checkboxes[landmark_idx].setChecked(True)

    def on_landmark_checkbox_changed(self, landmark_idx, state):
        """关节点复选框状态改变"""
        self.landmark_visibility[landmark_idx] = (state == Qt.CheckState.Checked.value)
        # 这里可以添加实时更新视频显示的逻辑

    def on_config_thickness_changed(self, value):
        """配置中线条粗细改变"""
        self.line_thickness = value
        self.config_thickness_label.setText(str(value))

    def on_config_size_changed(self, value):
        """配置中关节点大小改变"""
        self.landmark_size = value
        self.config_size_label.setText(str(value))

    def on_config_shape_changed(self, shape_name):
        """配置中关节点形状改变"""
        shape_map = {
            "圆形": "circle",
            "正方形": "square",
            "菱形": "diamond"
        }
        self.landmark_shape = shape_map.get(shape_name, "square")

    def on_config_landmark_color_changed(self, color_name):
        """配置中关键点颜色改变"""
        color_map = {
            "红色": (0, 0, 255),
            "绿色": (0, 255, 0),
            "蓝色": (255, 0, 0),
            "黄色": (0, 255, 255),
            "青色": (255, 255, 0),
            "白色": (255, 255, 255)
        }
        self.landmark_color = color_map.get(color_name, (0, 255, 0))

    def on_config_connection_color_changed(self, color_name):
        """配置中连接线颜色改变"""
        color_map = {
            "红色": (0, 0, 255),
            "绿色": (0, 255, 0),
            "蓝色": (255, 0, 0),
            "黄色": (0, 255, 255),
            "青色": (255, 255, 0),
            "白色": (255, 255, 255)
        }
        self.connection_color = color_map.get(color_name, (0, 0, 255))

    def apply_color_preset(self, preset_name):
        """应用颜色预设"""
        presets = {
            "经典": {"landmark": "绿色", "connection": "红色"},
            "活力": {"landmark": "红色", "connection": "黄色"},
            "柔和": {"landmark": "蓝色", "connection": "青色"}
        }

        if preset_name in presets:
            preset = presets[preset_name]
            self.config_landmark_color_combo.setCurrentText(preset["landmark"])
            self.config_connection_color_combo.setCurrentText(preset["connection"])
            self.update_status(f"已应用颜色预设: {preset_name}")

    def save_complete_config(self):
        """保存完整配置（关节点+显示+颜色）"""
        try:
            config_name = self.config_name_input.text().strip()
            if not config_name:
                QMessageBox.warning(self.landmark_selector_dialog, "警告", "请输入配置名称")
                return

            # 检查名称是否已存在
            if config_name in self.complete_configs:
                reply = QMessageBox.question(
                    self.landmark_selector_dialog,
                    "确认覆盖",
                    f"配置 '{config_name}' 已存在，是否覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            # 获取当前颜色设置的文本
            landmark_color_text = self.config_landmark_color_combo.currentText()
            connection_color_text = self.config_connection_color_combo.currentText()
            shape_text = self.config_shape_combo.currentText()

            # 保存完整配置
            complete_config = {
                "landmarks": self.landmark_visibility.copy(),
                "line_thickness": self.line_thickness,
                "landmark_size": self.landmark_size,
                "landmark_shape": shape_text,
                "landmark_color": landmark_color_text,
                "connection_color": connection_color_text
            }

            self.complete_configs[config_name] = complete_config

            # 保存到文件
            self.save_complete_configs_to_file()

            # 更新下拉框
            self.update_complete_config_combo()

            # 清空输入框
            self.config_name_input.clear()

            QMessageBox.information(
                self.landmark_selector_dialog,
                "保存成功",
                f"完整配置 '{config_name}' 已保存\n包含：关节点选择、显示设置、颜色设置"
            )

        except Exception as e:
            QMessageBox.critical(self.landmark_selector_dialog, "错误", f"保存配置失败: {str(e)}")

    def load_complete_config(self):
        """加载完整配置"""
        try:
            config_name = self.config_combo.currentText()
            if not config_name or config_name == "选择配置...":
                QMessageBox.warning(self.landmark_selector_dialog, "警告", "请选择要加载的配置")
                return

            if config_name not in self.complete_configs:
                QMessageBox.warning(self.landmark_selector_dialog, "警告", "配置不存在")
                return

            # 加载完整配置
            saved_config = self.complete_configs[config_name]

            # 更新关节点可见性
            landmarks_config = saved_config.get("landmarks", {})
            for i in range(33):
                self.landmark_visibility[i] = landmarks_config.get(i, True)

            # 更新显示设置
            self.line_thickness = saved_config.get("line_thickness", 2)
            self.landmark_size = saved_config.get("landmark_size", 8)
            self.landmark_shape = saved_config.get("landmark_shape", "square")

            # 更新颜色设置
            landmark_color_text = saved_config.get("landmark_color", "绿色")
            connection_color_text = saved_config.get("connection_color", "红色")
            shape_text = saved_config.get("landmark_shape", "正方形")

            # 应用颜色设置
            self.on_config_landmark_color_changed(landmark_color_text)
            self.on_config_connection_color_changed(connection_color_text)

            # 更新界面控件
            if hasattr(self, 'landmark_checkboxes'):
                for landmark_idx, checkbox in self.landmark_checkboxes.items():
                    checkbox.setChecked(self.landmark_visibility[landmark_idx])

            if hasattr(self, 'config_thickness_slider'):
                self.config_thickness_slider.setValue(self.line_thickness)
                self.config_thickness_label.setText(str(self.line_thickness))

            if hasattr(self, 'config_size_slider'):
                self.config_size_slider.setValue(self.landmark_size)
                self.config_size_label.setText(str(self.landmark_size))

            if hasattr(self, 'config_shape_combo'):
                self.config_shape_combo.setCurrentText(shape_text)

            if hasattr(self, 'config_landmark_color_combo'):
                self.config_landmark_color_combo.setCurrentText(landmark_color_text)

            if hasattr(self, 'config_connection_color_combo'):
                self.config_connection_color_combo.setCurrentText(connection_color_text)

            QMessageBox.information(
                self.landmark_selector_dialog,
                "加载成功",
                f"完整配置 '{config_name}' 已应用\n包含：关节点选择、显示设置、颜色设置"
            )

        except Exception as e:
            QMessageBox.critical(self.landmark_selector_dialog, "错误", f"加载配置失败: {str(e)}")

    def delete_complete_config(self):
        """删除完整配置"""
        try:
            config_name = self.config_combo.currentText()
            if not config_name or config_name == "选择配置...":
                QMessageBox.warning(self.landmark_selector_dialog, "警告", "请选择要删除的配置")
                return

            reply = QMessageBox.question(
                self.landmark_selector_dialog,
                "确认删除",
                f"确定要删除完整配置 '{config_name}' 吗？\n这将删除关节点选择、显示设置和颜色设置。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 删除配置
                if config_name in self.complete_configs:
                    del self.complete_configs[config_name]

                # 保存到文件
                self.save_complete_configs_to_file()

                # 更新下拉框
                self.update_complete_config_combo()

                QMessageBox.information(
                    self.landmark_selector_dialog,
                    "删除成功",
                    f"完整配置 '{config_name}' 已删除"
                )

        except Exception as e:
            QMessageBox.critical(self.landmark_selector_dialog, "错误", f"删除配置失败: {str(e)}")

    def load_saved_complete_configs(self):
        """加载保存的完整配置"""
        try:
            self.load_complete_configs_from_file()
            self.update_complete_config_combo()
        except Exception as e:
            print(f"加载完整配置时出错: {e}")
            self.complete_configs = {}



    def save_configs_to_file(self):
        """保存配置到文件"""
        try:
            import json
            import os

            # 创建配置目录
            config_dir = os.path.expanduser("~/.pose_detection_app")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            config_file = os.path.join(config_dir, "landmark_configs.json")

            # 转换为可序列化的格式
            serializable_configs = {}
            for name, config in self.landmark_configs.items():
                serializable_configs[name] = {str(k): v for k, v in config.items()}

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_configs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def load_configs_from_file(self):
        """从文件加载配置"""
        try:
            import json
            import os

            config_file = os.path.expanduser("~/.pose_detection_app/landmark_configs.json")

            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    serializable_configs = json.load(f)

                # 转换回原格式
                self.landmark_configs = {}
                for name, config in serializable_configs.items():
                    self.landmark_configs[name] = {int(k): v for k, v in config.items()}
            else:
                self.landmark_configs = {}

        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            self.landmark_configs = {}

    def save_complete_configs_to_file(self):
        """保存完整配置到文件"""
        try:
            import json
            import os

            # 创建配置目录
            config_dir = os.path.expanduser("~/.pose_detection_app")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            config_file = os.path.join(config_dir, "complete_configs.json")

            # 转换为可序列化的格式
            serializable_configs = {}
            for name, config in self.complete_configs.items():
                serializable_config = config.copy()
                # 转换landmarks字典的键为字符串
                if "landmarks" in serializable_config:
                    serializable_config["landmarks"] = {
                        str(k): v for k, v in serializable_config["landmarks"].items()
                    }
                serializable_configs[name] = serializable_config

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_configs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"保存完整配置文件时出错: {e}")

    def load_complete_configs_from_file(self):
        """从文件加载完整配置"""
        try:
            import json
            import os

            config_file = os.path.expanduser("~/.pose_detection_app/complete_configs.json")

            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    serializable_configs = json.load(f)

                # 转换回原格式
                self.complete_configs = {}
                for name, config in serializable_configs.items():
                    complete_config = config.copy()
                    # 转换landmarks字典的键回整数
                    if "landmarks" in complete_config:
                        complete_config["landmarks"] = {
                            int(k): v for k, v in complete_config["landmarks"].items()
                        }
                    self.complete_configs[name] = complete_config
            else:
                self.complete_configs = {}

        except Exception as e:
            print(f"加载完整配置文件时出错: {e}")
            self.complete_configs = {}

    def preset_upper_body(self):
        """预设：上半身关节点"""
        # 上半身：头部 + 上肢 + 躯干上部
        upper_body_landmarks = [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,  # 头部
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,  # 上肢
            23, 24  # 髋部（躯干连接）
        ]
        self.apply_preset_selection(upper_body_landmarks, "上半身")

    def preset_lower_body(self):
        """预设：下半身关节点"""
        # 下半身：髋部 + 腿部
        lower_body_landmarks = [
            23, 24, 25, 26, 27, 28, 29, 30, 31, 32  # 下肢
        ]
        self.apply_preset_selection(lower_body_landmarks, "下半身")

    def preset_core_joints(self):
        """预设：核心关节点"""
        # 核心关节：主要的身体连接点
        core_landmarks = [
            0,  # 鼻子
            11, 12,  # 肩膀
            13, 14,  # 肘部
            15, 16,  # 手腕
            23, 24,  # 髋部
            25, 26,  # 膝盖
            27, 28   # 脚踝
        ]
        self.apply_preset_selection(core_landmarks, "核心关节")

    def preset_face_only(self):
        """预设：仅面部关节点"""
        # 面部：眼、鼻、嘴、耳
        face_landmarks = [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10  # 面部所有点
        ]
        self.apply_preset_selection(face_landmarks, "面部")

    def apply_preset_selection(self, selected_landmarks, preset_name):
        """应用预设选择"""
        try:
            # 先全部取消选择
            for i in range(33):
                self.landmark_visibility[i] = False

            # 选择指定的关节点
            for landmark_idx in selected_landmarks:
                if landmark_idx < 33:
                    self.landmark_visibility[landmark_idx] = True

            # 更新复选框状态
            for landmark_idx, checkbox in self.landmark_checkboxes.items():
                checkbox.setChecked(self.landmark_visibility[landmark_idx])

            # 显示提示
            self.update_status(f"已应用预设: {preset_name}")

        except Exception as e:
            print(f"应用预设配置时出错: {e}")

    def update_toolbar_config_combo(self):
        """更新工具栏配置下拉框"""
        self.toolbar_config_combo.clear()
        self.toolbar_config_combo.addItem("选择配置...")

        # 添加预设配置
        self.toolbar_config_combo.addItem("🔸 全部关节")
        self.toolbar_config_combo.addItem("🔸 上半身")
        self.toolbar_config_combo.addItem("🔸 下半身")
        self.toolbar_config_combo.addItem("🔸 核心关节")
        self.toolbar_config_combo.addItem("🔸 面部")

        # 添加自定义完整配置
        if self.complete_configs:
            self.toolbar_config_combo.addItem("─────────")  # 分隔线
            for config_name in sorted(self.complete_configs.keys()):
                self.toolbar_config_combo.addItem(f"⭐ {config_name}")

    def on_toolbar_config_changed(self, config_text):
        """工具栏配置选择改变"""
        try:
            if config_text == "选择配置..." or config_text == "─────────":
                return

            # 处理预设配置
            if config_text == "🔸 全部关节":
                self.select_all_landmarks()
                self.update_status("已应用: 全部关节")
            elif config_text == "🔸 上半身":
                self.preset_upper_body()
            elif config_text == "🔸 下半身":
                self.preset_lower_body()
            elif config_text == "🔸 核心关节":
                self.preset_core_joints()
            elif config_text == "🔸 面部":
                self.preset_face_only()
            elif config_text.startswith("⭐ "):
                # 处理自定义完整配置
                config_name = config_text[2:]  # 移除"⭐ "前缀
                if config_name in self.complete_configs:
                    self.apply_complete_config_from_toolbar(config_name)

            # 重置选择
            self.toolbar_config_combo.setCurrentIndex(0)

        except Exception as e:
            print(f"应用工具栏配置时出错: {e}")

    def apply_complete_config_from_toolbar(self, config_name):
        """从工具栏应用完整配置"""
        try:
            if config_name not in self.complete_configs:
                return

            saved_config = self.complete_configs[config_name]

            # 更新关节点可见性
            landmarks_config = saved_config.get("landmarks", {})
            for i in range(33):
                self.landmark_visibility[i] = landmarks_config.get(i, True)

            # 更新显示设置
            self.line_thickness = saved_config.get("line_thickness", 2)
            self.landmark_size = saved_config.get("landmark_size", 8)
            self.landmark_shape = saved_config.get("landmark_shape", "square")

            # 更新颜色设置
            landmark_color_text = saved_config.get("landmark_color", "绿色")
            connection_color_text = saved_config.get("connection_color", "红色")

            # 应用颜色设置
            self.on_config_landmark_color_changed(landmark_color_text)
            self.on_config_connection_color_changed(connection_color_text)

            # 如果配置管理器窗口打开，更新界面控件
            if (hasattr(self, 'landmark_selector_dialog') and
                self.landmark_selector_dialog.isVisible()):

                # 更新复选框状态
                if hasattr(self, 'landmark_checkboxes'):
                    for landmark_idx, checkbox in self.landmark_checkboxes.items():
                        checkbox.setChecked(self.landmark_visibility[landmark_idx])

                # 更新显示设置控件
                if hasattr(self, 'config_thickness_slider'):
                    self.config_thickness_slider.setValue(self.line_thickness)
                    self.config_thickness_label.setText(str(self.line_thickness))

                if hasattr(self, 'config_size_slider'):
                    self.config_size_slider.setValue(self.landmark_size)
                    self.config_size_label.setText(str(self.landmark_size))

                if hasattr(self, 'config_shape_combo'):
                    shape_text = saved_config.get("landmark_shape", "正方形")
                    self.config_shape_combo.setCurrentText(shape_text)

                # 更新颜色设置控件
                if hasattr(self, 'config_landmark_color_combo'):
                    self.config_landmark_color_combo.setCurrentText(landmark_color_text)

                if hasattr(self, 'config_connection_color_combo'):
                    self.config_connection_color_combo.setCurrentText(connection_color_text)

            self.update_status(f"已应用完整配置: {config_name}")

        except Exception as e:
            print(f"应用完整配置时出错: {e}")

    def update_complete_config_combo(self):
        """更新完整配置下拉框"""
        # 更新配置管理器中的下拉框
        if hasattr(self, 'config_combo'):
            self.config_combo.clear()
            self.config_combo.addItem("选择配置...")

            for config_name in sorted(self.complete_configs.keys()):
                self.config_combo.addItem(config_name)

        # 同时更新工具栏的下拉框
        self.update_toolbar_config_combo()

    def update_status(self, message):
        """更新状态"""
        self.status_label.setText(message)
        self.toolbar_status.setText(message)

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 清理资源
        if self.cap1:
            self.cap1.release()
        if self.cap2:
            self.cap2.release()

        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("SnowNavi Pose Analyzer")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("SnowNavi")
    
    # 创建主窗口
    window = PoseDetectionApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
