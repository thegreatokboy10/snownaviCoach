#!/usr/bin/env python3
"""
测试颜色修复效果
"""

import cv2
import numpy as np

def test_fixed_colors():
    """测试修复后的颜色设置"""
    print("测试修复后的颜色设置...")
    
    # 修复后的颜色映射（BGR格式）
    color_map = {
        "红色": (0, 0, 255),    # BGR格式：蓝=0, 绿=0, 红=255
        "绿色": (0, 255, 0),    # BGR格式：蓝=0, 绿=255, 红=0
        "蓝色": (255, 0, 0),    # BGR格式：蓝=255, 绿=0, 红=0
        "黄色": (0, 255, 255),  # BGR格式：蓝=0, 绿=255, 红=255
        "紫色": (255, 0, 255),  # BGR格式：蓝=255, 绿=0, 红=255
        "青色": (255, 255, 0),  # BGR格式：蓝=255, 绿=255, 红=0
        "白色": (255, 255, 255) # BGR格式：蓝=255, 绿=255, 红=255
    }
    
    # 创建测试图像
    height, width = 500, 800
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 绘制颜色测试
    y_start = 50
    bar_height = 50
    bar_width = 100
    
    for i, (color_name, bgr_color) in enumerate(color_map.items()):
        y = y_start + i * (bar_height + 20)
        x = 50
        
        # 绘制颜色条
        cv2.rectangle(image, (x, y), (x + bar_width, y + bar_height), bgr_color, -1)
        
        # 添加颜色名称
        cv2.putText(image, color_name, (x + bar_width + 20, y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 添加BGR值
        bgr_text = f"BGR{bgr_color}"
        cv2.putText(image, bgr_text, (x + bar_width + 20, y + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # 绘制模拟的姿态关键点和连接线
        demo_x = x + bar_width + 250
        demo_y = y + 25
        
        # 模拟关键点
        cv2.circle(image, (demo_x, demo_y), 5, bgr_color, -1)
        cv2.circle(image, (demo_x, demo_y), 6, (0, 0, 0), 1)  # 黑色边框
        
        # 模拟连接线
        cv2.line(image, (demo_x + 20, demo_y), (demo_x + 80, demo_y), bgr_color, 3)
        
        print(f"✅ {color_name}: BGR{bgr_color} - 应该显示为{color_name}")
    
    # 添加标题
    cv2.putText(image, "Fixed Color Mapping Test", (50, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # 保存测试图像
    cv2.imwrite("color_fix_test.jpg", image)
    print("✅ 修复后的颜色测试图像已保存为 color_fix_test.jpg")
    
    return True

def test_default_colors():
    """测试默认颜色设置"""
    print("\n测试默认颜色设置...")
    
    # 默认设置
    default_landmark_color = (0, 255, 0)    # 绿色
    default_connection_color = (0, 0, 255)  # 红色（修复后）
    
    # 创建测试图像
    height, width = 300, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 模拟姿态检测结果
    points = [
        (150, 80),   # 头部
        (120, 120),  # 左肩
        (180, 120),  # 右肩
        (150, 160),  # 胸部
        (100, 160),  # 左肘
        (200, 160),  # 右肘
    ]
    
    connections = [
        (0, 1), (0, 2),  # 头到肩膀
        (1, 2),          # 肩膀连接
        (1, 3), (2, 3),  # 肩膀到胸部
        (1, 4), (2, 5),  # 肩膀到肘部
    ]
    
    # 绘制连接线（红色）
    for start_idx, end_idx in connections:
        start_point = points[start_idx]
        end_point = points[end_idx]
        cv2.line(image, start_point, end_point, default_connection_color, 2)
    
    # 绘制关键点（绿色）
    for point in points:
        cv2.circle(image, point, 3, default_landmark_color, -1)
        cv2.circle(image, point, 4, (0, 0, 0), 1)  # 黑色边框
    
    # 添加说明
    cv2.putText(image, "Default Colors (Fixed)", (20, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, f"Landmarks: GREEN BGR{default_landmark_color}", (20, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, default_landmark_color, 2)
    cv2.putText(image, f"Connections: RED BGR{default_connection_color}", (20, 80), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, default_connection_color, 2)
    
    # 在右侧显示修复前后对比
    cv2.putText(image, "Before Fix:", (350, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(image, "Connection: (255,0,0) = BLUE", (350, 120), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    cv2.putText(image, "After Fix:", (350, 160), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(image, "Connection: (0,0,255) = RED", (350, 180), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # 保存测试图像
    cv2.imwrite("default_colors_fixed.jpg", image)
    print("✅ 默认颜色测试图像已保存为 default_colors_fixed.jpg")
    print(f"✅ 关键点颜色: 绿色 BGR{default_landmark_color}")
    print(f"✅ 连接线颜色: 红色 BGR{default_connection_color} (已修复)")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("颜色修复效果测试")
    print("=" * 60)
    
    tests = [
        test_fixed_colors,
        test_default_colors,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("修复总结:")
    print("- ✅ 修正了BGR颜色值，确保显示正确的颜色")
    print("- ✅ 默认连接线颜色从 (255,0,0)蓝色 改为 (0,0,255)红色")
    print("- ✅ 添加了详细的BGR格式注释")
    print("- ✅ 颜色名称与实际显示颜色现在一致")
    print("\n现在选择'红色'应该显示真正的红色，而不是蓝色！")
    print("请启动应用程序测试: python pose_detection_app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
