#!/usr/bin/env python3
"""
测试颜色映射和显示
"""

import cv2
import numpy as np

def test_color_mapping():
    """测试颜色映射是否正确"""
    print("测试颜色映射...")
    
    # 定义颜色映射（BGR格式）
    color_map = {
        "红色": (0, 0, 255),
        "绿色": (0, 255, 0),
        "蓝色": (255, 0, 0),
        "黄色": (0, 255, 255),
        "紫色": (255, 0, 255),
        "青色": (255, 255, 0),
        "白色": (255, 255, 255)
    }
    
    # 创建测试图像
    height, width = 400, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 绘制颜色测试条
    y_start = 50
    bar_height = 40
    bar_width = 80
    
    for i, (color_name, bgr_color) in enumerate(color_map.items()):
        y = y_start + i * (bar_height + 10)
        x = 50
        
        # 绘制颜色条
        cv2.rectangle(image, (x, y), (x + bar_width, y + bar_height), bgr_color, -1)
        
        # 添加文字标签
        cv2.putText(image, color_name, (x + bar_width + 10, y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示BGR值
        bgr_text = f"BGR{bgr_color}"
        cv2.putText(image, bgr_text, (x + bar_width + 10, y + 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # 保存测试图像
    cv2.imwrite("color_test.jpg", image)
    print("✅ 颜色测试图像已保存为 color_test.jpg")
    
    # 显示图像（如果可能）
    try:
        cv2.imshow("Color Test", image)
        cv2.waitKey(3000)  # 显示3秒
        cv2.destroyAllWindows()
        print("✅ 颜色测试图像已显示")
    except:
        print("ℹ️  无法显示图像窗口，请查看保存的 color_test.jpg 文件")
    
    return True

def test_pose_colors():
    """测试姿态检测中的颜色绘制"""
    print("\n测试姿态检测颜色绘制...")
    
    # 创建测试图像
    height, width = 480, 640
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 模拟关键点和连接线
    test_points = [
        (320, 100),  # 头部
        (300, 150),  # 左肩
        (340, 150),  # 右肩
        (320, 200),  # 胸部
        (280, 200),  # 左肘
        (360, 200),  # 右肘
    ]
    
    test_connections = [
        (0, 1), (0, 2),  # 头到肩膀
        (1, 2),          # 肩膀连接
        (1, 3), (2, 3),  # 肩膀到胸部
        (1, 4), (2, 5),  # 肩膀到肘部
    ]
    
    # 测试不同颜色设置
    test_colors = [
        ("默认设置", (0, 255, 0), (255, 0, 0)),  # 绿色关键点，红色连接线
        ("红色设置", (0, 0, 255), (0, 0, 255)),  # 红色关键点，红色连接线
        ("蓝色设置", (255, 0, 0), (255, 0, 0)),  # 蓝色关键点，蓝色连接线
    ]
    
    for i, (name, landmark_color, connection_color) in enumerate(test_colors):
        test_image = image.copy()
        
        # 绘制连接线
        for start_idx, end_idx in test_connections:
            start_point = test_points[start_idx]
            end_point = test_points[end_idx]
            cv2.line(test_image, start_point, end_point, connection_color, 2)
        
        # 绘制关键点
        for point in test_points:
            cv2.circle(test_image, point, 3, landmark_color, -1)
            cv2.circle(test_image, point, 4, (0, 0, 0), 1)  # 黑色边框
        
        # 添加标题
        cv2.putText(test_image, name, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(test_image, f"Landmark: BGR{landmark_color}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(test_image, f"Connection: BGR{connection_color}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 保存测试图像
        filename = f"pose_test_{i+1}_{name}.jpg"
        cv2.imwrite(filename, test_image)
        print(f"✅ {name} 测试图像已保存为 {filename}")
    
    return True

def test_bgr_vs_rgb():
    """测试BGR和RGB的区别"""
    print("\n测试BGR vs RGB...")
    
    # 创建测试图像
    height, width = 200, 400
    
    # BGR格式（OpenCV默认）
    bgr_image = np.zeros((height, width, 3), dtype=np.uint8)
    bgr_image[:, :width//2] = [255, 0, 0]  # 蓝色
    bgr_image[:, width//2:] = [0, 0, 255]  # 红色
    
    # RGB格式
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    rgb_image[:, :width//2] = [255, 0, 0]  # 红色
    rgb_image[:, width//2:] = [0, 0, 255]  # 蓝色
    
    # 添加标签
    cv2.putText(bgr_image, "BGR: Blue | Red", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(rgb_image, "RGB: Red | Blue", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 保存图像
    cv2.imwrite("bgr_test.jpg", bgr_image)
    cv2.imwrite("rgb_test.jpg", rgb_image)
    
    print("✅ BGR测试图像已保存为 bgr_test.jpg")
    print("✅ RGB测试图像已保存为 rgb_test.jpg")
    print("ℹ️  注意：OpenCV使用BGR格式，所以 (255,0,0) 显示为蓝色")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("颜色映射和显示测试")
    print("=" * 60)
    
    tests = [
        test_color_mapping,
        test_pose_colors,
        test_bgr_vs_rgb,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！请查看生成的图像文件：")
    print("- color_test.jpg: 颜色映射测试")
    print("- pose_test_*.jpg: 姿态检测颜色测试")
    print("- bgr_test.jpg: BGR格式测试")
    print("- rgb_test.jpg: RGB格式测试")
    print("\n如果看到的颜色与预期不符，可能是BGR/RGB格式问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
