# ===================== 依赖导入 =====================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List
import os
import base64
from datetime import datetime

# matplotlib非交互式后端配置
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ===================== 全局常量配置 =====================
# 省份名称标准化映射
PROVINCE_STD_MAP = {
    "北京": "北京市", "天津": "天津市", "河北": "河北省", "山西": "山西省",
    "内蒙古": "内蒙古自治区", "内蒙古自治区": "内蒙古自治区",
    "辽宁": "辽宁省", "吉林": "吉林省", "黑龙江": "黑龙江省",
    "上海": "上海市", "江苏": "江苏省", "浙江": "浙江省", "安徽": "安徽省",
    "福建": "福建省", "江西": "江西省", "山东": "山东省", "河南": "河南省",
    "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省",
    "广西": "广西壮族自治区", "广西壮族自治区": "广西壮族自治区",
    "海南": "海南省", "重庆": "重庆市", "四川": "四川省", "贵州": "贵州省",
    "云南": "云南省", "西藏": "西藏自治区", "西藏自治区": "西藏自治区",
    "陕西": "陕西省", "甘肃": "甘肃省", "青海": "青海省",
    "宁夏": "宁夏回族自治区", "宁夏回族自治区": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区", "新疆维吾尔自治区": "新疆维吾尔自治区",
    "香港": "香港特别行政区", "澳门": "澳门特别行政区", "台湾": "台湾省"
}

# 中国省级GeoJSON公开地址
CHINA_GEOJSON_URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"

# matplotlib中文字体兜底
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 统一图表配色序列
CUSTOM_COLORS = ["#1e40af", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#f59e0b", "#fbbf24", "#fcd34d"]

# ===================== 页面全局配置 =====================
st.set_page_config(
    page_title="中国省级数据库2025版 可视化决策平台",
    page_icon="🇨🇳",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://docs.streamlit.io/",
        "Report a bug": "https://github.com/streamlit/streamlit/issues",
        "About": "中国省级数据库2025版 全维度可视化分析与省级发展决策支持平台"
    }
)

# ===================== 全新优化：精美自定义CSS样式 =====================
st.markdown("""
<style>
    /* 全局字体与背景 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', 'Microsoft YaHei', 'SimHei', sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #f1f5f9 0%, #f8fafc 100%);
    }
    
    /* 主标题样式 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 0.2rem 0 0.8rem 0;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    .sub-header {
        font-size: 1.45rem;
        font-weight: 600;
        color: #0f172a;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #3b82f6, #93c5fd, transparent) 1;
        display: inline-block;
    }
    .section-desc {
        color: #475569;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
        line-height: 1.6;
    }
    
    /* 统计卡片：左侧色条+悬浮效果 */
    .stat-card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1.1rem;
        margin: 0.6rem 0;
    }
    .stat-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.1rem;
        box-shadow: 0 2px 12px rgba(30, 64, 175, 0.06);
        text-align: left;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid #3b82f6;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 60px;
        height: 60px;
        background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(20px, -20px);
    }
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(30, 64, 175, 0.12);
    }
    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.4rem;
        position: relative;
        z-index: 1;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* 内容卡片：精致阴影+圆角 */
    .content-card {
        background: white;
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 2px 15px rgba(15, 23, 42, 0.05);
        margin: 0.8rem 0;
        transition: box-shadow 0.3s ease;
        border: 1px solid rgba(226, 232, 240, 0.7);
    }
    .content-card:hover {
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
    }
    .chart-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1rem;
        padding-left: 0.7rem;
        border-left: 3px solid #3b82f6;
        line-height: 1.2;
    }
    
    /* 建议模块优化 */
    .suggestion-box {
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.7rem 0;
        border-left: 4px solid;
        background: #f8fafc;
    }
    .suggestion-advantage {
        background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);
        border-color: #16a34a;
    }
    .suggestion-weakness {
        background: linear-gradient(90deg, #fef2f2 0%, #ffffff 100%);
        border-color: #dc2626;
    }
    .suggestion-trend {
        background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
        border-color: #2563eb;
    }
    .suggestion-conclusion {
        background: linear-gradient(90deg, #faf5ff 0%, #ffffff 100%);
        border-color: #9333ea;
    }
    .suggestion-title {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        color: #0f172a;
    }
    .suggestion-text {
        color: #334155;
        line-height: 1.7;
        font-size: 0.93rem;
    }
    .data-basis {
        color: #64748b;
        font-size: 0.82rem;
        margin-top: 0.4rem;
        font-style: italic;
    }
    
    /* 侧边栏美化 */
    .stSidebar {
        background: #ffffff;
        box-shadow: 4px 0 20px rgba(15, 23, 42, 0.05);
        border-right: 1px solid #e2e8f0;
    }
    .stSidebar [data-testid="stMarkdownContainer"] h2 {
        color: #0f172a;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
    }
    .stSidebar [data-testid="stMarkdownContainer"] h4 {
        color: #1e3a8a;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    /* 按钮样式统一 */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #3b82f6;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transform: translateY(-1px);
    }
    
    /* 展开器样式 */
    .streamlit-expanderHeader {
        font-weight: 500;
        color: #0f172a;
        background: #f8fafc;
        border-radius: 8px;
    }
    .streamlit-expanderContent {
        background: white;
        border-radius: 0 0 8px 8px;
    }
    
    /* 页脚 */
    .footer {
        text-align: center;
        margin-top: 2.5rem;
        padding: 1.5rem 0;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        font-size: 0.85rem;
        line-height: 1.8;
    }
    
    /* 加载动画 */
    .stSpinner > div {
        border-color: #3b82f6;
        border-top-color: transparent;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 2.5rem;
        font-weight: 500;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #1e40af;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* 下载按钮区域 */
    .download-section {
        background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #bfdbfe;
    }
</style>
""", unsafe_allow_html=True)

# ===================== 核心工具函数 =====================
def generate_word_cloud(freq_dict: Dict[str, float], title: str = ""):
    """生成词云图，异常兜底"""
    if not freq_dict:
        return None
    try:
        wc = WordCloud(
            width=1000, height=450, background_color='white',
            colormap='Blues', max_words=60, prefer_horizontal=0.7,
            font_path=None
        )
        wc.generate_from_frequencies(freq_dict)
        fig, ax = plt.subplots(figsize=(11, 4.8))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        if title:
            ax.set_title(title, fontsize=14, pad=10, color='#0f172a')
        plt.tight_layout()
        return fig
    except Exception:
        return None

