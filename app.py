from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='static', template_folder="templates")

# 啟用 CORS，允許特定來源訪問 '/upload'
CORS(app, resources={r"/*": {"origins": "https://gcpaccount.zeabur.app"}})

# 設定上傳與下載資料夾
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['DOWNLOAD_FOLDER'] = 'download'

# 確保上傳和下載資料夾存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# 測試 POST 路由
@app.route('/test', methods=['POST'])
def test_route():
    return jsonify(success=True, message="POST request successful")

# 首頁路由
@app.route('/')
def index():
    return render_template('index.html')

# 上傳檔案的 API
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file1' not in request.files or 'file2' not in request.files or 'template' not in request.files:
        return jsonify(success=False, message="Missing files")

    file1 = request.files['file1']
    file2 = request.files['file2']
    template = request.files['template']

    if file1.filename == '' or file2.filename == '' or template.filename == '':
        return jsonify(success=False, message="Empty filename")

    # 儲存檔案
    file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
    file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template.filename)

    file1.save(file1_path)
    file2.save(file2_path)
    template.save(template_path)

    try:
        # 處理檔案並返回結果檔案名
        output_filename = process_files(file1_path, file2_path, template_path)
        return jsonify(success=True, filename=output_filename)
    except Exception as e:
        return jsonify(success=False, message=str(e))

# 下載檔案 API
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

# 處理上傳檔案的邏輯
def process_files(df_path, df3_path, template_path):
    df = pd.read_excel(df_path)
    df3 = pd.read_excel(df3_path)

    df.columns = df.iloc[10]
    df = df.iloc[11:].reset_index(drop=True)
    df3.columns = df3.iloc[10]
    df3 = df3.iloc[11:].reset_index(drop=True)

    now = datetime.now()
    last_month = now - timedelta(days=30)
    invoice_month = last_month.strftime("%Y%m")
    df.insert(0, 'invoice_month', invoice_month)
    df3.insert(0, 'invoice_month', invoice_month)

    df_combined = pd.concat([df, df3], ignore_index=True)

    df2 = pd.read_csv(template_path)

    for i in range(min(len(df_combined.columns), len(df2.columns))):
        df2[df2.columns[i]] = df_combined[df_combined.columns[i]]

    output_filename = f'{invoice_month}_partner_discount_monthly_data_bq.csv'
    output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
    df2.to_csv(output_path, index=False)

    return output_filename

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
