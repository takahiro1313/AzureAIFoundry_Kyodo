import re
import json


def safe_get(data, keys, default="データ取得中..."):
    """ネストした辞書から安全にデータを取得"""
    try:
        result = data
        for key in keys.split('.'):
            if isinstance(result, dict):
                result = result.get(key, {})
            else:
                return default
        return result if result != {} and result != [] and result is not None else default
    except (AttributeError, TypeError, KeyError):
        return default


def safe_get_list(data, keys, default_list=None):
    """リストデータを安全に取得"""
    if default_list is None:
        default_list = []
    try:
        result = data
        for key in keys.split('.'):
            if isinstance(result, dict):
                result = result.get(key, [])
            else:
                return default_list
        return result if isinstance(result, list) and result else default_list
    except (AttributeError, TypeError, KeyError):
        return default_list


def extract_text_data(text, patterns, default="情報収集中"):
    """正規表現パターンでテキストからデータを抽出"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return default


def extract_year(text):
    """設立年の抽出"""
    patterns = [
        r'設立[：:]?\s*(\d{4})年',
        r'創業[：:]?\s*(\d{4})年',
        r'(\d{4})年設立',
        r'(\d{4})年創業'
    ]
    return extract_text_data(text, patterns, "設立年調査中")


def extract_employee_count(text):
    """従業員数の抽出"""
    patterns = [
        r'従業員[：:]?\s*約?(\d+(?:,\d+)?)\s*人',
        r'社員数[：:]?\s*約?(\d+(?:,\d+)?)\s*人',
        r'(\d+(?:,\d+)?)\s*人.*従業員'
    ]
    return extract_text_data(text, patterns, "従業員数調査中")


def extract_revenue(text):
    """売上高の抽出"""
    patterns = [
        r'売上[高]?[：:]?\s*約?(\d+(?:,\d+)?(?:\.\d+)?)\s*億円',
        r'売上[高]?[：:]?\s*約?(\d+(?:,\d+)?(?:\.\d+)?)\s*兆円',
        r'収益[：:]?\s*約?(\d+(?:,\d+)?(?:\.\d+)?)\s*億円'
    ]
    return extract_text_data(text, patterns, "売上高調査中")


def extract_business_overview(text):
    """事業概要の抽出"""
    patterns = [
        r'事業概要[：:]?\s*([^。]+)',
        r'主要事業[：:]?\s*([^。]+)',
        r'ビジネス内容[：:]?\s*([^。]+)'
    ]
    result = extract_text_data(text, patterns, "事業概要調査中")
    return result[:200] + "..." if len(result) > 200 else result


def extract_industry_name(text, target):
    """業界名の抽出"""
    patterns = [
        r'業界[：:]?\s*([^。 、]+)',
        r'([^。 、]+)業界',
        r'属する業界[：:]?\s*([^。 、]+)'
    ]
    result = extract_text_data(text, patterns, f"{target}の業界")
    return result.replace("業界", "") + "業界" if "業界" not in result else result


def extract_market_size(text):
    """市場規模の抽出"""
    patterns = [
        r'市場規模[：:]?\s*約?(\d+(?:,\d+)?(?:\.\d+)?)\s*億円',
        r'市場規模[：:]?\s*約?(\d+(?:,\d+)?(?:\.\d+)?)\s*兆円',
        r'マーケット規模[：:]?\s*約?(\d+(?:,\d+)?(?:\.\d+)?)\s*億円'
    ]
    return extract_text_data(text, patterns, "市場規模調査中")


def extract_challenges(text):
    """課題の抽出"""
    challenges = []
    patterns = [
        r'課題[：:]?\s*([^。]+)',
        r'問題点[：:]?\s*([^。]+)',
        r'改善点[：:]?\s*([^。]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:2]:
            challenges.append({
                "specific_issue": match.strip()[:100],
                "business_impact": "影響分析中"
            })
    if not challenges:
        challenges = [{"specific_issue": "詳細な課題分析を実行中", "business_impact": "ビジネス影響を調査中"}]
    return challenges


def extract_initiatives(text, focus_area):
    """取り組み・施策の抽出"""
    initiatives = []
    patterns = [
        r'取り組み[：:]?\s*([^。]+)',
        r'施策[：:]?\s*([^。]+)',
        r'導入[：:]?\s*([^。]+)',
        rf'{focus_area}.*?([^。]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:2]:
            initiatives.append({
                "initiative": match.strip()[:100],
                "results": {"quantitative": "効果測定中"}
            })
    if not initiatives:
        initiatives = [{
            "initiative": f"{focus_area}関連の取り組み調査中",
            "results": {"quantitative": "定量効果を分析中"}
        }]
    return initiatives


def extract_best_practices(text):
    """先進事例の抽出"""
    practices = []
    company_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|Ltd|社|通信|新聞))?).*?([^。]+)',
        r'(株式会社[^、。]+).*?([^。]+)',
        r'([^、。]+(?:社|通信|新聞)).*?([^。]+)'
    ]
    for pattern in company_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for company, result in matches[:3]:
            if len(company) > 1:
                practices.append({
                    "company": company.strip(),
                    "results": result.strip()[:150]
                })
    if not practices:
        practices = [{"company": "先進企業事例", "results": "成功事例を調査中"}]
    return practices


def extract_trends(text):
    """トレンドの抽出"""
    trends = []
    patterns = [
        r'トレンド[：:]?\s*([^。]+)',
        r'動向[：:]?\s*([^。]+)',
        r'傾向[：:]?\s*([^。]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:3]:
            trends.append({
                "trend_name": match.strip()[:50],
                "description": "詳細分析中"
            })
    if not trends:
        trends = [{"trend_name": "業界トレンド分析中", "description": "市場動向を調査中"}]
    return trends


def extract_metrics(text):
    """メトリクス・数値データの抽出"""
    metrics = {
        "efficiency_improvement": "調査中",
        "revenue_increase": "調査中",
        "cost_reduction": "調査中",
        "productivity_gain": "調査中",
    }
    efficiency_patterns = [
        r'効率[化]?.*?(\d+(?:\.\d+)?%)',
        r'改善.*?(\d+(?:\.\d+)?%)',
        r'短縮.*?(\d+(?:\.\d+)?%)',
    ]
    metrics["efficiency_improvement"] = extract_text_data(text, efficiency_patterns, "調査中")
    revenue_patterns = [
        r'収益.*?(\d+(?:\.\d+)?%)',
        r'売上.*?向上.*?(\d+(?:\.\d+)?%)',
        r'増収.*?(\d+(?:\.\d+)?%)',
    ]
    metrics["revenue_increase"] = extract_text_data(text, revenue_patterns, "調査中")
    return metrics


def extract_industry_voice(text):
    """業界関係者の声・コメントの抽出"""
    patterns = [
        r'[「『"]([^」』"]{20,})[」』"]',
        r'関係者.*?[：:]?\s*[「『"]([^」』"]+)[」』"]',
        r'業界.*?[：:]?\s*[「『"]([^」』"]+)[」』"]',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match and len(match.group(1)) > 20:
            return match.group(1)
    return "業界関係者の声を収集中..."


def validate_and_clean_response(parsed_data, target, focus_area):
    """レスポンスデータの検証とクリーニング"""
    required_structure = {
        "company_profile": {},
        "industry_analysis": {},
        "current_challenges": [],
        "focus_area_analysis": {},
        "best_practices": [],
        "market_trends": {},
        "industry_metrics": {},
        "industry_voice": "",
    }
    for key, default_value in required_structure.items():
        if key not in parsed_data:
            parsed_data[key] = default_value
    if not parsed_data["company_profile"].get("official_name"):
        parsed_data["company_profile"]["official_name"] = target
    if not isinstance(parsed_data["current_challenges"], list):
        parsed_data["current_challenges"] = []
    if not isinstance(parsed_data["best_practices"], list):
        parsed_data["best_practices"] = []
    if "current_initiatives" not in parsed_data["focus_area_analysis"]:
        parsed_data["focus_area_analysis"]["current_initiatives"] = []
    if "key_trends" not in parsed_data["market_trends"]:
        parsed_data["market_trends"]["key_trends"] = []
    return parsed_data


def parse_agent_response(agent_response, target, focus_area):
    """エージェント応答の解析（複数パターン対応）"""
    if "```json" in agent_response:
        try:
            json_start = agent_response.find("```json") + 7
            json_end = agent_response.find("```", json_start)
            json_str = agent_response[json_start:json_end].strip()
            parsed = json.loads(json_str)
            return validate_and_clean_response(parsed, target, focus_area)
        except json.JSONDecodeError:
            pass
    try:
        start_idx = agent_response.find('{')
        end_idx = agent_response.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = agent_response[start_idx:end_idx]
            parsed = json.loads(json_str)
            return validate_and_clean_response(parsed, target, focus_area)
    except json.JSONDecodeError:
        pass
    json_blocks = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', agent_response, re.DOTALL)
    for block in sorted(json_blocks, key=len, reverse=True):
        try:
            parsed = json.loads(block)
            return validate_and_clean_response(parsed, target, focus_area)
        except json.JSONDecodeError:
            continue
    return extract_structured_data_from_text(agent_response, target, focus_area)


def extract_structured_data_from_text(text, target, focus_area):
    """フリーテキストから構造化データを抽出"""
    extracted_data = {
        "company_profile": {
            "official_name": target,
            "established_year": extract_year(text),
            "employees": extract_employee_count(text),
            "revenue": extract_revenue(text),
            "business_overview": extract_business_overview(text),
        },
        "industry_analysis": {
            "industry_name": extract_industry_name(text, target),
            "market_size": extract_market_size(text),
            "top5_companies": [],
        },
        "current_challenges": extract_challenges(text),
        "focus_area_analysis": {
            "current_initiatives": extract_initiatives(text, focus_area),
        },
        "best_practices": extract_best_practices(text),
        "market_trends": {
            "key_trends": extract_trends(text),
        },
        "industry_metrics": extract_metrics(text),
        "industry_voice": extract_industry_voice(text),
    }
    return extracted_data






