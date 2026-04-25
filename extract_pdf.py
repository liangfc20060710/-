# -*- coding: utf-8 -*-
"""
PDF处理和AI分析核心模块
"""

import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional, Dict, Any
import base64
import io
from PIL import Image
import pytesseract
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 从配置文件中读取API密钥
try:
    from config import ZHIPU_API_KEY
except ImportError:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")

from zhipuai import ZhipuAI


class PdfProcessor:
    """PDF处理和分析器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ZHIPU_API_KEY
        self.client = ZhipuAI(api_key=self.api_key)
        self.vector_store = None  # 向量存储
        self.text_chunks = []  # 文本分块

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """从PDF提取文字（支持OCR）"""
        try:
            doc = fitz.open(pdf_path)
            full_text = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                # 尝试提取文字
                text = page.get_text()

                # 如果没有文字（扫描件），进行OCR
                if not text.strip():
                    print(f"第{page_num + 1}页无文字，正在OCR...")
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    try:
                        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                    except Exception as e:
                        text = f"[OCR失败: {e}]"

                full_text.append(f"\n--- 第{page_num + 1}页 ---{text}\n")

            doc.close()
            return "\n".join(full_text)

        except Exception as e:
            return f"PDF处理失败: {str(e)}"

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """将文本分成小块"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def get_text_embedding(self, text: str) -> List[float]:
        """获取文本的向量嵌入"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"获取文本嵌入失败: {e}")
            # 返回随机向量作为 fallback
            return [np.random.rand() for _ in range(1536)]

    def build_vector_index(self, text: str):
        """构建向量索引"""
        # 文本分块
        self.text_chunks = self.chunk_text(text)
        
        # 获取每个分块的嵌入
        embeddings = []
        for chunk in self.text_chunks:
            embedding = self.get_text_embedding(chunk)
            embeddings.append(embedding)
        
        # 构建向量存储
        self.vector_store = {
            "embeddings": np.array(embeddings),
            "chunks": self.text_chunks
        }
        
        print(f"成功构建向量索引，共{len(self.text_chunks)}个分块")

    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[str]:
        """检索与查询相关的文本分块"""
        if not self.vector_store:
            return []
        
        # 获取查询的嵌入
        query_embedding = self.get_text_embedding(query)
        
        # 计算相似度
        similarities = cosine_similarity(
            [query_embedding],
            self.vector_store["embeddings"]
        )[0]
        
        # 获取最相似的top_k个分块
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        relevant_chunks = [self.vector_store["chunks"][i] for i in top_indices]
        
        return relevant_chunks

    def analyze_pdf(self, pdf_path: str, question: str) -> str:
        """分析PDF并回答问题"""
        try:
            # 提取PDF内容
            pdf_content = self.extract_text_from_pdf(Path(pdf_path))

            # 构建向量索引
            self.build_vector_index(pdf_content)

            # 检索相关文本分块
            relevant_chunks = self.retrieve_relevant_chunks(question)
            relevant_content = "\n".join(relevant_chunks)

            # 构建提示词
            prompt = self._build_prompt(relevant_content, question)

            # 调用AI
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的PDF文档分析专家，基于文档内容回答问题"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"分析PDF失败: {e}")
            return f"分析PDF文件失败: {str(e)}"

    def analyze_pdf_stream(self, pdf_path: str, question: str):
        """流式分析（逐字返回）"""
        try:
            # 提取PDF内容
            pdf_content = self.extract_text_from_pdf(Path(pdf_path))

            # 构建向量索引
            self.build_vector_index(pdf_content)

            # 检索相关文本分块
            relevant_chunks = self.retrieve_relevant_chunks(question)
            relevant_content = "\n".join(relevant_chunks)

            prompt = self._build_prompt(relevant_content, question)

            # 流式响应
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的PDF文档分析专家，基于文档内容回答问题"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"流式分析PDF失败: {e}")
            yield f"分析PDF文件失败: {str(e)}"

    def analyze_document(self, file_path, question, file_type="pdf"):
        """通用文档分析方法，支持PDF、Excel和对话"""
        if file_type == "conversation":
            # 智能对话模式
            try:
                response = self.client.chat.completions.create(
                    model="glm-4",
                    messages=[
                        {"role": "system", "content": "你是一个专业的企业财务分析专家，能够回答关于企业财务、运营和管理的问题"},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"智能对话失败: {e}")
                return f"智能对话失败: {str(e)}"
        else:
            # 对于PDF和Excel文件，使用现有的分析方法
            return self.analyze_pdf(file_path, question)

    def extract_financial_data_from_excel(self, excel_path: str) -> Dict[str, Any]:
        """从Excel文件中提取财务数据"""
        try:
            df = pd.read_excel(excel_path)
            data = {
                "columns": df.columns.tolist(),
                "data": df.values.tolist(),
                "row_count": len(df),
                "has_numerical_data": False,
                "numerical_columns": [],
                "chart_data": {}
            }
            
            # 检测数值列
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numerical_cols:
                data["has_numerical_data"] = True
                data["numerical_columns"] = numerical_cols
                
                # 提取各列的数值数据用于图表
                for col in numerical_cols[:6]:  # 最多取6列
                    data["chart_data"][col] = df[col].dropna().tolist()
            
            return data
        except Exception as e:
            print(f"提取Excel数据失败: {e}")
            return {"error": str(e)}

    def extract_data_for_chart(self, excel_path: str, chart_type: str, question: str) -> Dict[str, Any]:
        """根据图表类型和问题提取数据"""
        try:
            df = pd.read_excel(excel_path)
            result = {
                "chart_type": chart_type,
                "columns": df.columns.tolist(),
                "data": {}
            }
            
            # 根据问题类型确定需要提取的数据
            question_lower = question.lower()
            
            # 尝试匹配列名
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['收入', 'revenue', 'sales']):
                    result["data"]["revenue"] = df[col].fillna(0).tolist()
                elif any(keyword in col_lower for keyword in ['利润', 'profit']):
                    result["data"]["profit"] = df[col].fillna(0).tolist()
                elif any(keyword in col_lower for keyword in ['成本', 'cost']):
                    result["data"]["cost"] = df[col].fillna(0).tolist()
                elif any(keyword in col_lower for keyword in ['资产', 'asset']):
                    result["data"]["asset"] = df[col].fillna(0).tolist()
                elif any(keyword in col_lower for keyword in ['负债', 'debt', 'liability']):
                    result["data"]["debt"] = df[col].fillna(0).tolist()
            
            # 如果没有匹配到，使用数值列
            if not result["data"]:
                numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                for col in numerical_cols[:5]:
                    # 使用实际的列名作为标签
                    result["data"][str(col)] = df[col].fillna(0).tolist()
            
            # 获取类别标签（通常是第一列或日期列）
            if len(df) > 0:
                result["labels"] = df.iloc[:, 0].astype(str).tolist()
            
            # 确保所有数据系列长度一致
            max_length = len(result.get("labels", []))
            if max_length == 0 and result["data"]:
                # 如果没有标签，使用第一个数据系列的长度
                first_key = next(iter(result["data"]), None)
                if first_key:
                    max_length = len(result["data"][first_key])
            
            # 调整所有数据系列的长度
            for key in result["data"]:
                data = result["data"][key]
                if len(data) > max_length:
                    # 截断过长的数据
                    result["data"][key] = data[:max_length]
                elif len(data) < max_length:
                    # 填充过短的数据
                    result["data"][key] = data + [0] * (max_length - len(data))
            
            # 确保标签长度与数据长度匹配
            if len(result.get("labels", [])) < max_length:
                # 填充标签
                current_labels = result.get("labels", [])
                for i in range(len(current_labels), max_length):
                    current_labels.append(f"项目{i+1}")
                result["labels"] = current_labels
            elif len(result.get("labels", [])) > max_length:
                # 截断标签
                result["labels"] = result["labels"][:max_length]
            
            return result
        except Exception as e:
            print(f"提取图表数据失败: {e}")
            return {"error": str(e)}

    def determine_chart_type(self, question: str) -> str:
        """根据问题确定应该生成的图表类型"""
        question_lower = question.lower()
        
        # 饼图关键词
        if any(keyword in question_lower for keyword in ['占比', '比例', '分配', '构成', 'pie', 'ratio', 'proportion', 'structure']):
            return "pie"
        
        # 折线图关键词
        elif any(keyword in question_lower for keyword in ['趋势', '变化', '增长', 'trend', 'growth', 'change', '时间']):
            return "line"
        
        # 柱状图关键词
        elif any(keyword in question_lower for keyword in ['比较', '对比', '排名', 'compare', 'rank', 'bar']):
            return "bar"
        
        # 雷达图关键词
        elif any(keyword in question_lower for keyword in ['雷达', '综合', '多维度', 'radar', 'overall']):
            return "radar"
        
        # 默认返回柱状图
        return "bar"

    def generate_chart_data_from_question(self, excel_path: str, question: str) -> Dict[str, Any]:
        """根据用户问题从Excel文件生成图表数据"""
        try:
            chart_type = self.determine_chart_type(question)
            chart_data = self.extract_data_for_chart(excel_path, chart_type, question)
            
            return {
                "code": 200,
                "chart_type": chart_type,
                "data": chart_data,
                "message": f"成功生成{chart_type}图表数据"
            }
        except Exception as e:
            return {
                "code": 500,
                "error": str(e),
                "message": "生成图表数据失败"
            }

    def get_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """自动识别并映射常见财务列名"""
        column_map = {}
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # 收入相关
            if any(k in col_lower for k in ['收入', 'revenue', 'sales', '销售额', '营业']):
                column_map[col] = 'revenue'
            # 成本相关
            elif any(k in col_lower for k in ['成本', 'cost', '费用', 'expense']):
                column_map[col] = 'cost'
            # 利润相关
            elif any(k in col_lower for k in ['利润', 'profit', '收益', 'gain']):
                column_map[col] = 'profit'
            # 资产相关
            elif any(k in col_lower for k in ['资产', 'asset', '财产']):
                column_map[col] = 'asset'
            # 负债相关
            elif any(k in col_lower for k in ['负债', 'debt', 'liability', '贷款']):
                column_map[col] = 'liability'
            # 现金流相关
            elif any(k in col_lower for k in ['现金', 'cash', '流量', 'flow']):
                column_map[col] = 'cash_flow'
            # 数量相关
            elif any(k in col_lower for k in ['数量', 'quantity', 'num', 'count']):
                column_map[col] = 'quantity'
            # 百分比相关
            elif any(k in col_lower for k in ['百分比', 'percent', 'rate', '比率']):
                column_map[col] = 'rate'
                
        return column_map

    def _build_prompt(self, pdf_content: str, question: str) -> str:
        """构建提示词"""
        return f"""请分析以下PDF文档并回答问题：

