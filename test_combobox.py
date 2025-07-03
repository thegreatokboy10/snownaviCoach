#!/usr/bin/env python3
"""
测试下拉菜单功能
"""

import tkinter as tk
from tkinter import ttk

class ComboboxTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("下拉菜单测试")
        self.root.geometry("400x300")
        
        # 测试变量
        self.color_var = tk.StringVar(value="绿色")
        self.event_count = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建测试控件"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="下拉菜单功能测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 说明
        info_label = ttk.Label(main_frame, text="点击下拉菜单选择颜色，观察是否正常响应")
        info_label.pack(pady=(0, 20))
        
        # 测试下拉菜单
        combo_frame = ttk.Frame(main_frame)
        combo_frame.pack(pady=(0, 20))
        
        ttk.Label(combo_frame, text="选择颜色:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_combo = ttk.Combobox(
            combo_frame,
            textvariable=self.color_var,
            values=["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"],
            state="readonly",
            width=10
        )
        self.color_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 绑定事件
        self.color_combo.bind('<<ComboboxSelected>>', self.on_color_change)
        
        # 显示当前值
        self.current_label = ttk.Label(combo_frame, text=f"当前: {self.color_var.get()}")
        self.current_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 事件计数显示
        self.count_label = ttk.Label(main_frame, text="事件触发次数: 0")
        self.count_label.pack(pady=(0, 10))
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="事件日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="清除日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="测试所有颜色", command=self.test_all_colors).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT)
        
    def on_color_change(self, event=None):
        """颜色改变事件"""
        try:
            self.event_count += 1
            color = self.color_var.get()
            
            # 更新显示
            self.current_label.config(text=f"当前: {color}")
            self.count_label.config(text=f"事件触发次数: {self.event_count}")
            
            # 添加日志
            self.log_text.insert(tk.END, f"[{self.event_count:3d}] 颜色已更改为: {color}\n")
            self.log_text.see(tk.END)
            
            print(f"颜色已更改为: {color}")
            
        except Exception as e:
            error_msg = f"错误: {e}"
            self.log_text.insert(tk.END, f"[ERR] {error_msg}\n")
            print(error_msg)
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete("1.0", tk.END)
        self.event_count = 0
        self.count_label.config(text="事件触发次数: 0")
        print("日志已清除")
    
    def test_all_colors(self):
        """测试所有颜色"""
        colors = ["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"]
        
        def set_next_color(index):
            if index < len(colors):
                self.color_var.set(colors[index])
                # 手动触发事件
                self.on_color_change()
                # 延迟设置下一个颜色
                self.root.after(500, lambda: set_next_color(index + 1))
        
        set_next_color(0)
    
    def run(self):
        """运行测试"""
        print("下拉菜单测试启动")
        print("请点击下拉菜单选择不同颜色")
        self.root.mainloop()

def main():
    """主函数"""
    print("=" * 40)
    print("下拉菜单功能测试")
    print("=" * 40)
    
    test = ComboboxTest()
    test.run()

if __name__ == "__main__":
    main()
