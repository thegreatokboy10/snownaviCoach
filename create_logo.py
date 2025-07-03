#!/usr/bin/env python3
"""
创建snownavi_logo.png文件的脚本
"""

import cv2
import numpy as np

def create_snownavi_logo():
    """创建SnowNavi Logo"""
    # 创建一个透明背景的图像 (200x80像素)
    width, height = 200, 80
    logo = np.zeros((height, width, 4), dtype=np.uint8)
    
    # 设置背景为透明
    logo[:, :, 3] = 0
    
    # 定义颜色 (BGR格式)
    blue_color = (255, 140, 0)  # 橙蓝色
    white_color = (255, 255, 255)  # 白色
    
    # 绘制雪花图标 (左侧)
    snowflake_center = (30, 40)
    snowflake_size = 15
    
    # 绘制雪花的六个方向线条
    angles = [0, 30, 60, 90, 120, 150]
    for angle in angles:
        angle_rad = np.radians(angle)
        end_x = int(snowflake_center[0] + snowflake_size * np.cos(angle_rad))
        end_y = int(snowflake_center[1] + snowflake_size * np.sin(angle_rad))
        
        cv2.line(logo, snowflake_center, (end_x, end_y), (*blue_color, 255), 2)
        
        # 添加小分支
        branch_size = 5
        branch_x1 = int(end_x - branch_size * np.cos(angle_rad + np.pi/4))
        branch_y1 = int(end_y - branch_size * np.sin(angle_rad + np.pi/4))
        branch_x2 = int(end_x - branch_size * np.cos(angle_rad - np.pi/4))
        branch_y2 = int(end_y - branch_size * np.sin(angle_rad - np.pi/4))
        
        cv2.line(logo, (end_x, end_y), (branch_x1, branch_y1), (*blue_color, 255), 1)
        cv2.line(logo, (end_x, end_y), (branch_x2, branch_y2), (*blue_color, 255), 1)
    
    # 绘制中心圆
    cv2.circle(logo, snowflake_center, 3, (*blue_color, 255), -1)
    
    # 添加文字 "SnowNavi"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    
    # 计算文字位置
    text = "SnowNavi"
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = 65
    text_y = 45
    
    # 绘制文字阴影
    cv2.putText(logo, text, (text_x + 1, text_y + 1), font, font_scale, (0, 0, 0, 180), thickness)
    
    # 绘制主文字
    cv2.putText(logo, text, (text_x, text_y), font, font_scale, (*white_color, 255), thickness)
    
    # 添加副标题 "Pose Analysis"
    subtitle = "Pose Analysis"
    font_scale_small = 0.4
    thickness_small = 1
    
    (sub_width, sub_height), _ = cv2.getTextSize(subtitle, font, font_scale_small, thickness_small)
    sub_x = text_x
    sub_y = text_y + 20
    
    # 绘制副标题阴影
    cv2.putText(logo, subtitle, (sub_x + 1, sub_y + 1), font, font_scale_small, (0, 0, 0, 120), thickness_small)
    
    # 绘制副标题
    cv2.putText(logo, subtitle, (sub_x, sub_y), font, font_scale_small, (*blue_color, 200), thickness_small)
    
    return logo

def main():
    """主函数"""
    print("正在创建SnowNavi Logo...")
    
    # 创建logo
    logo = create_snownavi_logo()
    
    # 保存为PNG文件
    cv2.imwrite('snownavi_logo.png', logo)
    
    print("✅ SnowNavi Logo已创建: snownavi_logo.png")
    print("📏 尺寸: 200x80像素")
    print("🎨 格式: PNG (带透明背景)")

if __name__ == "__main__":
    main()
