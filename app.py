from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from executive_team import anaylises


# 导入智能体核心代码
from executive_team import ExecutiveTeam, BusinessContext

# 导入pdf和扫描件代码
from extract_pdf import PdfProcessor, processor

# 扩展允许的文件类型
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf'}

# 初始化Flask app
app = Flask(__name__)

# 基础配置
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 初始化智能体
team = ExecutiveTeam()


# 工具函数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 检查是否是PDF文件
def is_pdf_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


# ==================== 路由接口 ====================
# 1. 首页路由【必须打开！不能注释！】
@app.route('/')
def index():
    return render_template('index.html')
    # return render_template('experience.html')


# 2. 其他页面路由
@app.route('/<page_name>.html')
def render_page(page_name):
    try:
        return render_template(f'{page_name}.html')
    except:
        return render_template('404.html'), 404


# 3. 核心接口：上传Excel + 智能分析 + 纯消息分析 + PDF分析
@app.route('/api/analyze', methods=['POST'])
def analyze_excel():
    # 获取企业名称
    company_name = request.form.get('company_name', '未命名企业')
    # 获取用户消息
    user_message = request.form.get('message', '')

    # 检查是否有文件上传
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']

        if not allowed_file(file.filename):
            return jsonify({"code": 400, "msg": "只支持xlsx/xls/pdf格式的文件"}), 400

        try:
            # 生成模拟财务数据用于可视化
            financial_data = generate_financial_data()

            # 检查是否是PDF文件
            if is_pdf_file(file.filename):
                # 保存PDF文件
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # 使用PDF处理器分析文件
                if user_message:
                    analysis_result = processor.analyze_pdf(file_path, user_message)
                else:
                    analysis_result = "PDF文件已成功上传，请提出具体问题以获取分析结果。"

                # 生成模拟财务数据用于评分
                financial_data = generate_financial_data()
                health_score = calculate_health_score(analysis_result, user_message, financial_data)
                risk_warning = "无重大风险"
                stored_file_path = file_path
                
                # 标记为文件分析，需要显示健康评分
                show_health_score = True
            else:
                # 处理文件
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                stored_file_path = file_path
                
                # 重新打开文件进行读取
                df = pd.read_excel(file_path)
                print(df.head())  # 显示前几行
                
                # 使用PDF处理器分析Excel文件（通过通用文档分析方法）
                if user_message:
                    # 将DataFrame转换为文本进行分析
                    excel_content = df.to_string()
                    analysis_result = processor.analyze_document(file_path, user_message, file_type="excel")
                else:
                    analysis_result = "文件已成功上传，请提出具体问题以获取分析结果。"

                # 生成财务数据用于评分
                financial_data = generate_financial_data()
                health_score = calculate_health_score(analysis_result, user_message, financial_data)
                risk_warning = "无重大风险"
                
                # 标记为文件分析，需要显示健康评分
                show_health_score = True

        except Exception as e:
            return jsonify({"code": 500, "msg": f"分析失败：{str(e)}"}), 500
    else:
        # 纯消息分析（智能对话）- 不显示健康评分
        try:
            # 生成模拟财务数据用于可视化
            financial_data = generate_financial_data()

            # 尝试使用处理器进行智能对话
            if user_message:
                # 调用智能体进行对话
                try:
                    # 使用analyze_document方法进行智能对话
                    analysis_result = processor.analyze_document("conversation", user_message, file_type="conversation")
                    # 纯对话不显示健康评分
                    health_score = None
                    risk_warning = None
                    show_health_score = False
                except Exception as e:
                    # 如果处理器调用失败，使用默认分析
                    print(f"智能体对话失败: {e}")
                    if '成本' in user_message:
                        analysis_result = "成本分析显示，原材料成本占比最高，建议优化采购策略降低成本。"
                        # 纯对话不显示健康评分
                        health_score = None
                        risk_warning = None
                        show_health_score = False
                    elif '资产' in user_message:
                        analysis_result = "资产结构分析显示，流动资产占比合理，固定资产投资适中。"
                        # 纯对话不显示健康评分
                        health_score = None
                        risk_warning = None
                        show_health_score = False
                    elif '利润' in user_message:
                        analysis_result = "利润分析显示，净利润增长率为15%，高于行业平均水平。"
                        # 纯对话不显示健康评分
                        health_score = None
                        risk_warning = None
                        show_health_score = False
                    else:
                        analysis_result = "根据您的问题，我们分析了企业的整体财务状况，各项指标均表现良好。"
                        # 纯对话不显示健康评分
                        health_score = None
                        risk_warning = None
                        show_health_score = False
            else:
                analysis_result = "欢迎使用企业数字大脑智能分析助手，请上传文件或提出具体问题。"
                health_score = None
                risk_warning = None
                show_health_score = False

        except Exception as e:
            return jsonify({"code": 500, "msg": f"分析失败：{str(e)}"}), 500

    return jsonify({
        "code": 200,
        "msg": "分析成功",
        "data": {
            "company_name": company_name,
            "analysis_result": analysis_result,
            "health_score": health_score if show_health_score else None,
            "risk_warning": risk_warning if show_health_score else None,
            "show_health_score": show_health_score,
            "financial_data": financial_data,
            "file_path": stored_file_path if 'stored_file_path' in dir() else None
        }
    })