<PDF文档内容>
{pdf_content}
</PDF文档内容>

用户问题：{question}

请基于文档内容给出详细回答。如果文档中没有相关信息，请说明。

要求：
1. 回答准确、详细
2. 引用文档中的具体内容
3. 如果信息不足，请明确指出
"""

    def get_pdf_info(self, pdf_path: Path) -> dict:
        """获取PDF基本信息"""
        try:
            doc = fitz.open(pdf_path)
            info = {
                "pages": len(doc),
                "filename": pdf_path.name,
                "size_mb": pdf_path.stat().st_size / 1024 / 1024,
                "has_text": False
            }

            # 检查是否有文字
            for page in doc:
                if page.get_text().strip():
                    info["has_text"] = True
                    break

            doc.close()
            return info
        except Exception as e:
            return {"error": str(e)}


# 全局处理器实例
class MockPdfProcessor:
    """模拟PDF处理器，用于测试"""
    
    def __init__(self):
        self.vector_store = None
        self.text_chunks = []
        self.document_content = ""  # 存储文档内容
    
    def analyze_pdf(self, pdf_path, question):
        # 模拟向量检索
        relevant_content = f"[模拟相关内容] 与问题 '{question}' 相关的PDF内容"
        return f"[模拟响应] 分析PDF文件：{pdf_path}，问题：{question}\n\n基于向量检索的相关内容：\n{relevant_content}\n\n这是一个模拟的分析结果，实际使用时需要提供真实的ZhipuAI API密钥。"

    def analyze_document(self, file_path, question, file_type="pdf"):
        """通用文档分析方法，支持PDF、Excel和对话"""
        # 模拟向量检索
        relevant_content = f"[模拟相关内容] 与问题 '{question}' 相关的{file_type.upper()}内容"
        
        # 根据文件类型提供不同的模拟响应
        if file_type == "excel":
            return f"[模拟Excel分析] 文件：{file_path}\n问题：{question}\n\n基于文件内容的分析：\n这是一个Excel文件，包含财务数据表格。根据您的问题，我分析了以下相关内容：\n{relevant_content}\n\n注意：这是一个模拟的分析结果，实际使用时需要提供真实的ZhipuAI API密钥。"
        elif file_type == "conversation":
            # 智能对话模式
            return f"[智能对话回复]\n\n问题：{question}\n\n回复：\n根据您的问题，我分析了企业的财务数据，发现以下关键点：\n{relevant_content}\n\n建议：\n1. 定期监控财务指标变化\n2. 优化成本结构\n3. 提高资产利用效率\n4. 加强现金流管理\n\n注意：这是一个模拟的智能对话回复，实际使用时需要提供真实的ZhipuAI API密钥。"
        else:
            return f"[模拟PDF分析] 文件：{file_path}\n问题：{question}\n\n基于向量检索的相关内容：\n{relevant_content}\n\n这是一个模拟的分析结果，实际使用时需要提供真实的ZhipuAI API密钥。"

    def extract_text_from_pdf(self, pdf_path):
        return f"[模拟文本] 从PDF文件 {pdf_path} 提取的文本内容"
    
    def build_vector_index(self, text):
        # 模拟构建向量索引
        self.text_chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
        self.vector_store = {
            "embeddings": np.random.rand(len(self.text_chunks), 1536),
            "chunks": self.text_chunks
        }
        self.document_content = text
        print(f"[模拟] 成功构建向量索引，共{len(self.text_chunks)}个分块")
    
    def retrieve_relevant_chunks(self, query, top_k=3):
        # 模拟检索相关分块
        if not self.vector_store:
            return []
        # 随机返回一些分块
        import random
        return random.sample(self.text_chunks, min(top_k, len(self.text_chunks)))
    
    def analyze_pdf_stream(self, pdf_path, question):
        # 模拟流式分析
        response = f"[模拟流式响应] 分析PDF文件：{pdf_path}，问题：{question}\n\n这是一个模拟的流式分析结果。"
        for char in response:
            yield char
            import time
            time.sleep(0.05)


# 尝试创建真实的处理器，如果失败则使用模拟处理器
try:
    processor = PdfProcessor()
except Exception as e:
    print(f"无法创建真实的PDF处理器，使用模拟处理器: {e}")
    processor = MockPdfProcessor()