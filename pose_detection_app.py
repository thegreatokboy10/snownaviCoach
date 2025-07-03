#!/usr/bin/env python3
"""
人体姿态检测应用程序
使用MediaPipe进行实时人体骨骼检测和可视化
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import queue
import base64
from io import BytesIO

class PoseDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人体姿态检测应用")
        self.root.geometry("1200x800")

        # MediaPipe相关变量（延迟初始化）
        self.mp_pose = None
        self.pose = None
        self.mp_drawing = None
        self.mp_drawing_styles = None
        self.mediapipe_initialized = False

        # 视频相关变量（支持双视频独立控制）
        self.video1_path = None
        self.video2_path = None
        self.cap1 = None
        self.cap2 = None

        # 独立播放控制
        self.is_playing1 = False
        self.is_playing2 = False
        self.should_stop1 = False
        self.should_stop2 = False

        # 帧数据
        self.current_frame1 = None
        self.current_frame2 = None
        self.total_frames1 = 0
        self.total_frames2 = 0
        self.current_frame_number1 = 0
        self.current_frame_number2 = 0

        # 视频属性
        self.fps1 = 30
        self.fps2 = 30
        self.frame_interval1 = 33  # 约30fps的间隔（毫秒）
        self.frame_interval2 = 33

        self.comparison_mode = False  # 是否为比较模式
        self.video2_loaded = False  # 标记是否加载了第二个视频

        # 悬浮窗引用
        self.landmark_selector_window = None
        self.settings_window = None
        self.export_window = None
        self.help_window = None

        # 工具栏图标
        self.toolbar_icons = {}



        # 性能优化变量
        self.frame_queue = queue.Queue(maxsize=2)  # 限制队列大小防止内存溢出
        self.processing_thread = None
        self.display_thread = None
        self.last_update_time = 0
        self.update_interval = 0.033  # 30fps

        # 骨骼线条自定义设置
        self.landmark_color = (0, 255, 0)  # 默认绿色 (BGR格式)
        self.connection_color = (0, 0, 255)  # 默认红色 (BGR格式) - 修正BGR值
        self.line_thickness = 2  # 默认线条粗细
        self.landmark_size = 8  # 关键点大小（默认较大的正方形）
        self.landmark_shape = "square"  # 关键点形状：circle（圆形）或 square（正方形）

        # 设置更新防抖
        self.settings_update_pending = False
        self.last_settings_update = 0

        # 创建图标
        self.create_toolbar_icons()

        # 创建GUI界面
        self.create_widgets()

        # 延迟初始化MediaPipe（避免阻塞UI）
        self.root.after(1000, self.initialize_mediapipe)

    def initialize_mediapipe(self):
        """延迟初始化MediaPipe，避免阻塞UI创建"""
        try:
            print("正在初始化MediaPipe...")
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.mp_holistic = mp.solutions.holistic

            # 使用标准的Pose模型进行单人检测
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,  # 使用中等复杂度获得更好效果
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            self.mediapipe_initialized = True
            print("MediaPipe初始化完成")
        except Exception as e:
            print(f"MediaPipe初始化失败: {e}")
            self.mediapipe_initialized = False

    def create_widgets(self):
        """创建GUI组件"""
        # 配置根窗口网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # 主内容区域可扩展

        # 创建工具栏
        self.create_toolbar()

        # 主框架
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架网格权重
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # 视频区域可扩展
        self.main_frame.rowconfigure(0, weight=0)  # 控制面板固定高度
        
        # 控制面板
        control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 第一行：文件选择
        file_frame = ttk.Frame(control_frame)
        file_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))

        # 视频1选择按钮
        self.select1_button = ttk.Button(
            file_frame,
            text="选择视频1",
            command=self.select_video1_file
        )
        self.select1_button.grid(row=0, column=0, padx=(0, 10))

        # 视频2选择按钮
        self.select2_button = ttk.Button(
            file_frame,
            text="选择视频2（比较）",
            command=self.select_video2_file
        )
        self.select2_button.grid(row=0, column=1, padx=(0, 10))

        # 比较模式切换
        self.comparison_var = tk.BooleanVar()
        self.comparison_check = ttk.Checkbutton(
            file_frame,
            text="比较模式",
            variable=self.comparison_var,
            command=self.toggle_comparison_mode
        )
        self.comparison_check.grid(row=0, column=2, padx=(10, 0))

        # 第二行：播放控制
        play_frame = ttk.Frame(control_frame)
        play_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))

        # 视频1播放控制
        video1_control_frame = ttk.LabelFrame(play_frame, text="视频1控制", padding="3")
        video1_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.play1_button = ttk.Button(
            video1_control_frame,
            text="播放",
            command=self.toggle_playback1,
            state="disabled"
        )
        self.play1_button.grid(row=0, column=0, padx=(0, 5))

        self.stop1_button = ttk.Button(
            video1_control_frame,
            text="停止",
            command=self.stop_playback1,
            state="disabled"
        )
        self.stop1_button.grid(row=0, column=1, padx=(0, 5))

        # 视频1进度条
        self.progress1_var = tk.DoubleVar()
        self.progress1_bar = ttk.Scale(
            video1_control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress1_var,
            command=self.on_progress1_change,
            state="disabled",
            length=150
        )
        self.progress1_bar.grid(row=0, column=2, padx=(5, 0))

        # 视频2播放控制（比较模式时显示）
        self.video2_control_frame = ttk.LabelFrame(play_frame, text="视频2控制", padding="3")

        self.play2_button = ttk.Button(
            self.video2_control_frame,
            text="播放",
            command=self.toggle_playback2,
            state="disabled"
        )
        self.play2_button.grid(row=0, column=0, padx=(0, 5))

        self.stop2_button = ttk.Button(
            self.video2_control_frame,
            text="停止",
            command=self.stop_playback2,
            state="disabled"
        )
        self.stop2_button.grid(row=0, column=1, padx=(0, 5))

        # 视频2进度条
        self.progress2_var = tk.DoubleVar()
        self.progress2_bar = ttk.Scale(
            self.video2_control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress2_var,
            command=self.on_progress2_change,
            state="disabled",
            length=150
        )
        self.progress2_bar.grid(row=0, column=2, padx=(5, 0))

        # 导出功能
        export_frame = ttk.LabelFrame(play_frame, text="导出", padding="3")
        export_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0))

        self.export1_button = ttk.Button(
            export_frame,
            text="导出视频1",
            command=self.export_video1,
            state="disabled"
        )
        self.export1_button.grid(row=0, column=0, padx=(0, 5))

        self.export2_button = ttk.Button(
            export_frame,
            text="导出视频2",
            command=self.export_video2,
            state="disabled"
        )
        self.export2_button.grid(row=0, column=1)

        # 信息标签
        self.info_label = ttk.Label(control_frame, text="请选择视频文件")
        self.info_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 视频显示区域（支持自适应和双视频比较）
        self.video_container = ttk.LabelFrame(self.main_frame, text="视频显示", padding="5")
        self.video_container.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建可滚动的Canvas用于自适应显示
        self.create_video_display_area()

        # 配置视频显示区域的网格权重
        self.video_container.columnconfigure(0, weight=1)
        self.video_container.rowconfigure(0, weight=1)

    def create_video_display_area(self):
        """创建自适应的视频显示区域"""
        # 创建主显示框架
        self.display_frame = ttk.Frame(self.video_container)
        self.display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 单视频模式显示区域（只显示姿态检测结果）
        self.single_video_frame = ttk.Frame(self.display_frame)

        # 视频1显示（只显示姿态检测）
        self.video1_pose_frame = ttk.LabelFrame(self.single_video_frame, text="姿态检测结果")
        self.video1_pose_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.video1_pose_label = ttk.Label(self.video1_pose_frame, text="姿态检测结果将在这里显示")
        self.video1_pose_label.pack(expand=True, fill=tk.BOTH)

        # 配置单视频模式网格权重
        self.single_video_frame.columnconfigure(0, weight=1)
        self.single_video_frame.rowconfigure(0, weight=1)

        # 双视频比较模式显示区域（智能布局）
        self.comparison_frame = ttk.Frame(self.display_frame)

        # 视频1显示区域
        self.video1_comp_pose_frame = ttk.LabelFrame(self.comparison_frame, text="视频1 - 姿态检测")
        self.video1_comp_pose_label = ttk.Label(self.video1_comp_pose_frame, text="视频1姿态检测结果")
        self.video1_comp_pose_label.pack(expand=True, fill=tk.BOTH)

        # 视频2显示区域
        self.video2_comp_pose_frame = ttk.LabelFrame(self.comparison_frame, text="视频2 - 姿态检测")
        self.video2_comp_pose_label = ttk.Label(self.video2_comp_pose_frame, text="视频2姿态检测结果")
        self.video2_comp_pose_label.pack(expand=True, fill=tk.BOTH)

        # 默认布局（将在确定视频比例后调整）
        self.comparison_layout = "vertical"  # vertical 或 horizontal
        self.setup_comparison_layout()

        # 配置主显示框架
        self.display_frame.columnconfigure(0, weight=1)
        self.display_frame.rowconfigure(0, weight=1)

        # 默认显示单视频模式
        self.single_video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)

        # 创建设置面板
        self.create_settings_panel()

    def setup_comparison_layout(self):
        """设置比较模式的布局"""
        if self.comparison_layout == "vertical":
            # 上下布局（适合横拍视频）
            self.video1_comp_pose_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 2))
            self.video2_comp_pose_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(2, 0))

            self.comparison_frame.columnconfigure(0, weight=1)
            self.comparison_frame.rowconfigure(0, weight=1)
            self.comparison_frame.rowconfigure(1, weight=1)
        else:
            # 左右布局（适合竖拍视频）
            self.video1_comp_pose_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
            self.video2_comp_pose_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))

            self.comparison_frame.columnconfigure(0, weight=1)
            self.comparison_frame.columnconfigure(1, weight=1)
            self.comparison_frame.rowconfigure(0, weight=1)

    def determine_layout_from_videos(self):
        """根据视频比例确定布局方式"""
        if not (self.cap1 and self.cap2):
            return

        # 获取视频1的宽高比
        width1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ratio1 = width1 / height1 if height1 > 0 else 1.0

        # 获取视频2的宽高比
        width2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ratio2 = width2 / height2 if height2 > 0 else 1.0

        # 判断是否为竖拍视频（宽高比 < 1）
        is_portrait1 = ratio1 < 1.0
        is_portrait2 = ratio2 < 1.0

        if is_portrait1 or is_portrait2:
            # 如果有竖拍视频，使用横向布局
            self.comparison_layout = "horizontal"
            print(f"检测到竖拍视频，使用横向布局 (视频1: {width1}x{height1}, 视频2: {width2}x{height2})")
        else:
            # 都是横拍视频，使用纵向布局
            self.comparison_layout = "vertical"
            print(f"检测到横拍视频，使用纵向布局 (视频1: {width1}x{height1}, 视频2: {width2}x{height2})")

        # 重新设置布局
        self.setup_comparison_layout()

    def create_settings_panel(self):
        """创建设置面板"""
        # 设置面板
        settings_frame = ttk.LabelFrame(self.main_frame, text="骨骼线条设置", padding="5")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # 关键点颜色设置
        landmark_color_frame = ttk.Frame(settings_frame)
        landmark_color_frame.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)

        ttk.Label(landmark_color_frame, text="关键点颜色:").grid(row=0, column=0, padx=(0, 5))
        self.landmark_color_var = tk.StringVar(value="绿色")
        self.landmark_color_combo = ttk.Combobox(
            landmark_color_frame,
            textvariable=self.landmark_color_var,
            values=["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"],
            state="readonly",
            width=8
        )
        self.landmark_color_combo.grid(row=0, column=1)
        # 直接绑定事件，优化后的处理函数已经足够快
        self.landmark_color_combo.bind('<<ComboboxSelected>>', self.on_landmark_color_change)

        # 连接线颜色设置
        connection_color_frame = ttk.Frame(settings_frame)
        connection_color_frame.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        ttk.Label(connection_color_frame, text="连接线颜色:").grid(row=0, column=0, padx=(0, 5))
        self.connection_color_var = tk.StringVar(value="红色")
        self.connection_color_combo = ttk.Combobox(
            connection_color_frame,
            textvariable=self.connection_color_var,
            values=["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"],
            state="readonly",
            width=8
        )
        self.connection_color_combo.grid(row=0, column=1)
        # 直接绑定事件，优化后的处理函数已经足够快
        self.connection_color_combo.bind('<<ComboboxSelected>>', self.on_connection_color_change)

        # 线条粗细设置
        thickness_frame = ttk.Frame(settings_frame)
        thickness_frame.grid(row=0, column=2, padx=(0, 10), sticky=tk.W)

        ttk.Label(thickness_frame, text="线条粗细:").grid(row=0, column=0, padx=(0, 5))
        self.thickness_var = tk.IntVar(value=2)
        self.thickness_scale = ttk.Scale(
            thickness_frame,
            from_=1,
            to=8,
            orient=tk.HORIZONTAL,
            variable=self.thickness_var,
            length=100
        )
        self.thickness_scale.grid(row=0, column=1, padx=(0, 5))

        # 使用鼠标释放事件而不是实时更新，减少卡顿
        self.thickness_scale.bind("<ButtonRelease-1>", self.on_thickness_release)
        self.thickness_scale.bind("<B1-Motion>", self.on_thickness_drag)

        self.thickness_label = ttk.Label(thickness_frame, text="2")
        self.thickness_label.grid(row=0, column=2)

        # 关节点大小设置
        landmark_size_frame = ttk.Frame(settings_frame)
        landmark_size_frame.grid(row=1, column=0, padx=(0, 10), sticky=tk.W, pady=(10, 0))

        ttk.Label(landmark_size_frame, text="关节点大小:").grid(row=0, column=0, padx=(0, 5))
        self.landmark_size_var = tk.IntVar(value=8)
        self.landmark_size_scale = ttk.Scale(
            landmark_size_frame,
            from_=3,
            to=15,
            orient=tk.HORIZONTAL,
            variable=self.landmark_size_var,
            length=100
        )
        self.landmark_size_scale.grid(row=0, column=1, padx=(0, 5))

        # 使用释放事件，避免频繁更新
        self.landmark_size_scale.bind("<ButtonRelease-1>", self.on_landmark_size_release)
        self.landmark_size_scale.bind("<B1-Motion>", self.on_landmark_size_drag)

        self.landmark_size_label = ttk.Label(landmark_size_frame, text="8")
        self.landmark_size_label.grid(row=0, column=2)

        # 关节点形状设置
        landmark_shape_frame = ttk.Frame(settings_frame)
        landmark_shape_frame.grid(row=1, column=1, padx=(0, 10), sticky=tk.W, pady=(10, 0))

        ttk.Label(landmark_shape_frame, text="关节点形状:").grid(row=0, column=0, padx=(0, 5))
        self.landmark_shape_var = tk.StringVar(value="正方形")
        self.landmark_shape_combo = ttk.Combobox(
            landmark_shape_frame,
            textvariable=self.landmark_shape_var,
            values=["圆形", "正方形", "菱形"],
            state="readonly",
            width=8
        )
        self.landmark_shape_combo.grid(row=0, column=1)
        self.landmark_shape_combo.bind('<<ComboboxSelected>>', self.on_landmark_shape_change)

        # 重置按钮
        reset_button = ttk.Button(
            settings_frame,
            text="重置默认",
            command=self.reset_settings
        )
        reset_button.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))



        # 配置设置面板的网格权重
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(2, weight=1)

        # 创建动态视频显示区域
        self.create_dynamic_video_area()

        # 初始化关节点选择器数据
        self.initialize_landmark_selector_data()









    def select_all_landmarks(self):
        """选择所有关节点"""
        for var in self.landmark_visibility.values():
            var.set(True)
        self.on_landmark_visibility_change()

    def deselect_all_landmarks(self):
        """取消选择所有关节点"""
        for var in self.landmark_visibility.values():
            var.set(False)
        self.on_landmark_visibility_change()

    def invert_landmark_selection(self):
        """反选关节点"""
        for var in self.landmark_visibility.values():
            var.set(not var.get())
        self.on_landmark_visibility_change()

    def select_landmark_group(self, group_name):
        """选择特定分组的关节点"""
        # 先取消所有选择
        for var in self.landmark_visibility.values():
            var.set(False)

        # 选择指定分组
        if group_name in self.landmark_groups:
            for landmark_idx in self.landmark_groups[group_name]:
                self.landmark_visibility[landmark_idx].set(True)

        self.on_landmark_visibility_change()

    def draw_body_diagram(self):
        """绘制人体关节示意图"""
        try:
            # 清除画布
            self.diagram_canvas.delete("all")

            # 定义关节点在示意图中的位置（相对坐标）
            self.diagram_positions = {
                # 头部
                0: (100, 30),   # 鼻子
                1: (95, 25),    # 左眼内侧
                2: (90, 25),    # 左眼
                3: (85, 25),    # 左眼外侧
                4: (105, 25),   # 右眼内侧
                5: (110, 25),   # 右眼
                6: (115, 25),   # 右眼外侧
                7: (80, 35),    # 左耳
                8: (120, 35),   # 右耳
                9: (95, 40),    # 嘴左
                10: (105, 40),  # 嘴右

                # 上身
                11: (70, 80),   # 左肩
                12: (130, 80),  # 右肩
                13: (50, 120),  # 左肘
                14: (150, 120), # 右肘
                15: (40, 160),  # 左腕
                16: (160, 160), # 右腕
                17: (35, 170),  # 左小指
                18: (165, 170), # 右小指
                19: (30, 165),  # 左食指
                20: (170, 165), # 右食指
                21: (45, 175),  # 左拇指
                22: (155, 175), # 右拇指

                # 下身
                23: (80, 180),  # 左髋
                24: (120, 180), # 右髋
                25: (75, 220),  # 左膝
                26: (125, 220), # 右膝
                27: (70, 260),  # 左踝
                28: (130, 260), # 右踝
                29: (65, 270),  # 左脚跟
                30: (135, 270), # 右脚跟
                31: (60, 275),  # 左脚趾
                32: (140, 275), # 右脚趾
            }

            # 绘制连接线（骨骼结构）
            connections = [
                # 头部连接
                (0, 1), (1, 2), (2, 3), (3, 7),  # 左眼到左耳
                (0, 4), (4, 5), (5, 6), (6, 8),  # 右眼到右耳
                (9, 10),  # 嘴部

                # 躯干
                (11, 12),  # 肩膀
                (11, 23), (12, 24),  # 肩到髋
                (23, 24),  # 髋部

                # 左臂
                (11, 13), (13, 15),  # 左肩到左腕
                (15, 17), (15, 19), (15, 21),  # 左手指

                # 右臂
                (12, 14), (14, 16),  # 右肩到右腕
                (16, 18), (16, 20), (16, 22),  # 右手指

                # 左腿
                (23, 25), (25, 27),  # 左髋到左踝
                (27, 29), (27, 31),  # 左脚

                # 右腿
                (24, 26), (26, 28),  # 右髋到右踝
                (28, 30), (28, 32),  # 右脚
            ]

            # 绘制连接线
            for start_idx, end_idx in connections:
                if start_idx in self.diagram_positions and end_idx in self.diagram_positions:
                    start_pos = self.diagram_positions[start_idx]
                    end_pos = self.diagram_positions[end_idx]

                    # 根据关节点是否选中决定线条颜色
                    start_selected = self.landmark_visibility[start_idx].get()
                    end_selected = self.landmark_visibility[end_idx].get()

                    if start_selected and end_selected:
                        color = "#0066CC"  # 蓝色 - 选中的连接
                        width = 2
                    else:
                        color = "#CCCCCC"  # 灰色 - 未选中的连接
                        width = 1

                    self.diagram_canvas.create_line(
                        start_pos[0], start_pos[1],
                        end_pos[0], end_pos[1],
                        fill=color, width=width
                    )

            # 绘制关节点
            for landmark_idx, pos in self.diagram_positions.items():
                x, y = pos
                is_selected = self.landmark_visibility[landmark_idx].get()

                if is_selected:
                    color = "#FF6600"  # 橙色 - 选中的关节点
                    size = 4
                else:
                    color = "#999999"  # 灰色 - 未选中的关节点
                    size = 3

                # 绘制关节点圆圈
                self.diagram_canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=color, outline="black", width=1,
                    tags=f"landmark_{landmark_idx}"
                )

                # 添加关节点编号
                self.diagram_canvas.create_text(
                    x, y, text=str(landmark_idx),
                    font=("Arial", 6), fill="white",
                    tags=f"landmark_{landmark_idx}"
                )

        except Exception as e:
            print(f"绘制人体示意图时出错: {e}")

    def on_diagram_click(self, event):
        """处理示意图点击事件"""
        try:
            # 获取点击位置
            x, y = event.x, event.y

            # 查找最近的关节点
            min_distance = float('inf')
            closest_landmark = None

            for landmark_idx, pos in self.diagram_positions.items():
                distance = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
                if distance < min_distance and distance < 15:  # 15像素的点击范围
                    min_distance = distance
                    closest_landmark = landmark_idx

            # 切换关节点状态
            if closest_landmark is not None:
                current_state = self.landmark_visibility[closest_landmark].get()
                self.landmark_visibility[closest_landmark].set(not current_state)

                # 重新绘制示意图
                self.draw_body_diagram()

                # 更新视频显示
                self.on_landmark_visibility_change()

                print(f"切换关节点 {closest_landmark}: {self.landmark_info[closest_landmark]} - {'选中' if not current_state else '取消选中'}")

        except Exception as e:
            print(f"处理示意图点击时出错: {e}")

    def on_landmark_visibility_change(self):
        """关节点可见性改变事件"""
        try:
            # 更新示意图
            if hasattr(self, 'diagram_canvas'):
                self.draw_body_diagram()

            # 更新显示
            if hasattr(self, 'current_frame1') and self.current_frame1 is not None:
                self.show_frame1()
            if hasattr(self, 'current_frame2') and self.current_frame2 is not None:
                self.show_frame2()

            # 保持焦点
            self.root.focus_force()
        except Exception as e:
            print(f"更新关节点可见性时出错: {e}")

    def toggle_playback1(self):
        """切换视频1播放/暂停状态"""
        if self.is_playing1:
            self.pause_playback1()
        else:
            self.start_playback1()

    def start_playback1(self):
        """开始播放视频1"""
        if not self.cap1:
            return

        self.is_playing1 = True
        self.should_stop1 = False
        self.play1_button.config(text="暂停")

        # 启动播放循环
        self.playback_loop1()

    def pause_playback1(self):
        """暂停播放视频1"""
        self.is_playing1 = False
        self.play1_button.config(text="播放")

    def stop_playback1(self):
        """停止播放视频1"""
        self.is_playing1 = False
        self.should_stop1 = True
        self.play1_button.config(text="播放")
        self.current_frame_number1 = 0
        self.show_frame1()

    def toggle_playback2(self):
        """切换视频2播放/暂停状态"""
        if self.is_playing2:
            self.pause_playback2()
        else:
            self.start_playback2()

    def start_playback2(self):
        """开始播放视频2"""
        if not self.cap2:
            return

        self.is_playing2 = True
        self.should_stop2 = False
        self.play2_button.config(text="暂停")

        # 启动播放循环
        self.playback_loop2()

    def pause_playback2(self):
        """暂停播放视频2"""
        self.is_playing2 = False
        self.play2_button.config(text="播放")

    def stop_playback2(self):
        """停止播放视频2"""
        self.is_playing2 = False
        self.should_stop2 = True
        self.play2_button.config(text="播放")
        self.current_frame_number2 = 0
        self.show_frame2()

    def playback_loop1(self):
        """视频1播放循环"""
        if not self.is_playing1 or self.current_frame_number1 >= self.total_frames1:
            if self.current_frame_number1 >= self.total_frames1:
                self.pause_playback1()
            return

        # 显示当前帧
        self.show_frame1()

        # 移动到下一帧
        self.current_frame_number1 += 1

        # 使用after方法调度下一次更新
        if self.is_playing1:
            self.root.after(self.frame_interval1, self.playback_loop1)

    def playback_loop2(self):
        """视频2播放循环"""
        if not self.is_playing2 or self.current_frame_number2 >= self.total_frames2:
            if self.current_frame_number2 >= self.total_frames2:
                self.pause_playback2()
            return

        # 显示当前帧
        self.show_frame2()

        # 移动到下一帧
        self.current_frame_number2 += 1

        # 使用after方法调度下一次更新
        if self.is_playing2:
            self.root.after(self.frame_interval2, self.playback_loop2)

    def show_frame1(self):
        """显示视频1当前帧"""
        if not self.cap1:
            return

        self.cap1.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number1)
        ret, frame = self.cap1.read()

        if ret:
            self.current_frame1 = frame.copy()
            # 更新显示
            if self.comparison_mode:
                if self.mediapipe_initialized:
                    pose_frame = self.process_pose_detection(self.current_frame1, video_num=1)
                    self.display_frame_in_label(pose_frame, self.video1_comp_pose_label, "pose")
            else:
                if self.mediapipe_initialized:
                    pose_frame = self.process_pose_detection(self.current_frame1, video_num=1)
                    self.display_frame_in_label(pose_frame, self.video1_pose_label, "pose")

            # 更新进度条
            if self.total_frames1 > 0:
                progress = (self.current_frame_number1 / self.total_frames1) * 100
                self.progress1_var.set(progress)

    def show_frame2(self):
        """显示视频2当前帧"""
        if not self.cap2:
            return

        self.cap2.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number2)
        ret, frame = self.cap2.read()

        if ret:
            self.current_frame2 = frame.copy()
            # 更新显示
            if self.mediapipe_initialized:
                pose_frame = self.process_pose_detection(self.current_frame2, video_num=2)
                self.display_frame_in_label(pose_frame, self.video2_comp_pose_label, "pose")

            # 更新进度条
            if self.total_frames2 > 0:
                progress = (self.current_frame_number2 / self.total_frames2) * 100
                self.progress2_var.set(progress)

    def on_progress1_change(self, value):
        """视频1进度条变化事件"""
        if not self.is_playing1 and self.cap1 and self.total_frames1 > 0:
            frame_number = int((float(value) / 100) * self.total_frames1)
            self.current_frame_number1 = max(0, min(frame_number, self.total_frames1 - 1))
            self.show_frame1()

    def on_progress2_change(self, value):
        """视频2进度条变化事件"""
        if not self.is_playing2 and self.cap2 and self.total_frames2 > 0:
            frame_number = int((float(value) / 100) * self.total_frames2)
            self.current_frame_number2 = max(0, min(frame_number, self.total_frames2 - 1))
            self.show_frame2()

    def select_video1_file(self):
        """选择视频1文件"""
        file_path = filedialog.askopenfilename(
            title="选择视频1文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.video1_path = file_path
            self.load_video1()

    def select_video2_file(self):
        """选择视频2文件（用于比较）"""
        file_path = filedialog.askopenfilename(
            title="选择视频2文件（用于比较）",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.video2_path = file_path
            self.load_video2()

    def toggle_comparison_mode(self):
        """切换比较模式"""
        self.comparison_mode = self.comparison_var.get()

        if self.comparison_mode:
            # 切换到比较模式
            self.single_video_frame.grid_remove()
            self.comparison_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            print("已切换到比较模式")
        else:
            # 切换到单视频模式
            self.comparison_frame.grid_remove()
            self.single_video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            print("已切换到单视频模式")

        # 更新显示
        self.update_video_display()

    def on_window_resize(self, event):
        """窗口大小变化事件"""
        # 只处理主窗口的resize事件
        if event.widget == self.root:
            self.root.after_idle(self.update_video_display)

    def update_video_display(self):
        """更新视频显示以适应窗口大小"""
        try:
            if self.comparison_mode:
                self.update_comparison_display()
            else:
                self.update_single_display()
        except Exception as e:
            print(f"更新视频显示时出错: {e}")

    def update_single_display(self):
        """更新单视频显示"""
        if self.current_frame1 is not None:
            self.display_frame_in_label(self.current_frame1, self.video1_original_label, "original")

            # 进行姿态检测
            if self.mediapipe_initialized:
                pose_frame = self.process_pose_detection(self.current_frame1)
                self.display_frame_in_label(pose_frame, self.video1_pose_label, "pose")

    def update_comparison_display(self):
        """更新比较模式显示"""
        if self.current_frame1 is not None:
            self.display_frame_in_label(self.current_frame1, self.video1_comp_original_label, "original")

            if self.mediapipe_initialized:
                pose_frame1 = self.process_pose_detection(self.current_frame1)
                self.display_frame_in_label(pose_frame1, self.video1_comp_pose_label, "pose")

        if self.current_frame2 is not None:
            self.display_frame_in_label(self.current_frame2, self.video2_comp_original_label, "original")

            if self.mediapipe_initialized:
                pose_frame2 = self.process_pose_detection(self.current_frame2)
                self.display_frame_in_label(pose_frame2, self.video2_comp_pose_label, "pose")

    def display_frame_in_label(self, frame, label, frame_type):
        """在指定标签中显示帧，自适应大小"""
        try:
            # 获取标签的实际大小
            label.update_idletasks()
            label_width = max(label.winfo_width(), 200)
            label_height = max(label.winfo_height(), 150)

            # 调整帧大小以适应标签
            if self.comparison_mode:
                # 比较模式下确保两个视频使用相同的显示尺寸
                if self.comparison_layout == "vertical":
                    # 上下布局时，使用固定的高度比例
                    max_width = label_width - 20
                    max_height = int((label_height - 20) * 0.9)  # 留出一些边距
                else:
                    # 左右布局时，使用固定的宽度比例
                    max_width = int((label_width - 20) * 0.9)
                    max_height = label_height - 20

                # 确保最小尺寸
                max_width = max(max_width, 200)
                max_height = max(max_height, 150)
            else:
                # 单视频模式下使用较大的尺寸
                max_width = label_width - 10
                max_height = label_height - 10

            resized_frame = self.resize_frame_adaptive(frame, max_width, max_height)

            # 转换为tkinter可显示的格式
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)

            # 更新标签
            label.config(image=photo)
            label.image = photo  # 保持引用

        except Exception as e:
            print(f"显示帧时出错: {e}")

    def resize_frame_adaptive(self, frame, max_width, max_height):
        """自适应调整帧大小"""
        if frame is None:
            return frame

        height, width = frame.shape[:2]

        # 计算缩放比例
        scale_w = max_width / width if width > 0 else 1
        scale_h = max_height / height if height > 0 else 1
        scale = min(scale_w, scale_h, 1.0)  # 不放大，只缩小

        # 调整大小
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(frame, (new_width, new_height))
        else:
            return frame

    def load_video1(self):
        """加载视频1文件"""
        try:
            # 停止当前播放
            if hasattr(self, 'is_playing1'):
                self.stop_playback1()

            if self.cap1:
                self.cap1.release()

            self.cap1 = cv2.VideoCapture(self.video1_path)

            if not self.cap1.isOpened():
                messagebox.showerror("错误", "无法打开视频1文件")
                return

            # 获取视频信息
            self.total_frames1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps1 = max(1, self.cap1.get(cv2.CAP_PROP_FPS))
            width1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 更新帧间隔
            self.frame_interval1 = max(16, int(1000 / self.fps1))

            # 更新界面信息
            self.update_info_display()

            # 启用控制按钮
            self.play1_button.config(state="normal")
            self.stop1_button.config(state="normal")
            self.progress1_bar.config(state="normal")
            self.export1_button.config(state="normal")

            # 重置状态
            self.current_frame_number1 = 0
            self.is_playing1 = False
            self.should_stop1 = False

            # 显示第一帧
            self.show_frame1()

            print(f"视频1加载成功: {width1}x{height1}, {self.total_frames1}帧, {self.fps1:.1f}fps")

        except Exception as e:
            messagebox.showerror("错误", f"加载视频1时出错: {str(e)}")

    def load_video2(self):
        """加载视频2文件"""
        try:
            if self.cap2:
                self.cap2.release()

            self.cap2 = cv2.VideoCapture(self.video2_path)

            if not self.cap2.isOpened():
                messagebox.showerror("错误", "无法打开视频2文件")
                return

            # 获取视频信息
            self.total_frames2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps2 = max(1, self.cap2.get(cv2.CAP_PROP_FPS))
            width2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
            height2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 更新帧间隔
            self.frame_interval2 = max(16, int(1000 / self.fps2))

            # 更新界面信息
            self.update_info_display()

            # 启用视频2控制按钮
            self.play2_button.config(state="normal")
            self.stop2_button.config(state="normal")
            self.progress2_bar.config(state="normal")
            self.export2_button.config(state="normal")

            # 显示视频2控制面板
            self.video2_control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))

            # 标记视频2已加载并更新布局
            self.video2_loaded = True
            self.update_video_layout()

            # 重置状态
            self.current_frame_number2 = 0
            self.is_playing2 = False
            self.should_stop2 = False

            # 自动启用比较模式并确定布局
            if not self.comparison_mode:
                self.comparison_var.set(True)
                self.toggle_comparison_mode()

            # 根据视频比例确定布局
            self.determine_layout_from_videos()

            # 显示第一帧
            self.show_frame2()

            print(f"视频2加载成功: {width2}x{height2}, {self.total_frames2}帧, {self.fps2:.1f}fps")

        except Exception as e:
            messagebox.showerror("错误", f"加载视频2时出错: {str(e)}")

    def update_info_display(self):
        """更新信息显示"""
        info_parts = []

        if self.video1_path:
            video1_name = self.video1_path.split('/')[-1]
            if hasattr(self, 'total_frames1'):
                info_parts.append(f"视频1: {video1_name} ({self.total_frames1}帧, {self.fps1:.1f}fps)")
            else:
                info_parts.append(f"视频1: {video1_name}")

        if self.video2_path:
            video2_name = self.video2_path.split('/')[-1]
            if hasattr(self, 'total_frames2'):
                info_parts.append(f"视频2: {video2_name} ({self.total_frames2}帧, {self.fps2:.1f}fps)")
            else:
                info_parts.append(f"视频2: {video2_name}")

        if not info_parts:
            info_parts.append("请选择视频文件")

        self.info_label.config(text=" | ".join(info_parts))

    def get_color_bgr(self, color_name):
        """将颜色名称转换为BGR值（OpenCV格式）"""
        color_map = {
            "红色": (0, 0, 255),    # BGR格式：蓝=0, 绿=0, 红=255
            "绿色": (0, 255, 0),    # BGR格式：蓝=0, 绿=255, 红=0
            "蓝色": (255, 0, 0),    # BGR格式：蓝=255, 绿=0, 红=0
            "黄色": (0, 255, 255),  # BGR格式：蓝=0, 绿=255, 红=255
            "紫色": (255, 0, 255),  # BGR格式：蓝=255, 绿=0, 红=255
            "青色": (255, 255, 0),  # BGR格式：蓝=255, 绿=255, 红=0
            "白色": (255, 255, 255) # BGR格式：蓝=255, 绿=255, 红=255
        }
        return color_map.get(color_name, (0, 255, 0))  # 默认绿色

    def on_landmark_color_change(self, event=None):
        """关键点颜色改变事件"""
        try:
            color_name = self.landmark_color_var.get()
            if color_name:
                self.landmark_color = self.get_color_bgr(color_name)
                print(f"关键点颜色已更改为: {color_name}")

                # 保持焦点在主窗口
                self.root.focus_force()
        except Exception as e:
            print(f"更改关键点颜色时出错: {e}")

    def on_connection_color_change(self, event=None):
        """连接线颜色改变事件"""
        try:
            color_name = self.connection_color_var.get()
            if color_name:
                self.connection_color = self.get_color_bgr(color_name)
                print(f"连接线颜色已更改为: {color_name}")

                # 保持焦点在主窗口
                self.root.focus_force()
        except Exception as e:
            print(f"更改连接线颜色时出错: {e}")

    def on_thickness_drag(self, event):
        """滑块拖动时只更新显示，不更新实际值"""
        try:
            value = self.thickness_var.get()
            self.thickness_label.config(text=str(value))
        except Exception as e:
            print(f"拖动滑块时出错: {e}")

    def on_thickness_release(self, event):
        """滑块释放时更新实际值"""
        try:
            thickness = self.thickness_var.get()
            self.line_thickness = thickness
            self.thickness_label.config(text=str(thickness))
            print(f"线条粗细已更改为: {thickness}")

            # 保持焦点在主窗口
            self.root.focus_force()
        except Exception as e:
            print(f"更新线条粗细时出错: {e}")

    def on_thickness_change(self, value):
        """线条粗细改变事件（保留用于重置功能）"""
        try:
            thickness = int(float(value))
            self.line_thickness = thickness
            self.thickness_label.config(text=str(thickness))
        except Exception as e:
            print(f"更改线条粗细时出错: {e}")

    def on_landmark_size_drag(self, event):
        """关节点大小拖动时只更新显示"""
        try:
            value = self.landmark_size_var.get()
            self.landmark_size_label.config(text=str(value))
        except Exception as e:
            print(f"拖动关节点大小滑块时出错: {e}")

    def on_landmark_size_release(self, event):
        """关节点大小释放时更新实际值"""
        try:
            size = self.landmark_size_var.get()
            self.landmark_size = size
            self.landmark_size_label.config(text=str(size))
            print(f"关节点大小已更改为: {size}")

            # 保持焦点在主窗口
            self.root.focus_force()
        except Exception as e:
            print(f"更新关节点大小时出错: {e}")

    def get_shape_type(self, shape_name):
        """将形状名称转换为内部标识"""
        shape_map = {
            "圆形": "circle",
            "正方形": "square",
            "菱形": "diamond"
        }
        return shape_map.get(shape_name, "square")  # 默认正方形

    def on_landmark_shape_change(self, event=None):
        """关节点形状改变事件"""
        try:
            shape_name = self.landmark_shape_var.get()
            if shape_name:
                self.landmark_shape = self.get_shape_type(shape_name)
                print(f"关节点形状已更改为: {shape_name}")

                # 保持焦点在主窗口
                self.root.focus_force()
        except Exception as e:
            print(f"更改关节点形状时出错: {e}")

    def reset_settings(self):
        """重置设置为默认值（优化版本）"""
        try:
            # 直接更新变量，避免触发事件
            self.landmark_color_var.set("绿色")
            self.connection_color_var.set("红色")
            self.thickness_var.set(2)
            self.landmark_size_var.set(8)
            self.landmark_shape_var.set("正方形")

            # 更新实际值
            self.landmark_color = (0, 255, 0)  # 绿色 (BGR)
            self.connection_color = (0, 0, 255)  # 红色 (BGR) - 修正BGR值
            self.line_thickness = 2
            self.landmark_size = 8
            self.landmark_shape = "square"

            # 更新显示标签
            self.thickness_label.config(text="2")
            self.landmark_size_label.config(text="8")

            print("设置已重置为默认值")
        except Exception as e:
            print(f"重置设置时出错: {e}")
            
    def load_video(self):
        """加载视频文件"""
        try:
            # 停止当前播放
            self.stop_playback()

            if self.cap:
                self.cap.release()

            self.cap = cv2.VideoCapture(self.video_path)

            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                return

            # 获取视频信息
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = max(1, self.cap.get(cv2.CAP_PROP_FPS))  # 防止除零错误
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 计算帧间隔（毫秒）
            self.frame_interval = max(16, int(1000 / self.fps))  # 最小16ms（约60fps）

            # 更新界面
            self.info_label.config(
                text=f"视频: {self.video_path.split('/')[-1]} | "
                     f"分辨率: {width}x{height} | "
                     f"帧数: {self.total_frames} | "
                     f"FPS: {self.fps:.1f}"
            )

            # 启用控制按钮
            self.play_button.config(state="normal")
            self.stop_button.config(state="normal")
            self.progress_bar.config(state="normal")

            # 重置状态
            self.current_frame_number = 0
            self.is_playing = False
            self.should_stop = False

            # 显示第一帧
            self.show_frame()

        except Exception as e:
            messagebox.showerror("错误", f"加载视频时出错: {str(e)}")
            
    def show_frame(self):
        """显示当前帧（支持双视频）"""
        # 限制更新频率
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
        self.last_update_time = current_time

        # 读取视频1帧
        if self.cap1:
            self.cap1.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number)
            ret1, frame1 = self.cap1.read()
            if ret1:
                self.current_frame1 = frame1.copy()
            else:
                self.current_frame1 = None

        # 读取视频2帧（如果在比较模式）
        if self.comparison_mode and self.cap2:
            # 确保视频2的帧号不超过其总帧数
            frame_number2 = min(self.current_frame_number, self.total_frames2 - 1) if self.total_frames2 > 0 else 0
            self.cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_number2)
            ret2, frame2 = self.cap2.read()
            if ret2:
                self.current_frame2 = frame2.copy()
            else:
                self.current_frame2 = None

        # 更新显示
        self.update_video_display()

        # 更新进度条（基于视频1）
        if self.total_frames1 > 0:
            progress = (self.current_frame_number / self.total_frames1) * 100
            self.progress_var.set(progress)

    def display_original_frame(self, frame):
        """快速显示原始帧"""
        try:
            original_display = self.resize_frame_for_display(frame)
            original_image = cv2.cvtColor(original_display, cv2.COLOR_BGR2RGB)
            original_pil = Image.fromarray(original_image)
            original_photo = ImageTk.PhotoImage(original_pil)

            self.original_label.config(image=original_photo)
            self.original_label.image = original_photo
        except Exception as e:
            print(f"显示原始帧时出错: {e}")

    def process_frames_background(self):
        """在后台线程中处理姿态检测"""
        while not self.should_stop:
            try:
                # 从队列获取帧
                frame, frame_number = self.frame_queue.get(timeout=0.1)

                # 进行姿态检测
                pose_frame = self.process_pose_detection(frame)

                # 在主线程中更新显示
                self.root.after(0, self.update_pose_display, pose_frame)

                self.frame_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"后台处理帧时出错: {e}")
                continue

    def update_pose_display(self, pose_frame):
        """在主线程中更新姿态检测显示"""
        try:
            pose_display = self.resize_frame_for_display(pose_frame)
            pose_image = cv2.cvtColor(pose_display, cv2.COLOR_BGR2RGB)
            pose_pil = Image.fromarray(pose_image)
            pose_photo = ImageTk.PhotoImage(pose_pil)

            self.pose_label.config(image=pose_photo)
            self.pose_label.image = pose_photo
        except Exception as e:
            print(f"更新姿态显示时出错: {e}")
            
    def resize_frame_for_display(self, frame, max_width=400, max_height=300):
        """调整帧大小以适应显示区域"""
        height, width = frame.shape[:2]
        
        # 计算缩放比例
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h)
        
        # 调整大小
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(frame, (new_width, new_height))
        
    def process_pose_detection(self, frame, video_num=1):
        """处理姿态检测（简化的单人检测版本）"""
        # 检查MediaPipe是否已初始化
        if not self.mediapipe_initialized or self.pose is None:
            return frame.copy()  # 返回原始帧

        try:
            # 转换颜色空间
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 使用标准的Pose模型进行检测
            results = self.pose.process(rgb_frame)

            # 创建带注释的帧
            annotated_frame = frame.copy()

            # 如果检测到姿态，绘制关键点和连接线
            if results.pose_landmarks:
                self.draw_custom_landmarks(annotated_frame, results.pose_landmarks)

            return annotated_frame

        except Exception as e:
            print(f"姿态检测处理出错: {e}")
            return frame.copy()



    def draw_custom_landmarks(self, image, landmarks):
        """使用自定义颜色和粗细绘制关键点"""
        if not self.mediapipe_initialized or self.mp_pose is None:
            return

        height, width, _ = image.shape

        # 绘制连接线
        for connection in self.mp_pose.POSE_CONNECTIONS:
            start_idx = connection[0]
            end_idx = connection[1]

            if start_idx < len(landmarks.landmark) and end_idx < len(landmarks.landmark):
                start_landmark = landmarks.landmark[start_idx]
                end_landmark = landmarks.landmark[end_idx]

                # 检查关键点可见性和用户选择
                start_visible = (start_landmark.visibility > 0.5 and
                               hasattr(self, 'landmark_visibility') and
                               self.landmark_visibility[start_idx].get())
                end_visible = (end_landmark.visibility > 0.5 and
                             hasattr(self, 'landmark_visibility') and
                             self.landmark_visibility[end_idx].get())

                if start_visible and end_visible:
                    start_point = (
                        int(start_landmark.x * width),
                        int(start_landmark.y * height)
                    )
                    end_point = (
                        int(end_landmark.x * width),
                        int(end_landmark.y * height)
                    )

                    # 绘制连接线
                    cv2.line(
                        image,
                        start_point,
                        end_point,
                        self.connection_color,
                        self.line_thickness
                    )

        # 绘制关键点
        for i, landmark in enumerate(landmarks.landmark):
            # 检查关键点可见性和用户选择
            landmark_visible = (landmark.visibility > 0.5 and
                              hasattr(self, 'landmark_visibility') and
                              self.landmark_visibility[i].get())

            if landmark_visible:
                x = int(landmark.x * width)
                y = int(landmark.y * height)

                # 根据形状绘制关键点
                self.draw_landmark_shape(image, x, y, self.landmark_size, self.landmark_shape, self.landmark_color)

    def draw_landmark_shape(self, image, x, y, size, shape, color):
        """绘制不同形状的关键点"""
        try:
            if shape == "circle":
                # 圆形
                cv2.circle(image, (x, y), size, color, -1)
                cv2.circle(image, (x, y), size + 1, (0, 0, 0), 1)  # 黑色边框

            elif shape == "square":
                # 正方形
                half_size = size
                cv2.rectangle(
                    image,
                    (x - half_size, y - half_size),
                    (x + half_size, y + half_size),
                    color,
                    -1
                )
                # 黑色边框
                cv2.rectangle(
                    image,
                    (x - half_size - 1, y - half_size - 1),
                    (x + half_size + 1, y + half_size + 1),
                    (0, 0, 0),
                    1
                )

            elif shape == "diamond":
                # 菱形
                points = np.array([
                    [x, y - size],      # 上
                    [x + size, y],      # 右
                    [x, y + size],      # 下
                    [x - size, y]       # 左
                ], np.int32)

                cv2.fillPoly(image, [points], color)
                # 黑色边框
                cv2.polylines(image, [points], True, (0, 0, 0), 1)

            else:
                # 默认圆形
                cv2.circle(image, (x, y), size, color, -1)
                cv2.circle(image, (x, y), size + 1, (0, 0, 0), 1)

        except Exception as e:
            print(f"绘制关键点形状时出错: {e}")
            # 出错时绘制默认圆形
            cv2.circle(image, (x, y), size, color, -1)
        
    def toggle_playback(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def start_playback(self):
        """开始播放"""
        if not self.cap:
            return

        self.is_playing = True
        self.should_stop = False
        self.play_button.config(text="暂停")

        # 启动后台处理线程
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self.process_frames_background)
            self.processing_thread.daemon = True
            self.processing_thread.start()

        # 启动播放循环
        self.playback_loop()

    def pause_playback(self):
        """暂停播放"""
        self.is_playing = False
        self.play_button.config(text="播放")

    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.should_stop = True
        self.play_button.config(text="播放")
        self.current_frame_number = 0

        # 清空队列
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

        self.show_frame()

    def playback_loop(self):
        """优化的播放循环（支持双视频）"""
        # 检查是否应该停止播放
        max_frames = self.total_frames1 if self.total_frames1 > 0 else 0

        if not self.is_playing or self.current_frame_number >= max_frames:
            if self.current_frame_number >= max_frames:
                self.pause_playback()
            return

        # 显示当前帧
        self.show_frame()

        # 移动到下一帧
        self.current_frame_number += 1

        # 使用after方法调度下一次更新，而不是sleep
        if self.is_playing:
            self.root.after(self.frame_interval, self.playback_loop)
            
    def on_progress_change(self, value):
        """进度条变化事件（支持双视频）"""
        if not self.is_playing and self.cap1 and self.total_frames1 > 0:
            frame_number = int((float(value) / 100) * self.total_frames1)
            self.current_frame_number = max(0, min(frame_number, self.total_frames1 - 1))
            self.show_frame()

    def export_video1(self):
        """导出视频1的姿态检测结果"""
        if not self.cap1 or not self.mediapipe_initialized:
            messagebox.showwarning("警告", "请先加载视频1并确保姿态检测已初始化")
            return

        # 选择保存路径
        output_path = filedialog.asksaveasfilename(
            title="保存视频1检测结果",
            defaultextension=".mp4",
            filetypes=[("MP4文件", "*.mp4"), ("AVI文件", "*.avi")]
        )

        if not output_path:
            return

        self.export_video_with_pose(self.cap1, self.total_frames1, self.fps1, output_path, "视频1")

    def export_video2(self):
        """导出视频2的姿态检测结果"""
        if not self.cap2 or not self.mediapipe_initialized:
            messagebox.showwarning("警告", "请先加载视频2并确保姿态检测已初始化")
            return

        # 选择保存路径
        output_path = filedialog.asksaveasfilename(
            title="保存视频2检测结果",
            defaultextension=".mp4",
            filetypes=[("MP4文件", "*.mp4"), ("AVI文件", "*.avi")]
        )

        if not output_path:
            return

        self.export_video_with_pose(self.cap2, self.total_frames2, self.fps2, output_path, "视频2")

    def export_video_with_pose(self, cap, total_frames, fps, output_path, video_name):
        """导出带有姿态检测的视频"""
        try:
            # 创建进度对话框
            progress_window = tk.Toplevel(self.root)
            progress_window.title(f"导出{video_name}")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)

            # 居中显示
            progress_window.transient(self.root)
            progress_window.grab_set()

            # 进度标签
            progress_label = ttk.Label(progress_window, text=f"正在导出{video_name}...")
            progress_label.pack(pady=10)

            # 进度条
            progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            progress_bar['maximum'] = total_frames

            # 状态标签
            status_label = ttk.Label(progress_window, text="准备中...")
            status_label.pack(pady=5)

            # 取消按钮
            cancel_export = False
            def cancel_callback():
                nonlocal cancel_export
                cancel_export = True
                progress_window.destroy()

            cancel_button = ttk.Button(progress_window, text="取消", command=cancel_callback)
            cancel_button.pack(pady=5)

            # 更新进度窗口
            progress_window.update()

            # 获取视频属性
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            if not out.isOpened():
                messagebox.showerror("错误", "无法创建输出视频文件")
                progress_window.destroy()
                return

            # 逐帧处理
            for frame_idx in range(total_frames):
                if cancel_export:
                    break

                # 读取帧
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    break

                # 进行姿态检测
                pose_frame = self.process_pose_detection(frame)

                # 写入帧
                out.write(pose_frame)

                # 更新进度
                progress_bar['value'] = frame_idx + 1
                status_label.config(text=f"处理帧 {frame_idx + 1}/{total_frames}")
                progress_window.update()

                # 每100帧强制更新一次界面
                if frame_idx % 100 == 0:
                    progress_window.update_idletasks()

            # 释放资源
            out.release()
            progress_window.destroy()

            if not cancel_export:
                messagebox.showinfo("成功", f"{video_name}导出完成！\n保存位置: {output_path}")
                print(f"{video_name}导出完成: {output_path}")
            else:
                # 删除未完成的文件
                try:
                    import os
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except:
                    pass
                print(f"{video_name}导出已取消")

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            messagebox.showerror("错误", f"导出{video_name}时出错: {str(e)}")
            print(f"导出{video_name}时出错: {e}")

    def create_dynamic_video_area(self):
        """创建动态视频显示区域"""
        # 主视频容器
        self.video_container = ttk.Frame(self.main_frame)
        self.video_container.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # 配置视频容器的网格权重
        self.video_container.columnconfigure(0, weight=1)
        self.video_container.columnconfigure(1, weight=1)
        self.video_container.rowconfigure(0, weight=1)

        # 视频1区域（始终显示）
        self.video1_frame = ttk.LabelFrame(self.video_container, text="视频1", padding="5")
        self.video1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # 视频1显示标签
        self.video1_label = ttk.Label(self.video1_frame, text="请选择视频文件", anchor="center")
        self.video1_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置视频1框架的网格权重
        self.video1_frame.columnconfigure(0, weight=1)
        self.video1_frame.rowconfigure(0, weight=1)

        # 视频2区域（动态显示）
        self.video2_frame = ttk.LabelFrame(self.video_container, text="视频2", padding="5")
        # 初始时不显示视频2区域

        # 视频2显示标签
        self.video2_label = ttk.Label(self.video2_frame, text="请选择第二个视频文件", anchor="center")
        self.video2_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置视频2框架的网格权重
        self.video2_frame.columnconfigure(0, weight=1)
        self.video2_frame.rowconfigure(0, weight=1)

    def create_floating_window_buttons(self):
        """创建悬浮窗按钮"""
        # 悬浮窗控制面板
        float_frame = ttk.LabelFrame(self.main_frame, text="工具窗口", padding="5")
        float_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # 关节点选择器按钮
        self.landmark_selector_button = ttk.Button(
            float_frame,
            text="关节点选择器",
            command=self.toggle_landmark_selector_window
        )
        self.landmark_selector_button.grid(row=0, column=0, padx=(0, 10))

        # 设置面板按钮
        self.settings_button = ttk.Button(
            float_frame,
            text="显示设置",
            command=self.toggle_settings_window
        )
        self.settings_button.grid(row=0, column=1, padx=(0, 10))

        # 性能监控标签
        self.performance_label = ttk.Label(float_frame, text="性能: 正常")
        self.performance_label.grid(row=0, column=2, padx=(20, 0))

    def update_video_layout(self):
        """根据视频加载状态更新布局"""
        if self.video2_loaded:
            # 显示双视频布局
            self.video1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
            self.video2_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))
            self.video_container.columnconfigure(0, weight=1)
            self.video_container.columnconfigure(1, weight=1)
        else:
            # 显示单视频布局
            self.video2_frame.grid_remove()
            self.video1_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.video_container.columnconfigure(0, weight=1)
            self.video_container.columnconfigure(1, weight=0)

    def toggle_landmark_selector_window(self):
        """切换关节点选择器悬浮窗"""
        if self.landmark_selector_window is None or not self.landmark_selector_window.winfo_exists():
            self.create_landmark_selector_window()
        else:
            self.landmark_selector_window.destroy()
            self.landmark_selector_window = None

    def toggle_settings_window(self):
        """切换设置悬浮窗"""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.create_settings_window()
        else:
            self.settings_window.destroy()
            self.settings_window = None

    def create_landmark_selector_window(self):
        """创建关节点选择器悬浮窗"""
        self.landmark_selector_window = tk.Toplevel(self.root)
        self.landmark_selector_window.title("关节点选择器")
        self.landmark_selector_window.geometry("300x500")
        self.landmark_selector_window.resizable(True, True)

        # 设置窗口属性
        self.landmark_selector_window.transient(self.root)

        # 创建关节点选择内容
        self.create_landmark_selector_content(self.landmark_selector_window)

        # 窗口关闭事件
        self.landmark_selector_window.protocol("WM_DELETE_WINDOW",
                                               lambda: self.close_landmark_selector_window())

    def create_settings_window(self):
        """创建设置悬浮窗"""
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("显示设置")
        self.settings_window.geometry("400x300")
        self.settings_window.resizable(False, False)

        # 设置窗口属性
        self.settings_window.transient(self.root)

        # 创建设置内容
        self.create_settings_content(self.settings_window)

        # 窗口关闭事件
        self.settings_window.protocol("WM_DELETE_WINDOW",
                                      lambda: self.close_settings_window())

    def close_landmark_selector_window(self):
        """关闭关节点选择器窗口"""
        if self.landmark_selector_window:
            self.landmark_selector_window.destroy()
            self.landmark_selector_window = None

    def close_settings_window(self):
        """关闭设置窗口"""
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None

    def toggle_color_settings_window(self):
        """切换颜色设置悬浮窗"""
        if not hasattr(self, 'color_settings_window') or self.color_settings_window is None or not self.color_settings_window.winfo_exists():
            self.create_color_settings_window()
        else:
            self.color_settings_window.destroy()
            self.color_settings_window = None

    def toggle_export_window(self):
        """切换导出悬浮窗"""
        if not hasattr(self, 'export_window') or self.export_window is None or not self.export_window.winfo_exists():
            self.create_export_window()
        else:
            self.export_window.destroy()
            self.export_window = None

    def toggle_performance_window(self):
        """切换性能监控悬浮窗"""
        if not hasattr(self, 'performance_window') or self.performance_window is None or not self.performance_window.winfo_exists():
            self.create_performance_window()
        else:
            self.performance_window.destroy()
            self.performance_window = None

    def toggle_help_window(self):
        """切换帮助悬浮窗"""
        if not hasattr(self, 'help_window') or self.help_window is None or not self.help_window.winfo_exists():
            self.create_help_window()
        else:
            self.help_window.destroy()
            self.help_window = None

    def create_color_settings_window(self):
        """创建颜色设置悬浮窗"""
        self.color_settings_window = tk.Toplevel(self.root)
        self.color_settings_window.title("颜色设置")
        self.color_settings_window.geometry("350x200")
        self.color_settings_window.resizable(False, False)

        # 设置窗口属性
        self.color_settings_window.transient(self.root)

        # 创建颜色设置内容
        main_frame = ttk.Frame(self.color_settings_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 关键点颜色
        ttk.Label(main_frame, text="关键点颜色:").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        color_combo1 = ttk.Combobox(main_frame, textvariable=self.landmark_color_var,
                                   values=["红色", "绿色", "蓝色", "黄色", "青色", "白色"],
                                   state="readonly", width=15)
        color_combo1.grid(row=0, column=1, padx=(0, 10))
        color_combo1.bind('<<ComboboxSelected>>', self.on_landmark_color_change)

        # 连接线颜色
        ttk.Label(main_frame, text="连接线颜色:").grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky=tk.W)
        color_combo2 = ttk.Combobox(main_frame, textvariable=self.connection_color_var,
                                   values=["红色", "绿色", "蓝色", "黄色", "青色", "白色"],
                                   state="readonly", width=15)
        color_combo2.grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        color_combo2.bind('<<ComboboxSelected>>', self.on_connection_color_change)

        # 预设颜色方案
        ttk.Label(main_frame, text="预设方案:").grid(row=2, column=0, padx=(0, 10), pady=(20, 0), sticky=tk.W)

        scheme_frame = ttk.Frame(main_frame)
        scheme_frame.grid(row=2, column=1, pady=(20, 0), sticky=tk.W)

        ttk.Button(scheme_frame, text="经典", command=lambda: self.apply_color_scheme("classic")).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(scheme_frame, text="活力", command=lambda: self.apply_color_scheme("vibrant")).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(scheme_frame, text="柔和", command=lambda: self.apply_color_scheme("soft")).grid(row=0, column=2)

        # 窗口关闭事件
        self.color_settings_window.protocol("WM_DELETE_WINDOW",
                                           lambda: self.close_color_settings_window())

    def create_export_window(self):
        """创建导出悬浮窗"""
        self.export_window = tk.Toplevel(self.root)
        self.export_window.title("导出视频")
        self.export_window.geometry("400x300")
        self.export_window.resizable(False, False)

        # 设置窗口属性
        self.export_window.transient(self.root)

        # 创建导出内容
        main_frame = ttk.Frame(self.export_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 导出选项
        ttk.Label(main_frame, text="导出选项", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # 视频选择
        ttk.Label(main_frame, text="选择视频:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.export_video_var = tk.StringVar(value="视频1")
        export_combo = ttk.Combobox(main_frame, textvariable=self.export_video_var,
                                   values=["视频1", "视频2", "对比视频"], state="readonly")
        export_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # 质量设置
        ttk.Label(main_frame, text="输出质量:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.export_quality_var = tk.StringVar(value="高质量")
        quality_combo = ttk.Combobox(main_frame, textvariable=self.export_quality_var,
                                    values=["高质量", "中等质量", "压缩质量"], state="readonly")
        quality_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # 帧率设置
        ttk.Label(main_frame, text="输出帧率:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.export_fps_var = tk.IntVar(value=30)
        fps_spin = ttk.Spinbox(main_frame, from_=15, to=60, textvariable=self.export_fps_var, width=10)
        fps_spin.grid(row=3, column=1, sticky=tk.W, pady=5)

        # 导出按钮
        export_btn = ttk.Button(main_frame, text="开始导出", command=self.start_export)
        export_btn.grid(row=4, column=0, columnspan=2, pady=20)

        # 进度条
        self.export_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.export_progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 状态标签
        self.export_status_label = ttk.Label(main_frame, text="准备导出")
        self.export_status_label.grid(row=6, column=0, columnspan=2, pady=5)

        main_frame.columnconfigure(1, weight=1)

        # 窗口关闭事件
        self.export_window.protocol("WM_DELETE_WINDOW", lambda: self.close_export_window())

    def create_performance_window(self):
        """创建性能监控悬浮窗"""
        self.performance_window = tk.Toplevel(self.root)
        self.performance_window.title("性能监控")
        self.performance_window.geometry("300x250")
        self.performance_window.resizable(False, False)

        # 设置窗口属性
        self.performance_window.transient(self.root)

        # 创建性能监控内容
        main_frame = ttk.Frame(self.performance_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="性能监控", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # FPS显示
        ttk.Label(main_frame, text="当前FPS:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fps_label = ttk.Label(main_frame, text="0", foreground="blue")
        self.fps_label.grid(row=1, column=1, sticky=tk.W, pady=5)

        # 内存使用
        ttk.Label(main_frame, text="内存使用:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.memory_label = ttk.Label(main_frame, text="0 MB", foreground="green")
        self.memory_label.grid(row=2, column=1, sticky=tk.W, pady=5)

        # CPU使用率
        ttk.Label(main_frame, text="CPU使用率:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cpu_label = ttk.Label(main_frame, text="0%", foreground="orange")
        self.cpu_label.grid(row=3, column=1, sticky=tk.W, pady=5)

        # 处理延迟
        ttk.Label(main_frame, text="处理延迟:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.latency_label = ttk.Label(main_frame, text="0 ms", foreground="red")
        self.latency_label.grid(row=4, column=1, sticky=tk.W, pady=5)

        # 优化建议
        ttk.Label(main_frame, text="优化建议:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, pady=(15, 5))
        self.optimization_text = tk.Text(main_frame, height=4, width=30, wrap=tk.WORD)
        self.optimization_text.grid(row=6, column=0, columnspan=2, pady=5)
        self.optimization_text.insert("1.0", "系统运行正常")

        # 启动性能监控
        self.start_performance_monitoring()

        # 窗口关闭事件
        self.performance_window.protocol("WM_DELETE_WINDOW", lambda: self.close_performance_window())

    def create_help_window(self):
        """创建帮助悬浮窗"""
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("帮助")
        self.help_window.geometry("500x400")
        self.help_window.resizable(True, True)

        # 设置窗口属性
        self.help_window.transient(self.root)

        # 创建帮助内容
        main_frame = ttk.Frame(self.help_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.help_window.columnconfigure(0, weight=1)
        self.help_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        ttk.Label(main_frame, text="姿态检测应用帮助", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(0, 10))

        # 创建滚动文本框
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        help_text = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)

        help_content = """
