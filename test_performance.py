#!/usr/bin/env python3
"""
性能测试脚本 - 测试优化后的应用程序性能
"""

import cv2
import mediapipe as mp
import time
import numpy as np

def test_pose_detection_performance():
    """测试姿态检测性能"""
    print("测试姿态检测性能...")
    
    # 初始化MediaPipe
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=0,  # 使用最低复杂度
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # 创建测试图像
    test_frames = []
    for i in range(10):
        # 创建不同的测试图像
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_frames.append(frame)
    
    # 测试处理时间
    start_time = time.time()
    processed_frames = 0
    
    for frame in test_frames:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        processed_frames += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    fps = processed_frames / total_time
    
    print(f"处理了 {processed_frames} 帧")
    print(f"总时间: {total_time:.2f} 秒")
    print(f"平均FPS: {fps:.1f}")
    
    if fps >= 15:
        print("✅ 性能良好 (>= 15 FPS)")
    elif fps >= 10:
        print("⚠️  性能一般 (10-15 FPS)")
    else:
        print("❌ 性能较差 (< 10 FPS)")
    
    return fps

def test_video_reading_performance():
    """测试视频读取性能"""
    print("\n测试视频读取性能...")
    
    # 创建一个临时视频文件进行测试
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video = 'temp_test_video.mp4'
    
    # 创建测试视频
    out = cv2.VideoWriter(temp_video, fourcc, 30.0, (640, 480))
    for i in range(100):  # 100帧
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # 测试读取性能
    cap = cv2.VideoCapture(temp_video)
    if not cap.isOpened():
        print("❌ 无法创建测试视频")
        return 0
    
    start_time = time.time()
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
    
    end_time = time.time()
    cap.release()
    
    # 清理临时文件
    import os
    try:
        os.remove(temp_video)
    except:
        pass
    
    total_time = end_time - start_time
    fps = frame_count / total_time if total_time > 0 else 0
    
    print(f"读取了 {frame_count} 帧")
    print(f"总时间: {total_time:.2f} 秒")
    print(f"读取FPS: {fps:.1f}")
    
    if fps >= 100:
        print("✅ 视频读取性能优秀")
    elif fps >= 50:
        print("✅ 视频读取性能良好")
    else:
        print("⚠️  视频读取性能一般")
    
    return fps

def test_image_processing_performance():
    """测试图像处理性能"""
    print("\n测试图像处理性能...")
    
    # 创建测试图像
    test_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # 测试调整大小性能
    start_time = time.time()
    for i in range(100):
        resized = cv2.resize(test_image, (400, 300))
        rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    end_time = time.time()
    
    total_time = end_time - start_time
    ops_per_second = 100 / total_time
    
    print(f"100次图像处理操作耗时: {total_time:.2f} 秒")
    print(f"每秒操作数: {ops_per_second:.1f}")
    
    if ops_per_second >= 50:
        print("✅ 图像处理性能优秀")
    elif ops_per_second >= 30:
        print("✅ 图像处理性能良好")
    else:
        print("⚠️  图像处理性能一般")
    
    return ops_per_second

def main():
    """主测试函数"""
    print("=" * 60)
    print("人体姿态检测应用 - 性能测试")
    print("=" * 60)
    
    # 运行各项性能测试
    pose_fps = test_pose_detection_performance()
    video_fps = test_video_reading_performance()
    image_ops = test_image_processing_performance()
    
    print("\n" + "=" * 60)
    print("性能测试总结:")
    print("=" * 60)
    print(f"姿态检测FPS: {pose_fps:.1f}")
    print(f"视频读取FPS: {video_fps:.1f}")
    print(f"图像处理OPS: {image_ops:.1f}")
    
    # 综合评估
    if pose_fps >= 15 and video_fps >= 50 and image_ops >= 30:
        print("\n🎉 整体性能优秀！应用程序应该运行流畅。")
    elif pose_fps >= 10 and video_fps >= 30 and image_ops >= 20:
        print("\n✅ 整体性能良好，应用程序应该基本流畅。")
    else:
        print("\n⚠️  性能可能不够理想，建议:")
        print("   - 降低视频分辨率")
        print("   - 使用更简单的姿态检测模型")
        print("   - 关闭其他占用资源的程序")
    
    print("\n启动优化后的应用程序:")
    print("python pose_detection_app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
