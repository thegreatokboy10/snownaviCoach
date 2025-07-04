# 故障排除指南

## 🔧 常见问题解决方案

### 1. 控件响应问题

#### 问题：颜色选择下拉菜单点击无响应或卡顿
**原因**：MediaPipe初始化阻塞UI创建，导致控件无法正常响应

**解决方案**：
- ✅ **已修复**：延迟初始化MediaPipe（1秒后初始化）
- ✅ **已优化**：简化事件处理函数
- ✅ **已优化**：添加异常处理机制
- ✅ **已修复**：移除不必要的延迟绑定

**验证方法**：
```bash
# 运行最终UI测试
python tests/test_final_ui.py

# 运行UI响应性测试
python tests/test_ui_responsiveness.py
```

**现象确认**：
- 应用启动后立即可以点击下拉菜单
- 1秒后看到"正在初始化MediaPipe..."消息
- 下拉菜单选择立即生效，控制台显示颜色更改信息

#### 问题：滑块拖动时界面卡顿
**原因**：实时事件触发过于频繁

**解决方案**：
- ✅ **已优化**：使用`<ButtonRelease-1>`事件替代实时更新
- ✅ **已优化**：拖动时只更新显示，释放时更新实际值
- ✅ **已优化**：防抖机制避免重复处理

**测试方法**：
1. 快速拖动线条粗细滑块
2. 观察界面是否流畅
3. 检查数值是否正确更新

### 2. 应用启动问题

#### 问题：应用启动失败
**可能原因**：
- 虚拟环境未激活
- 依赖包未安装
- Python版本不兼容

**解决步骤**：
```bash
# 1. 激活虚拟环境
source pose_detection_env/bin/activate

# 2. 检查依赖
python tests/test_pose_detection.py

# 3. 重新安装依赖（如果需要）
pip install -r requirements.txt

# 4. 启动应用
python pose_detection_app.py
```

#### 问题：MediaPipe初始化警告
**现象**：看到类似警告信息
```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
```

**说明**：这是正常的MediaPipe初始化信息，不影响功能使用

### 3. 视频播放问题

#### 问题：视频无法加载
**检查清单**：
- [ ] 视频格式是否支持（MP4, AVI, MOV, MKV, WMV, FLV）
- [ ] 视频文件是否损坏
- [ ] 文件路径是否包含特殊字符

**解决方法**：
1. 尝试使用MP4格式的视频
2. 确保视频文件完整无损坏
3. 避免文件路径包含中文或特殊字符

#### 问题：播放卡顿或跳帧
**优化建议**：
- 使用较小分辨率的视频（720p或以下）
- 关闭其他占用资源的程序
- 确保有足够的内存空间

### 4. 姿态检测问题

#### 问题：检测效果不佳
**改善方法**：
- 选择光线充足的视频
- 确保人物在画面中清晰可见
- 避免过度遮挡或极端角度
- 尝试调整检测参数

#### 问题：检测速度慢
**优化设置**：
- 当前已使用最轻量级模型（`model_complexity=0`）
- 多线程处理确保UI不卡顿
- 智能队列管理内存使用

### 5. 自定义样式问题

#### 问题：颜色更改不生效或显示错误颜色
**原因**：BGR颜色格式混淆，导致颜色名称与实际显示不符

**已修复的问题**：
- ✅ **BGR格式错误**：修正了颜色映射中的BGR值
- ✅ **默认颜色不匹配**：连接线默认颜色从蓝色改为红色
- ✅ **颜色名称混淆**：确保选择"红色"显示真正的红色

**检查步骤**：
1. 确认已选择视频文件
2. 点击播放按钮开始检测
3. 在检测过程中更改颜色设置
4. 观察右侧检测结果窗口

**验证修复**：
```bash
# 测试颜色修复效果
python tests/test_color_fix.py
```

#### 问题：重置按钮无效
**解决方法**：
- 点击"重置默认"按钮
- 等待1-2秒让设置生效
- 如果仍有问题，重启应用程序

### 6. 性能优化建议

#### 系统要求
- **CPU**：支持AVX指令集的现代处理器
- **内存**：建议8GB以上
- **存储**：至少1GB可用空间
- **操作系统**：macOS 10.14+, Windows 10+, Linux

#### 性能调优
```bash
# 检查当前性能
python tests/test_performance.py

# 检查UI响应性
python tests/test_ui_responsiveness.py
```

**期望指标**：
- 姿态检测：30+ FPS
- UI响应时间：<10ms
- 内存使用：<2GB

### 7. 开发调试

#### 启用详细日志
在应用程序中添加调试信息：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 常用调试命令
```bash
# 检查Python环境
python --version
pip list

# 检查OpenCV安装
python -c "import cv2; print(cv2.__version__)"

# 检查MediaPipe安装
python -c "import mediapipe; print(mediapipe.__version__)"

# 检查tkinter支持
python -c "import tkinter; print('tkinter OK')"
```

### 8. 联系支持

如果以上方法都无法解决问题：

1. **收集信息**：
   - 操作系统版本
   - Python版本
   - 错误信息截图
   - 问题复现步骤

2. **运行诊断**：
   ```bash
   python tests/test_pose_detection.py > diagnostic.log 2>&1
   ```

3. **提供反馈**：
   - 详细描述问题现象
   - 附上诊断日志
   - 说明期望的行为

## 🎯 快速诊断清单

遇到问题时，按以下顺序检查：

- [ ] 虚拟环境已激活
- [ ] 依赖包已安装
- [ ] 视频格式支持
- [ ] 系统资源充足
- [ ] 应用程序版本最新

大多数问题都可以通过重新激活环境和重启应用程序解决。
