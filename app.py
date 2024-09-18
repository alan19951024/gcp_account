from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import io
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://gcpaccount.zeabur.app"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_files():
    try:
        data = request.get_json()
        
        file1_content = data['file1'].split(',')[1]  # Remove 'data:filetype;base64,' part
        file2_content = data['file2'].split(',')[1]
        template_content = data['template'].split(',')[1]

        # 解碼 base64
        file1 = io.BytesIO(base64.b64decode(file1_content))
        file2 = io.BytesIO(base64.b64decode(file2_content))
        template = io.BytesIO(base64.b64decode(template_content))
        
        # 使用 pandas 讀取 CSV 格式
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        template_df = pd.read_csv(template)
        
        # 處理檔案邏輯
        now = datetime.now()
        last_month = now - timedelta(days=30)
        invoice_month = last_month.strftime("%Y%m")
        df1.insert(0, 'invoice_month', invoice_month)
        df2.insert(0, 'invoice_month', invoice_month)
        
        df_combined = pd.concat([df1, df2], ignore_index=True)
        
        for i in range(min(len(df_combined.columns), len(template_df.columns))):
            template_df[template_df.columns[i]] = df_combined[df_combined.columns[i]]
        
        output = io.StringIO()
        template_df.to_csv(output, index=False)
        output.seek(0)
        
        result = output.getvalue()
        return jsonify(success=True, result=result)
    
    except Exception as e:
        return jsonify(success=False, message=str(e))

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

