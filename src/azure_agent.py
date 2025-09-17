import json
import re
from azure.ai.projects import AIProjectClient
from azure.identity import (
    DefaultAzureCredential,
    AzureCliCredential,
    AzureDeveloperCliCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
)
from azure.ai.agents.models import ListSortOrder
import streamlit as st

from .data_processing import (
    parse_agent_response,
    extract_structured_data_from_text,
    safe_get,
)
def build_credential():
    """優先度つきで認証情報を構築する。
    1) サービスプリンシパル (secrets: AZURE_TENANT_ID/AZURE_CLIENT_ID/AZURE_CLIENT_SECRET)
    2) 環境変数 (EnvironmentCredential)
    3) Azure Developer CLI (azd auth login)
    4) Azure CLI (az login)
    5) ブラウザ対話 (InteractiveBrowserCredential)
    6) DefaultAzureCredential 最後の保険
    """
    try:
        tenant_id = st.secrets.get("AZURE_TENANT_ID")
        client_id = st.secrets.get("AZURE_CLIENT_ID")
        client_secret = st.secrets.get("AZURE_CLIENT_SECRET")
        if tenant_id and client_id and client_secret:
            return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    except Exception:
        pass

    candidates = []
    try:
        candidates.append(EnvironmentCredential())
    except Exception:
        pass
    try:
        candidates.append(AzureDeveloperCliCredential())
    except Exception:
        pass
    try:
        candidates.append(AzureCliCredential())
    except Exception:
        pass
    try:
        candidates.append(InteractiveBrowserCredential())
    except Exception:
        pass
    # 最後に Default を追加
    try:
        candidates.append(DefaultAzureCredential(exclude_broker=True))
    except Exception:
        pass
    if not candidates:
        # フォールバック
        return DefaultAzureCredential(exclude_broker=True)
    return ChainedTokenCredential(*candidates)

def get_credential():
    """streamlit.py と同じ経路: DefaultAzureCredential を常に使用"""
    return DefaultAzureCredential()


