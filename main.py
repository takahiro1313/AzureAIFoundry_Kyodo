import streamlit as st
import json
import time
import re
from datetime import datetime
import pandas as pd
from src import azure_agent, slide_generator
from src.azure_agent import create_fallback_response

# ページ設定
st.set_page_config(
    page_title="企業・個人調査AIエージェント",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .input-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .status-processing {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .status-complete {
        background-color: #d1edff;
        border-left: 4px solid #0066cc;
    }
    .status-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .data-quality-high { color: #28a745; font-weight: bold; }
    .data-quality-medium { color: #ffc107; font-weight: bold; }
    .data-quality-low { color: #dc3545; font-weight: bold; }
    
    /* ボタン中央配置用のCSS */
    .center-button {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }
    .center-button .stButton > button {
        width: 100%;
        max-width: 300px;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'research_status' not in st.session_state:
    st.session_state.research_status = 'ready'
if 'slide_generated' not in st.session_state:
    st.session_state.slide_generated = False
if 'search_params' not in st.session_state:
    st.session_state.search_params = {}

# データ処理関数は src/data_processing.py から使用
from src.data_processing import (
    safe_get, safe_get_list, extract_year, extract_employee_count, 
    extract_revenue, extract_business_overview, extract_industry_name,
    extract_market_size, extract_challenges, extract_initiatives,
    extract_best_practices, extract_trends, extract_metrics, extract_industry_voice
)

# Azure AI Agent関数は src/azure_agent.py から使用

# スライド生成関数は src/slide_generator.py から使用

# ===== UI関数群 =====

def validate_target(target):
    """調査対象のバリデーション"""
    if not target:
        return {"valid": False, "message": ""}
    
    if len(target) < 2:
        return {"valid": False, "message": "調査対象は2文字以上で入力してください"}
    
    if len(target) > 100:
        return {"valid": False, "message": "調査対象は100文字以内で入力してください"}
    
    # 不適切なキーワードチェック
    prohibited_keywords = ["test", "テスト", "検証", "sample"]
    if any(keyword.lower() in target.lower() for keyword in prohibited_keywords):
        return {"valid": False, "message": "実際の企業名または人名を入力してください"}
    
    return {"valid": True, "message": ""}

def get_focus_area_suggestions(focus_area):
    """調査観点のサジェスト"""
    suggestion_map = {
        "AI": ["生成AI", "機械学習", "自動化", "ChatGPT", "AI活用"],
        "DX": ["デジタル変革", "IT導入", "業務効率化", "クラウド", "デジタル化"],
        "マーケティング": ["デジタルマーケティング", "SNS活用", "広告戦略", "顧客分析"],
        "人材": ["採用戦略", "人材育成", "働き方改革", "組織改革", "人事制度"]
    }
    
    suggestions = []
    for key, values in suggestion_map.items():
        if key.lower() in focus_area.lower():
            suggestions.extend(values)
            break
    
    return suggestions[:3]

def display_enhanced_progress(target, focus_area):
    """拡張進捗表示"""
    st.markdown('<div class="status-box status-processing">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("🔄 AI Agentが調査を実行中...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        detail_text = st.empty()
        
    with col2:
        st.write("**調査設定**")
        st.write(f"🎯 **対象:** {target}")
        st.write(f"🔍 **観点:** {focus_area}")
        st.write(f"⏰ **開始:** {datetime.now().strftime('%H:%M:%S')}")
    
    # 詳細な進捗シミュレーション
    stages = [
        (15, "Azure AI Agentを初期化中...", "エージェント接続を確立"),
        (30, "Web検索を実行中...", "企業情報・業界データを収集"),
        (50, "業界分析を実行中...", "競合企業・市場規模を調査"),
        (70, "先進事例を調査中...", "ベストプラクティスを収集"),
        (85, "データを構造化中...", "JSON形式でデータを整理"),
        (95, "品質チェック実行中...", "データの妥当性を検証"),
        (100, "調査完了", "レポート生成準備完了")
    ]
    
    for progress, main_status, detail_status in stages:
        progress_bar.progress(progress)
        status_text.text(main_status)
        detail_text.text(f"📋 {detail_status}")
        time.sleep(0.3)  # 実際の処理時間に合わせて調整
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 実際の調査実行
    results = azure_agent.call_azure_ai_agent(target, focus_area, "")
    
    # streamlit.py と同じ判定
    if results:
        st.session_state.research_results = results
        st.session_state.research_status = 'completed'
        
        # データ品質の表示
        quality_score = results.get('data_quality_score', 0)
        if quality_score >= 8:
            st.success(f"✅ 調査完了！ 📊 データ品質: 優秀 ({quality_score:.1f}/10)")
        elif quality_score >= 6:
            st.success(f"✅ 調査完了！ 📊 データ品質: 良好 ({quality_score:.1f}/10)")
        elif quality_score >= 4:
            st.warning(f"⚠️ 調査完了（一部制限） 📊 データ品質: 改善の余地あり ({quality_score:.1f}/10)")
        else:
            st.info(f"ℹ️ 調査完了（フォールバックモード） 📊 データ品質: 基本レベル ({quality_score:.1f}/10)")
        
        st.rerun()
    else:
        st.session_state.research_status = 'error'
        st.rerun()

# ===== メイン関数 =====

def main():
    st.markdown('<h1 class="main-header">🔍 企業・個人調査AIエージェント</h1>', unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.header("システム情報")
        if st.button("🧪 Azure接続テスト", use_container_width=True):
            res = azure_agent.test_connection()
            if res.get("ok"):
                st.success("Azure接続: OK")
                with st.expander("レスポンス"):
                    st.json(res)
            else:
                st.error("Azure接続: 失敗")
                st.write(f"ステージ: {res.get('stage')}")
                st.write(f"詳細: {res.get('detail')}")
        st.info("""        
        **調査項目:**
        - 企業基本データ ✓
        - 業界構造・競合比較 ✓  
        - 業界トレンド ✓
        - 現状課題 ✓
        - 調査観点詳細分析 ✓
        - 先進事例・ベンチマーク ✓
        - スライド構成提案 ✓
        """)
        
        # システム状態表示
        if st.session_state.research_results:
            quality = st.session_state.research_results.get('data_quality_score', 0)
            if quality >= 8:
                st.success("✅ 高品質データで調査完了")
            elif quality >= 6:
                st.success("✅ 良品質データで調査完了")
            else:
                st.warning("⚠️ 基本データで調査完了")
            
            if st.session_state.slide_generated:
                st.success("✅ スライド生成完了")

    # 入力セクション
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.subheader("📝 調査対象の設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target = st.text_input(
                "調査対象 *",
                placeholder="例: 株式会社メルカリ、共同通信社",
                help="企業名または人名を入力してください"
            )
            
            # リアルタイムバリデーション
            if target:
                target_validation = validate_target(target)
                if not target_validation["valid"]:
                    st.warning(target_validation["message"])
                else:
                    st.success("✓ 有効な調査対象です")
            
        with col2:
            focus_area = st.text_input(
                "調査観点 *", 
                placeholder="例: 生成AI活用状況、DX推進の取り組み",
                help="調査したい観点をフリーワードで入力"
            )
            
            # サジェスト機能
            if focus_area:
                suggestions = get_focus_area_suggestions(focus_area)
                if suggestions:
                    st.info(f"💡 関連キーワード: {', '.join(suggestions)}")
        
        specific_requirements = st.text_area(
            "特定要求（任意）",
            placeholder="例: 直近1年の動向に絞って調査、定量データを重点的に収集",
            help="特に詳しく調べたい領域や制約条件があれば入力"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 実行ボタン
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        target_valid = validate_target(target).get("valid", False) if target else False
        can_execute = target and focus_area and target_valid
        
        # ボタンを中央に配置
        st.markdown('<div class="center-button">', unsafe_allow_html=True)
        if st.button("🚀 AI調査開始", type="primary", disabled=not can_execute):
            if can_execute:
                st.session_state.research_status = 'processing'
                st.session_state.research_results = None
                st.session_state.slide_generated = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 処理状況表示
    if st.session_state.research_status == 'processing':
        display_enhanced_progress(target, focus_area)
    
    # 結果表示
    if st.session_state.research_results and st.session_state.research_status == 'completed':
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.subheader("📊 調査結果")
        
        # データ品質とメタ情報
        results = st.session_state.research_results
        quality_score = results.get('data_quality_score', 0)
        search_count = results.get('search_count', 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            quality_class = "data-quality-high" if quality_score >= 8 else "data-quality-medium" if quality_score >= 6 else "data-quality-low"
            st.markdown(f'<span class="{quality_class}">品質スコア: {quality_score:.1f}/10</span>', unsafe_allow_html=True)
        with col2:
            st.metric("検索実行回数", search_count)
        with col3:
            status = results.get('research_status', 'unknown')
            status_text = "✅ 完了" if status == 'completed' else "🔄 フォールバック" if status == 'fallback' else "❓ 不明"
            st.write(f"**ステータス:** {status_text}")
        
        # タブで結果を整理
        tab1, tab2, tab3, tab4 = st.tabs(["📈 概要サマリー", "🏢 詳細データ", "📋 構造化データ", "🎯 スライド生成"])
        
        with tab1:
            st.write("### 📊 調査概要")
            
            # 企業基本情報
            company_profile = results.get('company_profile', {})
            if company_profile:
                st.write("#### 🏢 企業基本情報")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**正式名称:** {company_profile.get('official_name', target)}")
                    st.write(f"**設立年:** {company_profile.get('established_year', '調査中')}")
                with col2:
                    st.write(f"**従業員数:** {company_profile.get('employees', '調査中')}")
                    st.write(f"**売上高:** {company_profile.get('revenue', '調査中')}")
                
                business_overview = company_profile.get('business_overview', '')
                if business_overview and business_overview != "データ取得中...":
                    st.write(f"**事業概要:** {business_overview}")
            
            # 業界分析サマリー
            industry_analysis = results.get('industry_analysis', {})
            if industry_analysis:
                st.write("#### 🏭 業界分析")
                st.write(f"**業界:** {industry_analysis.get('industry_name', '調査中')}")
                st.write(f"**市場規模:** {industry_analysis.get('market_size', '調査中')}")
            
            # 主要課題
            challenges = results.get('current_challenges', [])
            if challenges:
                st.write("#### ⚠️ 主要課題")
                for i, challenge in enumerate(challenges[:3], 1):
                    issue = challenge.get('specific_issue', '課題情報なし')
                    st.write(f"{i}. {issue}")
            
            # 調査観点の現状
            focus_analysis = results.get('focus_area_analysis', {})
            initiatives = focus_analysis.get('current_initiatives', [])
            if initiatives:
                st.write(f"#### 🎯 {focus_area} - 現在の取り組み")
                for initiative in initiatives[:2]:
                    name = initiative.get('initiative', '取り組み名不明')
                    result = initiative.get('results', {})
                    if isinstance(result, dict):
                        effect = result.get('quantitative', '効果不明')
                    else:
                        effect = str(result)
                    st.write(f"• **{name}:** {effect}")
        
        with tab2:
            st.write("### 🔍 詳細分析結果")
            
            # エラー情報がある場合は表示
            if results.get('error_reason'):
                st.warning(f"⚠️ 注意: {results.get('error_reason')}")
            
            # 業界トレンド
            market_trends = results.get('market_trends', {})
            trends = market_trends.get('key_trends', [])
            if trends:
                st.write("#### 📈 業界トレンド")
                for trend in trends:
                    name = trend.get('trend_name', 'トレンド名不明')
                    desc = trend.get('description', '説明なし')
                    st.write(f"**{name}:** {desc}")
            
            # 先進事例
            best_practices = results.get('best_practices', [])
            if best_practices:
                st.write("#### 🌟 先進事例")
                for practice in best_practices:
                    company = practice.get('company', '企業名不明')
                    result = practice.get('results', '結果不明')
                    st.write(f"**{company}:** {result}")
            
            # 業界メトリクス
            metrics = results.get('industry_metrics', {})
            if metrics:
                st.write("#### 📊 業界メトリクス")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("効率改善率", metrics.get('efficiency_improvement', '調査中'))
                    st.metric("コスト削減率", metrics.get('cost_reduction', '調査中'))
                with col2:
                    st.metric("収益向上率", metrics.get('revenue_increase', '調査中'))
                    st.metric("生産性向上率", metrics.get('productivity_gain', '調査中'))
            
            # 業界の声
            industry_voice = results.get('industry_voice', '')
            if industry_voice and industry_voice != "業界関係者からの情報を収集中...":
                st.write("#### 💬 業界関係者の声")
                st.info(f'"{industry_voice}"')
        
        with tab3:
            st.write("### 📋 構造化データ（JSON形式）")
            
            # デバッグ情報の表示オプション
            show_debug = st.checkbox("デバッグ情報を表示", value=False)
            
            if show_debug and results.get('raw_response'):
                st.write("#### 🔧 生のエージェント応答")
                st.text_area("エージェント応答", results['raw_response'], height=200)
            
            # メインデータの表示
            st.write("#### 📊 構造化済みデータ")
            
            # メタデータを除いたクリーンなデータを表示
            clean_data = {k: v for k, v in results.items() 
                         if k not in ['raw_response', 'research_status', 'search_count', 'data_quality_score', 'error_reason']}
            
            st.json(clean_data)
            
            # データ完成度の表示
            total_fields = 8  # 主要フィールド数
            completed_fields = sum(1 for key in ['company_profile', 'industry_analysis', 'current_challenges', 
                                               'focus_area_analysis', 'best_practices', 'market_trends', 
                                               'industry_metrics', 'industry_voice'] 
                                 if results.get(key))
            
            completion_rate = (completed_fields / total_fields) * 100
            st.write(f"**データ完成度:** {completion_rate:.0f}% ({completed_fields}/{total_fields} フィールド)")
        
        with tab4:
            st.write("### 🎯 プレゼンテーション用スライド生成")
            
            if not st.session_state.slide_generated:
                st.write("調査結果を元に、4枚構成のHTMLスライドを生成します。")
                
                # スライド構成の説明
                st.write("#### 📋 スライド構成")
                slide_structure = [
                    "**スライド1:** 企業概要と主要課題",
                    "**スライド2:** 業界構造と市場動向", 
                    "**スライド3:** 調査観点の取り組み状況",
                    "**スライド4:** 先進事例とベンチマーク"
                ]
                for slide in slide_structure:
                    st.write(f"- {slide}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 スライド生成開始", type="primary"):
                        with st.spinner("HTMLスライドを生成中..."):
                            slide_result = slide_generator.generate_slides_with_html(results, target, focus_area)
                            if slide_result:
                                st.session_state.slide_result = slide_result
                                st.session_state.slide_generated = True
                                st.success("✅ スライド生成完了!")
                                st.rerun()
                            else:
                                st.error("❌ スライド生成に失敗しました")
                
                with col2:
                    st.info("💡 **スライドの特徴**\n- 実データを100%反映\n- プリント対応\n- ブラウザで閲覧可能\n- PDF変換可能")
            
            else:
                st.success("✅ スライド生成完了!")
                slide_result = st.session_state.slide_result
                
                # スライド情報
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("生成スライド数", f"{slide_result['slide_count']}枚")
                with col2:
                    st.metric("フォーマット", slide_result['format'])
                with col3:
                    st.metric("ファイルサイズ", f"{len(slide_result['html_content'])//1024}KB")
                
                # プレビュー表示
                st.write("#### 👀 スライドプレビュー")
                
                # HTMLをStreamlitで表示
                st.components.v1.html(
                    slide_result['html_content'],
                    height=600,
                    scrolling=True
                )
                
                # ダウンロード機能
                st.write("#### 💾 ダウンロード")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 HTMLファイルをダウンロード",
                        data=slide_result['html_content'],
                        file_name=slide_result['filename'],
                        mime='text/html',
                        type="primary",
                        help="ブラウザで開いてプレゼンテーション可能"
                    )
                
                with col2:
                    st.info("💡 **PDF化する場合**\nHTMLファイルをブラウザで開き、\n印刷 → PDFで保存してください")
                
                # スライドの詳細情報
                st.write("#### ℹ️ スライド詳細")
                st.write(f"- **ファイル名:** {slide_result['filename']}")
                st.write(f"- **生成時刻:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
                st.write(f"- **データ品質:** {results.get('data_quality_score', 0):.1f}/10")
                st.write(f"- **使用データ:** {results.get('search_count', 0)}回の検索結果")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 新しい調査を開始するボタン
        st.write("---")
        st.markdown('<div class="center-button">', unsafe_allow_html=True)
        if st.button("🔄 新しい調査を開始", type="secondary"):
                # セッション状態をクリア
                for key in ['research_results', 'research_status', 'slide_generated', 'slide_result']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.research_status = 'ready'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.research_status == 'error':
        st.markdown('<div class="status-box status-error">', unsafe_allow_html=True)
        st.error("❌ 調査中にエラーが発生しました。再度お試しください。")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 再試行"):
                st.session_state.research_status = 'ready'
                st.rerun()
        with col2:
            if st.button("🔄 リトライ"):
                st.session_state.research_status = 'ready'
                st.rerun()
    
    # フッター
    st.write("---")
    st.write("🔍 **企業・個人調査AIエージェント** | Powered by Azure AI Foundry & Streamlit")
    st.write("💡 本システムは調査結果を参考情報として提供します。最終的な意思決定には追加の検証をお勧めします。")

if __name__ == "__main__":
    main()