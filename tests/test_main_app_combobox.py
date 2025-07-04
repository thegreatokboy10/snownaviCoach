#!/usr/bin/env python3
"""
测试主应用程序中的下拉菜单功能
"""

import tkinter as tk
from tkinter import ttk

class MainAppComboboxTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("主应用下拉菜单测试")
        self.root.geometry("800x600")
        
        # 模拟主应用的变量
        self.landmark_color = (0, 255, 0)
        self.connection_color = (255, 0, 0)
        self.line_thickness = 2
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建类似主应用的控件布局"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 控制面板（模拟）
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(control_frame, text="这里是模拟的控制面板").pack()
        
        # 视频显示区域（模拟）
        video_frame = ttk.LabelFrame(main_frame, text="视频显示", padding="5")
        video_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(video_frame, text="这里是模拟的视频显示区域").pack(expand=True)
        
        # 设置面板（重点测试区域）
        settings_frame = ttk.LabelFrame(main_frame, text="骨骼线条设置", padding="5")
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
        
        self.thickness_scale.bind("<ButtonRelease-1>", self.on_thickness_release)
        self.thickness_scale.bind("<B1-Motion>", self.on_thickness_drag)
        
        self.thickness_label = ttk.Label(thickness_frame, text="2")
        self.thickness_label.grid(row=0, column=2)
        
        # 重置按钮
        reset_button = ttk.Button(
            settings_frame,
            text="重置默认",
            command=self.reset_settings
        )
        reset_button.grid(row=0, column=3, padx=(10, 0))
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="5")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_text = tk.Text(status_frame, height=6, width=60)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加初始状态
        self.log_message("应用程序已启动，请测试下拉菜单功能")
        
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
        return color_map.get(color_name, (0, 255, 0))
    
    def on_landmark_color_change(self, event=None):
        """关键点颜色改变事件"""
        try:
            color_name = self.landmark_color_var.get()
            if color_name:
                self.landmark_color = self.get_color_bgr(color_name)
                self.log_message(f"✅ 关键点颜色已更改为: {color_name} {self.landmark_color}")
        except Exception as e:
            self.log_message(f"❌ 更改关键点颜色时出错: {e}")
    
    def on_connection_color_change(self, event=None):
        """连接线颜色改变事件"""
        try:
            color_name = self.connection_color_var.get()
            if color_name:
                self.connection_color = self.get_color_bgr(color_name)
                self.log_message(f"✅ 连接线颜色已更改为: {color_name} {self.connection_color}")
        except Exception as e:
            self.log_message(f"❌ 更改连接线颜色时出错: {e}")
    
    def on_thickness_drag(self, event):
        """滑块拖动时只更新显示"""
        try:
            value = self.thickness_var.get()
            self.thickness_label.config(text=str(value))
        except Exception as e:
            self.log_message(f"❌ 拖动滑块时出错: {e}")
    
    def on_thickness_release(self, event):
        """滑块释放时更新实际值"""
        try:
            thickness = self.thickness_var.get()
            self.line_thickness = thickness
            self.thickness_label.config(text=str(thickness))
            self.log_message(f"✅ 线条粗细已更改为: {thickness}")
        except Exception as e:
            self.log_message(f"❌ 更新线条粗细时出错: {e}")
    
    def reset_settings(self):
        """重置设置为默认值"""
        try:
            self.landmark_color_var.set("绿色")
            self.connection_color_var.set("红色")
            self.thickness_var.set(2)
            
            self.landmark_color = (0, 255, 0)
            self.connection_color = (255, 0, 0)
            self.line_thickness = 2
            self.thickness_label.config(text="2")
            
            self.log_message("✅ 设置已重置为默认值")
        except Exception as e:
            self.log_message(f"❌ 重置设置时出错: {e}")
    
    def log_message(self, message):
        """记录消息到状态显示"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        print(message)
    
    def run(self):
        """运行测试"""
        print("主应用下拉菜单测试启动")
        print("请测试骨骼线条设置面板中的下拉菜单")
        self.root.mainloop()

def main():
    """主函数"""
    print("=" * 50)
    print("主应用程序下拉菜单功能测试")
    print("=" * 50)
    
    test = MainAppComboboxTest()
    test.run()

if __name__ == "__main__":
    main()
