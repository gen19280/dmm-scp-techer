import sys
sys.path.insert(0, 'src/dmm-scp-techer')
from scraper import has_reservation_available

# テストケース
test_cases = [
    ('予約可', True, '単独の「予約可」'),
    ('予約可予約可', True, '「予約可」の繰り返し'),
    ('予約可予約可予約可', True, '「予約可」の複数繰り返し'),
    ('今日は予約可です', True, '文の中の「予約可」'),
    ('予約可 あります', True, 'スペース区切りの「予約可」'),
    ('予約可\n次のページ', True, '改行区切りの「予約可」'),
    ('予約不可', False, '「予約不可」'),
    ('予約可能', False, '「予約可能」は除外'),
    ('予約可能数', False, '「予約可能数」は除外'),
    ('現在予約可', False, '「現在予約可」は除外（直後に「能」はないが、複合語であれば除外対象）'),
    ('予約', False, '「予約」だけ'),
    ('可', False, '「可」だけ'),
    ('', False, '空文字列'),
]

print('='*70)
print('「予約可」検出テスト')
print('='*70)

passed = 0
failed = 0

for text, expected, description in test_cases:
    result = has_reservation_available(text)
    status = '✅ PASS' if result == expected else '❌ FAIL'
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f'{status} | \'{text}\' → {result} (期待: {expected}) - {description}')

print('='*70)
print(f'✅ PASSED: {passed}/{len(test_cases)}')
print(f'❌ FAILED: {failed}/{len(test_cases)}')
print('='*70)