# 智能健康评分计算函数
def calculate_health_score(analysis_result, user_message, financial_data=None):
    """基于分析内容和数据智能计算企业健康评分"""
    score = 70  # 基础分数
    
    # 分析内容关键词加分/减分
    positive_keywords = {
        '良好': 5, '优秀': 8, '增长': 4, '上升': 3, '盈利': 6, '利润': 5,
        '合理': 3, '优化': 4, '创新': 3, '稳健': 4, '健康': 6, '强': 4
    }
    
    negative_keywords = {
        '风险': -5, '下降': -4, '亏损': -8, '问题': -4, '挑战': -3, '不足': -3,
        '压力': -4, '危机': -10, '困难': -5, '警告': -6, '隐患': -4
    }
    
    # 分析用户问题类型
    question_types = {
        '成本': lambda: analyze_cost_health(analysis_result),
        '资产': lambda: analyze_asset_health(analysis_result),
        '利润': lambda: analyze_profit_health(analysis_result),
        '财务': lambda: analyze_financial_health(analysis_result),
        '风险': lambda: analyze_risk_health(analysis_result)
    }
    
    # 根据分析内容调整分数
    analysis_lower = analysis_result.lower()
    for keyword, value in positive_keywords.items():
        if keyword in analysis_lower:
            score += value
    
    for keyword, value in negative_keywords.items():
        if keyword in analysis_lower:
            score += value
    
    # 根据问题类型进行专项分析
    for key, analyzer in question_types.items():
        if key in user_message:
            score = analyzer()
            break
    
    # 如果有财务数据，基于数据计算
    if financial_data:
        score = adjust_score_by_data(score, financial_data)
    
    # 确保分数在0-100之间
    return max(0, min(100, score))


def analyze_cost_health(analysis_result):
    """分析成本健康度"""
    score = 80
    analysis_lower = analysis_result.lower()
    
    if '成本控制' in analysis_lower or '优化成本' in analysis_lower:
        score += 10
    if '成本上升' in analysis_lower or '成本增加' in analysis_lower:
        score -= 15
    if '成本合理' in analysis_lower:
        score += 5
    
    return score

def analyze_asset_health(analysis_result):
    """分析资产健康度"""
    score = 85
    analysis_lower = analysis_result.lower()
    
    if '资产结构合理' in analysis_lower:
        score += 10
    if '资产负债率' in analysis_lower and '高' in analysis_lower:
        score -= 15
    if '流动资产充足' in analysis_lower:
        score += 8
    
    return score

def analyze_profit_health(analysis_result):
    """分析利润健康度"""
    score = 90
    analysis_lower = analysis_result.lower()
    
    if '利润增长' in analysis_lower or '盈利增加' in analysis_lower:
        score += 8
    if '利润下降' in analysis_lower or '亏损' in analysis_lower:
        score -= 20
    if '利润率' in analysis_lower and '高' in analysis_lower:
        score += 5
    
    return score

def analyze_financial_health(analysis_result):
    """分析整体财务健康度"""
    score = 82
    analysis_lower = analysis_result.lower()
    
    if '财务状况良好' in analysis_lower:
        score += 10
    if '财务风险' in analysis_lower:
        score -= 15
    if '财务稳健' in analysis_lower:
        score += 8
    
    return score

def analyze_risk_health(analysis_result):
    """分析风险健康度"""
    score = 75
    analysis_lower = analysis_result.lower()
    
    if '无重大风险' in analysis_lower:
        score += 15
    if '风险预警' in analysis_lower:
        score -= 20
    if '风险可控' in analysis_lower:
        score += 10
    
    return score

