import sys
sys.path.insert(0, 'src/dmm-scp-techer')
from scraper import has_reservation_available

# テストケース
test_cases = [
    ('予約可', True),
    ('予約可予約可', True),
    ('予約可予約可予約可', True),
    ('今日は予約可です', True),
    ('予約可 あります', True),
    ('予約不可', False),
    ('予約', False),
]

print('テスト結果:')
print('=' * 60)
for text, expected in test_cases:
    result = has_reservation_available(text)
    status = '✅' if result == expected else '❌'
    print(f'{status} "{text}" → {result} (期待: {expected})')
print('=' * 60)
