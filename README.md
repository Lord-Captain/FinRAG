# FinRAG - 金融智能问答系统

基于 **RAG（检索增强生成）** 的金融领域智能问答系统，支持 FAQ 精准匹配与知识库深度检索双通道协作。

## 系统架构

```
用户提问
  │
  ├─► FAQ 通道（MySQL + Redis + BM25）
  │     命中(≥0.85) → 直接返回标准答案
  │
  └─► RAG 通道（Milvus + BGE-M3 + LLM）
        向量检索 → Reranker 重排序 → LLM 生成回答
```

### 核心技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| Web 框架 | FastAPI + Uvicorn | 支持 WebSocket 流式输出 |
| 向量数据库 | Milvus 2.4 | 混合检索（稠密+稀疏） |
| 缓存 | Redis | FAQ 问题缓存，加速 BM25 初始化 |
| 关系数据库 | MySQL 8.0 | FAQ 标准问答对存储 |
| 向量化模型 | BGE-M3 | 支持稠密/稀疏/ColBERT 三种表示 |
| 重排序模型 | BGE-Reranker-Large | 精排检索结果 |
| 查询分类器 | BERT-base-chinese | 二分类：通用知识 vs 金融咨询 |
| 大语言模型 | 通义千问(qwen-plus) | 通过 DashScope API 调用 |
| 文本切分 | ChineseRecursiveTextSplitter | 中文递归切分 |
| FAQ 匹配 | BM25Okapi + jieba 分词 | 短文本精准匹配 |

## 项目结构

```
FinRAG/
├── integrated_qa_system/
│   ├── app.py                      # FastAPI Web 服务入口
│   ├── new_main.py                 # 命令行交互模式
│   ├── config.ini                  # 全局配置文件
│   ├── static/
│   │   └── index.html              # Web 聊天界面
│   ├── base/
│   │   ├── config.py               # 配置解析
│   │   └── logger.py               # 日志模块
│   ├── mysql_qa/                   # FAQ 三层架构
│   │   ├── data/financial_faq.csv  # 金融 FAQ 数据
│   │   ├── db/mysql_client.py      # MySQL 连接与查询
│   │   ├── cache/redis_client.py   # Redis 缓存层
│   │   ├── retrieval/bm25_search.py# BM25 相似度匹配
│   │   └── utils/preprocess.py     # jieba 分词预处理
│   ├── rag_qa/
│   │   ├── core/
│   │   │   ├── new_rag_system.py   # RAG 系统核心（流式+历史）
│   │   │   ├── vector_store.py     # Milvus 向量存储
│   │   │   ├── document_processor.py # 文档处理流水线
│   │   │   ├── query_classifier.py # BERT 查询分类
│   │   │   ├── strategy_selector.py# 策略选择器
│   │   │   └── prompts.py          # 提示词模板
│   │   ├── edu_document_loaders/   # 文档加载器（PDF/PPT/OCR）
│   │   ├── edu_text_spliter/       # 文本切分器
│   │   ├── models/                 # 预训练模型（需自行下载）
│   │   └── data/ai_data/           # 知识库文档（PDF）
│   └── rag_qa/rag_assessment/      # RAG 评估模块
├── test/                           # 测试脚本
├── docker-compose.yml              # Docker 服务编排
└── requirements.txt                # Python 依赖
```

## 支持领域

系统覆盖以下金融领域：

- **股票** - 股票交易、费率、行情等
- **基金** - 基金投资、申购赎回、费率等
- **银行** - 储蓄、贷款、信用卡、外汇等
- **保险** - 保险产品、理赔、退保等
- **期货** - 期货交易、保证金、交割等

## 快速开始

### 1. 环境要求

- Python 3.11+
- Docker（用于启动 Milvus / Redis）
- MySQL 8.0

### 2. 克隆项目

```bash
git clone https://github.com/Lord-Captain/FinRAG.git
cd FinRAG
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动基础服务

```bash
docker-compose up -d
```

> 首次启动需下载镜像（Milvus ~620MB），请耐心等待。

### 5. 准备数据

**导入 FAQ 数据到 MySQL：**

```sql
CREATE DATABASE IF NOT EXISTS subjects_kg DEFAULT CHARACTER SET utf8mb4;
```

```python
from integrated_qa_system.mysql_qa.db.mysql_client import MySQLClient
client = MySQLClient()
client.create_table()
client.insert_data('integrated_qa_system/mysql_qa/data/financial_faq.csv')
```

**构建向量索引：**

```python
from integrated_qa_system.rag_qa.core.vector_store import VectorStore
from integrated_qa_system.rag_qa.core.document_processor import process_documents

vs = VectorStore()
chunks = process_documents('integrated_qa_system/rag_qa/data/ai_data/', 1200, 300, 50)
vs.add_documents(chunks)
```

### 6. 运行系统

**命令行模式：**

```bash
cd integrated_qa_system
python new_main.py
```

**Web 服务模式：**

```bash
cd integrated_qa_system
python app.py
```

启动后访问 http://localhost:8080 打开 Web 聊天界面。

## 配置说明

编辑 `integrated_qa_system/config.ini`：

```ini
[llm]
model = qwen-plus
dashscope_api_key = your-api-key-here

[milvus]
collection_name = finrag_final

[retrieval]
retrieval_k = 3          # 检索返回数量
parent_chunk_size = 1200 # 父块大小
child_chunk_size = 300   # 子块大小
```

## 模型文件

以下模型需自行下载放置到 `integrated_qa_system/rag_qa/models/` 目录：

| 模型 | 用途 | 来源 |
|------|------|------|
| bert-base-chinese | 查询分类基础模型 | HuggingFace |
| bert_query_classifier | 金融咨询分类器 | 微调训练 |
| bge-m3 | 文本向量化 | BAAI |
| bge-reranker-large | 检索结果重排序 | BAAI |

## License

MIT
