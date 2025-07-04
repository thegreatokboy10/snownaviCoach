#!/usr/bin/env python3
"""
测试UI响应性和控件性能
"""

import tkinter as tk
from tkinter import ttk
import time
import threading

class UIResponsivenessTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UI响应性测试")
        self.root.geometry("600x400")
        
        # 测试变量
        self.color_var = tk.StringVar(value="绿色")
        self.thickness_var = tk.IntVar(value=2)
        self.event_count = 0
        self.last_event_time = 0
        self.response_times = []
        
        self.create_test_widgets()
        
    def create_test_widgets(self):
        """创建测试控件"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="UI响应性测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 测试说明
        info_text = """
测试说明：
1. 快速点击下拉菜单选择不同颜色
2. 快速拖动滑块改变数值
3. 观察界面是否卡顿或无响应
4. 查看事件响应时间统计
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # 测试控件区域
        test_frame = ttk.LabelFrame(main_frame, text="测试控件", padding="10")
        test_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 颜色选择测试
        color_frame = ttk.Frame(test_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="颜色选择:").pack(side=tk.LEFT, padx=(0, 10))
        color_combo = ttk.Combobox(
            color_frame,
            textvariable=self.color_var,
            values=["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"],
            state="readonly",
            width=10
        )
        color_combo.pack(side=tk.LEFT, padx=(0, 10))
        color_combo.bind('<<ComboboxSelected>>', self.on_color_change)
        
        # 滑块测试
        slider_frame = ttk.Frame(test_frame)
        slider_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(slider_frame, text="数值调节:").pack(side=tk.LEFT, padx=(0, 10))
        thickness_scale = ttk.Scale(
            slider_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.thickness_var,
            length=200
        )
        thickness_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        # 使用优化的事件绑定
        thickness_scale.bind("<ButtonRelease-1>", self.on_slider_release)
        thickness_scale.bind("<B1-Motion>", self.on_slider_drag)
        
        self.value_label = ttk.Label(slider_frame, text="2")
        self.value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_frame, text="响应统计", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=60)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="清除统计", command=self.clear_stats).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="开始压力测试", command=self.start_stress_test).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT)
        
        # 初始化统计显示
        self.update_stats()
        
    def on_color_change(self, event=None):
        """颜色改变事件"""
        start_time = time.time()
        try:
            color = self.color_var.get()
            # 模拟一些处理
            time.sleep(0.001)  # 1ms的模拟处理时间
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            self.record_event("颜色选择", color, response_time)
            
        except Exception as e:
            self.record_event("颜色选择", f"错误: {e}", 0)
    
    def on_slider_drag(self, event):
        """滑块拖动事件"""
        try:
            value = self.thickness_var.get()
            self.value_label.config(text=str(value))
        except Exception as e:
            print(f"拖动滑块时出错: {e}")
    
    def on_slider_release(self, event):
        """滑块释放事件"""
        start_time = time.time()
        try:
            value = self.thickness_var.get()
            # 模拟一些处理
            time.sleep(0.002)  # 2ms的模拟处理时间
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            self.record_event("滑块调节", str(value), response_time)
            
        except Exception as e:
            self.record_event("滑块调节", f"错误: {e}", 0)
    
    def record_event(self, event_type, value, response_time):
        """记录事件响应时间"""
        self.event_count += 1
        self.response_times.append(response_time)
        
        current_time = time.time()
        time_since_last = (current_time - self.last_event_time) * 1000 if self.last_event_time > 0 else 0
        self.last_event_time = current_time
        
        # 更新统计显示
        self.root.after_idle(lambda: self.update_stats_display(event_type, value, response_time, time_since_last))
    
    def update_stats_display(self, event_type, value, response_time, time_since_last):
        """更新统计显示"""
        try:
            self.stats_text.insert(tk.END, 
                f"[{self.event_count:3d}] {event_type}: {value} | "
                f"响应: {response_time:.1f}ms | "
                f"间隔: {time_since_last:.1f}ms\n"
            )
            self.stats_text.see(tk.END)
            
            # 保持最多50行
            lines = self.stats_text.get("1.0", tk.END).split('\n')
            if len(lines) > 50:
                self.stats_text.delete("1.0", "2.0")
                
        except Exception as e:
            print(f"更新统计显示时出错: {e}")
    
    def update_stats(self):
        """更新总体统计"""
        if self.response_times:
            avg_response = sum(self.response_times) / len(self.response_times)
            max_response = max(self.response_times)
            min_response = min(self.response_times)
            
            stats_summary = f"""
总体统计:
- 事件总数: {self.event_count}
- 平均响应时间: {avg_response:.1f}ms
- 最大响应时间: {max_response:.1f}ms  
- 最小响应时间: {min_response:.1f}ms
- 响应性评价: {'优秀' if avg_response < 10 else '良好' if avg_response < 50 else '需要优化'}

使用说明:
- 响应时间 < 10ms: 优秀
- 响应时间 10-50ms: 良好  
- 响应时间 > 50ms: 需要优化
            """
        else:
            stats_summary = """
总体统计:
- 暂无数据，请开始测试

使用说明:
- 快速操作控件测试响应性
- 观察响应时间和界面流畅度
            """
        
        # 定期更新统计
        self.root.after(1000, self.update_stats)
    
    def clear_stats(self):
        """清除统计数据"""
        self.event_count = 0
        self.response_times = []
        self.last_event_time = 0
        self.stats_text.delete("1.0", tk.END)
        print("统计数据已清除")
    
    def start_stress_test(self):
        """开始压力测试"""
        def stress_test():
            print("开始压力测试...")
            colors = ["红色", "绿色", "蓝色", "黄色", "紫色", "青色", "白色"]
            
            for i in range(20):  # 20次快速切换
                color = colors[i % len(colors)]
                self.root.after(i * 100, lambda c=color: self.color_var.set(c))
                self.root.after(i * 100 + 50, lambda v=i%8+1: self.thickness_var.set(v))
                
            print("压力测试完成")
        
        # 在后台线程中运行压力测试
        threading.Thread(target=stress_test, daemon=True).start()
    
    def run(self):
        """运行测试"""
        print("UI响应性测试启动")
        print("请操作界面控件，观察响应性能")
        self.root.mainloop()

def main():
    """主函数"""
    print("=" * 50)
    print("UI响应性测试工具")
    print("=" * 50)
    
    test = UIResponsivenessTest()
    test.run()

if __name__ == "__main__":
    main()
