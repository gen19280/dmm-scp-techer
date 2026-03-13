"""
DMM英会話の先生の予約状況をスクレイピングしてDiscordに通知するモジュール
"""

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


def scrape_teacher_status(teacher_url: str) -> str:
    """
    DMM英会話の先生情報ページをスクレイピングして、本文を取得する
    
    Args:
        teacher_url: スクレイピング対象のURL
        
    Returns:
        ページのテキスト内容
        
    Raises:
        requests.RequestException: HTTPリクエストに失敗した場合
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(teacher_url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # テキスト化して返す
    text = soup.get_text()
    return text


def has_reservation_available(text: str) -> bool:
    """
    テキストから「予約可」（1回以上の繰り返しを含む）を探す
    ただし「予約可能」「現在予約可」などの複合語は除外
    
    対応する例：
    - 「予約可」（単独）✅
    - 「予約可予約可」（繰り返し）✅
    - 「予約可予約可予約可」（複数繰り返し）✅
    - 「予約可 です」（スペース区切り）✅
    
    除外する例：
    - 「予約可能数」❌
    - 「現在予約可」❌
    
    Args:
        text: 検索対象のテキスト
        
    Returns:
        「予約可」が見つかったかどうか
    """
    # 「予約可」を検出するが、直後に「能」がない場合のみ
    # (?!能) = ネガティブルックアヘッド：直後に「能」がないことを確認
    pattern = r"予約可(?!能)"
    matches = re.findall(pattern, text)
    return bool(matches)


def send_discord_notification(webhook_url: str, message: str) -> None:
    """
    Discordウェブフックにメッセージを送信する
    
    Args:
        webhook_url: DiscordウェブフックのURL
        message: 送信するメッセージ内容
        
    Raises:
        requests.RequestException: ウェブフックへのリクエストに失敗した場合
    """
    payload = {
        "content": message,
        "username": "DMM英会話 予約状況",
        "tts": False
    }
    
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


def load_teacher_urls(config_path: Optional[str] = None) -> list:
    """
    設定ファイルから先生のURLリストを読み込む
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        URLリスト
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "teacher_urls.json"
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('urls', [])
    else:
        # デフォルトのURL
        return [
            "https://eikaiwa.dmm.com/teacher/index/43794/",
            "https://eikaiwa.dmm.com/teacher/index/40406/",
            "https://eikaiwa.dmm.com/teacher/index/52910/",
            "https://eikaiwa.dmm.com/teacher/index/55373/",
            "https://eikaiwa.dmm.com/teacher/index/50613/",
        ]


def main(
    teacher_urls: Optional[list] = None,
    webhook_url: Optional[str] = None
) -> None:
    """
    メイン処理：複数の先生について予約状況をスクレイピングして通知を実行
    
    Args:
        teacher_urls: スクレイピング対象の先生のURLリスト。指定されない場合はデフォルトを使用
        webhook_url: DiscordウェブフックのURL。指定されない場合は環境変数から取得
    """
    # .env ファイルを読み込む
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # デフォルトの .env を探す
    
    # webhook_urlが指定されていない場合は環境変数から取得
    if webhook_url is None:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            raise ValueError(
                "DISCORD_WEBHOOK_URLが指定されていません。"
                ".env ファイルまたは環境変数に設定してください。"
            )
    
    # デフォルトのURLを設定
    if teacher_urls is None:
        teacher_urls = load_teacher_urls()
    
    print(f"[{datetime.now().isoformat()}] スクレイピング開始: {len(teacher_urls)}名の先生")
    
    available_urls = []  # 予約可が見つかったURLを記録
    
    try:
        # 各URLをスクレイピング
        for teacher_url in teacher_urls:
            try:
                print(f"  - {teacher_url} を確認中...")
                page_text = scrape_teacher_status(teacher_url)
                
                # 「予約可」を確認
                if has_reservation_available(page_text):
                    available_urls.append(teacher_url)
                    print(f"    ✅ 予約可を検出")
                else:
                    print(f"    予約可は見つかりませんでした")
                    
            except requests.RequestException as e:
                print(f"    ⚠️  スクレイピング失敗: {str(e)}")
                continue
        
        # 予約可が見つかった場合のみ通知
        if available_urls:
            message = "🎯 予約可の先生が見つかりました！\n\n"
            message += "\n".join([f"• {url}" for url in available_urls])
            
            print(f"[{datetime.now().isoformat()}] 予約可を検出: {len(available_urls)}名")
            
            # Discord通知を送信
            send_discord_notification(webhook_url, message)
            print(f"[{datetime.now().isoformat()}] Discord通知を送信しました")
        else:
            print(f"[{datetime.now().isoformat()}] すべての先生について予約可は見つかりませんでした")
            
    except Exception as e:
        error_msg = f"❌ スクレイピング処理中にエラーが発生: {str(e)}"
        print(f"[{datetime.now().isoformat()}] {error_msg}")
        # エラーをDiscordに送信（オプション）
        try:
            send_discord_notification(webhook_url, error_msg)
        except Exception as notify_error:
            print(f"エラー通知の送信に失敗しました: {notify_error}")
        raise


if __name__ == "__main__":
    main()