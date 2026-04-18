
# 代理OCR和130+格式解析。将PDF和扫描件转化为LLM支持的文本
# from llama_cloud import LlamaCloud
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

#配置llm
Settings.llm = Ollama(
    model="llama3.1:latest",  # 大模型
    request_timeout=360.0,     # 超时时间
    base_url="http://localhost:11434"  # 默认地址
)

#将将PDF扫描件转换为文本
# from llama_parse import LlamaParse

# parser = LlamaParse(
#     api_key="your-api-key",  # 需要注册
#     result_type="markdown",
#     language="ch"  # 支持中文
# )

# documents = parser.load_data("path/to/your/document.pdf")

# 配置嵌入模型（使用Ollama）
Settings.embed_model = OllamaEmbedding(
    model_name="llama3.1:latest",  # 或者使用专门的嵌入模型如 "nomic-embed-text"
    base_url="http://localhost:11434"
)

# OCR配置（如果需要）
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr"  # Tesseract路径


# ==================== 加载文档 ====================
def load_documents():
    """加载data文件夹中的所有文档"""
    print("正在加载文档...")
    # 如果不存在data文件夹，创建它
    if not os.path.exists("./data"):
        os.makedirs("./data")
        print("❌ data文件夹不存在，已创建。请把PDF/图片文件放入./data文件夹")
        return []

    documents = SimpleDirectoryReader(
        input_dir="./data",
        required_exts=[".pdf", ".jpg", ".jpeg", ".png", ".txt", ".docx"],
        recursive=True  # 递归子文件夹
    ).load_data()
    print(f"加载了 {len(documents)} 个文档")
    return documents


# ==================== 构建索引 ====================
def build_index(documents):
    """构建向量索引"""
    if not documents:
        return None

    print("正在构建索引...")
    index = VectorStoreIndex.from_documents(documents)

    # 持久化保存
    index.storage_context.persist(persist_dir="./storage")
    print("索引已保存到 ./storage")
    return index


# ==================== 加载已有索引 ====================
def load_index():
    """从磁盘加载索引"""
    if os.path.exists("./storage"):
        print("正在加载已有索引...")
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)
        print("✅ 索引加载成功")
        return index
    return None


# ==================== 查询 ====================
def query_documents(index, question):
    """查询文档"""
    if index is None:
        return "❌ 索引不存在，请先添加文档"

    query_engine = index.as_query_engine(
        similarity_top_k=5,  # 返回最相关的5个片段
        response_mode="compact"  # 紧凑模式
    )
    response = query_engine.query(question)
    return response


# ==================== 主程序 ====================
def main():
    # 尝试加载已有索引
    index = load_index()

    # 如果没有，重新构建
    if index is None:
        documents = load_documents()
        if documents:  # 只有有文档时才构建
            index = build_index(documents)
        else:
            print("❌ 没有文档可处理，请先添加文件到./data文件夹")
            return

    # 交互式查询
    print("\n=== 文档知识库已就绪，开始提问（输入'退出'或'exit'结束）===")
    while True:
        question = input("\n你的问题: ")
        if question.lower() in ['退出', 'exit', 'quit']:
            break

        response = query_documents(index, question)
        print(f"\n回答: {response}")

if __name__ == "__main__":
    main()