"""
DMM英会話の先生の予約状況をスクレイピングして、予約可能な講師の一覧を生成するモジュール
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from dotenv import load_dotenv


def scrape_teacher_info(teacher_url: str) -> Dict[str, any]:
    """
    DMM英会話の先生情報ページをスクレイピングして、先生の情報を取得する
    
    Args:
        teacher_url: スクレイピング対象のURL
        
    Returns:
        先生の情報（名前、URL、予約可かどうか）
        
    Raises:
        requests.RequestException: HTTPリクエストに失敗した場合
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(teacher_url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 先生の名前を取得（ページタイトルから）
    title = soup.find('title')
    if title:
        title_text = title.text.strip()
        # "講師名 の講師詳細 - DMM英会話" から講師名を抽出
        if 'の講師詳細' in title_text:
            name = title_text.split('の講師詳細')[0]
        else:
            name = title_text.split(' | ')[0]
    else:
        name = "Unknown"
    
    # 顔写真のURLを取得
    img_tag = soup.find('img', class_='profile-pic')
    image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
    
    # 予約可かどうかをチェック
    reservation_available = soup.find('a', {'data-popup': 'cancelled_pop_up'}, string='予約可') is not None
    
    return {
        'name': name,
        'url': teacher_url,
        'image_url': image_url,
        'available': reservation_available
    }


def scrape_all_teachers(teacher_urls: List[str]) -> List[Dict[str, any]]:
    """
    複数の先生の情報をスクレイピングする
    
    Args:
        teacher_urls: スクレイピング対象のURLリスト
        
    Returns:
        先生情報のリスト
    """
    teachers = []
    for url in teacher_urls:
        try:
            print(f"  - {url} を確認中...")
            info = scrape_teacher_info(url)
            teachers.append(info)
            status = '予約可' if info['available'] else '予約不可'
            print(f"    ✅ {info['name']}: {status}")
        except requests.RequestException as e:
            print(f"    ⚠️  スクレイピング失敗: {str(e)}")
            teachers.append({
                'name': 'Error',
                'url': url,
                'available': False
            })
        except Exception as e:
            print(f"    ⚠️  エラー: {str(e)}")
            teachers.append({
                'name': 'Error',
                'url': url,
                'available': False
            })
    
    return teachers


def load_teacher_urls(config_path: Optional[str] = None) -> List[str]:
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


def save_teachers_data(teachers: List[Dict[str, any]], output_path: str) -> None:
    """
    先生のデータをJSONファイルに保存
    
    Args:
        teachers: 先生情報のリスト
        output_path: 出力ファイルのパス
    """
    data = {
        'last_updated': datetime.now().isoformat(),
        'teachers': teachers
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main(
    output_path: str = "frontend/public/data.json",
    config_path: Optional[str] = None
) -> None:
    """
    メイン処理：先生の情報をスクレイピングしてJSONファイルに保存
    
    Args:
        output_path: 出力JSONファイルのパス
        config_path: 設定ファイルのパス
    """
    print(f"[{datetime.now().isoformat()}] スクレイピング開始")
    
    # URLリストを読み込み
    teacher_urls = load_teacher_urls(config_path)
    print(f"対象URL数: {len(teacher_urls)}")
    
    # スクレイピング実行
    teachers = scrape_all_teachers(teacher_urls)
    
    # 結果を保存
    save_teachers_data(teachers, output_path)
    
    print(f"[{datetime.now().isoformat()}] スクレイピング完了。結果を {output_path} に保存しました")


if __name__ == "__main__":
    main()
