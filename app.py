# ===================== 依赖导入 =====================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List
import os
import re
import base64
from datetime import datetime

# 移除matplotlib和wordcloud依赖（词云图已替换为Plotly交互式图表）
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# from wordcloud import WordCloud

# ===================== 全局常量配置 =====================
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

CHINA_GEOJSON_URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"

# 字体配置已移除（不再使用matplotlib）
# try:
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
# except:
#     pass

# 科技感配色
CUSTOM_COLORS = ["#00d4ff", "#3b82f6", "#06b6d4", "#8b5cf6", "#f59e0b", "#10b981", "#ec4899", "#6366f1"]

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

# ===================== 科技感CSS样式 =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', 'Microsoft YaHei', 'SimHei', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #0f172a 50%, #1e293b 100%);
    }
    /* 主标题 - 霓虹科技感 */
    .main-header {
        font-size: 2.6rem;
        font-weight: 700;
        text-align: center;
        margin: 0.5rem 0 0.5rem 0;
        background: linear-gradient(135deg, #00d4ff 0%, #3b82f6 40%, #8b5cf6 70%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 1.2rem 0 0.6rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, #00d4ff, #3b82f6, transparent) 1;
        display: inline-block;
    }
    .section-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    /* 统计卡片 - 玻璃拟态 */
    .stat-card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.8rem;
        margin: 0.6rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 16px;
        padding: 1rem 0.9rem;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1), inset 0 1px 0 rgba(255,255,255,0.1);
        text-align: left;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 212, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #3b82f6, #8b5cf6);
        opacity: 0.6;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2), inset 0 1px 0 rgba(255,255,255,0.15);
        border-color: rgba(0, 212, 255, 0.4);
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00d4ff;
        margin-bottom: 0.3rem;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
    }
    .stat-label {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
        line-height: 1.3;
    }
    /* 内容卡片 - 深色玻璃 */
    .content-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(59, 130, 246, 0.15);
    }
    .content-card:hover {
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.15), inset 0 1px 0 rgba(255,255,255,0.1);
        border-color: rgba(59, 130, 246, 0.3);
    }
    /* 图表容器优化 */
    .chart-wrapper {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
        border-radius: 12px;
        padding: 0.8rem;
        margin: 0.4rem 0;
    }
    .chart-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.6rem;
        padding-left: 0.5rem;
        border-left: 3px solid #00d4ff;
        line-height: 1.2;
    }
    /* 建议模块 */
    .suggestion-box {
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
        margin: 0.4rem 0;
        border-left: 3px solid;
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.4) 100%);
    }
    .suggestion-advantage {
        border-color: #10b981;
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.3) 100%);
    }
    .suggestion-weakness {
        border-color: #ef4444;
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, rgba(15, 23, 42, 0.3) 100%);
    }
    .suggestion-trend {
        border-color: #3b82f6;
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(15, 23, 42, 0.3) 100%);
    }
    .suggestion-conclusion {
        border-color: #8b5cf6;
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.1) 0%, rgba(15, 23, 42, 0.3) 100%);
    }
    .suggestion-title {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
        color: #e2e8f0;
    }
    .suggestion-text {
        color: #cbd5e1;
        line-height: 1.5;
        font-size: 0.85rem;
    }
    .data-basis {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }
    /* 侧边栏 */
    .stSidebar {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.15);
    }
    .stSidebar [data-testid="stMarkdownContainer"] h2 {
        color: #e2e8f0;
        font-size: 1.2rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #00d4ff;
    }
    .stSidebar [data-testid="stMarkdownContainer"] h4 {
        color: #00d4ff;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
        font-size: 0.95rem;
    }
    /* 按钮 */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 255, 0.4);
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(59, 130, 246, 0.2) 100%);
        color: #e2e8f0;
        font-weight: 500;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(59, 130, 246, 0.35) 100%);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        transform: translateY(-1px);
        border-color: rgba(0, 212, 255, 0.6);
    }
    /* 页脚 */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1.2rem 0;
        color: #64748b;
        border-top: 1px solid rgba(0, 212, 255, 0.15);
        font-size: 0.8rem;
        line-height: 1.6;
    }
    /* 标签页 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #00d4ff;
        border-bottom: 2px solid #00d4ff;
    }
    /* 展开器 */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
        color: #e2e8f0;
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 255, 0.15);
    }
    .streamlit-expanderContent {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 0 0 10px 10px;
    }
    /* 新手引导 */
    .guide-box {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    .guide-step {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        margin: 0.6rem 0;
        padding: 0.6rem;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        border-left: 3px solid #00d4ff;
    }
    .guide-step-num {
        background: linear-gradient(135deg, #00d4ff, #3b82f6);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .guide-step-text {
        color: #cbd5e1;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    /* 数据表格 */
    .stDataFrame {
        background: rgba(15, 23, 42, 0.5);
    }
    /* 滑块和选择器 */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #3b82f6);
    }
    /* 多选框 */
    .stMultiSelect span[data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(59, 130, 246, 0.2));
        border: 1px solid rgba(0, 212, 255, 0.3);
        color: #e2e8f0;
    }
    /* 单选按钮 */
    .stRadio > div > label > div[data-testid="stMarkdownContainer"] {
        color: #e2e8f0;
    }
    /* 信息提示 */
    .stAlert {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #e2e8f0;
    }
    /* 加载动画 */
    .stSpinner > div {
        border-color: #00d4ff;
        border-top-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ===================== 核心工具函数 =====================
def generate_bubble_scatter(df_latest, selected_years, metric_unit):
    """生成省份规模-增速气泡图（替代词云图）"""
    if df_latest is None or len(df_latest) == 0:
        return None
    try:
        # 计算每个省份的增速
        year_span = selected_years[1] - selected_years[0]
        cagr_data = []
        for prov in df_latest["地区"].unique():
            prov_data = df_latest[df_latest["地区"] == prov].sort_values("年份")
            if len(prov_data) >= 2:
                s_val = prov_data.iloc[0]["指标值"]
                e_val = prov_data.iloc[-1]["指标值"]
                cagr = safe_cagr(s_val, e_val, year_span)
                latest_val = prov_data.iloc[-1]["指标值"]
                cagr_data.append({
                    "地区": prov,
                    "最新值": latest_val,
                    "年均增速": cagr,
                    "规模等级": "大型" if latest_val > df_latest["指标值"].quantile(0.75) else
                               "中型" if latest_val > df_latest["指标值"].quantile(0.25) else "小型"
                })
        if len(cagr_data) < 3:
            return None
        df_bubble = pd.DataFrame(cagr_data)
        fig = px.scatter(
            df_bubble, x="最新值", y="年均增速", size="最新值", color="规模等级",
            hover_name="地区", text="地区",
            color_discrete_map={"大型": "#00d4ff", "中型": "#3b82f6", "小型": "#8b5cf6"},
            template="plotly_dark",
            labels={"最新值": f"最新规模 ({metric_unit})", "年均增速": "年均增速"}
        )
        fig.update_traces(textposition="top center", textfont=dict(size=10, color="#e2e8f0"))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font_color="#e2e8f0"),
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0")
        )
        return fig
    except Exception:
        return None

