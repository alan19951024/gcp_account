from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='static',template_folder="templates")
CORS(app)  # 啟用所有路徑的 CORS 支持
# 如果只允許特定的路徑和域名:
CORS(app, resources={r"/upload": {"origins": "https://gcpaccount.zeabur.app"}})


app.config['UPLOAD_FOLDER'] = 'upload'
app.config['DOWNLOAD_FOLDER'] = 'download'

# 確保上傳和下載資料夾存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

@app.route('/test', methods=['POST'])
def test_route():
    return jsonify(success=True, message="POST request successful")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file1' not in request.files or 'file2' not in request.files or 'template' not in request.files:
        return jsonify(success=False, message="Missing files")

    file1 = request.files['file1']
    file2 = request.files['file2']
    template = request.files['template']

    if file1.filename == '' or file2.filename == '' or template.filename == '':
        return jsonify(success=False, message="Empty filename")

    file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
    file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template.filename)

    file1.save(file1_path)
    file2.save(file2_path)
    template.save(template_path)

    try:
        output_filename = process_files(file1_path, file2_path, template_path)
        return jsonify(success=True, filename=output_filename)
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

def process_files(df_path, df3_path, template_path):
    # 讀取 Excel 檔案
    df = pd.read_excel(df_path)
    df3 = pd.read_excel(df3_path)

    # 設定欄位名稱
    df.columns = df.iloc[10]
    df = df.iloc[11:].reset_index(drop=True)
    df3.columns = df3.iloc[10]
    df3 = df3.iloc[11:].reset_index(drop=True)

    # 新增 invoice_month 欄位
    now = datetime.now()
    last_month = now - timedelta(days=30)
    invoice_month = last_month.strftime("%Y%m")
    df.insert(0, 'invoice_month', invoice_month)
    df3.insert(0, 'invoice_month', invoice_month)

    # 將 df3 資料插入到 df 資料的最後一列
    df_combined = pd.concat([df, df3], ignore_index=True)

    # 讀取範本 CSV 檔案
    df2 = pd.read_csv(template_path)

    # 將 df_combined 的資料依順序寫入 df2
    for i in range(min(len(df_combined.columns), len(df2.columns))):
        df2[df2.columns[i]] = df_combined[df_combined.columns[i]]

    # 將結果寫入新的 CSV 檔案
    output_filename = f'{invoice_month}_partner_discount_monthly_data_bq.csv'
    output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
    df2.to_csv(output_path, index=False)

    return output_filename

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)
