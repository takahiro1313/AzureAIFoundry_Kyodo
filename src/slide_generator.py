from datetime import datetime
import streamlit as st

from .data_processing import safe_get, safe_get_list


def generate_html_slides(research_data, target, focus_area):
    """調査データからHTMLスライドを生成（完全変数化版）"""
    # 調査データから値を取得（デフォルト値付き）
    company_profile = research_data.get('company_profile', {})
    industry_analysis = research_data.get('industry_analysis', {})
    current_challenges = research_data.get('current_challenges', [])
    focus_area_analysis = research_data.get('focus_area_analysis', {})
    best_practices = research_data.get('best_practices', [])
    market_trends = research_data.get('market_trends', {})
    industry_metrics = research_data.get('industry_metrics', {})
    
    # 基本情報の取得
    company_name = company_profile.get('official_name', target)
    established_year = company_profile.get('established_year', '調査実行中')
    employees = company_profile.get('employees', '調査実行中')
    revenue = company_profile.get('revenue', '調査実行中')
    business_overview = company_profile.get('business_overview', '調査実行中')
    
    # 業界分析データの取得
    industry_name = industry_analysis.get('industry_name', '調査対象業界')
    market_size = industry_analysis.get('market_size', '調査実行中')
    top5_companies = industry_analysis.get('top5_companies', [])
    
    # 業界トレンドの取得
    key_trends = safe_get_list(market_trends, 'key_trends')
    
    # 業界メトリクスの取得
    efficiency_improvement = safe_get(industry_metrics, 'efficiency_improvement', '40-70%')
    revenue_increase = safe_get(industry_metrics, 'revenue_increase', '20-50%')
    cost_reduction = safe_get(industry_metrics, 'cost_reduction', '30-40%')
    productivity_gain = safe_get(industry_metrics, 'productivity_gain', '35%')
    
    # 業界の声
    industry_voice = safe_get(research_data, 'industry_voice', '業界関係者からの情報を収集中...')
    
    # 追加データ項目の取得
    revenue_structure = safe_get(company_profile, 'revenue_structure', '調査実行中')
    business_model = safe_get(company_profile, 'business_model', '調査実行中')
    market_position = safe_get(industry_analysis, 'market_position', '詳細分析実行中')
    current_level = safe_get(focus_area_analysis, 'current_level', '分析実行中')
    industry_average = safe_get(focus_area_analysis, 'industry_average', 'データ収集中')
    improvement_potential = safe_get(focus_area_analysis, 'improvement_potential', '評価中')
    
    # 課題データの取得
    challenges_html = ""
    for challenge in current_challenges[:3]:  # 最大3つまで表示
        challenge_text = challenge.get('specific_issue', '課題情報を収集中')
        challenges_html += f'<div class="bullet-point">{challenge_text}</div>'
    
    if not challenges_html:
        challenges_html = '<div class="bullet-point">課題情報を収集中...</div>'
    
    # 調査観点分析データの取得
    initiatives = focus_area_analysis.get('current_initiatives', [])
    initiatives_html = ""
    for initiative in initiatives[:3]:
        init_name = initiative.get('initiative', '取り組み情報を収集中')
        init_results = initiative.get('results', {}).get('quantitative', '効果測定中')
        initiatives_html += f'<div class="highlight-box"><strong>{init_name}:</strong> {init_results}</div>'
    
    if not initiatives_html:
        initiatives_html = f'<div class="highlight-box"><strong>{focus_area}の詳細分析:</strong> データ収集を実行中...</div>'
    
    # 先進事例データの取得
    best_practices_html = ""
    for practice in best_practices[:3]:
        company = practice.get('company', '先進企業')
        results = practice.get('results', '成果情報を調査中')
        best_practices_html += f'<div class="bullet-point"><strong>{company}:</strong> {results}</div>'
    
    if not best_practices_html:
        best_practices_html = f'<div class="bullet-point">{focus_area}に関する先進事例を調査中...</div>'
    
    # 業界トレンドHTMLの生成
    trends_html = ""
    if key_trends:
        for i, trend in enumerate(key_trends[:4], 1):
            trend_name = trend.get('trend_name', 'トレンド情報収集中')
            description = trend.get('description', '詳細分析中')
            trends_html += f'<div class="bullet-point">{trend_name}: {description}</div>'
    else:
        trends_html = '<div class="bullet-point">業界トレンドデータを収集中...</div>'
    
    # Top5企業テーブルの生成
    top5_table = "<tr><th>順位</th><th>企業名</th><th>市場シェア</th><th>強み</th></tr>"
    if top5_companies:
        for company in top5_companies[:5]:
            rank = company.get('rank', '-')
            name = company.get('company', '企業名調査中')
            share = company.get('market_share', '-%')
            strength = company.get('competitive_advantage', '調査中')
            top5_table += f"<tr><td>{rank}</td><td>{name}</td><td>{share}</td><td>{strength}</td></tr>"
    else:
        top5_table += "<tr><td colspan='4'>競合企業データを収集中...</td></tr>"
    
    # スライドテンプレート用CSS
    slide_css = """
    <style>
        .slide-container {
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
            font-family: 'Arial', sans-serif;
        }
        
        .slide {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 40px;
            margin: 20px 0;
            min-height: 500px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            page-break-after: always;
        }
        
        .slide-header {
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        
        .slide-title {
            font-size: 28px;
            font-weight: bold;
            color: #1f77b4;
            margin: 0;
        }
        
        .slide-content {
            display: flex;
            gap: 30px;
        }
        
        .content-left {
            flex: 1;
        }
        
        .content-right {
            flex: 1;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin: 20px 0 10px 0;
            display: flex;
            align-items: center;
        }
        
        .section-icon {
            width: 24px;
            height: 24px;
            margin-right: 8px;
            background: #1f77b4;
            border-radius: 50%;
            display: inline-block;
        }
        
        .bullet-point {
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .bullet-point::before {
            content: "•";
            color: #1f77b4;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .data-table th {
            background: #f8f9fa;
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }
        
        .data-table td {
            border: 1px solid #ddd;
            padding: 10px;
        }
        
        .highlight-box {
            background: #e3f2fd;
            border-left: 4px solid #1f77b4;
            padding: 15px;
            margin: 15px 0;
        }
        
        .metric-box {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 10px;
        }
        
        .metric-number {
            font-size: 36px;
            font-weight: bold;
            color: #1f77b4;
        }
        
        .metric-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        
        @media print {
            .slide {
                break-inside: avoid;
                page-break-after: always;
            }
        }
    </style>
    """
    
    # スライド1: 企業概要と現状の主要課題
    slide1 = f"""
    <div class="slide">
        <div class="slide-header">
            <h1 class="slide-title">{company_name}の現在地 — 事業概要・主要課題</h1>
        </div>
        <div class="slide-content">
            <div class="content-left">
                <div class="section-title">
                    <span class="section-icon"></span>事業構成
                </div>
                <div class="bullet-point">{business_overview}</div>
                <div class="bullet-point">主要サービス・製品: {focus_area}関連調査実行中</div>
                <div class="bullet-point">収益構造: {revenue_structure}</div>
                <div class="bullet-point">事業モデル: {business_model}</div>
                
                <div class="section-title">
                    <span class="section-icon"></span>現状の主要課題
                </div>
                {challenges_html}
            </div>
            <div class="content-right">
                <div class="highlight-box">
                    <strong>企業データサマリー</strong><br>
                    売上高: {revenue}<br>
                    従業員数: {employees}<br>
                    設立年: {established_year}<br>
                    業界: {industry_name}
                </div>
            </div>
        </div>
    </div>
    """
    
    # スライド2: 業界構造と競合ポジション
    slide2 = f"""
    <div class="slide">
        <div class="slide-header">
            <h1 class="slide-title">業界構造と日々の変化・競合動向（{industry_name}）</h1>
        </div>
        <div class="slide-content">
            <div class="content-left">
                <div class="section-title">
                    <span class="section-icon"></span>業界Top5企業
                </div>
                <table class="data-table">
                    {top5_table}
                </table>
                
                <div class="section-title">
                    <span class="section-icon"></span>市場データ
                </div>
                <div class="highlight-box">
                    <strong>市場規模:</strong> {market_size}<br>
                    <strong>調査対象ポジション:</strong> {market_position}
                </div>
            </div>
            <div class="content-right">
                <div class="highlight-box">
                    <strong>業界変化と主要トレンド</strong>
                    {trends_html}
                </div>
            </div>
        </div>
    </div>
    """
    
    # スライド3: 調査観点の活用事例（実データ使用）
    slide3 = f"""
    <div class="slide">
        <div class="slide-header">
            <h1 class="slide-title">{focus_area}の取り組み状況と活用事例</h1>
        </div>
        <div class="slide-content">
            <div class="content-left">
                <div class="section-title">
                    <span class="section-icon"></span>{company_name}の現状
                </div>
                {initiatives_html}
                
                <div class="section-title">
                    <span class="section-icon"></span>業界での位置づけ
                </div>
                <div class="highlight-box">
                    調査対象企業の{focus_area}への取り組みレベル: {current_level}<br>
                    業界平均との比較: {industry_average}<br>
                    改善ポテンシャル: {improvement_potential}
                </div>
            </div>
            <div class="content-right">
                <div class="section-title">
                    <span class="section-icon"></span>業界先進事例
                </div>
                {best_practices_html}
            </div>
        </div>
    </div>
    """
    
    # 先進事例の分類（海外・国内）
    overseas_cases = []
    domestic_cases = []
    overseas_keywords = ["AP通信", "ロイター", "Bloomberg", "Reuters", "AFP", "NYT", "BBC", "CNN", "Microsoft", "Google", "Apple"]
    domestic_keywords = ["日経", "朝日", "読売", "毎日", "共同通信", "時事通信", "ソフトバンク", "楽天", "メルカリ"]
    
    for practice in best_practices:
        company = practice.get('company', '')
        if any(keyword in company for keyword in overseas_keywords):
            overseas_cases.append(practice)
        elif any(keyword in company for keyword in domestic_keywords):
            domestic_cases.append(practice)
        else:
            domestic_cases.append(practice)
    
    # 海外事例HTML
    overseas_html = ""
    if overseas_cases:
        for case in overseas_cases[:3]:
            company = case.get('company', '海外企業')
            results = case.get('results', '成果調査中')
            overseas_html += f'<div class="bullet-point"><strong>{company}:</strong> {results}</div>'
    else:
        overseas_html = '<div class="bullet-point">海外企業の先進事例を収集中...</div>'
    
    # 国内事例HTML
    domestic_html = ""
    if domestic_cases:
        for case in domestic_cases[:3]:
            company = case.get('company', '国内企業')
            results = case.get('results', '成果調査中')
            domestic_html += f'<div class="bullet-point"><strong>{company}:</strong> {results}</div>'
    else:
        domestic_html = '<div class="bullet-point">国内企業の成功事例を収集中...</div>'

    # スライド4: 先進事例とベンチマーク
    slide4 = f"""
    <div class="slide">
        <div class="slide-header">
            <h1 class="slide-title">先進事例とベンチマーク — 国内外の成功ケース</h1>
        </div>
        <div class="slide-content">
            <div class="content-left">
                <div class="section-title">
                    <span class="section-icon"></span>海外の成功事例
                </div>
                {overseas_html}
                
                <div class="section-title">
                    <span class="section-icon"></span>国内の取り組み
                </div>
                {domestic_html}
            </div>
            <div class="content-right">
                <div class="highlight-box">
                    <strong>{focus_area}導入による主な効果</strong>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px;">
                        <div class="metric-box" style="flex: 1;">
                            <div class="metric-number">{efficiency_improvement}</div>
                            <div class="metric-label">効率改善率</div>
                        </div>
                        <div class="metric-box" style="flex: 1;">
                            <div class="metric-number">{revenue_increase}</div>
                            <div class="metric-label">収益向上率</div>
                        </div>
                        <div class="metric-box" style="flex: 1;">
                            <div class="metric-number">{cost_reduction}</div>
                            <div class="metric-label">コスト削減率</div>
                        </div>
                        <div class="metric-box" style="flex: 1;">
                            <div class="metric-number">{productivity_gain}</div>
                            <div class="metric-label">生産性向上率</div>
                        </div>
                    </div>
                </div>
                
                <div class="highlight-box">
                    <strong>業界の声</strong><br>
                    {industry_voice}
                </div>
            </div>
        </div>
    </div>
    """
    
    # 完全なHTML文書として結合
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{target} - {focus_area} 調査レポート</title>
        {slide_css}
    </head>
    <body>
        <div class="slide-container">
            {slide1}
            {slide2}
            {slide3}
            {slide4}
        </div>
    </body>
    </html>
    """
    
    return full_html


def generate_slides_with_html(research_data, target, focus_area):
    """HTMLスライドを生成する関数"""
    try:
        # HTMLスライドを生成
        html_slides = generate_html_slides(research_data, target, focus_area)
        
        # ファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.html"
        
        return {
            "html_content": html_slides,
            "filename": filename,
            "slide_count": 4,
            "format": "HTML"
        }
        
    except Exception as e:
        st.error(f"HTMLスライド生成エラー: {str(e)}")
        return None

