"""
DMM英会話の先生の予約状況をスクレイピングしてDiscordに通知するモジュール
"""

import os
import re
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
    
    - 「予約可」（単独）
    - 「予約可予約可」（繰り返し）
    - 「予約可予約可予約可」（複数繰り返し）
    いずれもマッチしたら True を返す
    
    Args:
        text: 検索対象のテキスト
        
    Returns:
        「予約可」が見つかったかどうか
    """
    # 「予約可」の1回以上の繰り返しを検索
    # 単独でも、繰り返しでも両方検出
    pattern = r"予約可+"
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


def main(
    teacher_url: str = "https://eikaiwa.dmm.com/teacher/index/51118/",
    webhook_url: Optional[str] = None
) -> None:
    """
    メイン処理：スクレイピングと通知を実行
    
    Args:
        teacher_url: スクレイピング対象の先生のURL
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
    
    print(f"[{datetime.now().isoformat()}] スクレイピング開始: {teacher_url}")
    
    try:
        # スクレイピング
        page_text = scrape_teacher_status(teacher_url)
        
        # 「予約可」を確認
        if has_reservation_available(page_text):
            message = "🎯 予約可"
            print(f"[{datetime.now().isoformat()}] 予約可を検出しました")
            
            # Discord通知を送信
            send_discord_notification(webhook_url, message)
            print(f"[{datetime.now().isoformat()}] Discord通知を送信しました")
        else:
            print(f"[{datetime.now().isoformat()}] 予約可は検出されませんでした")
            
    except requests.RequestException as e:
        error_msg = f"❌ スクレイピング失敗: {str(e)}"
        print(f"[{datetime.now().isoformat()}] {error_msg}")
        # エラーをDiscordに送信（オプション）
        try:
            send_discord_notification(webhook_url, error_msg)
        except Exception as notify_error:
            print(f"エラー通知の送信に失敗しました: {notify_error}")
        raise
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] 予期しないエラー: {e}")
        raise


if __name__ == "__main__":
    main()
