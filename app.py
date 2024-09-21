from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'supersecretkey'

# 確保上傳資料夾存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 主頁路由，顯示上傳表單
@app.route('/')
def index():
    return render_template('upload.html')

# 處理上傳檔案
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.json'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # 讀取 JSON 檔案並印出內容
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summaries = process_data(data)
        
        return render_template('display.html',summaries=summaries)

    flash('Invalid file type. Please upload a .json file.')
    return redirect(request.url)

def process_data(data):
    summaries = []

    title = data.get('JTITLE', '無標題')
    full_text = data.get('JFULL', '')

    cleaned_text = clean_summary_text(full_text)
    summary_sentences = cleaned_text.split("。")[:2]  # 截取前兩個句子
    summary_text = "。".join(summary_sentences) + "..." if len(summary_sentences) > 1 else summary_sentences[0]
        # 在這裡添加你要提取的資訊
    extracted_info = extract_info(full_text)

       # 美化摘要格式
    summary = {
        'title': title,
        'summary_text': summary_text,
        '判決結果': extracted_info['判決結果'],
        '引用法條': extracted_info['引用法條'],
        '賠償金額': extracted_info['賠償金額'],
    }
    summaries.append(summary)
    return summaries

def clean_summary_text(text):
    text = text.strip()  # 去除前後空格
    text = re.sub(r'\s+', ' ', text)  # 替換多個空白為單個空格
    return text


def extract_info(text):
    # 提取判決結果等信息的邏輯
    info = {
        "判決結果": None,
        "引用法條": None,
        "賠償金額": None
    }

    # 檢查判決結果
    if re.search(r"判決結果[:：]?(.*?)[。]", text):
        match = re.search(r"判決結果[:：]?(.*?)[。]", text)
        info["判決結果"] = match.group(1)

    # 檢查賠償金額 (匹配新台幣的金額格式)
    if re.search(r"新台幣[^\d]*(\d+(,\d{3})*(\.\d{1,2})?)元", text):
        match = re.search(r"新台幣[^\d]*(\d+(,\d{3})*(\.\d{1,2})?)元", text)
        info["賠償金額"] = match.group(0)

    # 檢查引用法律條文
    if re.search(r"依據[\u4e00-\u9fa5]+法", text):
        match = re.search(r"依據[\u4e00-\u9fa5]+法", text)
        info["引用法條"] = match.group(0)

    return info

if __name__ == '__main__':
    app.run(debug=True)
