# -*- coding: utf-8 -*-
"""
PDF处理和AI分析核心模块
"""

import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional
import base64
import io
from PIL import Image
import pytesseract

try:
    from config.local import local_config

    API_KEY = local_config.ZHIPU_API_KEY or os.getenv("ZHIPU_API_KEY")
except ImportError:
    API_KEY = os.getenv("ZHIPU_API_KEY")

from zhipuai import ZhipuAI


class PdfProcessor:
    """PDF处理和分析器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.client = ZhipuAI(api_key=self.api_key)

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

                full_text.append(f"\n--- 第{page_num + 1}页 ---\n{text}\n")

            doc.close()
            return "\n".join(full_text)

        except Exception as e:
            return f"PDF处理失败: {str(e)}"

    def analyze_pdf(self, pdf_path: Path, question: str) -> str:
        """分析PDF并回答问题"""
        # 提取PDF内容
        pdf_content = self.extract_text_from_pdf(pdf_path)

        # 限制长度
        if len(pdf_content) > 20000:
            pdf_content = pdf_content[:20000] + "\n...[内容过长，已截断]"

        # 构建提示词
        prompt = self._build_prompt(pdf_content, question)

        # 调用AI
        response = self.client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "你是一个专业的PDF文档分析专家"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        return response.choices[0].message.content

    def analyze_pdf_stream(self, pdf_path: Path, question: str):
        """流式分析（逐字返回）"""
        pdf_content = self.extract_text_from_pdf(pdf_path)

        if len(pdf_content) > 20000:
            pdf_content = pdf_content[:20000] + "\n...[内容过长，已截断]"

        prompt = self._build_prompt(pdf_content, question)

        # 流式响应
        response = self.client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "你是一个专业的PDF文档分析专家"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

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

    def analyze_pdf(self, pdf_path, question):
        return f"[模拟响应] 分析PDF文件：{pdf_path}，问题：{question}\n\n这是一个模拟的分析结果，实际使用时需要提供真实的ZhipuAI API密钥。"

    def extract_text_from_pdf(self, pdf_path):
        return f"[模拟文本] 从PDF文件 {pdf_path} 提取的文本内容"


# 尝试创建真实的处理器，如果失败则使用模拟处理器
try:
    processor = PdfProcessor()
except Exception as e:
    print(f"无法创建真实的PDF处理器，使用模拟处理器: {e}")
    processor = MockPdfProcessor()