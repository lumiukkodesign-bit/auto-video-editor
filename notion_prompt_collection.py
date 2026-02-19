"""
Notion プロンプト集作成スクリプト
auto-video-editor 向けの動画編集プロンプト集を Notion に作成します。
"""

import os
import json
import requests
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def create_prompt_database(token: str, parent_page_id: str) -> dict:
    """プロンプト集データベースを Notion に作成する"""
    url = f"{NOTION_API_URL}/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "icon": {"type": "emoji", "emoji": "🎬"},
        "title": [{"type": "text", "text": {"content": "動画編集プロンプト集"}}],
        "properties": {
            "プロンプト名": {"title": {}},
            "カテゴリ": {
                "select": {
                    "options": [
                        {"name": "シーン演出", "color": "blue"},
                        {"name": "トランジション", "color": "green"},
                        {"name": "テキスト・字幕", "color": "yellow"},
                        {"name": "音楽・効果音", "color": "orange"},
                        {"name": "カラーグレーディング", "color": "purple"},
                        {"name": "カット編集", "color": "red"},
                        {"name": "エフェクト", "color": "pink"},
                        {"name": "汎用", "color": "gray"},
                    ]
                }
            },
            "プロンプト": {"rich_text": {}},
            "使用例": {"rich_text": {}},
            "タグ": {"multi_select": {"options": []}},
            "難易度": {
                "select": {
                    "options": [
                        {"name": "初級", "color": "green"},
                        {"name": "中級", "color": "yellow"},
                        {"name": "上級", "color": "red"},
                    ]
                }
            },
        },
    }
    response = requests.post(url, headers=get_headers(token), json=payload)
    response.raise_for_status()
    return response.json()


def add_prompt_entry(token: str, database_id: str, entry: dict) -> dict:
    """プロンプトエントリをデータベースに追加する"""
    url = f"{NOTION_API_URL}/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "プロンプト名": {
                "title": [{"text": {"content": entry["name"]}}]
            },
            "カテゴリ": {"select": {"name": entry["category"]}},
            "プロンプト": {
                "rich_text": [{"text": {"content": entry["prompt"]}}]
            },
            "使用例": {
                "rich_text": [{"text": {"content": entry.get("example", "")}}]
            },
            "タグ": {
                "multi_select": [{"name": t} for t in entry.get("tags", [])]
            },
            "難易度": {"select": {"name": entry.get("difficulty", "初級")}},
        },
    }
    response = requests.post(url, headers=get_headers(token), json=payload)
    response.raise_for_status()
    return response.json()