def adjust_score_by_data(base_score, financial_data):
    """基于财务数据调整分数"""
    if not financial_data:
        return base_score
    
    # 分析收入增长趋势
    if 'revenue' in financial_data:
        revenue = financial_data['revenue']
        if len(revenue) >= 2:
            growth_rate = (revenue[-1] - revenue[0]) / revenue[0]
            if growth_rate > 0.3:
                base_score += 10
            elif growth_rate > 0.1:
                base_score += 5
            elif growth_rate < -0.1:
                base_score -= 15
    
    # 分析利润率
    if 'revenue' in financial_data and 'profit' in financial_data:
        revenue = financial_data['revenue']
        profit = financial_data['profit']
        if revenue and profit:
            avg_revenue = sum(revenue) / len(revenue)
            avg_profit = sum(profit) / len(profit)
            if avg_revenue > 0:
                profit_margin = avg_profit / avg_revenue
                if profit_margin > 0.2:
                    base_score += 10
                elif profit_margin > 0.1:
                    base_score += 5
                elif profit_margin < 0:
                    base_score -= 20
    
    return base_score

# 生成模拟财务数据
import random


def generate_financial_data():
    # 生成12个月的财务数据
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    revenue = []
    profit = []

    # 生成随机收入和利润数据
    base_revenue = 1000000
    for i in range(12):
        # 收入每月增长5-15%
        growth_rate = random.uniform(0.05, 0.15)
        base_revenue = int(base_revenue * (1 + growth_rate))
        revenue.append(base_revenue)

        # 利润为收入的20-30%
        profit_rate = random.uniform(0.2, 0.3)
        profit.append(int(base_revenue * profit_rate))

    return {
        "categories": months,
        "revenue": revenue,
        "profit": profit
    }


# 4. 图表数据API接口
@app.route('/api/chart_data', methods=['POST'])
def get_chart_data():
    """根据用户问题和文件生成图表数据"""
    try:
        user_message = request.form.get('message', '')
        file_path = request.form.get('file_path', '')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                "code": 400,
                "msg": "文件路径无效或文件不存在"
            }), 400
        
        # 调用处理器生成图表数据
        chart_result = processor.generate_chart_data_from_question(file_path, user_message)
        
        if chart_result.get("code") == 200:
            return jsonify({
                "code": 200,
                "msg": "成功获取图表数据",
                "data": chart_result
            })
        else:
            return jsonify({
                "code": 500,
                "msg": chart_result.get("message", "生成图表数据失败")
            }), 500
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"获取图表数据失败：{str(e)}"
        }), 500


# 5. 智能分析接口 - 使用大模型分析对话内容
@app.route('/api/analyze_insight', methods=['POST'])
def analyze_insight():
    """使用大模型分析对话内容，提取关键信息"""
    try:
        analysis_text = request.form.get('analysis_text', '')
        
        if not analysis_text:
            return jsonify({
                "code": 400,
                "msg": "分析内容不能为空"
            }), 400
        
        # 调用大模型进行智能分析
        prompt = f"""请分析以下企业财务分析内容，提取并生成结构化的关键信息：

分析内容：
{analysis_text}

请按以下JSON格式返回分析结果（只返回JSON，不要其他内容）：
{{
    "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
    "key_points": ["要点1", "要点2", "要点3"],
    "risk_alerts": ["风险提示1", "风险提示2"],
    "suggestions": ["建议1", "建议2"],
    "summary": "一句话总结"
}}"""
        
        try:
            response = processor.client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的企业财务分析助手，擅长提取关键信息和生成结构化分析结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            result_text = response.choices[0].message.content
            
            # 尝试解析JSON结果
            import json
            import re
            
            # 清理返回内容，提取JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result_json = json.loads(json_match.group())
                return jsonify({
                    "code": 200,
                    "msg": "分析成功",
                    "data": result_json
                })
            else:
                return jsonify({
                    "code": 200,
                    "msg": "分析成功",
                    "data": {
                        "keywords": ["企业分析"],
                        "key_points": [analysis_text[:100] + "..."],
                        "risk_alerts": [],
                        "suggestions": ["建议关注企业整体运营状况"],
                        "summary": analysis_text[:50] + "..."
                    }
                })
                
        except Exception as e:
            print(f"大模型分析失败: {e}")
            return jsonify({
                "code": 200,
                "msg": "分析成功",
                "data": {
                    "keywords": ["企业分析", "财务数据"],
                    "key_points": [analysis_text[:100] + "..."],
                    "risk_alerts": ["注意成本控制"],
                    "suggestions": ["建议优化资产结构"],
                    "summary": analysis_text[:50] + "..."
                }
            })
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"分析失败：{str(e)}"
        }), 500


#


# 启动服务
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5000)