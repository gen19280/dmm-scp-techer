# DMM英会話 予約状況スクレイピングツール

DMM英会話の先生のページをスクレイピングして、「予約可」という文字が見つかった場合、Discordウェブフックで通知するツールです。

## 機能

- 🔍 DMM英会話の先生ページをスクレイピング
- 🎯 「予約可」（厳格に3文字）を検出
- 💬 Discord ウェブフックで即座に通知
- ⏰ GitHub Actions で定期実行可能

## インストール

### 1. 依存関係をインストール

```bash
pip install -r requirements.txt
# または
pip install requests beautifulsoup4
```

### 2. 環境変数を設定

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## 使用方法

### ローカルで実行

```bash
# モジュールとして実行
python -m dmm_scp_techer

# または Python スクリプトとして
python -m dmm_scp_techer.scraper
```

### GitHub Actions で自動実行

1. リポジトリの Settings → Secrets and variables → Actions
2. `DISCORD_WEBHOOK_URL` というシークレットを追加
3. ワークフローは毎日 9:00, 12:00, 18:00, 21:00 JST に実行されます

スケジュール変更は `.github/workflows/schedule.yml` の `cron` を編集してください。

## カスタマイズ

### スクレイピング対象 URL の変更

`scraper.py` の `main()` 関数の引数を変更：

```python
main(teacher_url="https://eikaiwa.dmm.com/teacher/index/51118/")
```

### 通知スケジュールの変更

`.github/workflows/schedule.yml` の `cron` の値を変更：

```yaml
- cron: '0 0,3,9,12 * * *'  # 毎日 00:00, 03:00, 09:00, 12:00 UTC
```

[Cron の構文](https://docs.github.jp/en/actions/using-workflows/events-that-trigger-workflows#schedule)を参照してください。

## トラブルシューティング

### スクレイピングが失敗する場合

- User-Agent が正しく設定されているか確認
- サイトのレイアウト変更により HTML構造が異なる可能性

### Discord 通知が届かない場合

- `DISCORD_WEBHOOK_URL` が正しく設定されているか確認
- ウェブフック URL の有効期限を確認

## ライセンス

MIT