def estimate_search_count(response_text: str) -> int:
    """応答テキストから推定検索回数を計算"""
    word_count = len(response_text.split())
    company_mentions = len(re.findall(r'(?:株式会社|Inc\.|Corp\.|Ltd\.)', response_text))
    base_count = min(15, max(5, word_count // 200))
    bonus_count = min(5, company_mentions)
    return base_count + bonus_count


def calculate_response_quality(parsed_data: dict) -> float:
    """応答データの品質スコアを計算"""
    score = 0.0
    max_score = 10.0
    quality_checks = [
        ("company_profile.official_name", 1.5),
        ("company_profile.business_overview", 1.0),
        ("industry_analysis.industry_name", 1.0),
        ("current_challenges", 1.5),
        ("focus_area_analysis.current_initiatives", 2.0),
        ("best_practices", 1.5),
        ("market_trends.key_trends", 1.0),
        ("industry_metrics", 0.5),
    ]
    for field_path, weight in quality_checks:
        field_value = safe_get(parsed_data, field_path)
        if field_value and field_value != "データ取得中..." and field_value != "調査実行中":
            if isinstance(field_value, list) and len(field_value) > 0:
                score += weight
            elif isinstance(field_value, str) and len(field_value) > 10:
                score += weight
            elif isinstance(field_value, dict) and field_value:
                score += weight
    return min(score, max_score)


def create_fallback_response(target: str, focus_area: str, error_reason: str) -> dict:
    """フォールバック応答の生成（エラー理由付き）"""
    industry_map = {
        "メルカリ": "フリマアプリ・C2C",
        "共同通信": "通信社・メディア",
        "ソフトバンク": "通信・IT",
        "トヨタ": "自動車製造",
        "楽天": "EC・フィンテック",
    }
    target_industry = "調査対象業界"
    for company, industry in industry_map.items():
        if company in target:
            target_industry = industry
            break
    fallback_data = {
        "company_profile": {
            "official_name": target,
            "established_year": "設立年を調査中",
            "employees": "従業員数を調査中",
            "revenue": "売上規模を調査中",
            "business_overview": f"{target}は{target_industry}業界で事業を展開する企業です。{focus_area}を中心とした事業戦略の詳細を調査中です。",
        },
        "industry_analysis": {
            "industry_name": target_industry + "業界",
            "market_size": "市場規模を調査中",
            "top5_companies": [
                {"rank": 1, "company": "業界リーダー企業", "market_share": "シェア調査中", "competitive_advantage": "優位性分析中"}
            ],
        },
        "current_challenges": [
            {"specific_issue": f"{target}の主要課題を分析中", "business_impact": "ビジネス影響を評価中"},
            {"specific_issue": f"{focus_area}に関連する課題を調査中", "business_impact": "改善効果を試算中"},
        ],
        "focus_area_analysis": {
            "current_initiatives": [
                {"initiative": f"{focus_area}への取り組み状況を調査中", "results": {"quantitative": "効果測定を実行中"}}
            ]
        },
        "best_practices": [
            {"company": "業界先進企業", "results": f"{focus_area}における成功事例を収集中"}
        ],
        "market_trends": {
            "key_trends": [
                {"trend_name": f"{target_industry}のデジタル変革", "description": "業界全体でのDX推進動向を分析中"}
            ]
        },
        "industry_metrics": {
            "efficiency_improvement": "改善率を調査中",
            "revenue_increase": "成長率を調査中",
            "cost_reduction": "削減率を調査中",
            "productivity_gain": "生産性向上率を調査中",
        },
        "industry_voice": f"{target_industry}業界では「{focus_area}への注目が高まっている」との声が多く聞かれます。",
        "research_status": "fallback",
        "error_reason": error_reason,
        "search_count": 0,
        "data_quality_score": 4.0,
    }
    return fallback_data


def call_azure_ai_agent(target: str, focus_area: str, specific_requirements: str):
    """Azure AI Foundryエージェントを呼び出す関数（分割版）"""
    try:
        # secrets.tomlから設定を取得
        endpoint = st.secrets["AZURE_AI_ENDPOINT"]
        agent_id = st.secrets["AZURE_AGENT_ID"]

        project = AIProjectClient(
            credential=get_credential(),
            endpoint=endpoint,
        )
        agent = project.agents.get_agent(agent_id)
        thread = project.agents.threads.create()

        # streamlit.py と同じシンプルなプロンプト
        user_message = f"""
        企業・個人調査を実行してください。

        調査対象: {target}
        調査観点: {focus_area}
        特定要求: {specific_requirements if specific_requirements else "なし"}

        以下の7階層分析フレームワークで調査し、JSON形式で結果を返してください：

        1. 企業基本データ（正式名称、設立年、従業員数、売上高、事業概要）
        2. 業界構造・競合ポジション（業界名、市場規模、Top5企業、市場シェア）
        3. 業界トレンド・市場動向（主要トレンド、成長率、破壊的要因）
        4. 現状課題・問題点（組織、技術、市場面での具体的課題）
        5. 調査観点の詳細分析（現在の取り組み、使用ツール、定量効果）
        6. ベストプラクティス・先進事例（成功企業の具体的事例と成果）
        7. 実践的スライド構成提案

        必須JSON構造:
        {{
            "company_profile": {{
                "official_name": "正式企業名",
                "established_year": "設立年",
                "employees": "従業員数",
                "revenue": "売上高",
                "business_overview": "事業概要"
            }},
            "industry_analysis": {{
                "industry_name": "業界名",
                "market_size": "市場規模",
                "top5_companies": [
                    {{"rank": 1, "company": "企業名", "market_share": "シェア", "competitive_advantage": "競争優位性"}}
                ]
            }},
            "current_challenges": [
                {{"specific_issue": "具体的課題", "business_impact": "事業への影響"}}
            ],
            "focus_area_analysis": {{
                "current_initiatives": [
                    {{"initiative": "取り組み名", "results": {{"quantitative": "定量効果"}}}}
                ]
            }},
            "best_practices": [
                {{"company": "先進企業名", "results": "具体的成果"}}
            ]
        }}
        """

        message = project.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )
        run = project.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        if run.status == "failed":
            st.error(f"Agent実行失敗: {run.last_error}")
            return None

        messages = project.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING,
        )
        agent_response = None
        for message in messages:
            if message.role == "assistant" and message.text_messages:
                agent_response = message.text_messages[-1].text.value
        if not agent_response:
            st.error("エージェントからのレスポンスが取得できませんでした")
            return None

        parsed_response = parse_agent_response(agent_response, target, focus_area)
        if parsed_response:
            parsed_response["research_status"] = "completed"
            parsed_response["search_count"] = estimate_search_count(agent_response)
            parsed_response["data_quality_score"] = calculate_response_quality(parsed_response)
            parsed_response["raw_response"] = agent_response
            return parsed_response
        else:
            st.error("JSON解析に失敗しました")
            st.write("エージェントレスポンス:", agent_response)
            return None

    except Exception as e:
        st.error(f"Azure AI Agent呼び出しエラー: {str(e)}")
        
        # エラー時のフォールバック：構造化されたモックレスポンス
        st.warning("デモモードで動作します")
        return create_fallback_response(target, focus_area, f"exception: {str(e)}")


def test_connection() -> dict:
    """サンプル相当の最小接続テスト。詳細な失敗理由を返す。"""
    try:
        endpoint = st.secrets.get("AZURE_AI_ENDPOINT")
        agent_id = st.secrets.get("AZURE_AGENT_ID")
        if not endpoint or not agent_id:
            return {"ok": False, "stage": "config", "detail": "AZURE_AI_ENDPOINT / AZURE_AGENT_ID 未設定"}

        project = AIProjectClient(credential=get_credential(), endpoint=endpoint)
        agent = project.agents.get_agent(agent_id)
        thread = project.agents.threads.create()
        project.agents.messages.create(thread_id=thread.id, role="user", content="Hi Agent (connectivity test)\nReturn: ok")
        run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        if run.status == "failed":
            return {"ok": False, "stage": "run", "detail": str(run.last_error)}
        messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        texts = []
        for msg in messages:
            if msg.text_messages:
                texts.append({"role": msg.role, "text": msg.text_messages[-1].text.value})
        return {"ok": True, "stage": "done", "messages": texts}
    except Exception as e:
        return {"ok": False, "stage": "exception", "detail": str(e)}