def safe_cagr(start_val: float, end_val: float, years: int) -> float:
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return 0.0
    try:
        return (end_val / start_val) ** (1 / years) - 1
    except:
        return 0.0

def parse_indicator_name(col_name: str):
    match = re.search(r'(.+)\(([^)]+)\)$', col_name)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return col_name.strip(), ""

def get_image_base64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def generate_html_report(analysis_mode, selected_years, selected_provinces,
                        selected_metric, selected_metrics, df_filtered, df_full, metric_unit,
                        latest_year, avg_val=None, national_avg=None, max_val=None,
                        cv_val=None, total_cagr=None, detail_list=None, above_avg_count=None):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
            background: linear-gradient(135deg, #0a1628 0%, #0f172a 50%, #1e293b 100%);
            color: #e2e8f0;
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
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(59, 130, 246, 0.2) 50%, rgba(139, 92, 246, 0.2) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 212, 255, 0.1);
        }}
        .header h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; background: linear-gradient(135deg, #00d4ff, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .header p {{ font-size: 1rem; opacity: 0.8; color: #94a3b8; }}
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .meta-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-left: 4px solid #00d4ff;
        }}
        .meta-label {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.3rem; }}
        .meta-value {{ font-size: 1.1rem; font-weight: 600; color: #00d4ff; }}
        .section {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
            border-radius: 14px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.15);
        }}
        .section h2 {{
            font-size: 1.3rem;
            color: #e2e8f0;
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid transparent;
            border-image: linear-gradient(90deg, #00d4ff, #3b82f6, transparent) 1;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(15, 23, 42, 0.3) 100%);
            padding: 1.2rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }}
        .stat-box .number {{ font-size: 1.6rem; font-weight: 700; color: #00d4ff; text-shadow: 0 0 10px rgba(0, 212, 255, 0.4); }}
        .stat-box .label {{ font-size: 0.85rem; color: #94a3b8; margin-top: 0.3rem; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 0.8rem;
            text-align: left;
            border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            color: #cbd5e1;
        }}
        th {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
            color: #e2e8f0;
            font-weight: 600;
        }}
        tr:hover {{ background: rgba(0, 212, 255, 0.05); }}
        .rank-1 {{ background: linear-gradient(90deg, rgba(245, 158, 11, 0.15) 0%, transparent 100%); }}
        .rank-2 {{ background: linear-gradient(90deg, rgba(148, 163, 184, 0.1) 0%, transparent 100%); }}
        .rank-3 {{ background: linear-gradient(90deg, rgba(251, 146, 60, 0.1) 0%, transparent 100%); }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .badge-success {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .suggestion {{
            padding: 1rem 1.2rem;
            border-radius: 8px;
            margin: 0.6rem 0;
            border-left: 4px solid;
            background: rgba(15, 23, 42, 0.5);
        }}
        .sg-advantage {{ background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, transparent 100%); border-color: #10b981; }}
        .sg-weakness {{ background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, transparent 100%); border-color: #ef4444; }}
        .sg-trend {{ background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, transparent 100%); border-color: #3b82f6; }}
        .sg-conclusion {{ background: linear-gradient(90deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%); border-color: #8b5cf6; }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.85rem;
            border-top: 1px solid rgba(0, 212, 255, 0.15);
            margin-top: 2rem;
        }}
        .highlight {{ color: #00d4ff; font-weight: 600; }}
        @media print {{
            body {{ background: #0f172a; }}
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
        df_latest = df_filtered[df_filtered["年份"] == latest_year]
        df_latest_sorted = df_latest.sort_values("指标值", ascending=False).reset_index(drop=True)

        html_body += f"""
        <div class="section">
            <h2>📊 核心统计摘要</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">{avg_val:,.2f}</div>
                    <div class="label">省份均值{f" ({metric_unit})" if metric_unit else ""}</div>
                </div>
                <div class="stat-box">
                    <div class="number">{national_avg:,.2f}</div>
                    <div class="label">全国均值{f" ({metric_unit})" if metric_unit else ""}</div>
                </div>
                <div class="stat-box">
                    <div class="number">{max_val:,.2f}</div>
                    <div class="label">最高值{f" ({metric_unit})" if metric_unit else ""}</div>
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
                        <th>指标值{f" ({metric_unit})" if metric_unit else ""}</th>
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
            rank_pct = rank / total_prov_count if total_prov_count else 0

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
                span = int(prov_data.iloc[-1]["年份"] - prov_data.iloc[0]["年份"])
                cagr = safe_cagr(s_val, e_val, span)
            else:
                cagr = 0

            suggestions = []
            if vs_nat < 0.8:
                suggestions.append(f"<strong>补短板</strong>：当前指标仅为全国均值的{vs_nat:.0%}，需加大核心要素投入")
            if cagr < 0.03:
                suggestions.append("<strong>增动能</strong>：增长速度偏低，需培育新增长引擎")
            if rank <= total_prov_count * 0.25:
                suggestions.append("<strong>固优势</strong>：保持全国领先地位，发挥示范引领作用")
            elif rank <= total_prov_count * 0.5:
                suggestions.append("<strong>促提升</strong>：向第一梯队省份对标学习，突破瓶颈制约")
            suggestions.append("<strong>区域协同</strong>：加强与周边省份的产业协作与要素流动")

            html_body += f"""
            <div style="margin: 1rem 0; padding: 1rem; background: rgba(15, 23, 42, 0.5); border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.15);">
                <h4 style="color: #00d4ff; margin-bottom: 0.5rem;">📍 {prov} | 全国第{rank}名</h4>
                <p style="color: #cbd5e1;">指标值：<span class="highlight">{val:,.2f} {metric_unit}</span> |
                   相对全国均值：<span class="highlight">{vs_nat:.1%}</span> |
                   年均增速：<span class="highlight">{cagr:.2%}</span></p>
                <ul style="margin-top: 0.5rem; padding-left: 1.2rem; color: #cbd5e1;">
"""
            for s in suggestions:
                html_body += f"                    <li>{s}</li>\n"
            html_body += "                </ul>\n            </div>\n"

        html_body += "</div>"
    else:
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
                <span style="color:#10b981;"><strong>领先指标 {len(adv_metrics)} 个</strong></span>，
                <span style="color:#ef4444;"><strong>落后指标 {len(weak_metrics)} 个</strong></span>。
            </div>

            <div class="suggestion sg-advantage">
                <strong>1. 巩固优势领域</strong><br>
                {f"持续强化 <strong>{', '.join(adv_metrics)}</strong> 等领先指标的竞争优势。" if adv_metrics else "暂无显著领先指标，建议优先培育1-2个核心优势领域。"}
            </div>

            <div class="suggestion sg-weakness">
                <strong>2. 补齐短板弱项</strong><br>
                {f"重点补齐 <strong>{', '.join(weak_metrics)}</strong> 等短板指标，对标全国先进省份。" if weak_metrics else "无明显短板指标，整体发展较为均衡。"}
            </div>

            <div class="suggestion sg-trend">
                <strong>3. 区域协同发展</strong><br>
                积极融入国家区域重大战略，加强与周边省份的产业协作、人才交流和要素流动。
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
        st.error(f"❌ 数据文件未找到，请检查路径：{file_path}\n\n请确保CSV文件与app.py在同一目录。")
        st.stop()

    try:
        df_raw = None
        encoding_used = None
        for enc in ['gbk', 'gb2312', 'gb18030', 'utf-8-sig', 'utf-8']:
            try:
                df_raw = pd.read_csv(file_path, encoding=enc, low_memory=False)
                encoding_used = enc
                break
            except UnicodeDecodeError:
                continue

        if df_raw is None:
            st.error("❌ 无法读取CSV文件，编码不支持。请确保文件为GBK或UTF-8编码。")
            st.stop()

        required_cols = ['地区', '年份']
        for col in required_cols:
            if col not in df_raw.columns:
                st.error(f"❌ CSV文件中缺少必要列：{col}")
                st.stop()

        if '所属地域' not in df_raw.columns:
            df_raw['所属地域'] = '其他'

        df_raw['年份'] = pd.to_numeric(df_raw['年份'], errors='coerce')
        df_raw = df_raw.dropna(subset=['年份'])
        df_raw['年份'] = df_raw['年份'].astype(int)

        meta_cols = ['行政区划代码', '地区', '所属地域', '年份']
        indicator_cols = [c for c in df_raw.columns if c not in meta_cols]

        if len(indicator_cols) == 0:
            st.error("❌ CSV文件中未找到任何指标列")
            st.stop()

        id_vars = [c for c in meta_cols if c in df_raw.columns]
        df_long = df_raw.melt(
            id_vars=id_vars,
            value_vars=indicator_cols,
            var_name="指标名称",
            value_name="指标值"
        )

        df_long["指标值"] = pd.to_numeric(df_long["指标值"], errors='coerce')
        df_long = df_long.dropna(subset=["指标值"]).reset_index(drop=True)

        parsed = df_long["指标名称"].apply(parse_indicator_name)
        df_long["指标名称_纯"] = parsed.apply(lambda x: x[0])
        df_long["单位"] = parsed.apply(lambda x: x[1])

        df_long["地区_标准"] = df_long["地区"].map(PROVINCE_STD_MAP).fillna(df_long["地区"])

        return df_long

    except Exception as e:
        st.error(f"❌ 数据加载失败：{str(e)}\n\n请检查CSV文件格式是否正确")
        st.stop()

# ===================== 新手引导组件 =====================
def show_newbie_guide():
    """显示新手引导"""
    with st.expander("🚀 新手快速入门指南（点击展开）", expanded=False):
        st.markdown("""
        <div class="guide-box">
            <h4 style="color: #00d4ff; margin-bottom: 0.8rem;">👋 欢迎使用中国省级数据库可视化平台</h4>
            <p style="color: #94a3b8; margin-bottom: 1rem;">本系统支持3000+省级经济社会指标的多维度分析与决策支持，只需3步即可生成专业分析报告：</p>

            <div class="guide-step">
                <div class="guide-step-num">1</div>
                <div class="guide-step-text">
                    <strong style="color: #e2e8f0;">选择分析模式</strong><br>
                    <span style="color: #94a3b8;">🌍 省际对比：横向对比多个省份的同一指标，适合区域竞争分析</span><br>
                    <span style="color: #94a3b8;">📍 单省深度：纵向分析单个省份的多项指标，适合省内诊断</span>
                </div>
            </div>

            <div class="guide-step">
                <div class="guide-step-num">2</div>
                <div class="guide-step-text">
                    <strong style="color: #e2e8f0;">配置筛选条件</strong><br>
                    <span style="color: #94a3b8;">• 省份：选择需要分析的省份（支持全选/清空）</span><br>
                    <span style="color: #94a3b8;">• 时间：拖动滑块选择年份区间</span><br>
                    <span style="color: #94a3b8;">• 指标：选择关注的经济社会指标（如GDP、人口等）</span>
                </div>
            </div>

            <div class="guide-step">
                <div class="guide-step-num">3</div>
                <div class="guide-step-text">
                    <strong style="color: #e2e8f0;">查看分析与导出</strong><br>
                    <span style="color: #94a3b8;">• 自动生成交互式图表（地图、趋势、排名、雷达图等）</span><br>
                    <span style="color: #94a3b8;">• 查看智能诊断建议与发展策略</span><br>
                    <span style="color: #94a3b8;">• 下载CSV数据、TXT报告或精美HTML报告</span>
                </div>
            </div>

            <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(0, 212, 255, 0.05); border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.2);">
                <p style="color: #00d4ff; font-size: 0.9rem; margin: 0;">💡 <strong>小贴士：</strong>首次使用建议先尝试"省际对比"模式，选择"地区生产总值"指标，即可快速体验核心功能！</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===================== 主程序入口 =====================
def main():
    # 自动查找数据文件
    FILE_PATH = None
    possible_paths = [
        "./中国省级数据库2025版.csv",
        "中国省级数据库2025版.csv",
        "./中国省级数据库2025版.xlsx",
        "中国省级数据库2025版.xlsx",
        "/workspace/.uploads/1b6fa534-77f3-4e3f-a7f6-e9c7fb829a33_中国省级数据库2025版.csv",
        "/workspace/.uploads/d1cfc993-9057-4c1d-984b-afa52c0bed59_中国省级数据库2025版.xlsx"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            FILE_PATH = p
            break

    if FILE_PATH is None:
        st.error("❌ 未找到数据文件「中国省级数据库2025版.csv/.xlsx」，请确保文件与程序在同一目录")
        st.stop()

    df_full = load_and_standardize_data(FILE_PATH)

    # ---------- 侧边栏筛选系统 ----------
    st.sidebar.markdown("<h2 style='color: #00d4ff; text-align: center; margin-bottom: 1rem;'>🔍 分析设置</h2>", unsafe_allow_html=True)

    # 侧边栏顶部图片
    sidebar_img = get_image_base64("assets/sidebar_header.jpg")
    if sidebar_img:
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <img src="data:image/jpeg;base64,{sidebar_img}" style="width: 100%; border-radius: 12px; opacity: 0.8;">
        </div>
        """, unsafe_allow_html=True)

    analysis_mode = st.sidebar.radio(
        "分析模式",
        options=["🌍 省际对比分析", "📍 单省深度分析"],
        index=0,
        help="省际对比：多省份横向对比同一指标；单省深度：单个省份多指标纵向剖析"
    )
    st.sidebar.divider()

    # 省份选择
    st.sidebar.markdown("<h4 style='color: #00d4ff;'>🗺️ 省份选择</h4>", unsafe_allow_html=True)
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
    st.sidebar.markdown("<h4 style='color: #00d4ff;'>📅 时间区间</h4>", unsafe_allow_html=True)
    min_year = int(df_full["年份"].min())
    max_year = int(df_full["年份"].max())
    selected_years = st.sidebar.slider(
        "选择年份范围",
        min_value=min_year, max_value=max_year,
        value=(max(2012, min_year), max_year), step=1
    )
    st.sidebar.divider()

    # 指标选择
    st.sidebar.markdown("<h4 style='color: #00d4ff;'>📊 指标选择</h4>", unsafe_allow_html=True)
    all_metrics = sorted(df_full["指标名称_纯"].dropna().unique())

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
    st.sidebar.markdown("<h4 style='color: #00d4ff;'>⚙️ 显示设置</h4>", unsafe_allow_html=True)
    with st.sidebar.expander("图表配置", expanded=False):
        show_data_labels = st.checkbox("显示数据标签", value=False)
        chart_height = st.slider("图表高度", min_value=350, max_value=650, value=460, step=50)
        top_n = st.slider("排名展示数量", min_value=3, max_value=15, value=10, step=1)

    # ---------- 数据过滤与前置校验 ----------
    df_filtered = df_full[
        (df_full["地区"].isin(selected_provinces)) &
        (df_full["年份"] >= selected_years[0]) &
        (df_full["年份"] <= selected_years[1]) &
        (df_full["指标名称_纯"].isin(selected_metrics))
    ].copy()

    if len(df_filtered) == 0 or len(selected_provinces) == 0 or len(selected_metrics) == 0:
        st.error("⚠️ 当前筛选条件下无有效数据，请调整省份、指标或年份范围后重试")
        st.stop()

    # 通用信息
    latest_year = df_filtered["年份"].max()
    metric_info = df_full[df_full["指标名称_纯"] == selected_metric].iloc[0] if selected_metric else None
    metric_unit = metric_info["单位"] if metric_info is not None and pd.notna(metric_info["单位"]) else ""

    # ---------- 页面头部（科技感Hero区域） ----------
    hero_img = get_image_base64("assets/hero_banner.jpg")
    if hero_img:
        st.markdown(f"""
        <div style="position: relative; width: 100%; margin-bottom: 1rem;">
            <img src="data:image/jpeg;base64,{hero_img}" style="width: 100%; border-radius: 16px; box-shadow: 0 10px 40px rgba(0, 212, 255, 0.2);">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; width: 90%;">
                <h1 style="font-size: 2.8rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #ffffff 0%, #00d4ff 50%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px rgba(0, 212, 255, 0.5); letter-spacing: 3px;">中国省级数据库2025版</h1>
                <p style="font-size: 1.2rem; color: rgba(255,255,255,0.9); margin-top: 0.5rem; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">可视化决策支持平台 | 3000+指标 · 31省份 · 34年数据</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<h1 class="main-header">中国省级数据库2025版 可视化决策平台</h1>', unsafe_allow_html=True)

    # 新手引导
    show_newbie_guide()

    # 科技感分隔图
    section_img = get_image_base64("assets/section_divider.jpg")
    if section_img:
        st.markdown(f"""
        <div style="margin: 0.5rem 0; border-radius: 12px; overflow: hidden;">
            <img src="data:image/jpeg;base64,{section_img}" style="width: 100%; height: 80px; object-fit: cover; opacity: 0.7;">
        </div>
        """, unsafe_allow_html=True)

    # 状态栏
    mode_desc = "省际横向对比分析" if analysis_mode == "🌍 省际对比分析" else f"{selected_provinces[0]} 多维度深度分析"
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(0, 212, 255, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 12px; padding: 0.8rem 1.2rem; margin: 0.8rem 0;">
        <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;">
            🎯 <strong>当前模式：</strong>{mode_desc} &nbsp;&nbsp;|&nbsp;&nbsp;
            📅 <strong>时间区间：</strong>{selected_years[0]} - {selected_years[1]}年 &nbsp;&nbsp;|&nbsp;&nbsp;
            📍 <strong>覆盖省份：</strong>{len(selected_provinces)}个 &nbsp;&nbsp;|&nbsp;&nbsp;
            📊 <strong>指标数：</strong>{len(selected_metrics)}个
        </p>
    </div>
    """, unsafe_allow_html=True)

    if analysis_mode == "🌍 省际对比分析":
        unit_display = f"（{metric_unit}）" if metric_unit else ""
        st.markdown(f'<div class="section-desc" style="text-align: center; color: #94a3b8;">💡 指标说明：{selected_metric}{unit_display}</div>', unsafe_allow_html=True)

    # ==================================================================
    # 模式一：省际对比分析
    # ==================================================================
    if analysis_mode == "🌍 省际对比分析":
        df_latest = df_filtered[df_filtered["年份"] == latest_year]
        national_avg = df_full[(df_full["指标名称_纯"] == selected_metric) & (df_full["年份"] == latest_year)]["指标值"].mean()
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
            <div class="stat-card"><div class="stat-value">{avg_val:,.2f}</div><div class="stat-label">省份均值{f"（{metric_unit}）" if metric_unit else ""}</div></div>
            <div class="stat-card"><div class="stat-value">{national_avg:,.2f}</div><div class="stat-label">全国均值{f"（{metric_unit}）" if metric_unit else ""}</div></div>
            <div class="stat-card"><div class="stat-value">{max_val:,.2f}</div><div class="stat-label">最高值{f"（{metric_unit}）" if metric_unit else ""}</div></div>
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
                    color_continuous_scale="Cividis",
                    labels={"指标值": f"{selected_metric}"},
                    template="plotly_dark",
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
                    margin=dict(l=0, r=30, t=0, b=0),
                    coloraxis_colorbar=dict(title="", thickness=15, len=0.7, tickfont=dict(color="#e2e8f0"), xpad=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            except Exception:
                st.warning("⚠️ 地图资源加载失败，已降级为条形图展示")
                df_rank_bar = df_latest.sort_values("指标值", ascending=True).tail(top_n)
                fig_fallback = px.bar(
                    df_rank_bar, y="地区", x="指标值", orientation="h",
                    color="指标值", color_continuous_scale="Cividis", template="plotly_dark"
                )
                fig_fallback.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_fallback, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_rank:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">省份排名 Top {top_n}（{latest_year}年）</div>', unsafe_allow_html=True)
            df_rank = df_latest.sort_values("指标值", ascending=False).head(top_n).sort_values("指标值", ascending=True)
            fig_rank = px.bar(
                df_rank, y="地区", x="指标值", orientation="h",
                color="指标值", color_continuous_scale="Cividis",
                text_auto=".2f" if show_data_labels else False,
                labels={"指标值": metric_unit, "地区": ""},
                template="plotly_dark"
            )
            fig_rank.update_layout(
                height=chart_height + 60, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=9, color="#e2e8f0")),
                margin=dict(l=10, r=10, t=10, b=40), xaxis_title="",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0")
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
            go.Bar(x=df_yearly["年份"], y=df_yearly["增速%"], name="增速%", marker_color="#00d4ff", marker_line_width=0),
            row=1, col=2
        )
        fig_sub1.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)

        fig_sub1.update_layout(
            height=chart_height, template="plotly_dark",
            legend=dict(orientation="v", yanchor="top", y=1.0, xanchor="left", x=1.02, font=dict(size=10, color="#e2e8f0")),
            margin=dict(l=10, r=120, t=30, b=10),
            colorway=CUSTOM_COLORS,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0")
        )
        fig_sub1.update_yaxes(title_text=f"{selected_metric} ({metric_unit})", row=1, col=1, gridcolor="rgba(255,255,255,0.1)")
        fig_sub1.update_yaxes(title_text="同比增速 (%)", row=1, col=2, gridcolor="rgba(255,255,255,0.1)")
        fig_sub1.update_xaxes(gridcolor="rgba(255,255,255,0.1)")
        st.plotly_chart(fig_sub1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第三行：箱线图 + 饼图 + 热力矩阵 ----
        col_box, col_pie, col_heat = st.columns([1, 1, 1.2])

        with col_box:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📦 分地域分布箱线图</div>', unsafe_allow_html=True)
            fig_box = px.box(
                df_filtered, x="所属地域", y="指标值", color="所属地域",
                points="outliers", template="plotly_dark",
                labels={"指标值": metric_unit, "所属地域": ""},
                color_discrete_sequence=CUSTOM_COLORS
            )
            fig_box.update_layout(height=chart_height, showlegend=True,
                                  legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=9, color="#e2e8f0")),
                                  margin=dict(l=10, r=10, t=10, b=40),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"))
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_pie:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">🥧 {latest_year}年省份占比</div>', unsafe_allow_html=True)
            df_pie = df_latest.sort_values("指标值", ascending=False).head(10)
            fig_pie = px.pie(
                df_pie, values="指标值", names="地区", hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=CUSTOM_COLORS
            )
            fig_pie.update_traces(textinfo="percent+label", textfont_size=10, textfont_color="#e2e8f0", pull=[0.02]*10)
            fig_pie.update_layout(
                height=chart_height,
                legend=dict(orientation="v", yanchor="top", y=1.0, xanchor="left", x=1.02, font=dict(size=9, color="#e2e8f0")),
                margin=dict(l=10, r=120, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_heat:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔬 省份发展聚类分析（规模 vs 增速）</div>', unsafe_allow_html=True)
            # 聚类分析：将省份按最新值和年均增速分为四个象限
            cluster_data = []
            year_span = selected_years[1] - selected_years[0]
            for prov in df_latest["地区"].unique():
                prov_data = df_filtered[df_filtered["地区"] == prov].sort_values("年份")
                if len(prov_data) >= 2:
                    s_val = prov_data.iloc[0]["指标值"]
                    e_val = prov_data.iloc[-1]["指标值"]
                    cagr = safe_cagr(s_val, e_val, year_span)
                    latest_val = prov_data.iloc[-1]["指标值"]
                    cluster_data.append({
                        "地区": prov,
                        "最新值": latest_val,
                        "年均增速": cagr
                    })
            if len(cluster_data) >= 3:
                df_cluster = pd.DataFrame(cluster_data)
                median_val = df_cluster["最新值"].median()
                median_cagr = df_cluster["年均增速"].median()
                df_cluster["发展类型"] = df_cluster.apply(
                    lambda r: "明星型（高规模高增长）" if r["最新值"] >= median_val and r["年均增速"] >= median_cagr else
                              "现金牛型（高规模低增长）" if r["最新值"] >= median_val else
                              "问题型（低规模高增长）" if r["年均增速"] >= median_cagr else
                              "瘦狗型（低规模低增长）", axis=1
                )
                color_map = {
                    "明星型（高规模高增长）": "#10b981",
                    "现金牛型（高规模低增长）": "#f59e0b",
                    "问题型（低规模高增长）": "#3b82f6",
                    "瘦狗型（低规模低增长）": "#ef4444"
                }
                fig_cluster = px.scatter(
                    df_cluster, x="最新值", y="年均增速", color="发展类型",
                    hover_name="地区", text="地区",
                    color_discrete_map=color_map,
                    template="plotly_dark",
                    labels={"最新值": f"最新规模 ({metric_unit})", "年均增速": "年均增速"}
                )
                fig_cluster.update_traces(textposition="top center", textfont=dict(size=10, color="#e2e8f0"))
                fig_cluster.add_vline(x=median_val, line_dash="dash", line_color="rgba(255,255,255,0.3)")
                fig_cluster.add_hline(y=median_cagr, line_dash="dash", line_color="rgba(255,255,255,0.3)")
                fig_cluster.update_layout(
                    height=chart_height,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font_color="#e2e8f0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0")
                )
                st.plotly_chart(fig_cluster, use_container_width=True)
            else:
                st.info("聚类分析数据不足")
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第四行：省份规模-增速气泡图（替代词云图） ----
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-title">🫧 {latest_year}年省份规模-增速气泡图</div>', unsafe_allow_html=True)
        bubble_fig = generate_bubble_scatter(df_filtered, selected_years, metric_unit)
        if bubble_fig:
            st.plotly_chart(bubble_fig, use_container_width=True)
        else:
            st.info("气泡图数据不足，请确保选择多个省份和年份")
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
                span = int(prov_data.iloc[-1]["年份"] - prov_data.iloc[0]["年份"])
                cagr = safe_cagr(s_val, e_val, span)
            else:
                cagr = 0

            rank_pct = rank / total_prov_count if total_prov_count else 0
            if rank_pct <= 0.25:
                tier, tier_cls = "第一梯队（全国领先）", "suggestion-advantage"
            elif rank_pct <= 0.5:
                tier, tier_cls = "第二梯队（中上游）", "suggestion-trend"
            elif rank_pct <= 0.75:
                tier, tier_cls = "第三梯队（中下游）", "suggestion-weakness"
            else:
                tier, tier_cls = "第四梯队（追赶型）", "suggestion-weakness"

            unit_str = f" {metric_unit}" if metric_unit else ""
            with st.expander(f"📍 {prov} | 全国第{rank}名 | {val:,.2f}{unit_str}", expanded=(idx < 3)):
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
                        <div class="data-basis">全国均值 {national_avg:,.2f}{f" {metric_unit}" if metric_unit else ""}</div>
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
                    <div class="suggestion-box" style="background:linear-gradient(90deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.4) 100%); border-color:#64748b;">
                        <div class="suggestion-title">对标追赶对象</div>
                        <div class="suggestion-text"><b>{bench_prov}</b></div>
                        <div class="data-basis">差距 {gap:.1%}，目标值 {bench_val:,.2f}{f" {metric_unit}" if metric_unit else ""}</div>
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
            m_val = df_prov_latest[df_prov_latest["指标名称_纯"] == m]["指标值"].mean()
            nat_avg = df_full[(df_full["指标名称_纯"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
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
            <div class="stat-card"><div class="stat-value">{prov_name}</div><div class="stat-label">分析省份</div></div>
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
                prov_val = df_prov_latest[df_prov_latest["指标名称_纯"] == m]["指标值"].mean()
                nat_val = df_full[(df_full["指标名称_纯"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
                if pd.notna(prov_val) and pd.notna(nat_val) and nat_val > 0:
                    radar_data.append({"指标": m, prov_name: round(prov_val / nat_val, 3), "全国平均": 1.0})

            if len(radar_data) >= 3:
                df_radar = pd.DataFrame(radar_data)
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=df_radar[prov_name], theta=df_radar["指标"],
                    fill="toself", name=prov_name, line_color="#00d4ff", fillcolor="rgba(0, 212, 255, 0.2)"
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=df_radar["全国平均"], theta=df_radar["指标"],
                    fill="toself", name="全国平均", line_color="#64748b", fillcolor="rgba(100, 116, 139, 0.1)"
                ))
                max_r = max(df_radar[prov_name].max(), 1.5)
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, max_r], gridcolor="rgba(255,255,255,0.1)"), angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")),
                    height=chart_height + 20, template="plotly_dark",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font_color="#e2e8f0"),
                    margin=dict(l=10, r=10, t=20, b=40),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("请选择至少3个指标以生成雷达图")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_wc:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">📊 指标规模-增速矩阵图</div>', unsafe_allow_html=True)
            # 单省模式下：各指标最新值 vs 年均增速散点图
            metric_scatter_data = []
            for m in selected_metrics:
                m_data = df_prov[df_prov["指标名称_纯"] == m].sort_values("年份")
                if len(m_data) >= 2:
                    s_val = m_data.iloc[0]["指标值"]
                    e_val = m_data.iloc[-1]["指标值"]
                    span = int(m_data.iloc[-1]["年份"] - m_data.iloc[0]["年份"])
                    cagr = safe_cagr(s_val, e_val, span)
                    latest_val = m_data.iloc[-1]["指标值"]
                    nat_avg = df_full[(df_full["指标名称_纯"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
                    vs_nat = latest_val / nat_avg if nat_avg and nat_avg > 0 else 0
                    metric_scatter_data.append({
                        "指标": m,
                        "最新值": latest_val,
                        "年均增速": cagr,
                        "相对全国": vs_nat,
                        "发展类型": "高规模高增长" if latest_val > nat_avg and cagr > 0.05 else
                                   "高规模低增长" if latest_val > nat_avg else
                                   "低规模高增长" if cagr > 0.05 else "低规模低增长"
                    })
            if len(metric_scatter_data) >= 3:
                df_ms = pd.DataFrame(metric_scatter_data)
                fig_ms = px.scatter(
                    df_ms, x="最新值", y="年均增速", size="相对全国", color="发展类型",
                    hover_name="指标", text="指标",
                    color_discrete_map={"高规模高增长": "#10b981", "高规模低增长": "#f59e0b",
                                        "低规模高增长": "#3b82f6", "低规模低增长": "#ef4444"},
                    template="plotly_dark",
                    labels={"最新值": "指标规模", "年均增速": "年均增速"}
                )
                fig_ms.update_traces(textposition="top center", textfont=dict(size=9, color="#e2e8f0"))
                fig_ms.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_ms.update_layout(
                    height=chart_height + 20,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font_color="#e2e8f0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0")
                )
                st.plotly_chart(fig_ms, use_container_width=True)
            else:
                st.info("请选择至少3个指标以生成分散矩阵图")
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
            m_data = df_prov[df_prov["指标名称_纯"] == m].sort_values("年份")
            unit = df_full[df_full["指标名称_纯"] == m]["单位"].iloc[0] if len(df_full[df_full["指标名称_纯"] == m]) > 0 else ""

            fig_multi.add_trace(
                go.Scatter(x=m_data["年份"], y=m_data["指标值"], name=m,
                          mode="lines+markers", line=dict(width=2.5, color=CUSTOM_COLORS[i % len(CUSTOM_COLORS)]), showlegend=False),
                row=row, col=col
            )
            fig_multi.update_yaxes(title_text=unit, row=row, col=col, gridcolor="rgba(255,255,255,0.1)")

        fig_multi.update_layout(
            height=chart_height + 120, template="plotly_dark",
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            showlegend=False
        )
        fig_multi.update_xaxes(gridcolor="rgba(255,255,255,0.1)")
        st.plotly_chart(fig_multi, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- 第三行：增速对比 + 规模对比 ----
        col_growth, col_bar = st.columns(2)

        with col_growth:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📉 各指标年均复合增速对比</div>', unsafe_allow_html=True)

            cagr_list = []
            for m in selected_metrics:
                m_data = df_prov[df_prov["指标名称_纯"] == m].sort_values("年份")
                if len(m_data) >= 2:
                    s_val = m_data.iloc[0]["指标值"]
                    e_val = m_data.iloc[-1]["指标值"]
                    span = int(m_data.iloc[-1]["年份"] - m_data.iloc[0]["年份"])
                    cagr = safe_cagr(s_val, e_val, span)
                    cagr_list.append({"指标": m, "年均增速": cagr})

            if cagr_list:
                df_cagr = pd.DataFrame(cagr_list).sort_values("年均增速", ascending=True)
                fig_cagr = px.bar(
                    df_cagr, y="指标", x="年均增速", orientation="h",
                    color="年均增速", color_continuous_scale="Cividis",
                    text_auto=".2%", template="plotly_dark"
                )
                fig_cagr.add_vline(x=0, line_dash="dash", line_color="gray")
                fig_cagr.update_layout(height=chart_height, showlegend=True,
                                       legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=9, color="#e2e8f0")),
                                       margin=dict(l=10, r=10, t=10, b=40),
                                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"))
                st.plotly_chart(fig_cagr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_bar:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">📊 {latest_year}年指标规模对比</div>', unsafe_allow_html=True)
            df_bar = df_prov_latest.sort_values("指标值", ascending=True)
            fig_bar = px.bar(
                df_bar, y="指标名称_纯", x="指标值", orientation="h",
                color="指标值", color_continuous_scale="Cividis",
                text_auto=".2f" if show_data_labels else False,
                template="plotly_dark"
            )
            fig_bar.update_layout(height=chart_height, showlegend=True,
                                  legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=9, color="#e2e8f0")),
                                  margin=dict(l=10, r=10, t=10, b=40),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"))
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- 综合诊断与建议 ----
        st.markdown('<h2 class="sub-header">💡 综合诊断与发展建议</h2>', unsafe_allow_html=True)

        detail_list = []
        for m in selected_metrics:
            m_val = df_prov_latest[df_prov_latest["指标名称_纯"] == m]["指标值"].mean()
            nat_avg = df_full[(df_full["指标名称_纯"] == m) & (df_full["年份"] == latest_year)]["指标值"].mean()
            unit = df_full[df_full["指标名称_纯"] == m]["单位"].iloc[0] if len(df_full[df_full["指标名称_纯"] == m]) > 0 else ""

            m_data = df_prov[df_prov["指标名称_纯"] == m].sort_values("年份")
            cagr = safe_cagr(m_data.iloc[0]["指标值"], m_data.iloc[-1]["指标值"],
                           int(m_data.iloc[-1]["年份"] - m_data.iloc[0]["年份"])) if len(m_data) >= 2 else 0

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
                    <b style="color:#10b981;">领先指标 {len(adv_metrics)} 个</b>，
                    <b style="color:#ef4444;">落后指标 {len(weak_metrics)} 个</b>，
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
    # 数据导出模块
    # ==================================================================
    st.markdown('<h2 class="sub-header">📋 数据预览与导出</h2>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    tab_data, tab_report = st.tabs(["明细数据", "分析报告"])
    with tab_data:
        show_cols = ["地区", "所属地域", "年份", "指标名称_纯", "指标值", "单位"]
        show_cols = [c for c in show_cols if c in df_filtered.columns]
        st.dataframe(df_filtered[show_cols].head(200), use_container_width=True, hide_index=True)

        csv_data = df_filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 下载完整明细数据 (CSV)",
            data=csv_data,
            file_name=f"省级数据库_分析数据_{selected_years[0]}-{selected_years[1]}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with tab_report:
        report = f"""中国省级数据库2025版 分析报告
{'='*50}
分析模式：{mode_desc}
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
            if analysis_mode == "🌍 省际对比分析":
                html_report = generate_html_report(
                    analysis_mode, selected_years, selected_provinces,
                    selected_metric, selected_metrics, df_filtered, df_full, metric_unit,
                    latest_year, avg_val, national_avg, max_val, cv_val, total_cagr
                )
            else:
                html_report = generate_html_report(
                    analysis_mode, selected_years, selected_provinces,
                    selected_metric, selected_metrics, df_filtered, df_full, metric_unit,
                    latest_year, detail_list=detail_list, above_avg_count=above_avg_count
                )

            st.download_button(
                label="🌐 下载精美HTML报告",
                data=html_report.encode("utf-8"),
                file_name=f"省级数据库HTML报告_{pd.Timestamp.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # 底部科技感配图
    network_img = get_image_base64("assets/network_bg.jpg")
    if network_img:
        st.markdown(f"""
        <div style="margin: 1rem 0 0.5rem 0; border-radius: 12px; overflow: hidden;">
            <img src="data:image/jpeg;base64,{network_img}" style="width: 100%; height: 120px; object-fit: cover; opacity: 0.5;">
        </div>
        """, unsafe_allow_html=True)

    # ---- 页脚 ----
    st.markdown("""
    <div class="footer">
        数据来源：中国省级数据库2025版 &nbsp;|&nbsp; 技术架构：Streamlit + Plotly + Pandas &nbsp;|&nbsp; 支持3000+省级经济社会指标可视化分析
        <br>© 2025 中国省级数据库可视化分析与决策支持平台
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
