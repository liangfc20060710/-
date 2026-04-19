
# 代理OCR和130+格式解析。将PDF和扫描件转化为LLM支持的文本
# from llama_cloud import LlamaCloud
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage,Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

#配置llm
Settings.llm = Ollama(
    model="llama3:latest",  # 大模型
    request_timeout=360.0,     # 超时时间
    base_url="http://localhost:11434"  # 默认地址
)


# 配置嵌入模型（使用Ollama）
Settings.embed_model = OllamaEmbedding(
    model_name="llama3:latest",  # 或者使用专门的嵌入模型如 "nomic-embed-text"
    base_url="http://localhost:11434"
)

# OCR配置（如果需要）
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr"  # Tesseract路径


def pdf_to_text_with_ocr(pdf_path):
    """将PDF（包括扫描版）转为文本"""
    text = ""
    pdf = fitz.open(pdf_path)

    for page_num in range(pdf.page_count):
        page = pdf[page_num]

        # 尝试直接提取文本
        page_text = page.get_text()
        if page_text.strip():
            text += page_text + "\n"
        else:
            # 如果是扫描页，用OCR
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            text += ocr_text + "\n"

    pdf.close()
    return text

# ==================== 加载文档 ====================
def load_documents():
    """加载data文件夹中的所有文档"""
    print("正在加载文档...")
    if not os.path.exists("./data"):
        os.makedirs("./data")
        print("❌ data文件夹不存在，请放入文件")
        return []

    documents = []
    for filename in os.listdir("./data"):
        filepath = os.path.join("./data", filename)

        if filename.lower().endswith('.pdf'):
            text = pdf_to_text_with_ocr(filepath)
            doc = Document(text=text, metadata={"filename": filename})
            documents.append(doc)
            print(f"  加载PDF: {filename} (长度: {len(text)})")
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            text = pytesseract.image_to_string(
                Image.open(filepath),
                lang='chi_sim+eng'
            )
            doc = Document(text=text, metadata={"filename": filename})
            documents.append(doc)
            print(f"  加载图片: {filename} (长度: {len(text)})")

    print(f"加载了 {len(documents)} 个文档")
    return documents


# ==================== 构建索引 ====================
def build_index(documents):
    """构建向量索引"""
    if not documents:
        return None

    print("正在构建索引...")
    index = VectorStoreIndex.from_documents(documents,
        show_progress=True)
    # 调试：检查索引中的文本片段
    print(f"\n索引包含 {len(documents)} 个文档")
    print(f"第一个文档长度: {len(documents[0].text)} 字符")
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
        similarity_top_k=10,  # 返回最相关的5个片段
        response_mode="tree_summarize",  # 紧凑模式
        verbose = True  # 显示查询过程
    )
    response = query_engine.query(question)
    return response


# ==================== 主程序 ====================

import shutil
def main():
    # 检查data文件夹中的文件数量
    data_files = os.listdir("./data") if os.path.exists("./data") else []

    # 判断条件：storage不存在 或 data文件夹为空
    if not os.path.exists("./storage") or len(data_files) == 0:
        print("=" * 50)
        print("首次运行或发现新文件，正在重新构建索引...")
        print("=" * 50)

        # 加载文档
        documents = load_documents()

        if not documents:
            print("❌ 没有文档可处理，请把PDF文件放入./data文件夹")
            return

        # 构建索引
        index = build_index(documents)

        if index is None:
            print("❌ 索引构建失败")
            return

        print("✅ 索引构建完成！")
    else:
        print("=" * 50)
        print("发现已有索引，正在加载...")
        print("=" * 50)

        # 加载已有索引
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)

        if index is None:
            print("❌ 索引加载失败")
            return

        print("✅ 索引加载成功！")
        print(f"   文档数量: {len(data_files)} 个")
        print(f"   文件列表: {', '.join(data_files)}")

    # ==================== 开始交互式查询 ====================
    print("\n" + "=" * 50)
    print("文档知识库已就绪，开始提问（输入'退出'或'exit'结束）")
    print("=" * 50)

    while True:
        question = input("\n你的问题: ").strip()

        if not question:
            continue

        if question.lower() in ['退出', 'exit', 'quit', 'q']:
            print("感谢使用，再见！")
            break

        print("\n正在查询，请稍候...")
        response = query_documents(index, question)

        print("\n" + "-" * 50)
        print("回答:", response)
        print("-" * 50)

if __name__ == "__main__":
    main()