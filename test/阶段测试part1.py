'''
RAG 系统架构与路由设计
请描述用户发起查询后，RAG 从接收 query 到返回答案的完整流程，
并说明 FAQ 模块与 RAG 模块的切换条件、Redis/MySQL/Milvus 各自职责，以及为何采用「FAQ 优先 + RAG 兜底」
'''

'''
文档入库与父子块策略
说明父块+子块切分策略的设计原因；解释为何「子块检索、父块返回」；
说明 父块ID 与 父块内容 的作用；若检索命中准确但回答缺背景，如何从分块角度排查优化？
'''

'''
混合检索与重排序
说明稠密检索与稀疏检索各自擅长什么；
解释 WeightedRanker(0.7, 1.0) 的含义及稀疏向量权重更高的原因；说明 Rerank 的作用；
若系统响应变慢，优先排查哪个环节？
'''

'''
RAG 评估与质量优化
说明 RAGAS 四个核心指标（Faithfulness（忠实度）、Answer Relevancy（答案相关性）、
Context Relevance（上下文相关性）、Context Recall（上下文召回率））各自衡量什么；
若 Faithfulness 低但 Context Recall 正常如何优化？若 Context Recall 低如何优化？
'''