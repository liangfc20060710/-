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

                health_score = 90
                risk_warning = "无重大风险"
            else:
                # 读取Excel文件
                df = pd.read_excel(file)
                # 打印Excel内容（或者可以在这里处理数据）
                print(df.head())  # 显示前几行

                # 生成分析结果
                analysis_result = "根据Excel文件分析，企业财务状况良好，各项指标均在合理范围内。"
                health_score = 92
                risk_warning = "无重大风险"

        except Exception as e:
            return jsonify({"code": 500, "msg": f"分析失败：{str(e)}"}), 500
    else:
        # 纯消息分析
        try:
            # 生成模拟财务数据用于可视化
            financial_data = generate_financial_data()

            # 根据用户消息生成分析结果
            if user_message:
                if '成本' in user_message:
                    analysis_result = "成本分析显示，原材料成本占比最高，建议优化采购策略降低成本。"
                    health_score = 88
                    risk_warning = "成本控制存在一定风险"
                elif '资产' in user_message:
                    analysis_result = "资产结构分析显示，流动资产占比合理，固定资产投资适中。"
                    health_score = 90
                    risk_warning = "无重大风险"
                elif '利润' in user_message:
                    analysis_result = "利润分析显示，净利润增长率为15%，高于行业平均水平。"
                    health_score = 95
                    risk_warning = "无重大风险"
                else:
                    analysis_result = "根据您的问题，我们分析了企业的整体财务状况，各项指标均表现良好。"
                    health_score = 92
                    risk_warning = "无重大风险"
            else:
                analysis_result = "欢迎使用企业数字大脑智能分析助手，请上传文件或提出具体问题。"
                health_score = 85
                risk_warning = "暂无风险评估"

        except Exception as e:
            return jsonify({"code": 500, "msg": f"分析失败：{str(e)}"}), 500

    return jsonify({
        "code": 200,
        "msg": "分析成功",
        "data": {
            "company_name": company_name,
            "analysis_result": analysis_result,
            "health_score": health_score,
            "risk_warning": risk_warning,
            "financial_data": financial_data
        }
    })


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


#


# 启动服务
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5000)