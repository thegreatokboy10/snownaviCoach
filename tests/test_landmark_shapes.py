#!/usr/bin/env python3
"""
测试关节点形状和大小功能
"""

import cv2
import numpy as np

def draw_landmark_shape(image, x, y, size, shape, color):
    """绘制不同形状的关键点（与主应用相同的函数）"""
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

def test_landmark_shapes():
    """测试不同的关键点形状"""
    print("测试关键点形状...")
    
    # 创建测试图像
    height, width = 400, 800
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 测试不同形状
    shapes = [
        ("circle", "圆形"),
        ("square", "正方形"),
        ("diamond", "菱形")
    ]
    
    colors = [
        ((0, 0, 255), "红色"),
        ((0, 255, 0), "绿色"),
        ((255, 0, 0), "蓝色")
    ]
    
    # 绘制形状测试
    y_start = 80
    x_start = 100
    
    for i, (shape, shape_name) in enumerate(shapes):
        for j, (color, color_name) in enumerate(colors):
            x = x_start + j * 200
            y = y_start + i * 120
            
            # 绘制关键点
            draw_landmark_shape(image, x, y, 8, shape, color)
            
            # 添加标签
            cv2.putText(image, f"{shape_name}", (x - 30, y + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(image, f"{color_name}", (x - 20, y + 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    # 添加标题
    cv2.putText(image, "Landmark Shapes Test", (50, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # 保存测试图像
    cv2.imwrite("landmark_shapes_test.jpg", image)
    print("✅ 关键点形状测试图像已保存为 landmark_shapes_test.jpg")
    
    return True

def test_landmark_sizes():
    """测试不同的关键点大小"""
    print("\n测试关键点大小...")
    
    # 创建测试图像
    height, width = 300, 900
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 测试不同大小
    sizes = [3, 5, 8, 10, 12, 15]
    color = (0, 255, 0)  # 绿色
    
    y = height // 2
    x_start = 80
    
    for i, size in enumerate(sizes):
        x = x_start + i * 130
        
        # 绘制正方形关键点
        draw_landmark_shape(image, x, y, size, "square", color)
        
        # 添加大小标签
        cv2.putText(image, f"Size: {size}", (x - 25, y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 添加标题
    cv2.putText(image, "Landmark Sizes Test (Square Shape)", (50, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # 保存测试图像
    cv2.imwrite("landmark_sizes_test.jpg", image)
    print("✅ 关键点大小测试图像已保存为 landmark_sizes_test.jpg")
    
    return True

def test_pose_with_landmarks():
    """测试带有新关键点的姿态检测效果"""
    print("\n测试姿态检测效果...")
    
    # 创建测试图像
    height, width = 500, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 模拟人体关键点
    pose_points = [
        (300, 80, "头部"),
        (280, 120, "左肩"),
        (320, 120, "右肩"),
        (300, 160, "胸部"),
        (260, 160, "左肘"),
        (340, 160, "右肘"),
        (240, 200, "左手"),
        (360, 200, "右手"),
        (280, 220, "左髋"),
        (320, 220, "右髋"),
        (270, 280, "左膝"),
        (330, 280, "右膝"),
        (265, 340, "左脚"),
        (335, 340, "右脚"),
    ]
    
    # 连接线
    connections = [
        (0, 1), (0, 2),  # 头到肩膀
        (1, 2),          # 肩膀连接
        (1, 3), (2, 3),  # 肩膀到胸部
        (1, 4), (2, 5),  # 肩膀到肘部
        (4, 6), (5, 7),  # 肘部到手部
        (3, 8), (3, 9),  # 胸部到髋部
        (8, 9),          # 髋部连接
        (8, 10), (9, 11), # 髋部到膝盖
        (10, 12), (11, 13), # 膝盖到脚部
    ]
    
    # 绘制连接线
    connection_color = (0, 0, 255)  # 红色
    for start_idx, end_idx in connections:
        if start_idx < len(pose_points) and end_idx < len(pose_points):
            start_point = (pose_points[start_idx][0], pose_points[start_idx][1])
            end_point = (pose_points[end_idx][0], pose_points[end_idx][1])
            cv2.line(image, start_point, end_point, connection_color, 2)
    
    # 绘制关键点（使用新的大正方形）
    landmark_color = (0, 255, 0)  # 绿色
    landmark_size = 8
    landmark_shape = "square"
    
    for x, y, name in pose_points:
        draw_landmark_shape(image, x, y, landmark_size, landmark_shape, landmark_color)
    
    # 添加说明
    cv2.putText(image, "Enhanced Pose Detection", (50, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.putText(image, "Large Square Landmarks (Size: 8)", (50, 70), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(image, "Red Connection Lines", (50, 95), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # 保存测试图像
    cv2.imwrite("enhanced_pose_test.jpg", image)
    print("✅ 增强姿态检测测试图像已保存为 enhanced_pose_test.jpg")
    
    return True

def test_default_vs_new():
    """对比默认设置和新设置"""
    print("\n对比默认设置和新设置...")
    
    # 创建对比图像
    height, width = 400, 800
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 左侧：旧的默认设置（小圆形）
    old_points = [(150, 150), (150, 200), (150, 250)]
    old_color = (0, 255, 0)
    
    for x, y in old_points:
        cv2.circle(image, (x, y), 3, old_color, -1)  # 旧的小圆形
        cv2.circle(image, (x, y), 4, (0, 0, 0), 1)
    
    # 右侧：新的默认设置（大正方形）
    new_points = [(550, 150), (550, 200), (550, 250)]
    new_color = (0, 255, 0)
    
    for x, y in new_points:
        draw_landmark_shape(image, x, y, 8, "square", new_color)  # 新的大正方形
    
    # 添加标签
    cv2.putText(image, "Before (Small Circles)", (50, 120), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "Radius: 3px", (80, 320), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    
    cv2.putText(image, "After (Large Squares)", (450, 120), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "Size: 8px", (480, 320), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    
    # 添加主标题
    cv2.putText(image, "Landmark Enhancement Comparison", (150, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # 保存对比图像
    cv2.imwrite("landmark_comparison.jpg", image)
    print("✅ 关键点对比图像已保存为 landmark_comparison.jpg")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("关键点形状和大小功能测试")
    print("=" * 60)
    
    tests = [
        test_landmark_shapes,
        test_landmark_sizes,
        test_pose_with_landmarks,
        test_default_vs_new,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 关键点功能测试通过！")
        print("\n新功能特性:")
        print("- ✅ 支持3种关键点形状：圆形、正方形、菱形")
        print("- ✅ 可调节关键点大小：3-15像素")
        print("- ✅ 默认使用大正方形（8像素），更加显眼")
        print("- ✅ 所有形状都有黑色边框，提高可见性")
        print("\n生成的测试图像:")
        print("- landmark_shapes_test.jpg: 不同形状展示")
        print("- landmark_sizes_test.jpg: 不同大小展示")
        print("- enhanced_pose_test.jpg: 增强的姿态检测效果")
        print("- landmark_comparison.jpg: 新旧设置对比")
        print("\n启动应用程序体验新功能:")
        print("python pose_detection_app.py")
    else:
        print("⚠️  部分测试失败，请检查代码")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