🎯 基本操作指南

📁 文件操作：
• 点击"选择视频1"加载主视频文件
• 点击"选择视频2"加载对比视频文件（可选）
• 支持常见视频格式：MP4, AVI, MOV等

▶️ 播放控制：
• 播放/暂停：控制视频播放状态
• 进度条：拖动调整播放位置
• 帧控制：精确到帧的播放控制

🛠️ 工具栏功能：

👤 关节点选择器：
• 选择要显示的身体关节点
• 支持按身体部位分组选择
• 交互式人体示意图点击选择

⚙️ 显示设置：
• 调整关节点和连接线的显示样式
• 支持大小、粗细、形状自定义

🎨 颜色设置：
• 自定义关节点和连接线颜色
• 预设颜色方案快速应用

💾 导出功能：
• 导出带姿态检测的视频
• 支持多种质量和帧率选项

📊 性能监控：
• 实时查看FPS、内存使用等
• 获取优化建议

🔧 高级功能：

🎯 关节点筛选：
• 头部：鼻子、眼部、耳朵、嘴部
• 上肢：肩膀、肘部、手腕、手指
• 躯干：肩膀、髋部连接
• 下肢：髋部、膝盖、脚踝、脚部

📐 自适应布局：
• 单视频模式：默认全屏显示
• 双视频模式：自动并排对比
• 响应式界面适配不同屏幕