PROMPTS = [
    # ---- シーン演出 ----
    {
        "name": "ドラマチックな出だし",
        "category": "シーン演出",
        "prompt": (
            "映像の冒頭3秒を暗転からスローモーションでフェードインし、"
            "緊張感のあるBGMを重ねてドラマチックな出だしを演出してください。"
        ),
        "example": "予告編、プロモーション動画の冒頭シーンに使用",
        "tags": ["フェードイン", "スローモーション", "オープニング"],
        "difficulty": "初級",
    },
    {
        "name": "クライマックスの盛り上がり演出",
        "category": "シーン演出",
        "prompt": (
            "映像のクライマックス部分でズームイン + BGMのテンポアップ + "
            "明度を徐々に上げるカラー補正を組み合わせて盛り上がりを演出してください。"
        ),
        "example": "スポーツハイライト、イベント動画のクライマックスに使用",
        "tags": ["ズーム", "クライマックス", "演出"],
        "difficulty": "中級",
    },
    # ---- トランジション ----
    {
        "name": "スムーズなジャンプカット",
        "category": "トランジション",
        "prompt": (
            "同一被写体の連続カットをジャンプカットで繋ぎ、"
            "各カット間に5フレームのクロスディゾルブを加えて自然な流れを作ってください。"
        ),
        "example": "Vlog、インタビュー動画のテンポアップに使用",
        "tags": ["ジャンプカット", "クロスディゾルブ", "テンポ"],
        "difficulty": "初級",
    },
    {
        "name": "J カット / L カット",
        "category": "トランジション",
        "prompt": (
            "次のシーンの音声を現在のシーンの映像終了より0.5秒前から始める Jカット、"
            "または現在の音声を次のシーンの映像開始後まで継続する Lカットを適用してください。"
        ),
        "example": "ドキュメンタリー、インタビュー動画のシーン切り替えに使用",
        "tags": ["Jカット", "Lカット", "音声"],
        "difficulty": "中級",
    },
    {
        "name": "ワイプトランジション",
        "category": "トランジション",
        "prompt": (
            "左から右へ画面をワイプするトランジションを0.3秒で適用し、"
            "ワイプ境界にソフトエッジ（幅30px）を加えてください。"
        ),
        "example": "プレゼン動画、チュートリアル動画のスライド切り替えに使用",
        "tags": ["ワイプ", "スライド"],
        "difficulty": "初級",
    },
    # ---- テキスト・字幕 ----
    {
        "name": "キネティックタイポグラフィ",
        "category": "テキスト・字幕",
        "prompt": (
            "テキストを単語ごとに0.1秒ずつ遅らせてフェードインし、"
            "最後の単語が表示された後に全体を1秒かけてスケールアップしてください。"
        ),
        "example": "プロモーション動画、SNS広告のキャッチコピー表示に使用",
        "tags": ["タイポグラフィ", "アニメーション", "テキスト"],
        "difficulty": "中級",
    },
    {
        "name": "字幕の自動タイミング調整",
        "category": "テキスト・字幕",
        "prompt": (
            "音声認識結果をもとに字幕を自動生成し、"
            "各字幕の表示開始を音声より0.1秒早め、終了を0.2秒遅らせて読みやすく調整してください。"
        ),
        "example": "講義動画、インタビュー動画の字幕挿入に使用",
        "tags": ["字幕", "音声認識", "自動化"],
        "difficulty": "上級",
    },
    {
        "name": "ローワーサード テロップ",
        "category": "テキスト・字幕",
        "prompt": (
            "画面下部1/3の位置に名前・肩書きを表示するローワーサードを作成し、"
            "左からスライドインして3秒表示後にフェードアウトしてください。"
        ),
        "example": "ニュース風動画、インタビュー動画の人物紹介に使用",
        "tags": ["テロップ", "ローワーサード", "紹介"],
        "difficulty": "初級",
    },
    # ---- 音楽・効果音 ----
    {
        "name": "BGMのビートに合わせたカット",
        "category": "音楽・効果音",
        "prompt": (
            "BGMのビート（BPM）を検出し、"
            "ビートのタイミングに映像カットを自動で合わせてください。"
        ),
        "example": "ミュージックビデオ、ハイライトリールに使用",
        "tags": ["ビート", "BGM", "自動編集"],
        "difficulty": "上級",
    },
    {
        "name": "フェードアウトエンディング",
        "category": "音楽・効果音",
        "prompt": (
            "映像終了の3秒前からBGMのボリュームを徐々に下げ、"
            "映像が暗転と同時に無音になるよう調整してください。"
        ),
        "example": "あらゆる動画のエンディング処理に使用",
        "tags": ["フェードアウト", "エンディング", "BGM"],
        "difficulty": "初級",
    },
    {
        "name": "効果音の自動挿入",
        "category": "音楽・効果音",
        "prompt": (
            "映像内の特定アクション（ドア開閉、拍手、爆発など）を検出し、"
            "対応する効果音ライブラリから最適な音源を自動で挿入してください。"
        ),
        "example": "ゲーム実況、アクション動画に使用",
        "tags": ["効果音", "自動化", "アクション"],
        "difficulty": "上級",
    },
    # ---- カラーグレーディング ----
    {
        "name": "シネマティックLUT適用",
        "category": "カラーグレーディング",
        "prompt": (
            "映像にシネマティックなティールアンドオレンジLUTを適用し、"
            "強度を70%に設定してオリジナルの色味を残してください。"
        ),
        "example": "映画風プロモーション動画、旅行動画に使用",
        "tags": ["LUT", "シネマティック", "カラー"],
        "difficulty": "初級",
    },
    {
        "name": "夜景の明度・ノイズ補正",
        "category": "カラーグレーディング",
        "prompt": (
            "暗所撮影映像のシャドウを持ち上げ（+20）、"
            "ノイズリダクションを適用してから彩度を+10してください。"
        ),
        "example": "夜景・室内撮影動画のクオリティ改善に使用",
        "tags": ["ノイズ", "夜景", "明度"],
        "difficulty": "中級",
    },
    # ---- カット編集 ----
    {
        "name": "無音部分の自動カット",
        "category": "カット編集",
        "prompt": (
            "音声レベルが-40dB以下の区間を検出し、"
            "0.5秒以上続く無音部分を自動で除去してください。"
        ),
        "example": "講義動画、インタビュー動画の間延び除去に使用",
        "tags": ["無音カット", "自動化", "テンポ"],
        "difficulty": "中級",
    },
    {
        "name": "ハイライトシーン抽出",
        "category": "カット編集",
        "prompt": (
            "映像全体から動きの大きいシーン・音量の大きいシーンを検出し、"
            "上位20%のシーンを抽出してハイライトリールを作成してください。"
        ),
        "example": "スポーツ動画、イベント動画のダイジェスト作成に使用",
        "tags": ["ハイライト", "自動抽出", "ダイジェスト"],
        "difficulty": "上級",
    },
    # ---- エフェクト ----
    {
        "name": "グリッチエフェクト",
        "category": "エフェクト",
        "prompt": (
            "タイトル表示時に0.5秒間のグリッチエフェクト（RGB分離 + ノイズライン）を適用し、"
            "デジタル感・近未来感を演出してください。"
        ),
        "example": "ゲーム動画、テック系プロモーション動画のタイトルに使用",
        "tags": ["グリッチ", "エフェクト", "タイトル"],
        "difficulty": "中級",
    },
    {
        "name": "スローモーション変換",
        "category": "エフェクト",
        "prompt": (
            "指定区間をフレーム補間（オプティカルフロー）を使って"
            "2倍スローモーション（0.5x速度）に変換してください。"
        ),
        "example": "スポーツ、料理、自然映像の強調に使用",
        "tags": ["スローモーション", "フレーム補間"],
        "difficulty": "中級",
    },
    # ---- 汎用 ----
    {
        "name": "縦型動画へのリサイズ",
        "category": "汎用",
        "prompt": (
            "横型動画（16:9）をInstagram Reels / TikTok向けの縦型（9:16）にリサイズし、"
            "被写体を中心に自動クロップしてください。"
        ),
        "example": "SNS投稿用動画の縦型変換に使用",
        "tags": ["リサイズ", "縦型", "SNS"],
        "difficulty": "初級",
    },
    {
        "name": "サムネイル自動生成",
        "category": "汎用",
        "prompt": (
            "動画の中から最も動きのあるフレームを3枚候補として抽出し、"
            "各候補にタイトルテキストを重ねてサムネイル画像を生成してください。"
        ),
        "example": "YouTube動画のサムネイル作成に使用",
        "tags": ["サムネイル", "自動生成"],
        "difficulty": "上級",
    },
]


def main():
    token = os.environ.get("NOTION_TOKEN")
    parent_page_id = os.environ.get("NOTION_PAGE_ID")

    if not token:
        raise ValueError(
            "環境変数 NOTION_TOKEN が設定されていません。\n"
            ".env ファイルまたは環境変数を設定してください。"
        )
    if not parent_page_id:
        raise ValueError(
            "環境変数 NOTION_PAGE_ID が設定されていません。\n"
            "プロンプト集を作成する Notion ページのIDを設定してください。"
        )

    print("Notion に動画編集プロンプト集データベースを作成中...")
    db = create_prompt_database(token, parent_page_id)
    database_id = db["id"]
    print(f"データベース作成完了: {db['url']}")

    print(f"\n{len(PROMPTS)} 件のプロンプトを追加中...")
    for i, prompt in enumerate(PROMPTS, 1):
        add_prompt_entry(token, database_id, prompt)
        print(f"  [{i:02d}/{len(PROMPTS)}] {prompt['name']} ({prompt['category']})")

    print("\n完了! Notion でプロンプト集を確認してください。")
    print(f"URL: {db['url']}")


if __name__ == "__main__":
    main()
