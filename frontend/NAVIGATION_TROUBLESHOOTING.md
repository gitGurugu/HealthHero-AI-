# 导航跳转故障排除指南

## 问题描述
从仪表盘页面点击"数据大屏"链接无法正常跳转。

## 可能的原因和解决方案

### 1. 浏览器安全策略限制
**问题**: 某些浏览器可能阻止本地文件之间的跳转
**解决方案**:
- 使用本地服务器运行项目（推荐）
- 或者在浏览器中直接输入文件路径

### 2. 文件路径问题
**问题**: `health-dashboard.html` 文件不在正确位置
**解决方案**:
- 确保 `health-dashboard.html` 文件在 `frontend` 目录下
- 检查文件名拼写是否正确

### 3. JavaScript错误
**问题**: 页面JavaScript出现错误，阻止了跳转
**解决方案**:
- 按F12打开浏览器开发者工具
- 查看Console标签页是否有错误信息
- 如有错误，请截图反馈

## 多种跳转方式

### 方式1: 侧边栏链接
点击左侧导航栏中的"数据大屏"链接

### 方式2: 快速操作按钮
在概览页面中点击"打开数据大屏"按钮

### 方式3: 直接访问
在浏览器地址栏中输入：
```
file:///你的项目路径/frontend/health-dashboard.html
```

### 方式4: 新窗口打开
使用快速操作按钮会在新窗口中打开数据大屏

## 推荐解决方案

### 使用本地服务器（最佳方案）

1. **Python用户**:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   然后访问: `http://localhost:8080/dashboard.html`

2. **Node.js用户**:
   ```bash
   cd frontend
   npx http-server -p 8080
   ```
   然后访问: `http://localhost:8080/dashboard.html`

3. **使用VS Code Live Server插件**:
   - 安装Live Server插件
   - 右键点击`dashboard.html`
   - 选择"Open with Live Server"

## 测试步骤

1. 打开 `frontend/test-navigation.html` 进行跳转测试
2. 检查所有链接是否正常工作
3. 查看浏览器控制台是否有错误信息

## 常见错误信息

### "Cannot access local file"
- **原因**: 浏览器安全策略
- **解决**: 使用本地服务器

### "404 Not Found"
- **原因**: 文件路径错误
- **解决**: 检查文件位置和路径

### "Uncaught TypeError"
- **原因**: JavaScript错误
- **解决**: 检查控制台错误信息

## 联系支持

如果以上方法都无法解决问题，请提供以下信息：
1. 使用的浏览器和版本
2. 操作系统
3. 浏览器控制台的错误信息截图
4. 具体的操作步骤

## 快速验证

运行以下命令验证文件是否存在：
```bash
# Windows
dir frontend\health-dashboard.html

# Linux/Mac
ls -la frontend/health-dashboard.html
```

如果文件存在，应该会显示文件信息。 