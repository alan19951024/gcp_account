from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static', template_folder="templates")

# 啟用 CORS，允許特定來源訪問
CORS(app, resources={r"/*": {"origins": "https://gcpaccount.zeabur.app"}})

# 測試 POST 路由
@app.route('/test', methods=['POST'])
def test_route():
    return jsonify(success=True, message="POST request successful")

# 首頁路由
@app.route('/')
def index():
    return render_template('index.html')

# 接收處理檔案資料的 API
@app.route('/process', methods=['POST'])
def process_data():
    try:
        data = request.get_json()

        # 從前端接收檔案內容
        file1_content = data.get('file1')
        file2_content = data.get('file2')
        template_content = data.get('template')

        if not file1_content or not file2_content or not template_content:
            return jsonify(success=False, message="Missing file content"), 400

        # 處理檔案內容
        output_data = process_files(file1_content, file2_content, template_content)

        return jsonify(success=True, result=output_data)

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

# 處理檔案資料的邏輯
def process_files(file1_content, file2_content, template_content):
    # 將傳遞過來的資料轉換為 DataFrame
    df = pd.read_csv(pd.compat.StringIO(file1_content))
    df3 = pd.read_csv(pd.compat.StringIO(file2_content))

    # 設定欄位名稱
    df.columns = df.iloc[10]
    df = df.iloc[11:].reset_index(drop=True)
    df3.columns = df3.iloc[10]
    df3 = df3.iloc[11:].reset_index(drop=True)

    # 加入 invoice_month 欄位
    now = datetime.now()
    last_month = now - timedelta(days=30)
    invoice_month = last_month.strftime("%Y%m")
    df.insert(0, 'invoice_month', invoice_month)
    df3.insert(0, 'invoice_month', invoice_month)

    # 合併資料
    df_combined = pd.concat([df, df3], ignore_index=True)

    # 讀取模板資料
    df2 = pd.read_csv(pd.compat.StringIO(template_content))

    # 將合併資料寫入模板
    for i in range(min(len(df_combined.columns), len(df2.columns))):
        df2[df2.columns[i]] = df_combined[df_combined.columns[i]]

    # 將結果轉換為 CSV 字串
    result_csv = df2.to_csv(index=False)

    return result_csv

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