⚡ 性能优化：
• 智能帧缓存管理
• 多线程处理提升响应速度
• 内存使用优化

💡 使用技巧：
• 使用工具提示了解按钮功能
• 悬浮窗可独立移动和调整
• 支持键盘快捷键操作
• 实时预览设置变化

❓ 常见问题：
• 如果检测不准确，尝试调整视频质量
• 性能问题时可关闭不需要的关节点
• 导出时间取决于视频长度和质量设置

📞 技术支持：
如遇到问题，请检查：
1. 视频文件格式是否支持
2. 系统内存是否充足
3. MediaPipe是否正确安装
        """

        help_text.insert("1.0", help_content)
        help_text.config(state="disabled")  # 设为只读

        help_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 窗口关闭事件
        self.help_window.protocol("WM_DELETE_WINDOW", lambda: self.close_help_window())

    def close_color_settings_window(self):
        """关闭颜色设置窗口"""
        if hasattr(self, 'color_settings_window') and self.color_settings_window:
            self.color_settings_window.destroy()
            self.color_settings_window = None

    def close_export_window(self):
        """关闭导出窗口"""
        if hasattr(self, 'export_window') and self.export_window:
            self.export_window.destroy()
            self.export_window = None

    def close_performance_window(self):
        """关闭性能监控窗口"""
        if hasattr(self, 'performance_window') and self.performance_window:
            self.performance_window.destroy()
            self.performance_window = None
            self.stop_performance_monitoring()

    def close_help_window(self):
        """关闭帮助窗口"""
        if hasattr(self, 'help_window') and self.help_window:
            self.help_window.destroy()
            self.help_window = None

    def apply_color_scheme(self, scheme_name):
        """应用预设颜色方案"""
        try:
            if scheme_name == "classic":
                self.landmark_color_var.set("绿色")
                self.connection_color_var.set("红色")
            elif scheme_name == "vibrant":
                self.landmark_color_var.set("黄色")
                self.connection_color_var.set("青色")
            elif scheme_name == "soft":
                self.landmark_color_var.set("白色")
                self.connection_color_var.set("蓝色")

            # 应用颜色变化
            self.on_landmark_color_change()
            self.on_connection_color_change()

            print(f"已应用{scheme_name}颜色方案")
        except Exception as e:
            print(f"应用颜色方案时出错: {e}")

    def start_export(self):
        """开始导出视频"""
        try:
            # 这里添加导出逻辑
            self.export_status_label.config(text="导出功能开发中...")
            print("导出功能开发中...")
        except Exception as e:
            print(f"导出时出错: {e}")

    def start_performance_monitoring(self):
        """启动性能监控"""
        try:
            # 这里添加性能监控逻辑
            self.update_performance_stats()
        except Exception as e:
            print(f"启动性能监控时出错: {e}")

    def stop_performance_monitoring(self):
        """停止性能监控"""
        try:
            # 停止性能监控定时器
            if hasattr(self, 'performance_timer'):
                self.root.after_cancel(self.performance_timer)
        except Exception as e:
            print(f"停止性能监控时出错: {e}")

    def update_performance_stats(self):
        """更新性能统计"""
        try:
            if hasattr(self, 'performance_window') and self.performance_window and self.performance_window.winfo_exists():
                import psutil
                import os

                # 获取当前进程
                process = psutil.Process(os.getpid())

                # 更新内存使用
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_label.config(text=f"{memory_mb:.1f} MB")

                # 更新CPU使用率
                cpu_percent = process.cpu_percent()
                self.cpu_label.config(text=f"{cpu_percent:.1f}%")

                # 模拟FPS和延迟（实际应用中应该从视频处理中获取）
                self.fps_label.config(text="30")
                self.latency_label.config(text="16 ms")

                # 更新优化建议
                suggestions = []
                if memory_mb > 500:
                    suggestions.append("内存使用较高，建议关闭不需要的关节点")
                if cpu_percent > 80:
                    suggestions.append("CPU使用率高，建议降低视频质量")

                if suggestions:
                    self.optimization_text.delete("1.0", tk.END)
                    self.optimization_text.insert("1.0", "\n".join(suggestions))
                else:
                    self.optimization_text.delete("1.0", tk.END)
                    self.optimization_text.insert("1.0", "系统运行正常")

                # 每秒更新一次
                self.performance_timer = self.root.after(1000, self.update_performance_stats)

        except ImportError:
            # 如果没有psutil，显示模拟数据
            if hasattr(self, 'performance_window') and self.performance_window and self.performance_window.winfo_exists():
                self.memory_label.config(text="N/A")
                self.cpu_label.config(text="N/A")
                self.fps_label.config(text="30")
                self.latency_label.config(text="16 ms")
        except Exception as e:
            print(f"更新性能统计时出错: {e}")

    def update_status(self, message, color="black"):
        """更新状态栏信息"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=message, foreground=color)
        except Exception as e:
            print(f"更新状态时出错: {e}")

    def smart_open_video(self):
        """智能打开视频功能"""
        try:
            # 检查当前视频状态
            video1_loaded = hasattr(self, 'cap1') and self.cap1 is not None
            video2_loaded = hasattr(self, 'cap2') and self.cap2 is not None

            if not video1_loaded:
                # 第一次打开 - 加载视频1
                self.load_video1()
                self.update_status("已加载视频1", "green")
            elif not video2_loaded:
                # 第二次打开 - 加载视频2并启用比较模式
                self.load_video2()
                self.update_status("已加载视频2，启用比较模式", "blue")
            else:
                # 已有两个视频 - 询问替换哪个
                self.show_video_replace_dialog()

        except Exception as e:
            print(f"智能打开视频时出错: {e}")
            self.update_status("打开视频失败", "red")

    def show_video_replace_dialog(self):
        """显示视频替换对话框"""
        try:
            # 创建替换选择对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("替换视频")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (150 // 2)
            dialog.geometry(f"300x150+{x}+{y}")

            # 对话框内容
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            ttk.Label(main_frame, text="已有两个视频，请选择要替换的视频:",
                     font=("Arial", 10)).grid(row=0, column=0, columnspan=2, pady=(0, 20))

            # 按钮
            ttk.Button(main_frame, text="替换视频1",
                      command=lambda: self.replace_video(dialog, 1)).grid(row=1, column=0, padx=(0, 10))
            ttk.Button(main_frame, text="替换视频2",
                      command=lambda: self.replace_video(dialog, 2)).grid(row=1, column=1, padx=(10, 0))

            # 取消按钮
            ttk.Button(main_frame, text="取消",
                      command=dialog.destroy).grid(row=2, column=0, columnspan=2, pady=(20, 0))

        except Exception as e:
            print(f"显示视频替换对话框时出错: {e}")

    def replace_video(self, dialog, video_num):
        """替换指定的视频"""
        try:
            dialog.destroy()

            if video_num == 1:
                self.load_video1()
                self.update_status("已替换视频1", "green")
            else:
                self.load_video2()
                self.update_status("已替换视频2", "blue")

        except Exception as e:
            print(f"替换视频{video_num}时出错: {e}")
            self.update_status(f"替换视频{video_num}失败", "red")

    def create_landmark_selector_content(self, parent):
        """创建关节点选择器内容"""
        # 主框架
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(control_frame, text="全选", command=self.select_all_landmarks).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(control_frame, text="全不选", command=self.deselect_all_landmarks).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(control_frame, text="反选", command=self.invert_landmark_selection).grid(row=0, column=2, padx=(0, 10))

        # 分组按钮
        ttk.Button(control_frame, text="头部", command=lambda: self.select_landmark_group("头部")).grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        ttk.Button(control_frame, text="上肢", command=lambda: self.select_landmark_group("上肢")).grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        ttk.Button(control_frame, text="躯干", command=lambda: self.select_landmark_group("躯干")).grid(row=1, column=2, padx=(0, 5), pady=(5, 0))
        ttk.Button(control_frame, text="下肢", command=lambda: self.select_landmark_group("下肢")).grid(row=1, column=3, padx=(0, 5), pady=(5, 0))

        # 人体示意图和关节点列表的容器
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # 人体示意图
        diagram_frame = ttk.LabelFrame(content_frame, text="人体示意图", padding="5")
        diagram_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # 创建示意图画布
        self.float_diagram_canvas = tk.Canvas(diagram_frame, width=120, height=200, bg="white", relief="sunken", bd=1)
        self.float_diagram_canvas.grid(row=0, column=0)

        # 绘制人体示意图
        self.draw_compact_body_diagram()

        # 绑定点击事件
        self.float_diagram_canvas.bind("<Button-1>", self.on_float_diagram_click)

        # 关节点列表
        list_frame = ttk.LabelFrame(content_frame, text="关节点列表", padding="5")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))

        # 创建滚动列表
        list_canvas = tk.Canvas(list_frame, height=200)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
        scrollable_list = ttk.Frame(list_canvas)

        scrollable_list.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=scrollable_list, anchor="nw")
        list_canvas.configure(yscrollcommand=scrollbar.set)

        # 创建关节点复选框
        self.create_landmark_checkboxes(scrollable_list)

        list_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_settings_content(self, parent):
        """创建设置内容"""
        # 主框架
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # 颜色设置
        color_frame = ttk.LabelFrame(main_frame, text="颜色设置", padding="5")
        color_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 关键点颜色
        ttk.Label(color_frame, text="关键点颜色:").grid(row=0, column=0, padx=(0, 5))
        self.float_landmark_color_var = tk.StringVar(value="绿色")
        landmark_color_combo = ttk.Combobox(color_frame, textvariable=self.float_landmark_color_var,
                                          values=["红色", "绿色", "蓝色", "黄色", "青色", "白色"],
                                          state="readonly", width=10)
        landmark_color_combo.grid(row=0, column=1, padx=(0, 10))
        landmark_color_combo.bind('<<ComboboxSelected>>', self.on_float_landmark_color_change)

        # 连接线颜色
        ttk.Label(color_frame, text="连接线颜色:").grid(row=0, column=2, padx=(0, 5))
        self.float_connection_color_var = tk.StringVar(value="红色")
        connection_color_combo = ttk.Combobox(color_frame, textvariable=self.float_connection_color_var,
                                            values=["红色", "绿色", "蓝色", "黄色", "青色", "白色"],
                                            state="readonly", width=10)
        connection_color_combo.grid(row=0, column=3)
        connection_color_combo.bind('<<ComboboxSelected>>', self.on_float_connection_color_change)

        # 大小设置
        size_frame = ttk.LabelFrame(main_frame, text="大小设置", padding="5")
        size_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 线条粗细
        ttk.Label(size_frame, text="线条粗细:").grid(row=0, column=0, padx=(0, 5))
        self.float_thickness_var = tk.IntVar(value=2)
        thickness_scale = ttk.Scale(size_frame, from_=1, to=8, orient=tk.HORIZONTAL,
                                   variable=self.float_thickness_var, length=100)
        thickness_scale.grid(row=0, column=1, padx=(0, 5))
        thickness_scale.bind("<ButtonRelease-1>", self.on_float_thickness_change)

        self.float_thickness_label = ttk.Label(size_frame, text="2")
        self.float_thickness_label.grid(row=0, column=2, padx=(5, 10))

        # 关节点大小
        ttk.Label(size_frame, text="关节点大小:").grid(row=0, column=3, padx=(0, 5))
        self.float_landmark_size_var = tk.IntVar(value=8)
        size_scale = ttk.Scale(size_frame, from_=3, to=15, orient=tk.HORIZONTAL,
                              variable=self.float_landmark_size_var, length=100)
        size_scale.grid(row=0, column=4, padx=(0, 5))
        size_scale.bind("<ButtonRelease-1>", self.on_float_landmark_size_change)

        self.float_size_label = ttk.Label(size_frame, text="8")
        self.float_size_label.grid(row=0, column=5, padx=(5, 0))

        # 形状设置
        shape_frame = ttk.LabelFrame(main_frame, text="形状设置", padding="5")
        shape_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(shape_frame, text="关节点形状:").grid(row=0, column=0, padx=(0, 5))
        self.float_landmark_shape_var = tk.StringVar(value="正方形")
        shape_combo = ttk.Combobox(shape_frame, textvariable=self.float_landmark_shape_var,
                                  values=["圆形", "正方形", "菱形"], state="readonly", width=10)
        shape_combo.grid(row=0, column=1)
        shape_combo.bind('<<ComboboxSelected>>', self.on_float_landmark_shape_change)

        # 重置按钮
        ttk.Button(main_frame, text="重置默认", command=self.reset_float_settings).grid(row=3, column=0, pady=(10, 0))

    def draw_compact_body_diagram(self):
        """绘制紧凑的人体关节示意图"""
        try:
            # 清除画布
            self.float_diagram_canvas.delete("all")

            # 定义紧凑的关节点位置
            compact_positions = {
                # 头部
                0: (60, 15),   # 鼻子
                1: (57, 12),   # 左眼内侧
                2: (54, 12),   # 左眼
                3: (51, 12),   # 左眼外侧
                4: (63, 12),   # 右眼内侧
                5: (66, 12),   # 右眼
                6: (69, 12),   # 右眼外侧
                7: (48, 18),   # 左耳
                8: (72, 18),   # 右耳
                9: (57, 20),   # 嘴左
                10: (63, 20),  # 嘴右

                # 上身
                11: (42, 40),  # 左肩
                12: (78, 40),  # 右肩
                13: (30, 60),  # 左肘
                14: (90, 60),  # 右肘
                15: (24, 80),  # 左腕
                16: (96, 80),  # 右腕
                17: (21, 85),  # 左小指
                18: (99, 85),  # 右小指
                19: (18, 82),  # 左食指
                20: (102, 82), # 右食指
                21: (27, 87),  # 左拇指
                22: (93, 87),  # 右拇指

                # 下身
                23: (48, 90),  # 左髋
                24: (72, 90),  # 右髋
                25: (45, 110), # 左膝
                26: (75, 110), # 右膝
                27: (42, 130), # 左踝
                28: (78, 130), # 右踝
                29: (39, 135), # 左脚跟
                30: (81, 135), # 右脚跟
                31: (36, 138), # 左脚趾
                32: (84, 138), # 右脚趾
            }

            # 绘制连接线
            connections = [
                (11, 12), (11, 23), (12, 24), (23, 24),  # 躯干
                (11, 13), (13, 15), (12, 14), (14, 16),  # 手臂
                (15, 17), (15, 19), (15, 21),  # 左手
                (16, 18), (16, 20), (16, 22),  # 右手
                (23, 25), (25, 27), (24, 26), (26, 28),  # 腿部
                (27, 29), (27, 31), (28, 30), (28, 32),  # 脚部
            ]

            for start_idx, end_idx in connections:
                if start_idx in compact_positions and end_idx in compact_positions:
                    start_pos = compact_positions[start_idx]
                    end_pos = compact_positions[end_idx]

                    start_selected = self.landmark_visibility[start_idx].get()
                    end_selected = self.landmark_visibility[end_idx].get()

                    if start_selected and end_selected:
                        color = "#0066CC"
                        width = 2
                    else:
                        color = "#CCCCCC"
                        width = 1

                    self.float_diagram_canvas.create_line(
                        start_pos[0], start_pos[1], end_pos[0], end_pos[1],
                        fill=color, width=width
                    )

            # 绘制关节点
            for landmark_idx, pos in compact_positions.items():
                x, y = pos
                is_selected = self.landmark_visibility[landmark_idx].get()

                if is_selected:
                    color = "#FF6600"
                    size = 3
                else:
                    color = "#999999"
                    size = 2

                self.float_diagram_canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=color, outline="black", width=1,
                    tags=f"landmark_{landmark_idx}"
                )

                # 添加关节点编号（小字体）
                self.float_diagram_canvas.create_text(
                    x, y, text=str(landmark_idx),
                    font=("Arial", 5), fill="white",
                    tags=f"landmark_{landmark_idx}"
                )

            # 存储位置信息供点击检测使用
            self.compact_positions = compact_positions

        except Exception as e:
            print(f"绘制紧凑人体示意图时出错: {e}")

    def on_float_diagram_click(self, event):
        """处理悬浮窗示意图点击事件"""
        try:
            x, y = event.x, event.y

            min_distance = float('inf')
            closest_landmark = None

            for landmark_idx, pos in self.compact_positions.items():
                distance = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
                if distance < min_distance and distance < 10:
                    min_distance = distance
                    closest_landmark = landmark_idx

            if closest_landmark is not None:
                current_state = self.landmark_visibility[closest_landmark].get()
                self.landmark_visibility[closest_landmark].set(not current_state)

                self.draw_compact_body_diagram()
                self.on_landmark_visibility_change()

        except Exception as e:
            print(f"处理悬浮窗示意图点击时出错: {e}")

    def create_landmark_checkboxes(self, parent):
        """创建关节点复选框列表"""
        row = 0
        for group_name, landmark_indices in self.landmark_groups.items():
            # 分组标题
            group_label = ttk.Label(parent, text=f"{group_name}:", font=("Arial", 9, "bold"))
            group_label.grid(row=row, column=0, sticky=tk.W, pady=(5, 2))
            row += 1

            # 该分组的关节点复选框
            for landmark_idx in landmark_indices:
                landmark_name = self.landmark_info[landmark_idx]
                cb = ttk.Checkbutton(
                    parent,
                    text=f"{landmark_idx}: {landmark_name}",
                    variable=self.landmark_visibility[landmark_idx],
                    command=self.on_landmark_visibility_change
                )
                cb.grid(row=row, column=0, sticky=tk.W, padx=(10, 0), pady=1)
                row += 1

    def on_float_landmark_color_change(self, event=None):
        """悬浮窗关键点颜色改变事件"""
        try:
            color_name = self.float_landmark_color_var.get()
            if color_name:
                self.landmark_color = self.get_color_bgr(color_name)
                # 同步到主设置
                if hasattr(self, 'landmark_color_var'):
                    self.landmark_color_var.set(color_name)
                print(f"关键点颜色已更改为: {color_name}")
        except Exception as e:
            print(f"更改关键点颜色时出错: {e}")

    def on_float_connection_color_change(self, event=None):
        """悬浮窗连接线颜色改变事件"""
        try:
            color_name = self.float_connection_color_var.get()
            if color_name:
                self.connection_color = self.get_color_bgr(color_name)
                # 同步到主设置
                if hasattr(self, 'connection_color_var'):
                    self.connection_color_var.set(color_name)
                print(f"连接线颜色已更改为: {color_name}")
        except Exception as e:
            print(f"更改连接线颜色时出错: {e}")

    def on_float_thickness_change(self, event):
        """悬浮窗线条粗细改变事件"""
        try:
            thickness = self.float_thickness_var.get()
            self.line_thickness = thickness
            self.float_thickness_label.config(text=str(thickness))
            # 同步到主设置
            if hasattr(self, 'thickness_var'):
                self.thickness_var.set(thickness)
            print(f"线条粗细已更改为: {thickness}")
        except Exception as e:
            print(f"更改线条粗细时出错: {e}")

    def on_float_landmark_size_change(self, event):
        """悬浮窗关节点大小改变事件"""
        try:
            size = self.float_landmark_size_var.get()
            self.landmark_size = size
            self.float_size_label.config(text=str(size))
            # 同步到主设置
            if hasattr(self, 'landmark_size_var'):
                self.landmark_size_var.set(size)
            print(f"关节点大小已更改为: {size}")
        except Exception as e:
            print(f"更改关节点大小时出错: {e}")

    def on_float_landmark_shape_change(self, event=None):
        """悬浮窗关节点形状改变事件"""
        try:
            shape_name = self.float_landmark_shape_var.get()
            if shape_name:
                self.landmark_shape = self.get_shape_type(shape_name)
                # 同步到主设置
                if hasattr(self, 'landmark_shape_var'):
                    self.landmark_shape_var.set(shape_name)
                print(f"关节点形状已更改为: {shape_name}")
        except Exception as e:
            print(f"更改关节点形状时出错: {e}")

    def reset_float_settings(self):
        """重置悬浮窗设置为默认值"""
        try:
            # 重置颜色
            self.float_landmark_color_var.set("绿色")
            self.float_connection_color_var.set("红色")
            self.landmark_color = (0, 255, 0)
            self.connection_color = (0, 0, 255)

            # 重置大小
            self.float_thickness_var.set(2)
            self.float_landmark_size_var.set(8)
            self.line_thickness = 2
            self.landmark_size = 8

            # 重置形状
            self.float_landmark_shape_var.set("正方形")
            self.landmark_shape = "square"

            # 更新标签
            self.float_thickness_label.config(text="2")
            self.float_size_label.config(text="8")

            # 同步到主设置
            if hasattr(self, 'landmark_color_var'):
                self.landmark_color_var.set("绿色")
            if hasattr(self, 'connection_color_var'):
                self.connection_color_var.set("红色")
            if hasattr(self, 'thickness_var'):
                self.thickness_var.set(2)
            if hasattr(self, 'landmark_size_var'):
                self.landmark_size_var.set(8)
            if hasattr(self, 'landmark_shape_var'):
                self.landmark_shape_var.set("正方形")

            print("设置已重置为默认值")
        except Exception as e:
            print(f"重置设置时出错: {e}")

    def initialize_landmark_selector_data(self):
        """初始化关节点选择器数据"""
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
        self.landmark_visibility = {i: tk.BooleanVar(value=True) for i in range(33)}

    def cleanup(self):
        """清理资源"""
        # 关闭悬浮窗
        if self.landmark_selector_window:
            self.landmark_selector_window.destroy()
        if self.settings_window:
            self.settings_window.destroy()
        # 停止所有播放
        self.should_stop1 = True
        self.should_stop2 = True
        self.is_playing1 = False
        self.is_playing2 = False

        # 等待线程结束
        if hasattr(self, 'processing_thread') and self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)

        # 清空队列
        if hasattr(self, 'frame_queue'):
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break

        # 释放视频资源
        if self.cap1:
            self.cap1.release()
            self.cap1 = None

        if self.cap2:
            self.cap2.release()
            self.cap2 = None

    def create_toolbar_icons(self):
        """创建工具栏图标"""
        try:
            # 创建24x24像素的图标
            icon_size = (24, 24)

            # 打开视频图标 - 文件夹图标
            self.toolbar_icons['open'] = self.create_icon_image("open", icon_size, "#FF5722")

            # 关节点选择器图标 - 人形图标
            self.toolbar_icons['joints'] = self.create_icon_image("joints", icon_size, "#4CAF50")

            # 显示设置图标 - 齿轮图标
            self.toolbar_icons['settings'] = self.create_icon_image("settings", icon_size, "#2196F3")

            # 颜色设置图标 - 调色板图标
            self.toolbar_icons['colors'] = self.create_icon_image("colors", icon_size, "#FF9800")

            # 导出图标 - 下载图标
            self.toolbar_icons['export'] = self.create_icon_image("export", icon_size, "#9C27B0")

            # 帮助图标 - 问号图标
            self.toolbar_icons['help'] = self.create_icon_image("help", icon_size, "#607D8B")

            # 性能监控图标 - 图表图标
            self.toolbar_icons['performance'] = self.create_icon_image("performance", icon_size, "#FF5722")

        except Exception as e:
            print(f"创建工具栏图标时出错: {e}")
            # 如果图标创建失败，使用空字典
            self.toolbar_icons = {}

    def create_icon_image(self, icon_type, size, bg_color="#FFFFFF"):
        """创建图标图像"""
        try:
            # 创建一个带背景的图像
            img = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # 绘制圆形背景
            margin = 2
            draw.ellipse([margin, margin, size[0]-margin, size[1]-margin],
                        fill=bg_color, outline="#CCCCCC", width=1)

            center_x, center_y = size[0] // 2, size[1] // 2

            if icon_type == "open":  # 打开文件图标
                # 绘制文件夹图标
                draw.rectangle([center_x-7, center_y-3, center_x+7, center_y+5],
                             fill="white", outline="black", width=1)
                # 文件夹标签
                draw.rectangle([center_x-5, center_y-5, center_x-1, center_y-3],
                             fill="white", outline="black", width=1)
                # 播放按钮
                triangle_points = [center_x-2, center_y-1, center_x-2, center_y+3, center_x+2, center_y+1]
                draw.polygon(triangle_points, fill="black")

            elif icon_type == "joints":  # 人形图标
                # 绘制简单的人形
                # 头部
                draw.ellipse([center_x-3, 6, center_x+3, 12], fill="white", outline="black")
                # 身体
                draw.rectangle([center_x-2, 12, center_x+2, 18], fill="white", outline="black")
                # 手臂
                draw.line([center_x-2, 14, center_x-5, 16], fill="black", width=1)
                draw.line([center_x+2, 14, center_x+5, 16], fill="black", width=1)
                # 腿部
                draw.line([center_x-1, 18, center_x-3, 22], fill="black", width=1)
                draw.line([center_x+1, 18, center_x+3, 22], fill="black", width=1)

            elif icon_type == "settings":  # 齿轮图标
                # 绘制齿轮
                draw.ellipse([center_x-6, center_y-6, center_x+6, center_y+6],
                           fill="white", outline="black", width=1)
                draw.ellipse([center_x-3, center_y-3, center_x+3, center_y+3],
                           fill="black")

            elif icon_type == "colors":  # 调色板图标
                # 绘制调色板
                draw.ellipse([center_x-7, center_y-5, center_x+7, center_y+5],
                           fill="white", outline="black", width=1)
                # 颜色点
                colors = ["red", "green", "blue", "yellow"]
                positions = [(center_x-4, center_y-2), (center_x+4, center_y-2),
                           (center_x-4, center_y+2), (center_x+4, center_y+2)]
                for i, color in enumerate(colors):
                    if i < len(positions):
                        x, y = positions[i]
                        draw.ellipse([x-1, y-1, x+1, y+1], fill=color)

            elif icon_type == "export":  # 保存图标
                # 绘制软盘图标
                draw.rectangle([center_x-6, center_y-6, center_x+6, center_y+6],
                             fill="white", outline="black", width=1)
                draw.rectangle([center_x-4, center_y-6, center_x+4, center_y-2],
                             fill="black")
                draw.rectangle([center_x-2, center_y-4, center_x+2, center_y],
                             fill="white")

            elif icon_type == "help":  # 帮助图标
                # 绘制问号
                draw.ellipse([center_x-7, center_y-7, center_x+7, center_y+7],
                           fill="white", outline="black", width=1)
                # 简化的问号形状
                draw.ellipse([center_x-1, center_y+2, center_x+1, center_y+4], fill="black")

            elif icon_type == "performance":  # 图表图标
                # 绘制柱状图
                draw.rectangle([center_x-6, center_y-6, center_x+6, center_y+6],
                             fill="white", outline="black", width=1)
                # 柱子
                heights = [3, 5, 2, 4]
                for i, h in enumerate(heights):
                    x = center_x - 4 + i * 2
                    draw.rectangle([x, center_y+4-h, x+1, center_y+4], fill="blue")

            return ImageTk.PhotoImage(img)

        except Exception as e:
            print(f"创建图标 {icon_type} 时出错: {e}")
            # 返回一个简单的空白图标
            img = Image.new('RGBA', size, (200, 200, 200, 255))
            return ImageTk.PhotoImage(img)

    def create_toolbar(self):
        """创建工具栏"""
        # 工具栏框架
        self.toolbar_frame = ttk.Frame(self.root, relief="raised", padding="2")
        self.toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # 配置工具栏网格权重
        self.toolbar_frame.columnconfigure(10, weight=1)  # 最后一列用于填充空间

        # 工具栏按钮配置
        toolbar_buttons = [
            ("open", "打开视频", self.smart_open_video),
            ("joints", "关节点选择器", self.toggle_landmark_selector_window),
            ("settings", "显示设置", self.toggle_settings_window),
            ("colors", "颜色设置", self.toggle_color_settings_window),
            ("export", "导出视频", self.toggle_export_window),
            ("performance", "性能监控", self.toggle_performance_window),
            ("help", "帮助", self.toggle_help_window),
        ]

        # 创建工具栏按钮
        for i, (icon_key, tooltip, command) in enumerate(toolbar_buttons):
            icon = self.toolbar_icons.get(icon_key)

            btn = ttk.Button(
                self.toolbar_frame,
                image=icon if icon else None,
                text=tooltip[:2] if not icon else "",  # 如果没有图标则显示文字缩写
                command=command,
                width=3 if icon else 8
            )
            btn.grid(row=0, column=i, padx=1, pady=1)

            # 添加工具提示
            self.create_tooltip(btn, tooltip)

        # 添加分隔符
        separator = ttk.Separator(self.toolbar_frame, orient='vertical')
        separator.grid(row=0, column=len(toolbar_buttons), sticky='ns', padx=5)

        # 状态标签
        self.status_label = ttk.Label(self.toolbar_frame, text="就绪", foreground="green")
        self.status_label.grid(row=0, column=len(toolbar_buttons)+1, padx=10)

    def create_tooltip(self, widget, text):
        """为控件创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="lightyellow",
                            relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def __del__(self):
        """析构函数"""
        self.cleanup()

def main():
    """主函数"""
    root = tk.Tk()
    app = PoseDetectionApp(root)

    # 添加窗口关闭事件处理
    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
