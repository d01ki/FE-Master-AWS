# 🚀 デプロイ確認ガイド

## デプロイ確認用エンドポイント

このアプリケーションには、デプロイが正常に完了したかを確認するための2つのエンドポイントが用意されています。

### 1. ブラウザ表示用 - デプロイ確認ページ

**URL:** `/deploy-check`

デプロイ後、ブラウザで以下のURLにアクセスしてください：

```
https://your-app-domain.com/deploy-check
```

**表示される情報:**
- ✅ デプロイステータス（正常/エラー）
- 🌍 環境（開発/本番）
- 💾 データベースタイプ（PostgreSQL/SQLite）
- 📦 アプリバージョン
- 🕐 確認日時

このページが表示されれば、アプリケーションは正常にデプロイされています！

### 2. API用 - ヘルスチェックエンドポイント

**URL:** `/health`

ロードバランサーやモニタリングツール用のJSON形式のヘルスチェックエンドポイントです。

**リクエスト例:**
```bash
curl https://your-app-domain.com/health
```

**レスポンス例（正常時）:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-16T05:22:00.000Z",
  "database": "healthy",
  "version": "1.0.0"
}
```

**HTTPステータスコード:**
- `200` - 正常
- `503` - サービス利用不可（データベース接続エラーなど）

## AWSへのデプロイ手順

### 事前準備

1. **環境変数の設定**
   デプロイ前に以下の環境変数を設定してください：

   ```bash
   SECRET_KEY=your-secret-key-here
   ADMIN_PASSWORD=your-admin-password-here
   DATABASE_URL=postgresql://user:password@host:5432/dbname  # PostgreSQL使用時
   FLASK_ENV=production
   DEBUG=false
   PORT=5002
   ```

2. **必要なファイルの確認**
   - `requirements.txt` - Pythonパッケージのリスト
   - `app.py` - メインアプリケーションファイル
   - すべての依存ファイル（routes, templates, static等）

### デプロイ後の確認手順

1. **デプロイ完了の確認**
   ```bash
   # アプリケーションのURLを確認
   https://your-app-domain.com/deploy-check
   ```

2. **ヘルスチェックの確認**
   ```bash
   curl https://your-app-domain.com/health
   ```

3. **データベース接続の確認**
   デプロイ確認ページで「データベース: POSTGRESQL」と表示されていることを確認

4. **ログの確認**
   AWSのログストリームでエラーがないことを確認

### トラブルシューティング

#### ❌ `/deploy-check`にアクセスできない

**原因:**
- アプリケーションが起動していない
- ポート設定が間違っている
- セキュリティグループの設定が間違っている

**解決方法:**
```bash
# ログを確認
tail -f /var/log/your-app.log

# プロセスを確認
ps aux | grep python

# ポートを確認
netstat -tlnp | grep 5002
```

#### ❌ データベース接続エラー

**原因:**
- `DATABASE_URL`が正しく設定されていない
- データベースサーバーに接続できない

**解決方法:**
```bash
# 環境変数を確認
echo $DATABASE_URL

# データベースに手動接続を試す
psql $DATABASE_URL
```

#### ❌ 500 Internal Server Error

**原因:**
- 環境変数が不足している
- 依存パッケージがインストールされていない

**解決方法:**
```bash
# 必須環境変数を確認
echo $SECRET_KEY
echo $ADMIN_PASSWORD

# 依存パッケージを再インストール
pip install -r requirements.txt
```

## モニタリング設定

### CloudWatch Logsの確認

アプリケーションのログを確認：
```bash
aws logs tail /aws/application/your-app --follow
```

### ヘルスチェックの自動監視

CloudWatch Alarmsを設定して、ヘルスチェックを定期的に監視：

```bash
# 1分ごとにヘルスチェック
*/1 * * * * curl -f https://your-app-domain.com/health || echo "Health check failed"
```

## 次のステップ

デプロイが成功したら：

1. ✅ トップページにアクセス: `https://your-app-domain.com/`
2. ✅ ユーザー登録を試す
3. ✅ 管理者ページにアクセス: `https://your-app-domain.com/admin`
4. ✅ 問題データをアップロード

---

## サポート

問題が発生した場合は、以下を確認してください：

1. [STATUS.md](STATUS.md) - 現在の実装状況
2. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 詳細なデプロイガイド
3. アプリケーションログ
4. `/health`エンドポイントのレスポンス

Happy deploying! 🎉
