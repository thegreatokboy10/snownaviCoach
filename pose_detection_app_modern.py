#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化姿态检测应用 - 使用CustomTkinter框架
支持智能视频加载、关节点筛选、实时姿态检测等功能
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import queue
import base64
from io import BytesIO

# 设置CustomTkinter外观
ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

class ModernPoseDetectionApp:
    def __init__(self):
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("现代化姿态检测应用")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 应用状态
        self.mediapipe_initialized = False
        self.cap1 = None
        self.cap2 = None
        self.video2_loaded = False
        self.is_playing1 = False
        self.is_playing2 = False
        self.should_stop1 = False
        self.should_stop2 = False
        self.current_frame1 = None
        self.current_frame2 = None
        
        # 姿态检测设置
        self.landmark_color = (0, 255, 0)  # 绿色
        self.connection_color = (0, 0, 255)  # 红色
        self.line_thickness = 2
        self.landmark_size = 8
        self.landmark_shape = "square"
        
        # 悬浮窗引用
        self.landmark_selector_window = None
        self.settings_window = None
        self.color_settings_window = None
        self.export_window = None
        self.performance_window = None
        self.help_window = None
        
        # 工具栏图标
        self.toolbar_icons = {}
        
        # 创建界面
        self.create_modern_ui()
        
        # 初始化关节点选择器数据
        self.initialize_landmark_selector_data()
        
        # 延迟初始化MediaPipe
        self.root.after(1000, self.initialize_mediapipe)

    def create_modern_ui(self):
        """创建现代化UI界面"""
        # 配置网格权重
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # 创建顶部工具栏
        self.create_modern_toolbar()
        
        # 创建主内容区域
        self.create_main_content_area()
        
        # 创建底部状态栏
        self.create_status_bar()

    def create_modern_toolbar(self):
        """创建现代化工具栏"""
        # 工具栏框架
        self.toolbar_frame = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.toolbar_frame.grid_columnconfigure(10, weight=1)
        
        # 应用标题
        title_label = ctk.CTkLabel(
            self.toolbar_frame, 
            text="🎯 姿态检测分析", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # 工具按钮
        self.create_toolbar_buttons()

    def create_toolbar_buttons(self):
        """创建工具栏按钮"""
        # 按钮配置
        buttons_config = [
            ("📁", "打开视频", self.smart_open_video, "#FF5722"),
            ("👤", "关节选择", self.toggle_landmark_selector_window, "#4CAF50"),
            ("⚙️", "显示设置", self.toggle_settings_window, "#2196F3"),
            ("🎨", "颜色设置", self.toggle_color_settings_window, "#FF9800"),
            ("💾", "导出视频", self.toggle_export_window, "#9C27B0"),
            ("📊", "性能监控", self.toggle_performance_window, "#FF5722"),
            ("❓", "帮助", self.toggle_help_window, "#607D8B"),
        ]
        
        # 创建按钮
        for i, (icon, tooltip, command, color) in enumerate(buttons_config):
            btn = ctk.CTkButton(
                self.toolbar_frame,
                text=icon,
                width=50,
                height=35,
                font=ctk.CTkFont(size=16),
                fg_color=color,
                hover_color=self.darken_color(color),
                command=command,
                corner_radius=8
            )
            btn.grid(row=0, column=i+1, padx=5, pady=12)
            
            # 添加工具提示
            self.create_tooltip(btn, tooltip)

    def create_main_content_area(self):
        """创建主内容区域"""
        # 主内容框架
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 创建动态视频区域
        self.create_dynamic_video_area()

    def create_dynamic_video_area(self):
        """创建动态视频显示区域"""
        # 视频容器
        self.video_container = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.video_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.video_container.grid_columnconfigure(0, weight=1)
        self.video_container.grid_columnconfigure(1, weight=1)
        self.video_container.grid_rowconfigure(0, weight=1)
        
        # 视频1区域
        self.video1_frame = ctk.CTkFrame(self.video_container, corner_radius=8)
        self.video1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.video1_frame.grid_columnconfigure(0, weight=1)
        self.video1_frame.grid_rowconfigure(0, weight=1)
        
        # 视频1标签
        self.video1_label = ctk.CTkLabel(
            self.video1_frame, 
            text="🎬 点击工具栏打开视频文件\n支持 MP4, AVI, MOV 等格式",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40")
        )
        self.video1_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # 视频2区域（初始隐藏）
        self.video2_frame = ctk.CTkFrame(self.video_container, corner_radius=8)
        self.video2_frame.grid_columnconfigure(0, weight=1)
        self.video2_frame.grid_rowconfigure(0, weight=1)
        
        # 视频2标签
        self.video2_label = ctk.CTkLabel(
            self.video2_frame, 
            text="🎬 第二个视频\n用于对比分析",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40")
        )
        self.video2_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # 创建播放控制面板
        self.create_playback_controls()

    def create_playback_controls(self):
        """创建播放控制面板"""
        # 控制面板框架
        self.control_frame = ctk.CTkFrame(self.main_frame, height=80, corner_radius=8)
        self.control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.control_frame.grid_columnconfigure(1, weight=1)
        
        # 播放按钮
        self.play_button = ctk.CTkButton(
            self.control_frame,
            text="▶️",
            width=60,
            height=40,
            font=ctk.CTkFont(size=20),
            command=self.toggle_playback,
            corner_radius=20
        )
        self.play_button.grid(row=0, column=0, padx=10, pady=20)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_slider = ctk.CTkSlider(
            self.control_frame,
            from_=0,
            to=100,
            variable=self.progress_var,
            command=self.on_progress_change,
            height=20
        )
        self.progress_slider.grid(row=0, column=1, sticky="ew", padx=10, pady=20)
        
        # 时间标签
        self.time_label = ctk.CTkLabel(
            self.control_frame,
            text="00:00 / 00:00",
            font=ctk.CTkFont(size=12)
        )
        self.time_label.grid(row=0, column=2, padx=10, pady=20)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # FPS标签
        self.fps_status_label = ctk.CTkLabel(
            self.status_frame,
            text="FPS: --",
            font=ctk.CTkFont(size=11)
        )
        self.fps_status_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

    def darken_color(self, hex_color):
        """使颜色变暗用于悬停效果"""
        # 简单的颜色变暗算法
        color_map = {
            "#FF5722": "#E64A19",
            "#4CAF50": "#388E3C", 
            "#2196F3": "#1976D2",
            "#FF9800": "#F57C00",
            "#9C27B0": "#7B1FA2",
            "#607D8B": "#455A64"
        }
        return color_map.get(hex_color, hex_color)

    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ctk.CTkLabel(
                tooltip, 
                text=text, 
                fg_color=("gray80", "gray20"),
                corner_radius=5,
                font=ctk.CTkFont(size=10)
            )
            label.pack(padx=5, pady=3)
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def initialize_mediapipe(self):
        """初始化MediaPipe"""
        try:
            print("正在初始化MediaPipe...")
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
            self.update_status("MediaPipe初始化完成", "green")
            print("MediaPipe初始化完成")
        except Exception as e:
            print(f"MediaPipe初始化失败: {e}")
            self.update_status("MediaPipe初始化失败", "red")
            self.mediapipe_initialized = False

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

    def load_video1(self):
        """加载视频1"""
        try:
            file_path = filedialog.askopenfilename(
                title="选择视频文件",
                filetypes=[
                    ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                    ("所有文件", "*.*")
                ]
            )

            if file_path:
                # 释放之前的视频
                if self.cap1:
                    self.cap1.release()

                # 打开新视频
                self.cap1 = cv2.VideoCapture(file_path)
                if self.cap1.isOpened():
                    # 获取视频信息
                    self.total_frames1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
                    self.fps1 = self.cap1.get(cv2.CAP_PROP_FPS)

                    # 显示第一帧
                    ret, frame = self.cap1.read()
                    if ret:
                        self.current_frame1 = frame
                        self.display_frame_in_label(frame, self.video1_label)

                    # 重置播放状态
                    self.is_playing1 = False
                    self.should_stop1 = False

                    print(f"视频1加载成功: {file_path}")
                    return True
                else:
                    messagebox.showerror("错误", "无法打开视频文件")
                    return False
        except Exception as e:
            print(f"加载视频1时出错: {e}")
            messagebox.showerror("错误", f"加载视频时出错: {str(e)}")
            return False

    def load_video2(self):
        """加载视频2"""
        try:
            file_path = filedialog.askopenfilename(
                title="选择第二个视频文件",
                filetypes=[
                    ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                    ("所有文件", "*.*")
                ]
            )

            if file_path:
                # 释放之前的视频
                if self.cap2:
                    self.cap2.release()

                # 打开新视频
                self.cap2 = cv2.VideoCapture(file_path)
                if self.cap2.isOpened():
                    # 获取视频信息
                    self.total_frames2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))
                    self.fps2 = self.cap2.get(cv2.CAP_PROP_FPS)

                    # 显示第一帧
                    ret, frame = self.cap2.read()
                    if ret:
                        self.current_frame2 = frame
                        self.display_frame_in_label(frame, self.video2_label)

                    # 启用比较模式
                    self.video2_loaded = True
                    self.update_video_layout()

                    # 重置播放状态
                    self.is_playing2 = False
                    self.should_stop2 = False

                    print(f"视频2加载成功: {file_path}")
                    return True
                else:
                    messagebox.showerror("错误", "无法打开视频文件")
                    return False
        except Exception as e:
            print(f"加载视频2时出错: {e}")
            messagebox.showerror("错误", f"加载视频时出错: {str(e)}")
            return False
        
    def show_video_replace_dialog(self):
        """显示视频替换对话框"""
        try:
            # 创建现代化对话框
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("替换视频")
            dialog.geometry("350x200")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"350x200+{x}+{y}")

            # 对话框内容
            main_frame = ctk.CTkFrame(dialog)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # 标题
            title_label = ctk.CTkLabel(
                main_frame,
                text="已有两个视频",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(10, 5))

            # 说明
            desc_label = ctk.CTkLabel(
                main_frame,
                text="请选择要替换的视频:",
                font=ctk.CTkFont(size=12)
            )
            desc_label.pack(pady=(0, 20))

            # 按钮框架
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=10)

            # 按钮
            btn1 = ctk.CTkButton(
                button_frame,
                text="替换视频1",
                command=lambda: self.replace_video(dialog, 1),
                width=120,
                height=35
            )
            btn1.pack(side="left", padx=5)

            btn2 = ctk.CTkButton(
                button_frame,
                text="替换视频2",
                command=lambda: self.replace_video(dialog, 2),
                width=120,
                height=35
            )
            btn2.pack(side="left", padx=5)

            # 取消按钮
            cancel_btn = ctk.CTkButton(
                main_frame,
                text="取消",
                command=dialog.destroy,
                width=100,
                height=30,
                fg_color="gray",
                hover_color="darkgray"
            )
            cancel_btn.pack(pady=(20, 10))

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

    def display_frame_in_label(self, frame, label):
        """在标签中显示帧"""
        try:
            # 获取标签大小
            label.update_idletasks()
            label_width = max(label.winfo_width(), 300)
            label_height = max(label.winfo_height(), 200)

            # 调整帧大小
            frame_height, frame_width = frame.shape[:2]
            scale_x = label_width / frame_width
            scale_y = label_height / frame_height
            scale = min(scale_x, scale_y) * 0.9  # 留一些边距

            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)

            resized_frame = cv2.resize(frame, (new_width, new_height))

            # 转换为PIL图像
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)

            # 更新标签
            label.configure(image=photo, text="")
            label.image = photo  # 保持引用

        except Exception as e:
            print(f"显示帧时出错: {e}")

    def update_status(self, message, color="white"):
        """更新状态栏"""
        try:
            color_map = {
                "green": "#4CAF50",
                "red": "#F44336",
                "blue": "#2196F3",
                "orange": "#FF9800",
                "white": None
            }

            text_color = color_map.get(color, color)
            if text_color:
                self.status_label.configure(text=message, text_color=text_color)
            else:
                self.status_label.configure(text=message)

        except Exception as e:
            print(f"更新状态时出错: {e}")

    def toggle_landmark_selector_window(self):
        """切换关节点选择器窗口"""
        if self.landmark_selector_window is None or not self.landmark_selector_window.winfo_exists():
            self.create_modern_landmark_selector()
        else:
            self.landmark_selector_window.destroy()
            self.landmark_selector_window = None

    def create_modern_landmark_selector(self):
        """创建现代化关节点选择器"""
        self.landmark_selector_window = ctk.CTkToplevel(self.root)
        self.landmark_selector_window.title("关节点选择器")
        self.landmark_selector_window.geometry("400x600")
        self.landmark_selector_window.transient(self.root)

        # 主框架
        main_frame = ctk.CTkScrollableFrame(self.landmark_selector_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="👤 关节点选择器",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # 控制按钮
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", pady=(0, 20))

        buttons = [
            ("全选", self.select_all_landmarks),
            ("全不选", self.deselect_all_landmarks),
            ("反选", self.invert_landmark_selection)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(control_frame, text=text, command=command, width=80)
            btn.grid(row=0, column=i, padx=5, pady=10)

        # 分组按钮
        group_frame = ctk.CTkFrame(main_frame)
        group_frame.pack(fill="x", pady=(0, 20))

        for i, group_name in enumerate(self.landmark_groups.keys()):
            btn = ctk.CTkButton(
                group_frame,
                text=f"选择{group_name}",
                command=lambda g=group_name: self.select_landmark_group(g),
                width=80
            )
            btn.grid(row=0, column=i, padx=5, pady=10)

        # 关节点复选框
        for group_name, landmark_indices in self.landmark_groups.items():
            # 分组标题
            group_label = ctk.CTkLabel(
                main_frame,
                text=f"{group_name}:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            group_label.pack(anchor="w", pady=(20, 10))

            # 该分组的关节点
            for landmark_idx in landmark_indices:
                landmark_name = self.landmark_info[landmark_idx]

                checkbox = ctk.CTkCheckBox(
                    main_frame,
                    text=f"{landmark_idx}: {landmark_name}",
                    variable=self.landmark_visibility[landmark_idx],
                    command=self.on_landmark_visibility_change
                )
                checkbox.pack(anchor="w", padx=20, pady=2)

    def toggle_settings_window(self):
        """切换设置窗口"""
        print("显示设置")

    def toggle_color_settings_window(self):
        """切换颜色设置窗口"""
        print("颜色设置")

    def toggle_export_window(self):
        """切换导出窗口"""
        print("导出视频")

    def toggle_performance_window(self):
        """切换性能监控窗口"""
        print("性能监控")

    def toggle_help_window(self):
        """切换帮助窗口"""
        print("帮助")
        
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

    def on_landmark_visibility_change(self):
        """关节点可见性改变事件"""
        try:
            # 这里可以添加实时更新视频显示的逻辑
            print("关节点可见性已更新")
        except Exception as e:
            print(f"更新关节点可见性时出错: {e}")

    def toggle_playback(self):
        """切换播放状态"""
        if self.cap1 is None:
            self.update_status("请先加载视频", "orange")
            return

        if self.is_playing1:
            self.is_playing1 = False
            self.play_button.configure(text="▶️")
            self.update_status("播放已暂停", "orange")
        else:
            self.is_playing1 = True
            self.play_button.configure(text="⏸️")
            self.update_status("正在播放", "green")
            # 这里可以添加播放逻辑

    def on_progress_change(self, value):
        """进度条改变事件"""
        print(f"进度: {value}")
        # 这里可以添加跳转到指定位置的逻辑

    def update_video_layout(self):
        """更新视频布局"""
        if self.video2_loaded:
            # 显示双视频布局
            self.video2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            self.update_status("双视频比较模式", "blue")
        else:
            # 隐藏视频2
            self.video2_frame.grid_remove()

    def cleanup(self):
        """清理资源"""
        try:
            # 停止播放
            self.is_playing1 = False
            self.is_playing2 = False
            self.should_stop1 = True
            self.should_stop2 = True

            # 释放视频资源
            if self.cap1:
                self.cap1.release()
            if self.cap2:
                self.cap2.release()

            # 关闭悬浮窗
            windows = [
                'landmark_selector_window', 'settings_window', 'color_settings_window',
                'export_window', 'performance_window', 'help_window'
            ]

            for window_name in windows:
                window = getattr(self, window_name, None)
                if window and hasattr(window, 'destroy'):
                    try:
                        window.destroy()
                    except:
                        pass

            print("资源清理完成")
        except Exception as e:
            print(f"清理资源时出错: {e}")

    def run(self):
        """运行应用"""
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """窗口关闭事件"""
        self.cleanup()
        self.root.destroy()

def main():
    """主函数"""
    app = ModernPoseDetectionApp()
    app.run()

if __name__ == "__main__":
    main()