def safe_cagr(start_val: float, end_val: float, years: int) -> float:
    """安全计算复合增长率"""
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return 0.0
    try:
        return (end_val / start_val) ** (1 / years) - 1
    except:
        return 0.0

def generate_html_report(analysis_mode, selected_category, selected_years, selected_provinces, 
                        selected_metric, selected_metrics, df_filtered, df_full, metric_unit, 
                        metric_desc, latest_year, avg_val=None, national_avg=None, max_val=None, 
                        cv_val=None, total_cagr=None, detail_list=None, above_avg_count=None):
    """生成精美的HTML格式分析报告"""
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 构建HTML头部样式
    html_head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中国省级数据库2025版 - 分析报告</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(180deg, #f1f5f9 0%, #f8fafc 100%);
            color: #0f172a;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .header {{
            text-align: center;
            padding: 2.5rem 0;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #0ea5e9 100%);
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(30, 58, 138, 0.2);
        }}
        .header h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1rem; opacity: 0.9; }}
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .meta-card {{
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid #3b82f6;
        }}
        .meta-label {{ font-size: 0.85rem; color: #64748b; margin-bottom: 0.3rem; }}
        .meta-value {{ font-size: 1.1rem; font-weight: 600; color: #1e3a8a; }}
        .section {{
            background: white;
            border-radius: 14px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 15px rgba(15, 23, 42, 0.05);
            border: 1px solid rgba(226, 232, 240, 0.7);
        }}
        .section h2 {{
            font-size: 1.3rem;
            color: #0f172a;
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid transparent;
            border-image: linear-gradient(90deg, #3b82f6, #93c5fd, transparent) 1;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            padding: 1.2rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #dbeafe;
        }}
        .stat-box .number {{ font-size: 1.6rem; font-weight: 700; color: #1e40af; }}
        .stat-box .label {{ font-size: 0.85rem; color: #64748b; margin-top: 0.3rem; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 0.8rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            font-weight: 600;
        }}
        tr:hover {{ background: #f8fafc; }}
        .rank-1 {{ background: linear-gradient(90deg, #fef3c7 0%, transparent 100%); }}
        .rank-2 {{ background: linear-gradient(90deg, #f3f4f6 0%, transparent 100%); }}
        .rank-3 {{ background: linear-gradient(90deg, #fff7ed 0%, transparent 100%); }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .suggestion {{
            padding: 1rem 1.2rem;
            border-radius: 8px;
            margin: 0.6rem 0;
            border-left: 4px solid;
        }}
        .sg-advantage {{ background: #f0fdf4; border-color: #16a34a; }}
        .sg-weakness {{ background: #fef2f2; border-color: #dc2626; }}
        .sg-trend {{ background: #eff6ff; border-color: #2563eb; }}
        .sg-conclusion {{ background: #faf5ff; border-color: #9333ea; }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.85rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }}
        .highlight {{ color: #1e40af; font-weight: 600; }}
        @media print {{
            body {{ background: white; }}
            .section {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🇨🇳 中国省级数据库2025版</h1>
            <p>可视化决策支持平台 - 数据分析报告</p>
        </div>
        
        <div class="meta-info">
            <div class="meta-card">
                <div class="meta-label">分析模式</div>
                <div class="meta-value">{"省际对比分析" if "省际" in analysis_mode else "单省深度分析"}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">指标大类</div>
                <div class="meta-value">{selected_category}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">时间区间</div>
                <div class="meta-value">{selected_years[0]} - {selected_years[1]}年</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">覆盖省份</div>
                <div class="meta-value">{len(selected_provinces)}个</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">生成时间</div>
                <div class="meta-value">{now_str}</div>
            </div>
        </div>
"""
    
    html_body = ""
    
    if "省际" in analysis_mode:
        # 省际对比分析报告
        df_latest = df_filtered[df_filtered["年份"] == latest_year]
        df_latest_sorted = df_latest.sort_values("指标值", ascending=False).reset_index(drop=True)
        
        html_body += f"""
        <div class="section">
            <h2>📊 核心统计摘要</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">{avg_val:,.2f}</div>
                    <div class="label">省份均值 ({metric_unit})</div>
                </div>
                <div class="stat-box">
                    <div class="number">{national_avg:,.2f}</div>
                    <div class="label">全国均值 ({metric_unit})</div>
                </div>
                <div class="stat-box">
                    <div class="number">{max_val:,.2f}</div>
                    <div class="label">最高值 ({metric_unit})</div>
                </div>
                <div class="stat-box">
                    <div class="number">{cv_val:.1%}</div>
                    <div class="label">省际离散度</div>
                </div>
                <div class="stat-box">
                    <div class="number">{total_cagr:.2%}</div>
                    <div class="label">整体年均增速</div>
                </div>
                <div class="stat-box">
                    <div class="number">{selected_years[1]-selected_years[0]+1}</div>
                    <div class="label">分析年度跨度</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 省份排名 ({latest_year}年)</h2>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>省份</th>
                        <th>指标值 ({metric_unit})</th>
                        <th>相对全国均值</th>
                        <th>发展梯队</th>
                    </tr>
                </thead>
                <tbody>
"""
        total_prov_count = df_full[df_full["年份"] == latest_year]["地区"].nunique()
        for i, row in df_latest_sorted.iterrows():
            rank = i + 1
            prov = row["地区"]
            val = row["指标值"]
            vs_nat = val / national_avg if national_avg else 0
            rank_pct = rank / total_prov_count
            
            if rank_pct <= 0.25:
                tier = "第一梯队"
                tier_class = "badge-success"
            elif rank_pct <= 0.5:
                tier = "第二梯队"
                tier_class = "badge-warning"
            elif rank_pct <= 0.75:
                tier = "第三梯队"
                tier_class = "badge-warning"
            else:
                tier = "第四梯队"
                tier_class = "badge-danger"
            
            rank_class = ""
            if rank == 1: rank_class = "rank-1"
            elif rank == 2: rank_class = "rank-2"
            elif rank == 3: rank_class = "rank-3"
            
            html_body += f"""
                    <tr class="{rank_class}">
                        <td><strong>#{rank}</strong></td>
                        <td>{prov}</td>
                        <td>{val:,.2f}</td>
                        <td>{vs_nat:.1%}</td>
                        <td><span class="badge {tier_class}">{tier}</span></td>
                    </tr>
"""
        
        html_body += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>💡 分省诊断与发展建议</h2>
"""
        for i, row in df_latest_sorted.head(10).iterrows():
            rank = i + 1
            prov = row["地区"]
            val = row["指标值"]
            vs_nat = val / national_avg if national_avg else 0
            
            prov_data = df_filtered[df_filtered["地区"] == prov].sort_values("年份")
            if len(prov_data) >= 2:
                s_val = prov_data.iloc[0]["指标值"]
                e_val = prov_data.iloc[-1]["指标值"]
                span = prov_data.iloc[-1]["年份"] - prov_data.iloc[0]["年份"]
                cagr = safe_cagr(s_val, e_val, span)
            else:
                cagr = 0
            
            suggestions = []
            if vs_nat < 0.8:
                suggestions.append("<strong>补短板</strong>：当前指标仅为全国均值的{:.0%}，需加大核心要素投入".format(vs_nat))
            if cagr < 0.03:
                suggestions.append("<strong>增动能</strong>：增长速度偏低，需培育新增长引擎")
            if rank <= total_prov_count * 0.25:
                suggestions.append("<strong>固优势</strong>：保持全国领先地位，发挥示范引领作用")
            elif rank <= total_prov_count * 0.5:
                suggestions.append("<strong>促提升</strong>：向第一梯队省份对标学习，突破瓶颈制约")
            suggestions.append("<strong>区域协同</strong>：加强与周边省份的产业协作与要素流动")
            
            html_body += f"""
            <div style="margin: 1rem 0; padding: 1rem; background: #f8fafc; border-radius: 8px;">
                <h4 style="color: #1e40af; margin-bottom: 0.5rem;">📍 {prov} | 全国第{rank}名</h4>
                <p>指标值：<span class="highlight">{val:,.2f} {metric_unit}</span> | 
                   相对全国均值：<span class="highlight">{vs_nat:.1%}</span> | 
                   年均增速：<span class="highlight">{cagr:.2%}</span></p>
                <ul style="margin-top: 0.5rem; padding-left: 1.2rem;">
"""
            for s in suggestions:
                html_body += f"                    <li>{s}</li>\n"
            html_body += "                </ul>\n            </div>\n"
        
        html_body += "</div>"
    else:
        # 单省深度分析报告
        prov_name = selected_provinces[0]
        
        html_body += f"""
        <div class="section">
            <h2>📊 综合发展概览 - {prov_name}</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">{len(selected_metrics)}</div>
                    <div class="label">分析指标数</div>
                </div>
                <div class="stat-box">
                    <div class="number">{above_avg_count}</div>
                    <div class="label">领先全国指标数</div>
                </div>
                <div class="stat-box">
                    <div class="number">{above_avg_count/len(selected_metrics):.1%}</div>
                    <div class="label">指标领先占比</div>
                </div>
                <div class="stat-box">
                    <div class="number">{latest_year}</div>
                    <div class="label">最新数据年份</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 分指标详情对比</h2>
            <table>
                <thead>
                    <tr>
                        <th>指标名称</th>
                        <th>{prov_name}值</th>
                        <th>全国均值</th>
                        <th>单位</th>
                        <th>相对水平</th>
                        <th>年均增速</th>
                        <th>发展状态</th>
                    </tr>
                </thead>
                <tbody>
"""
        for d in detail_list:
            status_class = "badge-success" if "领先" in d["发展状态"] else "badge-warning" if "持平" in d["发展状态"] else "badge-danger"
            html_body += f"""
                    <tr>
                        <td><strong>{d['指标名称']}</strong></td>
                        <td>{d[f'{prov_name}值']}</td>
                        <td>{d['全国均值']}</td>
                        <td>{d['单位']}</td>
                        <td>{d['相对水平']}</td>
                        <td>{d['年均增速']}</td>
                        <td><span class="badge {status_class}">{d['发展状态']}</span></td>
                    </tr>
"""
        
        html_body += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>💡 综合发展建议</h2>
"""
        adv_metrics = [d["指标名称"] for d in detail_list if "领先" in d["发展状态"]]
        weak_metrics = [d["指标名称"] for d in detail_list if "落后" in d["发展状态"]]
        
        html_body += f"""
            <div class="suggestion sg-conclusion">
                <strong>综合评价：</strong>本次分析的 <span class="highlight">{len(selected_metrics)}个指标</span> 中，
                <span style="color:#16a34a;"><strong>领先指标 {len(adv_metrics)} 个</strong></span>，
                <span style="color:#dc2626;"><strong>落后指标 {len(weak_metrics)} 个</strong></span>。
            </div>
            
            <div class="suggestion sg-advantage">
                <strong>1. 巩固优势领域</strong><br>
                {f"持续强化 <strong>{', '.join(adv_metrics)}</strong> 等领先指标的竞争优势，发挥辐射带动作用。" if adv_metrics else "暂无显著领先指标，建议优先培育1-2个核心优势领域。"}
            </div>
            
            <div class="suggestion sg-weakness">
                <strong>2. 补齐短板弱项</strong><br>
                {f"重点补齐 <strong>{', '.join(weak_metrics)}</strong> 等短板指标，对标全国先进省份，制定专项提升方案。" if weak_metrics else "无明显短板指标，整体发展较为均衡，重点在于提质增效。"}
            </div>
            
            <div class="suggestion sg-trend">
                <strong>3. 区域协同发展</strong><br>
                积极融入国家区域重大战略，加强与周边省份的产业协作、人才交流和要素流动，通过区域联动实现优势互补。
            </div>
        </div>
"""
    
    html_foot = f"""
        <div class="footer">
            <p>数据来源：中国省级数据库2025版 | 技术架构：Streamlit + Plotly + Pandas</p>
            <p>© 2025 中国省级数据库可视化分析与决策支持平台 | 生成时间：{now_str}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_head + html_body + html_foot

# ===================== 数据加载与标准化 =====================
@st.cache_data(ttl=3600, show_spinner="正在加载全量省级数据库，请稍候...")
def load_and_standardize_data(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        st.error(f"❌ 数据文件未找到，请检查路径：{file_path}\n\n请确保Excel文件与app.py在同一目录。")
        st.stop()
    
    try:
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        
        if "原始数据-长面板" in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name="原始数据-长面板", engine='openpyxl')
            
            year_cols = [col for col in df.columns if str(col).isdigit() and 1990 <= int(col) <= 2030]
            dim_cols = []
            for col in ["行政区划代码", "地区", "所属地域", "一级标题", "指标名称", "单位", "指标解释"]:
                if col in df.columns:
                    dim_cols.append(col)
            
            df_long = df.melt(
                id_vars=dim_cols, value_vars=year_cols,
                var_name="年份", value_name="指标值"
            )
            df_long["年份"] = df_long["年份"].astype(int)
            df_long["指标值"] = pd.to_numeric(df_long["指标值"], errors='coerce')
            df_long = df_long.dropna(subset=["指标值"]).reset_index(drop=True)
            
            df_long["地区_标准"] = df_long["地区"].map(PROVINCE_STD_MAP).fillna(df_long["地区"])
            
            if "一级标题" not in df_long.columns:
                df_long["一级标题"] = "综合指标"
            if "所属地域" not in df_long.columns:
                df_long["所属地域"] = "其他"
            if "单位" not in df_long.columns:
                df_long["单位"] = ""
            if "指标解释" not in df_long.columns:
                df_long["指标解释"] = "暂无说明"
            
            return df_long
        else:
            st.error("❌ Excel中未找到「原始数据-长面板」工作表，请检查文件结构")
            st.stop()
    except Exception as e:
        st.error(f"❌ 数据加载失败：{str(e)}\n\n请检查Excel文件是否损坏或格式是否正确")
        st.stop()

# ===================== 主程序入口 =====================
def main():
    # 自动查找数据文件
    FILE_PATH = None
    possible_paths = [
        "./中国省级数据库2025版.xlsx",
        "中国省级数据库2025版.xlsx",
        "/workspace/.uploads/d1cfc993-9057-4c1d-984b-afa52c0bed59_中国省级数据库2025版.xlsx"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            FILE_PATH = p
            break
    
    if FILE_PATH is None:
        st.error("❌ 未找到数据文件「中国省级数据库2025版.xlsx」，请确保文件与程序在同一目录")
        st.stop()
    
    df_full = load_and_standardize_data(FILE_PATH)

    # ---------- 侧边栏筛选系统 ----------
    st.sidebar.markdown("<h2>🔍 分析设置</h2>", unsafe_allow_html=True)

    analysis_mode = st.sidebar.radio(
        "分析模式",
        options=["🌍 省际对比分析", "📍 单省深度分析"],
        index=0,
        help="省际对比：多省份横向对比同一指标；单省深度：单个省份多指标纵向剖析"
    )
    st.sidebar.divider()

    # 省份选择
    st.sidebar.markdown("#### 🗺️ 省份选择")
    all_provinces = sorted(df_full["地区"].dropna().unique())

    if analysis_mode == "🌍 省际对比分析":
        col_btn1, col_btn2 = st.sidebar.columns(2)
        with col_btn1:
            if st.button("全选", use_container_width=True):
                st.session_state.sel_provs = all_provinces
        with col_btn2:
            if st.button("清空", use_container_width=True):
                st.session_state.sel_provs = []
        
        selected_provinces = st.sidebar.multiselect(
            "选择对比省份",
            options=all_provinces,
            default=all_provinces[:8],
            key="sel_provs",
            help="可多选，建议8-15个省份保证图表可读性"
        )
    else:
        selected_province = st.sidebar.selectbox(
            "选择分析省份",
            options=all_provinces,
            index=0
        )
        selected_provinces = [selected_province]

    # 年份范围
    st.sidebar.markdown("#### 📅 时间区间")
    min_year = int(df_full["年份"].min())
    max_year = int(df_full["年份"].max())
    selected_years = st.sidebar.slider(
        "选择年份范围",
        min_value=min_year, max_value=max_year,
        value=(2012, max_year), step=1
    )
    st.sidebar.divider()

    # 指标选择
    st.sidebar.markdown("#### 📊 指标选择")
    all_categories = sorted(df_full["一级标题"].dropna().unique())
    selected_category = st.sidebar.selectbox("指标大类", options=all_categories, index=0)
    df_category = df_full[df_full["一级标题"] == selected_category]
    all_metrics = sorted(df_category["指标名称"].dropna().unique())

    if analysis_mode == "🌍 省际对比分析":
        selected_metric = st.sidebar.selectbox("分析指标", options=all_metrics, index=0)
        selected_metrics = [selected_metric]
    else:
        selected_metrics = st.sidebar.multiselect(
            "分析指标（最多8个）",
            options=all_metrics,
            default=all_metrics[:4]
        )
        if len(selected_metrics) > 8:
            st.sidebar.warning("最多选择8个指标，已自动截取前8个")
            selected_metrics = selected_metrics[:8]
        selected_metric = selected_metrics[0] if selected_metrics else ""

    # 可视化配置
    st.sidebar.markdown("#### ⚙️ 显示设置")
    with st.sidebar.expander("图表配置", expanded=False):
        show_data_labels = st.checkbox("显示数据标签", value=False)
        chart_height = st.slider("图表高度", min_value=350, max_value=650, value=460, step=50)
        top_n = st.slider("排名展示数量", min_value=3, max_value=15, value=10, step=1)

    # ---------- 数据过滤与前置校验 ----------
    df_filtered = df_full[
        (df_full["地区"].isin(selected_provinces)) &
        (df_full["年份"] >= selected_years[0]) &
        (df_full["年份"] <= selected_years[1]) &
        (df_full["指标名称"].isin(selected_metrics))
    ].copy()

    if len(df_filtered) == 0 or len(selected_provinces) == 0 or len(selected_metrics) == 0:
        st.error("⚠️ 当前筛选条件下无有效数据，请调整省份、指标或年份范围后重试")
        st.stop()

    # 通用信息
    latest_year = df_filtered["年份"].max()
    earliest_year = df_filtered["年份"].min()
    metric_info = df_full[df_full["指标名称"] == selected_metric].iloc[0] if selected_metric else None
    metric_unit = metric_info["单位"] if metric_info is not None and pd.notna(metric_info["单位"]) else ""
    metric_desc = metric_info["指标解释"] if metric_info is not None and pd.notna(metric_info["指标解释"]) else "暂无说明"

    # ---------- 页面头部 ----------
    st.markdown('<h1 class="main-header">中国省级数据库2025版 可视化决策平台</h1>', unsafe_allow_html=True)
    mode_desc = "省际横向对比分析" if analysis_mode == "🌍 省际对比分析" else f"{selected_provinces[0]} 多维度深度分析"
    st.markdown(f"""
    <div class="section-desc" style="text-align: center; font-size: 1rem;">
        🎯 当前模式：<b>{mode_desc}</b> &nbsp;|&nbsp; 
        📂 指标大类：<b>{selected_category}</b> &nbsp;|&nbsp; 
        📅 时间区间：<b>{selected_years[0]} - {selected_years[1]}年</b> &nbsp;|&nbsp; 
        📍 覆盖省份：<b>{len(selected_provinces)}个</b>
    </div>
    """, unsafe_allow_html=True)
    if analysis_mode == "🌍 省际对比分析":
        st.markdown(f'<div class="section-desc" style="text-align: center;">💡 指标说明：{selected_metric}（{metric_unit}）- {metric_desc}</div>', unsafe_allow_html=True)

    # ==================================================================
    # 模式一：省际对比分析
    # ==================================================================
    if analysis_mode == "🌍 省际对比分析":
        df_latest = df_filtered[df_filtered["年份"] == latest_year]
        national_avg = df_full[(df_full["指标名称"] == selected_metric) & (df_full["年份"] == latest_year)]["指标值"].mean()
        df_earliest = df_filtered[df_filtered["年份"] == selected_years[0]]
        year_span = latest_year - selected_years[0]
        total_cagr = safe_cagr(df_earliest["指标值"].sum(), df_latest["指标值"].sum(), year_span)
        avg_val = df_latest["指标值"].mean()
        max_val = df_latest["指标值"].max()
        std_val = df_latest["指标值"].std()
        cv_val = std_val / avg_val if avg_val != 0 else 0

        # ---- 核心统计看板 ----
        st.markdown('<h2 class="sub-header">📊 核心指标概览</h2>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stat-card-container">
            <div class="stat-card"><div class="stat-value">{avg_val:,.2f}</div><div class="stat-label">省份均值（{metric_unit}）</div></div>
            <div class="stat-card"><div class="stat-value">{national_avg:,.2f}</div><div class="stat-label">全国均值（{metric_unit}）</div></div>
            <div class="stat-card"><div class="stat-value">{max_val:,.2f}</div><div class="stat-label">最高值（{metric_unit}）</div></div>
            <div class="stat-card"><div class="stat-value">{cv_val:.1%}</div><div class="stat-label">省际离散度</div></div>
            <div class="stat-card"><div class="stat-value">{total_cagr:.2%}</div><div class="stat-label">整体年均增速</div></div>
            <div class="stat-card"><div class="stat-value">{year_span+1}</div><div class="stat-label">分析年度跨度</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ---- 第一行：地图 + 排名 ----
        st.markdown('<h2 class="sub-header">🗺️ 空间分布与排名</h2>', unsafe_allow_html=True)
        col_map, col_rank = st.columns([1.2, 1])

        with col_map:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">{latest_year}年全国省级热力分布图</div>', unsafe_allow_html=True)
            try:
                df_map = df_latest.groupby("地区_标准")["指标值"].mean().reset_index()
                fig_map = px.choropleth(
                    df_map,
                    geojson=CHINA_GEOJSON_URL,
                    locations="地区_标准",
                    featureidkey="properties.name",
                    color="指标值",
                    color_continuous_scale="Blues",
                    labels={"指标值": f"{selected_metric}"},
                    template="plotly_white",
                    hover_data={"地区_标准": False, "指标值": ":,.2f"}
                )
                fig_map.update_geos(
                    visible=False, scope="asia",
                    center={"lat": 35, "lon": 105},
                    projection_scale=2.2,
                    showcountries=False, showland=False
                )
                fig_map.update_layout(
                    height=chart_height + 60,
                    margin=dict(l=0, r=0, t=0, b=0),
                    coloraxis_colorbar=dict(title="", thickness=15, len=0.7)
                )
                st.plotly_chart(fig_map, use_container_width=True)
            except Exception:
                st.warning("⚠️ 地图资源加载失败，已降级为条形图展示")
                df_rank_bar = df_latest.sort_values("指标值", ascending=True).tail(top_n)
                fig_fallback = px.bar(
                    df_rank_bar, y="地区", x="指标值", orientation="h",
                    color="指标值", color_continuous_scale="Blues", template="plotly_white"
                )
                st.plotly_chart(fig_fallback, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_rank:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">省份排名 Top {top_n}（{latest_year}年）</div>', unsafe_allow_html=True)
            df_rank = df_latest.sort_values("指标值", ascending=False).head(top_n).sort_values("指标值", ascending=True)
            fig_rank = px.bar(
                df_rank, y="地区", x="指标值", orientation="h",
                color="指标值", color_continuous_scale="Blues",
                text_auto=".2f" if show_data_labels else False,
                labels={"指标值": metric_unit, "地区": ""},
                template="plotly_white"
            )
            fig_rank.update_layout(
                height=chart_height + 60, showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10), xaxis_title=""
            )
            st.plotly_chart(fig_rank, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第二行：趋势+增速组合子图 ----
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 历年趋势与同比增速组合图</div>', unsafe_allow_html=True)
        
        fig_sub1 = make_subplots(
            rows=1, cols=2,
            subplot_titles=("各省份历年变化趋势", "整体年度同比增速"),
            column_widths=[0.65, 0.35]
        )

        for prov in selected_provinces:
            prov_data = df_filtered[df_filtered["地区"] == prov].sort_values("年份")
            fig_sub1.add_trace(
                go.Scatter(x=prov_data["年份"], y=prov_data["指标值"], name=prov, mode="lines+markers", line=dict(width=2)),
                row=1, col=1
            )

        df_yearly = df_filtered.groupby("年份")["指标值"].mean().reset_index()
        df_yearly["增速%"] = df_yearly["指标值"].pct_change() * 100
        df_yearly = df_yearly.dropna()
        fig_sub1.add_trace(
            go.Bar(x=df_yearly["年份"], y=df_yearly["增速%"], name="增速%", marker_color="#3b82f6", marker_line_width=0),
            row=1, col=2
        )
        fig_sub1.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)

        fig_sub1.update_layout(
            height=chart_height, template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=30, b=10),
            colorway=CUSTOM_COLORS
        )
        fig_sub1.update_yaxes(title_text=f"{selected_metric} ({metric_unit})", row=1, col=1)
        fig_sub1.update_yaxes(title_text="同比增速 (%)", row=1, col=2)
        st.plotly_chart(fig_sub1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第三行：箱线图 + 饼图 + 热力矩阵 ----
        col_box, col_pie, col_heat = st.columns([1, 1, 1.2])

        with col_box:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📦 分地域分布箱线图</div>', unsafe_allow_html=True)
            fig_box = px.box(
                df_filtered, x="所属地域", y="指标值", color="所属地域",
                points="outliers", template="plotly_white",
                labels={"指标值": metric_unit, "所属地域": ""},
                color_discrete_sequence=CUSTOM_COLORS
            )
            fig_box.update_layout(height=chart_height, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_pie:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">🥧 {latest_year}年省份占比</div>', unsafe_allow_html=True)
            df_pie = df_latest.sort_values("指标值", ascending=False).head(10)
            fig_pie = px.pie(
                df_pie, values="指标值", names="地区", hole=0.4,
                template="plotly_white",
                color_discrete_sequence=CUSTOM_COLORS
            )
            fig_pie.update_traces(textinfo="percent", textfont_size=11)
            fig_pie.update_layout(
                height=chart_height,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font_size=10),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_heat:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔥 省份-年份热力矩阵</div>', unsafe_allow_html=True)
            df_heat = df_filtered.pivot_table(index="地区", columns="年份", values="指标值", aggfunc="mean")
            fig_heat = px.imshow(
                df_heat, color_continuous_scale="RdBu_r",
                template="plotly_white", text_auto=".1f" if show_data_labels else False
            )
            fig_heat.update_layout(height=chart_height, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_heat, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第四行：词云图 ----
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-title">☁️ {latest_year}年省份规模词云</div>', unsafe_allow_html=True)
        freq_dict = dict(zip(df_latest["地区"], df_latest["指标值"].abs()))
        wc_fig = generate_word_cloud(freq_dict)
        if wc_fig:
            st.pyplot(wc_fig, use_container_width=True)
        else:
            st.info("词云生成暂不可用，可查看上方图表获取数据")
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- 省级诊断建议 ----
        st.markdown('<h2 class="sub-header">💡 分省诊断与发展建议</h2>', unsafe_allow_html=True)
        df_latest_sorted = df_latest.sort_values("指标值", ascending=False).reset_index(drop=True)
        total_prov_count = df_full[df_full["年份"] == latest_year]["地区"].nunique()

        for idx, row in df_latest_sorted.iterrows():
            prov = row["地区"]
            val = row["指标值"]
            rank = idx + 1
            vs_nat = val / national_avg if national_avg else 0

            prov_data = df_filtered[df_filtered["地区"] == prov].sort_values("年份")
            if len(prov_data) >= 2:
                s_val = prov_data.iloc[0]["指标值"]
                e_val = prov_data.iloc[-1]["指标值"]
                span = prov_data.iloc[-1]["年份"] - prov_data.iloc[0]["年份"]
                cagr = safe_cagr(s_val, e_val, span)
            else:
                cagr = 0

            rank_pct = rank / total_prov_count
            if rank_pct <= 0.25:
                tier, tier_cls = "第一梯队（全国领先）", "suggestion-advantage"
            elif rank_pct <= 0.5:
                tier, tier_cls = "第二梯队（中上游）", "suggestion-trend"
            elif rank_pct <= 0.75:
                tier, tier_cls = "第三梯队（中下游）", "suggestion-weakness"
            else:
                tier, tier_cls = "第四梯队（追赶型）", "suggestion-weakness"

            with st.expander(f"📍 {prov} | 全国第{rank}名 | {val:,.2f} {metric_unit}", expanded=(idx < 3)):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="suggestion-box {tier_cls}">
                        <div class="suggestion-title">综合梯队定位</div>
                        <div class="suggestion-text">处于全国<b>{tier}</b></div>
                        <div class="data-basis">全国排名第{rank}位 / 共{total_prov_count}个省份</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="suggestion-box suggestion-conclusion">
                        <div class="suggestion-title">相对全国水平</div>
                        <div class="suggestion-text">为全国均值的<b>{vs_nat:.1%}</b></div>
                        <div class="data-basis">全国均值 {national_avg:,.2f} {metric_unit}</div>
                    </div>
                    """, unsafe_allow_html=True)

                col3, col4 = st.columns(2)
                with col3:
                    st.markdown(f"""
                    <div class="suggestion-box suggestion-trend">
                        <div class="suggestion-title">年均复合增速</div>
                        <div class="suggestion-text"><b>{cagr:.2%}</b></div>
                        <div class="data-basis">{selected_years[0]}-{selected_years[1]}年</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    bench_prov = df_latest_sorted.iloc[idx-1]["地区"] if idx > 0 else "暂无"
                    bench_val = df_latest_sorted.iloc[idx-1]["指标值"] if idx > 0 else 0
                    gap = (bench_val - val) / val if val > 0 and idx > 0 else 0
                    st.markdown(f"""
                    <div class="suggestion-box" style="background:#f8fafc; border-color:#475569;">
                        <div class="suggestion-title">对标追赶对象</div>
                        <div class="suggestion-text"><b>{bench_prov}</b></div>
                        <div class="data-basis">差距 {gap:.1%}，目标值 {bench_val:,.2f} {metric_unit}</div>
                    </div>
                    """, unsafe_allow_html=True)

                suggestions = []
                if vs_nat < 0.8:
                    suggestions.append(f"**补短板**：当前指标仅为全国均值的{vs_nat:.0%}，需加大核心要素投入，重点提升总量规模，力争3-5年达到全国平均水平")
                if cagr < 0.03:
                    suggestions.append("**增动能**：增长速度偏低，需培育新增长引擎，优化产业结构，提升发展内生动力")
                if rank_pct <= 0.25:
                    suggestions.append("**固优势**：保持全国领先地位，发挥示范引领作用，探索高质量发展新路径，形成可复制经验")
                if 0.25 < rank_pct <= 0.5:
                    suggestions.append("**促提升**：巩固现有基础，向第一梯队省份对标学习，突破瓶颈制约，争取位次前移")
                suggestions.append("**区域协同**：加强与周边省份的产业协作与要素流动，融入区域发展大局，实现协同增长")

                st.markdown("##### 📌 针对性发展建议")
                for s in suggestions:
                    st.markdown(f"- {s}")

    # ==================================================================
    # 模式二：单省深度分析
    # ==================================================================
    else:
        prov_name = selected_provinces[0]
        df_prov = df_filtered[df_filtered["地区"] == prov_name].copy()
        df_prov_latest = df_prov[df_prov["年份"] == latest_year]

        above_avg_count = 0
        for m in selected_metrics:
            m_val = df_prov_latest[df_prov_latest["指标名称"] == m]["指标值"].mean()
            nat_avg = df_full[(df_full["指标名称"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
            if pd.notna(m_val) and pd.notna(nat_avg) and m_val > nat_avg:
                above_avg_count += 1

        st.markdown('<h2 class="sub-header">📊 综合发展概览</h2>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stat-card-container">
            <div class="stat-card"><div class="stat-value">{len(selected_metrics)}</div><div class="stat-label">分析指标数</div></div>
            <div class="stat-card"><div class="stat-value">{above_avg_count}</div><div class="stat-label">领先全国指标数</div></div>
            <div class="stat-card"><div class="stat-value">{above_avg_count/len(selected_metrics):.1%}</div><div class="stat-label">指标领先占比</div></div>
            <div class="stat-card"><div class="stat-value">{latest_year}</div><div class="stat-label">最新数据年份</div></div>
            <div class="stat-card"><div class="stat-value">{selected_years[1]-selected_years[0]+1}</div><div class="stat-label">分析年度跨度</div></div>
            <div class="stat-card"><div class="stat-value">{selected_category}</div><div class="stat-label">指标大类</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ---- 第一行：雷达图 + 词云 ----
        st.markdown('<h2 class="sub-header">🕸️ 多维度结构分析</h2>', unsafe_allow_html=True)
        col_radar, col_wc = st.columns(2)

        with col_radar:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">{latest_year}年指标雷达对比（vs全国均值）</div>', unsafe_allow_html=True)
            
            radar_data = []
            for m in selected_metrics:
                prov_val = df_prov_latest[df_prov_latest["指标名称"] == m]["指标值"].mean()
                nat_val = df_full[(df_full["指标名称"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
                if pd.notna(prov_val) and pd.notna(nat_val) and nat_val > 0:
                    radar_data.append({"指标": m, prov_name: round(prov_val / nat_val, 3), "全国平均": 1.0})
            
            if len(radar_data) >= 3:
                df_radar = pd.DataFrame(radar_data)
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=df_radar[prov_name], theta=df_radar["指标"],
                    fill="toself", name=prov_name, line_color="#1e40af", fillcolor="rgba(30, 64, 175, 0.2)"
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=df_radar["全国平均"], theta=df_radar["指标"],
                    fill="toself", name="全国平均", line_color="#94a3b8", fillcolor="rgba(148, 163, 184, 0.1)"
                ))
                max_r = max(df_radar[prov_name].max(), 1.5)
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, max_r], gridcolor="#e2e8f0"), angularaxis=dict(gridcolor="#e2e8f0")),
                    height=chart_height + 20, template="plotly_white",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("请选择至少3个指标以生成雷达图")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_wc:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">指标规模词云图</div>', unsafe_allow_html=True)
            metric_freq = dict(zip(df_prov_latest["指标名称"], df_prov_latest["指标值"].abs()))
            wc_fig = generate_word_cloud(metric_freq, f"{prov_name} 指标规模分布")
            if wc_fig:
                st.pyplot(wc_fig, use_container_width=True)
            else:
                st.info("词云生成暂不可用")
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第二行：2×2 多指标趋势子图 ----
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 多指标历年趋势子图（前4个指标）</div>', unsafe_allow_html=True)
        
        plot_metrics = selected_metrics[:4]
        fig_multi = make_subplots(
            rows=2, cols=2,
            subplot_titles=plot_metrics,
            vertical_spacing=0.15, horizontal_spacing=0.12
        )

        for i, m in enumerate(plot_metrics):
            row = i // 2 + 1
            col = i % 2 + 1
            m_data = df_prov[df_prov["指标名称"] == m].sort_values("年份")
            unit = df_full[df_full["指标名称"] == m]["单位"].iloc[0] if len(df_full[df_full["指标名称"] == m]) > 0 else ""
            
            fig_multi.add_trace(
                go.Scatter(x=m_data["年份"], y=m_data["指标值"], name=m,
                          mode="lines+markers", line=dict(width=2.5, color=CUSTOM_COLORS[i % len(CUSTOM_COLORS)]), showlegend=False),
                row=row, col=col
            )
            fig_multi.update_yaxes(title_text=unit, row=row, col=col)

        fig_multi.update_layout(
            height=chart_height + 120, template="plotly_white",
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_multi, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第三行：增速对比 + 规模对比 ----
        col_growth, col_bar = st.columns(2)

        with col_growth:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📉 各指标年均复合增速对比</div>', unsafe_allow_html=True)
            
            cagr_list = []
            for m in selected_metrics:
                m_data = df_prov[df_prov["指标名称"] == m].sort_values("年份")
                if len(m_data) >= 2:
                    s_val = m_data.iloc[0]["指标值"]
                    e_val = m_data.iloc[-1]["指标值"]
                    span = m_data.iloc[-1]["年份"] - m_data.iloc[0]["年份"]
                    cagr = safe_cagr(s_val, e_val, span)
                    cagr_list.append({"指标": m, "年均增速": cagr})
            
            if cagr_list:
                df_cagr = pd.DataFrame(cagr_list).sort_values("年均增速", ascending=True)
                fig_cagr = px.bar(
                    df_cagr, y="指标", x="年均增速", orientation="h",
                    color="年均增速", color_continuous_scale="RdBu",
                    text_auto=".2%", template="plotly_white"
                )
                fig_cagr.add_vline(x=0, line_dash="dash", line_color="gray")
                fig_cagr.update_layout(height=chart_height, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_cagr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_bar:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">📊 {latest_year}年指标规模对比</div>', unsafe_allow_html=True)
            df_bar = df_prov_latest.sort_values("指标值", ascending=True)
            fig_bar = px.bar(
                df_bar, y="指标名称", x="指标值", orientation="h",
                color="指标值", color_continuous_scale="Blues",
                text_auto=".2f" if show_data_labels else False,
                template="plotly_white"
            )
            fig_bar.update_layout(height=chart_height, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- 综合诊断与建议 ----
        st.markdown('<h2 class="sub-header">💡 综合诊断与发展建议</h2>', unsafe_allow_html=True)
        
        detail_list = []
        for m in selected_metrics:
            m_val = df_prov_latest[df_prov_latest["指标名称"] == m]["指标值"].mean()
            nat_avg = df_full[(df_full["指标名称"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
            unit = df_full[df_full["指标名称"] == m]["单位"].iloc[0] if len(df_full[df_full["指标名称"] == m]) > 0 else ""
            
            m_data = df_prov[df_prov["指标名称"] == m].sort_values("年份")
            cagr = safe_cagr(m_data.iloc[0]["指标值"], m_data.iloc[-1]["指标值"],
                           m_data.iloc[-1]["年份"] - m_data.iloc[0]["年份"]) if len(m_data) >= 2 else 0
            
            vs_nat = m_val / nat_avg if nat_avg and nat_avg > 0 else 0
            status = "✅ 领先" if vs_nat >= 1.1 else "⚠️ 持平" if vs_nat >= 0.9 else "❌ 落后"
            
            detail_list.append({
                "指标名称": m, f"{prov_name}值": round(m_val, 2),
                "全国均值": round(nat_avg, 2), "单位": unit,
                "相对水平": f"{vs_nat:.1%}", "年均增速": f"{cagr:.2%}",
                "发展状态": status
            })

        tab1, tab2 = st.tabs(["📋 指标详情对比", "📌 综合发展建议"])
        with tab1:
            st.dataframe(pd.DataFrame(detail_list), use_container_width=True, hide_index=True)

        with tab2:
            adv_metrics = [d["指标名称"] for d in detail_list if d["发展状态"] == "✅ 领先"]
            weak_metrics = [d["指标名称"] for d in detail_list if d["发展状态"] == "❌ 落后"]
            slow_metrics = [d["指标名称"] for d in detail_list if float(d["年均增速"].strip('%'))/100 < 0.03]

            st.markdown(f"""
            <div class="suggestion-box suggestion-conclusion">
                <div class="suggestion-title">综合评价</div>
                <div class="suggestion-text">
                    本次分析的 <b>{len(selected_metrics)}个指标</b> 中，
                    <b style="color:#16a34a;">领先指标 {len(adv_metrics)} 个</b>，
                    <b style="color:#dc2626;">落后指标 {len(weak_metrics)} 个</b>，
                    整体发展{"较为均衡，优势突出" if len(adv_metrics) > len(selected_metrics)/2 else "存在明显短板，需重点突破"}。
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 1. 巩固优势领域")
            if adv_metrics:
                st.markdown(f"持续强化 **{', '.join(adv_metrics)}** 等领先指标的竞争优势，发挥辐射带动作用，打造特色发展名片，形成区域标杆效应。")
            else:
                st.markdown("暂无显著领先指标，建议优先培育1-2个核心优势领域，集中资源突破，形成发展亮点。")

            st.markdown("##### 2. 补齐短板弱项")
            if weak_metrics:
                st.markdown(f"重点补齐 **{', '.join(weak_metrics)}** 等短板指标，对标全国先进省份，深入分析差距成因，制定专项提升方案，加大投入力度，力争3-5年内接近或达到全国平均水平。")
            else:
                st.markdown("无明显短板指标，整体发展较为均衡，重点在于提质增效，向高质量发展转型。")

            st.markdown("##### 3. 提升增长动能")
            if slow_metrics:
                st.markdown(f"针对 **{', '.join(slow_metrics)}** 等增速放缓的指标，深入挖掘增长瓶颈，创新发展模式，培育新的增长点，推动指标增速回升至全国平均水平以上。")
            else:
                st.markdown("各项指标增长态势良好，继续保持当前发展节奏，稳步提升发展质量与效益。")

            st.markdown("##### 4. 区域协同发展")
            st.markdown("积极融入国家区域重大战略，加强与周边省份的产业协作、人才交流和要素流动，通过区域联动实现优势互补、互利共赢，提升整体发展能级。")

    # ==================================================================
    # 数据导出模块（增强版）
    # ==================================================================
    st.markdown('<h2 class="sub-header">📋 数据预览与导出</h2>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    tab_data, tab_report = st.tabs(["明细数据", "分析报告"])
    with tab_data:
        show_cols = ["地区", "所属地域", "年份", "一级标题", "指标名称", "指标值", "单位"]
        show_cols = [c for c in show_cols if c in df_filtered.columns]
        st.dataframe(df_filtered[show_cols].head(200), use_container_width=True, hide_index=True)
        
        csv_data = df_filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 下载完整明细数据 (CSV)",
            data=csv_data,
            file_name=f"省级数据库_{selected_category}_分析数据_{selected_years[0]}-{selected_years[1]}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with tab_report:
        # 生成文本报告
        report = f"""中国省级数据库2025版 分析报告
{'='*50}
分析模式：{mode_desc}
指标大类：{selected_category}
时间区间：{selected_years[0]}年 - {selected_years[1]}年
覆盖省份：{len(selected_provinces)}个
生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

一、核心统计摘要
{'-'*30}
"""
        if analysis_mode == "🌍 省际对比分析":
            report += f"""
分析指标：{selected_metric}（{metric_unit}）
省份均值：{avg_val:,.2f} {metric_unit}
全国均值：{national_avg:,.2f} {metric_unit}
最高值：{max_val:,.2f} {metric_unit}
省际离散度：{cv_val:.2%}
整体年均增速：{total_cagr:.2%}

二、省份排名（{latest_year}年）
{'-'*30}
"""
            df_latest_sorted = df_filtered[df_filtered["年份"] == latest_year].sort_values("指标值", ascending=False).reset_index(drop=True)
            for i, r in df_latest_sorted.iterrows():
                report += f"第{i+1}名 {r['地区']}：{r['指标值']:,.2f} {metric_unit}\n"
        else:
            report += f"""
分析省份：{prov_name}
分析指标数：{len(selected_metrics)}个
高于全国均值指标数：{above_avg_count}个
指标领先占比：{above_avg_count/len(selected_metrics):.1%}

二、分指标详情
{'-'*30}
"""
            for d in detail_list:
                report += f"{d['指标名称']}：{d[f'{prov_name}值']} {d['单位']}，全国均值{d['全国均值']}，相对水平{d['相对水平']}，年均增速{d['年均增速']}\n"
        
        report += f"\n{'='*50}\n数据来源：中国省级数据库2025版\n"
        
        st.text_area("报告预览", report, height=300)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 下载文本报告 (TXT)",
                data=report.encode("utf-8"),
                file_name=f"省级数据库分析报告_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
                use_container_width=True
            )
        
        with col_dl2:
            # 生成并下载HTML报告
            if analysis_mode == "🌍 省际对比分析":
                html_report = generate_html_report(
                    analysis_mode, selected_category, selected_years, selected_provinces,
                    selected_metric, selected_metrics, df_filtered, df_full, metric_unit,
                    metric_desc, latest_year, avg_val, national_avg, max_val, cv_val, total_cagr
                )
            else:
                html_report = generate_html_report(
                    analysis_mode, selected_category, selected_years, selected_provinces,
                    selected_metric, selected_metrics, df_filtered, df_full, metric_unit,
                    metric_desc, latest_year, detail_list=detail_list, above_avg_count=above_avg_count
                )
            
            st.download_button(
                label="🌐 下载精美HTML报告",
                data=html_report.encode("utf-8"),
                file_name=f"省级数据库HTML报告_{pd.Timestamp.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # ---- 页脚 ----
    st.markdown("""
    <div class="footer">
        数据来源：中国省级数据库2025版 &nbsp;|&nbsp; 技术架构：Streamlit + Plotly + Pandas &nbsp;|&nbsp; 支持3000+省级经济社会指标可视化分析
        <br>© 2025 中国省级数据库可视化分析与决策支持平台
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
