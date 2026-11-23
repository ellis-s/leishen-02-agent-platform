# leishen-02-agent-platform

## 安装依赖



```bash
# 安装依赖
pip install uv

uv sync

# 或者使用 pip 安装依赖
pip install -r requirements.txt
```



## 启动服务

1. 启动服务
   ```bash
   uvicorn src:app --host 0.0.0.0 --port 8000
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