from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from executive_team import anaylises
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 导入智能体核心代码
from executive_team import ExecutiveTeam, BusinessContext


#导入pdf和扫描件代码
from extract_pdf import load_documents,build_index,load_index,query_documents

# 初始化Flask app
app = Flask(__name__)

# 基础配置
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# 初始化智能体
team = ExecutiveTeam()

# 工具函数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# 3. 核心接口：上传Excel + 智能分析
@app.route('/api/analyze', methods=['POST'])



def analyze_excel():

    jiegou_data=anaylises()

    # return ('hello world')
    # if 'file' not in request.files:
    #     return jsonify({"code": 400, "msg": "没有上传文件"}), 400

    # file = request.files['file']
    # company_name = request.form.get('company_name', '未命名企业')

    # if file.filename == '':
    #     return jsonify({"code": 400, "msg": "文件名为空"}), 400

    # if not allowed_file(file.filename):
    #     return jsonify({"code": 400, "msg": "只支持xlsx/xls格式的Excel文件"}), 400

    # try:
    #     filename = secure_filename(file.filename)
    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #     file.save(file_path)

    #     df = pd.read_excel(file_path)
    #     excel_data = df.to_dict('records')

    #     context = BusinessContext()
    #     context.company_name = company_name
    #     context.financial_data = excel_data

    #     analysis_result = team.run_analysis(context)

    #     os.remove(file_path)

    #     return jsonify({
    #         "code": 200,
    #         "msg": "分析成功",
    #         "data": {
    #             "company_name": company_name,
    #             "analysis_result": analysis_result,
    #             "health_score": context.health_score,
    #             "risk_warning": context.risk_warning
    #         }
    #     })

    # except Exception as e:
    #     return jsonify({"code": 500, "msg": f"分析失败：{str(e)}"}), 500
    return render_template('gallery.html',
                            chengben_Data=jiegou_data
                            )



#前端将文件通过POST请求上传，后端接收文件
@app.route('/api/analyze', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        # 打印Excel内容（或者可以在这里处理数据）
        print(df.head())  # 显示前几行
        return jsonify({"message": "File uploaded and read successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to read the file: {str(e)}"}), 500

#



# 启动服务
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5000)