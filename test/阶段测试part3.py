'''
6. 向量库检索
前置条件：
先成功运行编码题 1，确保 Milvus 集合 edu_rag_exam_hybrid 中已有 dense_vector 和 sparse_vector 数据。
任务：
补全 TODO，实现「用户提问 -> BGE-M3 查询向量化 -> Milvus 混合检索 -> BGE Reranker 精排 -> 拼接 Prompt -> 打印结果」。
评分标准

项目	分值
HybridMilvusRetriever.search 正确执行 dense+sparse 混合检索	12
BGEReranker.rerank 正确调用本地 bge-reranker-large 精排	8
PromptBuilder.build Prompt 结构完整，按父块去重	6
MiniRAG.ask 流程串联正确，main 可运行	4
'''

'''
本题代码：rag_query.py
起始代码


'''

"""
运行：python rag_query.py
编码题2：BGE-M3 混合检索 + BGE Reranker 精排 + Prompt 生成
"""
"""
编码题2：BGE-M3 混合检索 + BGE Reranker 精排 + Prompt 生成
运行：python rag_query.py
"""
from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker

from build_knowledge_base import SimpleEmbedder


class HybridMilvusRetriever:
    """Milvus 混合检索器：dense_vector + sparse_vector"""

    def __init__(
        self,
        uri: str = "http://localhost:19530",
        collection_name: str = "edu_rag_exam_hybrid",
        embedder: SimpleEmbedder | None = None,
    ):
        self.client = MilvusClient(uri=uri)
        self.collection_name = collection_name
        self.embedder = embedder or SimpleEmbedder()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        返回文档列表，每项包含：
        text / parent_id / parent_content / source / score
        """
        # TODO 1（12分）：实现 dense+sparse 混合检索
        # 要求：
        #   1. 使用 self.embedder.encode([query]) 同时生成 query dense/sparse
        #   2. 构造 dense_vector 的 AnnSearchRequest
        #   3. 构造 sparse_vector 的 AnnSearchRequest
        #   4. 使用 WeightedRanker 融合，建议 dense 权重 0.7，sparse 权重 0.3
        #   5. 调用 client.hybrid_search
        #   6. 解析返回结果，保留 text / parent_id / parent_content / source / score

        # 1. 生成 query 的 dense 和 sparse 向量
        vectors = self.embedder.encode([query])
        dense_vec = vectors["dense"][0]
        sparse_vec = vectors["sparse"][0]

        # 2. 构造 dense_vector 的 AnnSearchRequest
        dense_req = AnnSearchRequest(
            data=[dense_vec],
            anns_field="dense_vector",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=top_k,
        )
        #   3. 构造 sparse_vector 的 AnnSearchRequest
        sparse_req = AnnSearchRequest(
            data=[sparse_vec],
            anns_field="sparse_vector",
            param={"metric_type": "IP"},
            limit=top_k,
        )

        # 4. 使用 WeightedRanker 融合，建议 dense 权重 0.7，sparse 权重 0.3
        # 5. 调用 client.hybrid_search
        results = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[dense_req, sparse_req],
            ranker=WeightedRanker(0.7, 0.3),
            limit=top_k,
            output_fields=["text", "parent_id", "parent_content", "source"],
        )

        # 6. 解析返回结果，保留 text / parent_id / parent_content / source / score
        docs = []
        for hits in results:
            for hit in hits:
                docs.append({
                    "text": hit["entity"]["text"],
                    "parent_id": hit["entity"]["parent_id"],
                    "parent_content": hit["entity"]["parent_content"],
                    "source": hit["entity"]["source"],
                    "score": hit["distance"],
                })
        return docs


class BGEReranker:
    """使用本地 bge-reranker-large 进行精排"""

    def __init__(self, model_path: str = "./models/bge-reranker-large"):
        from FlagEmbedding import FlagReranker
        self.model_path = model_path
        self.model = FlagReranker(model_path, use_fp16=False)

    def rerank(self, query: str, docs: list[dict], top_n: int = 3) -> list[dict]:
        # TODO 2（8分）：调用本地 bge-reranker-large 对候选文档精排
        # 要求：
        #   1. 输入 pair 格式为 [query, doc["text"]]
        #   2. 使用 self.model.compute_score(pairs, normalize=True)
        #   3. 将分数写入 doc["rerank_score"]
        #   4. 按 rerank_score 降序返回 top_n
        if not docs:
            return []

        # 1. 构造 pairs
        pairs = [[query, doc["text"]] for doc in docs]

        # 2. 使用 self.model.compute_score(pairs, normalize=True)
        scores = self.model.compute_score(pairs, normalize=True)

        # 3. 写入分数doc["rerank_score"]并排序
        for doc, score in zip(docs, scores):
            doc["rerank_score"] = float(score)

        sorted_docs = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
        # 4.按 rerank_score 降序返回 top_n
        return sorted_docs[:top_n]


class PromptBuilder:
    """RAG Prompt 拼接器"""

    def build(self, query: str, docs: list[dict], phone: str = "400-123-4567") -> str:
        """
        Prompt 必须包含：
          1. 角色设定
          2. 上下文：来自 parent_content，按 parent_id 去重后拼接
          3. 用户问题
          4. 拒答话术：信息不足时联系人工客服
        """
        # TODO 3（6分）：按 parent_id 去重，拼接 parent_content，生成 Prompt
        seen_parent_ids = set()
        unique_contexts = []
        for doc in docs:
            pid = doc.get("parent_id", "")
            if pid and pid not in seen_parent_ids:
                seen_parent_ids.add(pid)
                unique_contexts.append(doc.get("parent_content", ""))

        context_text = "\n\n".join(unique_contexts) if unique_contexts else "无相关上下文"

        prompt = f"""你是一个专业的教育知识问答助手。请根据以下参考资料回答用户问题。
        如果参考资料不足以回答问题，请明确告知用户信息不足，并建议联系人工客服（电话：{phone}）。

        【参考资料】
        {context_text}

        【用户问题】
        {query}

        【回答要求】
        1. 仅基于参考资料回答，不要编造信息。
        2. 若资料不足，必须包含拒答话术并提供客服电话。
        3. 回答简洁、准确、有条理。"""
        return prompt


class MiniRAG:
    """简版 RAG 问答入口"""

    def __init__(self):
        self.retriever = HybridMilvusRetriever()
        self.reranker = BGEReranker()
        self.prompt_builder = PromptBuilder()

    def ask(self, query: str) -> dict:
        # TODO 4（4分）：串联 hybrid search -> rerank -> build prompt，并调用大模型进行回复（符合openai接口或者ollama本地模型）
        # 1. 混合检索
        retrieved = self.retriever.search(query, top_k=5)

        # 2. 精排
        reranked = self.reranker.rerank(query, retrieved, top_n=3)

        # 3. 构建 Prompt
        prompt = self.prompt_builder.build(query, reranked)

        # 4. 调用 LLM 生成回答
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=512,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"LLM 调用失败：{str(e)}"
        return {
        "query": query,
        "retrieved": retrieved,
        "reranked": reranked,
        "prompt": prompt,
        "answer": answer,
    }


def main():
    rag = MiniRAG()

    test_queries = [
        "BGE-M3如何支持混合检索？",
        "RAG系统中文档为什么要切分为父块和子块？",
    ]

    for q in test_queries:
        result = rag.ask(q)
        print("=" * 60)
        print(f"【用户问题】{result['query']}")
        print(f"【混合检索命中】{len(result['retrieved'])} 条")
        print(f"【精排后Top】{len(result['reranked'])} 条")
        for i, d in enumerate(result["reranked"], 1):
            print(
                f"  {i}. rerank={d.get('rerank_score', 0):.4f} "
                f"hybrid={d.get('score', 0):.4f} {d.get('text', '')[:50]}..."
            )
        print("【最终Prompt】")
        print(result["prompt"])
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()