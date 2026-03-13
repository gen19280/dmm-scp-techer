# DMM英会話 予約状況スクレイピングツール

DMM英会話の先生のページをスクレイピングして、予約可能な講師の一覧を表示するWebアプリケーションです。GitHub Pagesでホスティングされます。

## 機能

- 🔍 DMM英会話の先生ページをスクレイピング
- 🎯 `data-popup="cancelled_pop_up">予約可</a>` の要素を検出
- 🌐 予約可能な講師の一覧をWebページで表示
- ⏰ GitHub Actions で定期的にデータを更新
- 📱 レスポンシブデザイン

## インストール

### ローカル開発

1. Python 環境をセットアップ
```bash
pip install -e .
```

2. フロントエンドの依存関係をインストール
```bash
cd frontend
npm install
```

3. スクレイピングを実行
```bash
python -m src.dmm_scp_techer.scraper
```

4. フロントエンドを起動
```bash
cd frontend
npm run dev
```

## GitHub Pages デプロイ

このプロジェクトはGitHub Actionsを使って自動的にGitHub Pagesにデプロイされます。

### セットアップ

1. リポジトリの Settings → Pages
2. Source を "GitHub Actions" に設定
3. mainブランチにプッシュすると自動デプロイ

### ワークフロー

- `main` ブランチにプッシュされると自動的にビルド・デプロイ
- スクレイピング → データ生成 → フロントエンドビルド → GitHub Pages デプロイ

## カスタマイズ

### スクレイピング対象 URL の変更

`teacher_urls.json` を編集して対象の講師URLを追加・変更してください。

```json
{
  "urls": [
    "https://eikaiwa.dmm.com/teacher/index/50477/",
    "https://eikaiwa.dmm.com/teacher/index/43794/"
  ]
}
```

### デザインのカスタマイズ

`frontend/src/App.css` を編集してスタイルを変更してください。

## 技術スタック

- **バックエンド**: Python + BeautifulSoup4
- **フロントエンド**: React + TypeScript + Vite
- **デプロイ**: GitHub Pages + GitHub Actions
- **データ形式**: JSON

## 注意事項

- このツールはDMM英会話の利用規約を遵守してください
- スクレイピングはサーバーに負荷をかける可能性があるため、実行間隔に注意してください
- GitHub Actionsの無料枠内で使用することを推奨します

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

