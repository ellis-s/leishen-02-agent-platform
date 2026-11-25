# leishen-02-agent-platform



## 本地启动项目
1. 启动Docker容器
2. 安装依赖
3. 启动服务

### 1. 启动Docker容器

```bash
# 启动Docker容器
docker-compose up -d
```

### 2. 安装依赖

```bash
# 安装依赖
pip install uv

uv sync

# 或者使用 pip 安装依赖
pip install -r requirements.txt
```



### 3. 启动服务

1. 启动服务
   ```bash
   fastapi dev src/main.py
   ```
2. 访问服务
   - 访问 [http://localhost:8000/health](http://localhost:8000/health)


## 测试

```bash
# 运行所有测试
pytest test/

# 运行测试的时候，在控制台显示 print 函数结果
pytest test/ --show-capture 
# 简写
pytest test/ -s



# 运行单个文件
pytest test/test_sample.py

# 运行指定的一个函数
pytest test/test_sample.py::test_add
```