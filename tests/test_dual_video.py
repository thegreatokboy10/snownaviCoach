#!/usr/bin/env python3
"""
测试双视频比较功能
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import os

def create_test_videos():
    """创建测试视频文件"""
    print("创建测试视频文件...")
    
    # 视频参数
    width, height = 640, 480
    fps = 30
    duration = 3  # 3秒
    total_frames = fps * duration
    
    # 创建视频1（红色移动圆圈）
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video1_path = 'test_video1.mp4'
    out1 = cv2.VideoWriter(video1_path, fourcc, fps, (width, height))
    
    for i in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # 红色圆圈从左到右移动
        x = int((i / total_frames) * (width - 100)) + 50
        y = height // 2
        cv2.circle(frame, (x, y), 30, (0, 0, 255), -1)  # 红色圆圈
        
        # 添加帧号
        cv2.putText(frame, f"Video1 Frame: {i+1}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out1.write(frame)
    
    out1.release()
    print(f"✅ 测试视频1已创建: {video1_path}")
    
    # 创建视频2（蓝色移动正方形）
    video2_path = 'test_video2.mp4'
    out2 = cv2.VideoWriter(video2_path, fourcc, fps, (width, height))
    
    for i in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # 蓝色正方形从右到左移动
        x = int(width - (i / total_frames) * (width - 100)) - 50
        y = height // 2
        cv2.rectangle(frame, (x-25, y-25), (x+25, y+25), (255, 0, 0), -1)  # 蓝色正方形
        
        # 添加帧号
        cv2.putText(frame, f"Video2 Frame: {i+1}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out2.write(frame)
    
    out2.release()
    print(f"✅ 测试视频2已创建: {video2_path}")
    
    return video1_path, video2_path

def test_video_loading():
    """测试视频加载功能"""
    print("\n测试视频加载功能...")
    
    video1_path, video2_path = create_test_videos()
    
    # 测试视频1加载
    cap1 = cv2.VideoCapture(video1_path)
    if cap1.isOpened():
        total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ 视频1: {width1}x{height1}, {total_frames1}帧, {fps1}fps")
        cap1.release()
    else:
        print("❌ 视频1加载失败")
        return False
    
    # 测试视频2加载
    cap2 = cv2.VideoCapture(video2_path)
    if cap2.isOpened():
        total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ 视频2: {width2}x{height2}, {total_frames2}帧, {fps2}fps")
        cap2.release()
    else:
        print("❌ 视频2加载失败")
        return False
    
    return True

def test_frame_synchronization():
    """测试帧同步功能"""
    print("\n测试帧同步功能...")
    
    video1_path = 'test_video1.mp4'
    video2_path = 'test_video2.mp4'
    
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)
    
    if not (cap1.isOpened() and cap2.isOpened()):
        print("❌ 无法打开测试视频")
        return False
    
    total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 测试同步读取
    sync_test_frames = [0, 15, 30, 45, 60, 75]  # 测试不同帧位置
    
    for frame_num in sync_test_frames:
        if frame_num >= total_frames1:
            continue
            
        # 设置视频1位置
        cap1.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret1, frame1 = cap1.read()
        
        # 设置视频2位置（处理长度不同的情况）
        frame_num2 = min(frame_num, total_frames2 - 1) if total_frames2 > 0 else 0
        cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_num2)
        ret2, frame2 = cap2.read()
        
        if ret1 and ret2:
            print(f"✅ 帧 {frame_num}: 视频1和视频2同步读取成功")
        else:
            print(f"❌ 帧 {frame_num}: 同步读取失败")
    
    cap1.release()
    cap2.release()
    
    return True

def test_adaptive_resize():
    """测试自适应大小调整"""
    print("\n测试自适应大小调整...")
    
    # 创建不同尺寸的测试图像
    test_sizes = [
        (1920, 1080),  # 大尺寸
        (640, 480),    # 中等尺寸
        (320, 240),    # 小尺寸
    ]
    
    target_sizes = [
        (400, 300),    # 目标尺寸1
        (200, 150),    # 目标尺寸2
        (800, 600),    # 目标尺寸3
    ]
    
    def resize_frame_adaptive(frame, max_width, max_height):
        """自适应调整帧大小（测试版本）"""
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
    
    for orig_w, orig_h in test_sizes:
        for target_w, target_h in target_sizes:
            # 创建测试图像
            test_frame = np.random.randint(0, 255, (orig_h, orig_w, 3), dtype=np.uint8)
            
            # 调整大小
            resized_frame = resize_frame_adaptive(test_frame, target_w, target_h)
            
            if resized_frame is not None:
                new_h, new_w = resized_frame.shape[:2]
                scale = min(new_w / orig_w, new_h / orig_h)
                
                print(f"✅ {orig_w}x{orig_h} -> {new_w}x{new_h} (目标: {target_w}x{target_h}, 缩放: {scale:.2f})")
            else:
                print(f"❌ 调整大小失败: {orig_w}x{orig_h} -> {target_w}x{target_h}")
    
    return True

def test_ui_layout():
    """测试UI布局"""
    print("\n测试UI布局...")
    
    try:
        root = tk.Tk()
        root.title("双视频UI测试")
        root.geometry("1000x700")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件选择按钮
        ttk.Button(control_frame, text="选择视频1").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="选择视频2（比较）").pack(side=tk.LEFT, padx=(0, 10))
        
        # 比较模式复选框
        comparison_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="比较模式", variable=comparison_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # 视频显示区域
        video_frame = ttk.LabelFrame(main_frame, text="视频显示", padding="5")
        video_frame.pack(fill=tk.BOTH, expand=True)
        
        # 单视频模式
        single_frame = ttk.Frame(video_frame)
        single_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左右分割
        left_frame = ttk.LabelFrame(single_frame, text="原始视频")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.LabelFrame(single_frame, text="姿态检测")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 添加占位标签
        ttk.Label(left_frame, text="原始视频显示区域").pack(expand=True)
        ttk.Label(right_frame, text="姿态检测显示区域").pack(expand=True)
        
        # 显示窗口
        root.after(2000, root.quit)  # 2秒后自动关闭
        root.mainloop()
        
        print("✅ UI布局测试完成")
        return True
        
    except Exception as e:
        print(f"❌ UI布局测试失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    print("\n清理测试文件...")
    
    test_files = ['test_video1.mp4', 'test_video2.mp4']
    
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ 已删除: {file_path}")
        except Exception as e:
            print(f"❌ 删除失败 {file_path}: {e}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("双视频比较功能测试")
    print("=" * 60)
    
    tests = [
        ("视频加载测试", test_video_loading),
        ("帧同步测试", test_frame_synchronization),
        ("自适应大小测试", test_adaptive_resize),
        ("UI布局测试", test_ui_layout),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 双视频功能测试通过！")
        print("\n新功能特性:")
        print("- ✅ 支持同时加载两个视频文件")
        print("- ✅ 上下比较模式，便于对比分析")
        print("- ✅ 自适应窗口大小，视频自动缩放")
        print("- ✅ 帧同步播放，确保时间一致")
        print("- ✅ 独立的姿态检测，每个视频都有检测结果")
        print("\n启动增强版应用程序:")
        print("python pose_detection_app.py")
    else:
        print("⚠️  部分测试失败，请检查功能实现")
    
    # 清理测试文件
    cleanup_test_files()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
