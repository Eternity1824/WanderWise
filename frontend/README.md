# WanderWise 地图导航前端

WanderWise是一个基于React和Google Maps API的地图导航应用，用于展示地点并提供导航功能。

## 功能特点

- 在Google地图上展示地点标记
- 选择多个地点并创建路线
- 按方位顺序（如从北到南）对地点进行排序
- 搜索地点
- 显示地点详细信息
- 计算路线总距离和预计时间

## 技术栈

- React 18
- TypeScript
- Vite
- Google Maps API (@react-google-maps/api)
- Axios

## 安装与运行

### 前提条件

- Node.js 16+
- npm 或 yarn
- Google Maps API密钥

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/wanderwise-frontend.git
cd wanderwise-frontend
```

2. 安装依赖

```bash
npm install
# 或
yarn install
```

3. 配置环境变量

复制`.env.example`文件并重命名为`.env.local`，然后填入你的Google Maps API密钥：

```bash
cp .env.example .env.local
```

编辑`.env.local`文件：

```
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
VITE_API_BASE_URL=http://your-backend-api-url/api
```

4. 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

应用将在 http://localhost:5173 运行。

## 项目结构

```
src/
├── assets/           # 静态资源
├── components/       # React组件
│   └── map/          # 地图相关组件
├── context/          # React上下文
├── hooks/            # 自定义钩子
├── services/         # API服务
├── types/            # TypeScript类型定义
├── utils/            # 工具函数
├── App.tsx           # 主应用组件
└── main.tsx          # 应用入口
```

## 使用指南

1. 在地图上查看地点标记
2. 点击标记查看地点详情
3. 双击标记选择地点
4. 在导航面板中选择排序方向（如从北到南）
5. 点击"排序地点"按钮对选定地点进行排序
6. 点击"创建路线"按钮生成路线
7. 使用搜索栏搜索特定地点

## 后端API

应用需要连接到提供以下API端点的后端服务：

- `GET /api/locations` - 获取所有地点
- `GET /api/locations/:id` - 获取单个地点
- `GET /api/locations/search?query=xxx` - 搜索地点
- `POST /api/routes` - 创建路线

## 贡献指南

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT
