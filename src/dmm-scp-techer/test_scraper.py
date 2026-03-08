"""
スクレイピング機能のテスト
"""

import os
import sys
from pathlib import Path

# パスを調整
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper import has_reservation_available


def test_has_reservation_available():
    """「予約可」の検出テスト"""
    
    # テストケース
    test_cases = [
        # (テキスト, 期待される結果, 説明)
        ("予約可", True, "厳格に3文字"),
        ("今日は予約可です", True, "文の中の「予約可」"),
        ("予約可 ありません", True, "空白区切り"),
        ("予約可\n次のページ", True, "改行区切り"),
        ("予約不可", False, "「予約不可」"),
        ("予約可能です", False, "「予約可能」（4文字）"),
        ("予約", False, "「予約」だけ"),
        ("可", False, "「可」だけ"),
        ("", False, "空文字列"),
        ("予約可予約可", True, "複数の「予約可」"),
    ]
    
    print("=" * 60)
    print("「予約可」検出テスト")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for text, expected, description in test_cases:
        result = has_reservation_available(text)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | '{text}' → {result} (期待: {expected}) - {description}")
    
    print("=" * 60)
    print(f"✅ PASSED: {passed}/{len(test_cases)}")
    print(f"❌ FAILED: {failed}/{len(test_cases)}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = test_has_reservation_available()
    sys.exit(0 if success else 1)
