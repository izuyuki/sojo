import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
import json
import plotly.graph_objects as go

# 環境変数の読み込み
load_dotenv()

# Gemini APIの設定
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(pdf_file):
    """PDFからテキストを抽出する関数"""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_document(text):
    """文書を分析する関数"""
    prompt = f"""
    以下の行政文書を分析し、以下の項目について詳細な分析を行ってください：
    1. 対象ペルソナの特定
    2. 促したい行動の特定
    3. 行動プロセスマップの作成
    4. タッチポイントの分析
    5. EASTフレームワークに基づく分析
    6. 改善提案

    文書内容：
    {text}

    分析結果は以下のJSON形式で出力してください：
    {{
        "persona": "対象ペルソナの詳細",
        "target_action": "促したい行動",
        "process_map": [
            {{
                "step": "ステップ名",
                "description": "説明",
                "touchpoint": "タッチポイント"
            }}
        ],
        "east_analysis": {{
            "easy": "Easyの分析",
            "attractive": "Attractiveの分析",
            "social": "Socialの分析",
            "timely": "Timelyの分析"
        }},
        "improvements": [
            "改善提案1",
            "改善提案2"
        ],
        "additional_touchpoints": [
            "追加タッチポイント1",
            "追加タッチポイント2"
        ]
    }}
    """
    
    response = model.generate_content(prompt)
    return json.loads(response.text)

def create_process_map(process_map_data):
    """プロセスマップを可視化する関数"""
    fig = go.Figure()
    
    # ノードの位置を計算
    y_positions = [i for i in range(len(process_map_data))]
    
    # ノードを追加
    for i, step in enumerate(process_map_data):
        fig.add_trace(go.Scatter(
            x=[0],
            y=[y_positions[i]],
            mode='markers+text',
            marker=dict(size=20, color='lightblue'),
            text=[step['step']],
            textposition="middle right",
            name=step['step']
        ))
        
        # 説明を追加
        fig.add_trace(go.Scatter(
            x=[1],
            y=[y_positions[i]],
            mode='text',
            text=[step['description']],
            textposition="middle left",
            showlegend=False
        ))
        
        # タッチポイントを追加
        fig.add_trace(go.Scatter(
            x=[2],
            y=[y_positions[i]],
            mode='text',
            text=[step['touchpoint']],
            textposition="middle left",
            showlegend=False
        ))
    
    # レイアウトの設定
    fig.update_layout(
        title="行動プロセスマップ",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        showlegend=False,
        height=400 + len(process_map_data) * 50
    )
    
    return fig

# Streamlit UI
st.title("行政文書分析ツール")
st.write("PDFファイルをアップロードして、文書の分析を行います。")

uploaded_file = st.file_uploader("PDFファイルをアップロード", type=['pdf'])

if uploaded_file is not None:
    with st.spinner('文書を分析中...'):
        # PDFからテキストを抽出
        text = extract_text_from_pdf(uploaded_file)
        
        # 文書を分析
        analysis_result = analyze_document(text)
        
        # 結果の表示
        st.header("分析結果")
        
        # ペルソナ
        st.subheader("対象ペルソナ")
        st.write(analysis_result['persona'])
        
        # 目標行動
        st.subheader("促したい行動")
        st.write(analysis_result['target_action'])
        
        # プロセスマップ
        st.subheader("行動プロセスマップ")
        fig = create_process_map(analysis_result['process_map'])
        st.plotly_chart(fig)
        
        # EAST分析
        st.subheader("EASTフレームワーク分析")
        east = analysis_result['east_analysis']
        st.write("Easy:", east['easy'])
        st.write("Attractive:", east['attractive'])
        st.write("Social:", east['social'])
        st.write("Timely:", east['timely'])
        
        # 改善提案
        st.subheader("改善提案")
        for improvement in analysis_result['improvements']:
            st.write(f"- {improvement}")
        
        # 追加タッチポイント
        st.subheader("追加タッチポイント")
        for touchpoint in analysis_result['additional_touchpoints']:
            st.write(f"- {touchpoint}") 
