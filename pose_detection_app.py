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
from PIL import Image, ImageTk
import threading
import time
import queue

class PoseDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人体姿态检测应用")
        self.root.geometry("1200x800")

        # 初始化MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # 降低复杂度提高性能
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # 视频相关变量
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.should_stop = False
        self.current_frame = None
        self.total_frames = 0
        self.current_frame_number = 0
        self.fps = 30
        self.frame_interval = 33  # 约30fps的间隔（毫秒）

        # 性能优化变量
        self.frame_queue = queue.Queue(maxsize=2)  # 限制队列大小防止内存溢出
        self.processing_thread = None
        self.display_thread = None
        self.last_update_time = 0
        self.update_interval = 0.033  # 30fps

        # 骨骼线条自定义设置
        self.landmark_color = (0, 255, 0)  # 默认绿色 (BGR格式)
        self.connection_color = (255, 0, 0)  # 默认红色 (BGR格式)
        self.line_thickness = 2  # 默认线条粗细
        self.landmark_radius = 3  # 关键点半径

        # 创建GUI界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 文件选择按钮
        self.select_button = ttk.Button(
            control_frame, 
            text="选择视频文件", 
            command=self.select_video_file
        )
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        # 播放控制按钮
        self.play_button = ttk.Button(
            control_frame, 
            text="播放", 
            command=self.toggle_playback,
            state="disabled"
        )
        self.play_button.grid(row=0, column=1, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = ttk.Button(
            control_frame, 
            text="停止", 
            command=self.stop_playback,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=2, padx=(0, 10))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.on_progress_change,
            state="disabled"
        )
        self.progress_bar.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(10, 0))
        control_frame.columnconfigure(3, weight=1)
        
        # 信息标签
        self.info_label = ttk.Label(control_frame, text="请选择视频文件")
        self.info_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 视频显示区域
        video_frame = ttk.LabelFrame(main_frame, text="视频显示", padding="5")
        video_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 原始视频显示
        original_frame = ttk.LabelFrame(video_frame, text="原始视频")
        original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.original_label = ttk.Label(original_frame, text="原始视频将在这里显示")
        self.original_label.pack(expand=True, fill=tk.BOTH)
        
        # 姿态检测结果显示
        pose_frame = ttk.LabelFrame(video_frame, text="姿态检测结果")
        pose_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.pose_label = ttk.Label(pose_frame, text="姿态检测结果将在这里显示")
        self.pose_label.pack(expand=True, fill=tk.BOTH)
        
        # 配置视频显示区域的网格权重
        video_frame.columnconfigure(0, weight=1)
        video_frame.columnconfigure(1, weight=1)
        video_frame.rowconfigure(0, weight=1)

        # 设置面板
        settings_frame = ttk.LabelFrame(main_frame, text="骨骼线条设置", padding="5")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # 关键点颜色设置
        landmark_color_frame = ttk.Frame(settings_frame)
        landmark_color_frame.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)

        ttk.Label(landmark_color_frame, text="关键点颜色:").grid(row=0, column=0, padx=(0, 5))
        self.landmark_color_var = tk.StringVar(value="绿色")
        landmark_color_combo = ttk.Combobox(
            landmark_color_frame,
            textvariable=self.landmark_color_var,
            values=["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"],
            state="readonly",
            width=8
        )
        landmark_color_combo.grid(row=0, column=1)
        landmark_color_combo.bind('<<ComboboxSelected>>', self.on_landmark_color_change)

        # 连接线颜色设置
        connection_color_frame = ttk.Frame(settings_frame)
        connection_color_frame.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        ttk.Label(connection_color_frame, text="连接线颜色:").grid(row=0, column=0, padx=(0, 5))
        self.connection_color_var = tk.StringVar(value="红色")
        connection_color_combo = ttk.Combobox(
            connection_color_frame,
            textvariable=self.connection_color_var,
            values=["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"],
            state="readonly",
            width=8
        )
        connection_color_combo.grid(row=0, column=1)
        connection_color_combo.bind('<<ComboboxSelected>>', self.on_connection_color_change)

        # 线条粗细设置
        thickness_frame = ttk.Frame(settings_frame)
        thickness_frame.grid(row=0, column=2, padx=(0, 10), sticky=tk.W)

        ttk.Label(thickness_frame, text="线条粗细:").grid(row=0, column=0, padx=(0, 5))
        self.thickness_var = tk.IntVar(value=2)
        thickness_scale = ttk.Scale(
            thickness_frame,
            from_=1,
            to=8,
            orient=tk.HORIZONTAL,
            variable=self.thickness_var,
            command=self.on_thickness_change,
            length=100
        )
        thickness_scale.grid(row=0, column=1, padx=(0, 5))

        self.thickness_label = ttk.Label(thickness_frame, text="2")
        self.thickness_label.grid(row=0, column=2)

        # 重置按钮
        reset_button = ttk.Button(
            settings_frame,
            text="重置默认",
            command=self.reset_settings
        )
        reset_button.grid(row=0, column=3, padx=(10, 0))
        
    def select_video_file(self):
        """选择视频文件"""
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.video_path = file_path
            self.load_video()

    def get_color_bgr(self, color_name):
        """将颜色名称转换为BGR值"""
        color_map = {
            "红色": (0, 0, 255),
            "绿色": (0, 255, 0),
            "蓝色": (255, 0, 0),
            "黄色": (0, 255, 255),
            "紫色": (255, 0, 255),
            "青色": (255, 255, 0),
            "白色": (255, 255, 255)
        }
        return color_map.get(color_name, (0, 255, 0))  # 默认绿色

    def on_landmark_color_change(self, event=None):
        """关键点颜色改变事件"""
        color_name = self.landmark_color_var.get()
        self.landmark_color = self.get_color_bgr(color_name)
        print(f"关键点颜色已更改为: {color_name}")

    def on_connection_color_change(self, event=None):
        """连接线颜色改变事件"""
        color_name = self.connection_color_var.get()
        self.connection_color = self.get_color_bgr(color_name)
        print(f"连接线颜色已更改为: {color_name}")

    def on_thickness_change(self, value):
        """线条粗细改变事件"""
        thickness = int(float(value))
        self.line_thickness = thickness
        self.thickness_label.config(text=str(thickness))
        print(f"线条粗细已更改为: {thickness}")

    def reset_settings(self):
        """重置设置为默认值"""
        self.landmark_color_var.set("绿色")
        self.connection_color_var.set("红色")
        self.thickness_var.set(2)

        self.landmark_color = (0, 255, 0)
        self.connection_color = (255, 0, 0)
        self.line_thickness = 2
        self.thickness_label.config(text="2")

        print("设置已重置为默认值")
            
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
        """显示当前帧（优化版本）"""
        if not self.cap:
            return

        # 限制更新频率
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
        self.last_update_time = current_time

        # 设置视频位置
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number)
        ret, frame = self.cap.read()

        if not ret:
            return

        self.current_frame = frame.copy()

        # 在后台线程中处理姿态检测
        if not self.frame_queue.full():
            try:
                self.frame_queue.put_nowait((frame.copy(), self.current_frame_number))
            except queue.Full:
                pass  # 如果队列满了就跳过这一帧

        # 显示原始帧（快速处理）
        self.display_original_frame(frame)

        # 更新进度条
        if self.total_frames > 0:
            progress = (self.current_frame_number / self.total_frames) * 100
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
        
    def process_pose_detection(self, frame):
        """处理姿态检测（使用自定义样式）"""
        # 转换颜色空间
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 进行姿态检测
        results = self.pose.process(rgb_frame)

        # 绘制姿态关键点
        annotated_frame = frame.copy()
        if results.pose_landmarks:
            # 使用自定义样式绘制
            self.draw_custom_landmarks(annotated_frame, results.pose_landmarks)

        return annotated_frame

    def draw_custom_landmarks(self, image, landmarks):
        """使用自定义颜色和粗细绘制关键点"""
        height, width, _ = image.shape

        # 绘制连接线
        for connection in self.mp_pose.POSE_CONNECTIONS:
            start_idx = connection[0]
            end_idx = connection[1]

            if start_idx < len(landmarks.landmark) and end_idx < len(landmarks.landmark):
                start_landmark = landmarks.landmark[start_idx]
                end_landmark = landmarks.landmark[end_idx]

                # 检查关键点可见性
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
                    cv2.line(
                        image,
                        start_point,
                        end_point,
                        self.connection_color,
                        self.line_thickness
                    )

        # 绘制关键点
        for landmark in landmarks.landmark:
            if landmark.visibility > 0.5:
                x = int(landmark.x * width)
                y = int(landmark.y * height)

                # 绘制关键点圆圈
                cv2.circle(
                    image,
                    (x, y),
                    self.landmark_radius,
                    self.landmark_color,
                    -1  # 填充圆圈
                )

                # 绘制关键点边框
                cv2.circle(
                    image,
                    (x, y),
                    self.landmark_radius + 1,
                    (0, 0, 0),  # 黑色边框
                    1
                )
        
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
        """优化的播放循环"""
        if not self.is_playing or self.current_frame_number >= self.total_frames:
            if self.current_frame_number >= self.total_frames:
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
        """进度条变化事件"""
        if not self.is_playing and self.cap and self.total_frames > 0:
            frame_number = int((float(value) / 100) * self.total_frames)
            self.current_frame_number = max(0, min(frame_number, self.total_frames - 1))
            self.show_frame()

    def cleanup(self):
        """清理资源"""
        self.should_stop = True
        self.is_playing = False

        # 等待线程结束
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)

        # 清空队列
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

        # 释放视频资源
        if self.cap:
            self.cap.release()
            self.cap = None

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
