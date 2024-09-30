## Chat2SQLGraph

**Chat2SQLGraph** 是一个基于对话的智能数据分析和可视化工具。通过自然语言对话，用户可以生成 SQL 查询、执行数据检索，并自动将查询结果转化为可视化图表。该项目利用大语言模型（LLM）实现自然语言到 SQL 的翻译，并将 SQL 查询结果直观地展现在图表中，极大地方便了用户的数据分析过程。

即将推出全新前端代码和在线体验。


### 主要功能：

- **自然语言转 SQL 查询**：通过与系统的对话，生成复杂的 SQL 查询语句。
- **智能数据检索**：执行生成的 SQL 查询，获取数据库中的数据。
- **自动数据可视化**：将 SQL 查询结果转化为图表，如柱状图、饼图、折线图等，帮助用户更好地理解数据。
- **易于集成和扩展**：支持不同的数据库系统和图表库，适用于各种数据分析场景。

### 应用场景：

- 数据分析师快速生成和执行 SQL 查询并可视化结果。
- 产品经理和业务分析师通过自然语言探索数据洞察。
- 数据科学团队协作分析和共享可视化结果。

### 使用方法

#### 预备工具

- python 3.12
- poetry
- postgres

#### 运行后端项目

1. 创建虚拟环境
```bash
python -m venv venv 
# py -m venv venv
```

2. 激活环境
```bash
.\venv\Scripts\activate
```

3. 安装后端所需依赖
```bash
poetry install
```

4. 修改配置文件 config.yaml 配置为自己的数据库信息

5. 运行数据库迁移
```bash
python backend/manage.py makemigrations
```

6. 运行项目
```bash
python main.py
```


### 参与者

以下是本项目的主要参与者（排名不分先后）：

| github | 角色 | 
|------|------|
| [@bigcyy](https://github.com/bigcyy) | 后端开发 | 
| [@夏安](https://github.com/1653756334) | 前端开发 | 

**Chat2SQLGraph** ,欢迎贡献和反馈！

