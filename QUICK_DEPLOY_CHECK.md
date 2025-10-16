# 🎯 クイックスタート: デプロイ確認

## ローカルでテストする

デプロイ前にローカル環境で確認用ページをテストできます。

### 1. 環境準備

```bash
# リポジトリをクローン
git clone https://github.com/d01ki/FE-Master-AWS.git
cd FE-Master-AWS

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. 環境変数を設定

`.env`ファイルを作成：

```bash
SECRET_KEY=dev-secret-key-for-testing
ADMIN_PASSWORD=admin123
DEBUG=true
FLASK_ENV=development
DATABASE_URL=sqlite:///fe_exam.db
PORT=5002
```

### 3. アプリケーションを起動

```bash
python app.py
```

以下のメッセージが表示されれば成功：

```
🚀 Starting Flask app on port 5002
🔧 Debug mode: ON (開発環境)
💾 Database: SQLITE
🔒 Cookie Secure: OFF (開発環境)
 * Running on http://0.0.0.0:5002
```

### 4. デプロイ確認ページにアクセス

ブラウザで以下のURLを開く：

```
http://localhost:5002/deploy-check
```

**表示されるべき内容:**
- ✅ デプロイ成功！
- ステータス: 正常
- 環境: 開発環境
- データベース: SQLITE
- バージョン: 1.0.0

### 5. ヘルスチェックAPIを確認

別のターミナルで：

```bash
curl http://localhost:5002/health
```

**期待される出力:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-16T05:23:00.000Z",
  "database": "healthy",
  "version": "1.0.0"
}
```

---

## AWSにデプロイして確認する

### 方法1: シンプルな確認（推奨）

デプロイ後、すぐにブラウザでアクセス：

```
https://your-app-domain.com/deploy-check
```

緑のチェックマーク✅が表示されればOK！

### 方法2: コマンドラインで確認

```bash
# ヘルスチェック
curl https://your-app-domain.com/health

# 期待される結果
# {"status":"ok","timestamp":"...","database":"healthy","version":"1.0.0"}
```

### 方法3: 継続的な監視

```bash
# 10秒ごとにヘルスチェック（Ctrl+Cで停止）
watch -n 10 'curl -s https://your-app-domain.com/health | jq .'
```

---

## トラブルシューティング

### ❌ ページが表示されない

```bash
# 1. アプリが起動しているか確認
ps aux | grep python

# 2. ポートが開いているか確認
netstat -tlnp | grep 5002

# 3. ログを確認
tail -f /var/log/your-app.log
```

### ❌ データベースエラー

```bash
# 環境変数を確認
echo $DATABASE_URL

# データベースに直接接続してみる
# SQLiteの場合
sqlite3 fe_exam.db "SELECT 1;"

# PostgreSQLの場合
psql $DATABASE_URL -c "SELECT 1;"
```

### ❌ 500エラー

```bash
# Flaskをデバッグモードで起動
DEBUG=true python app.py

# エラーの詳細がブラウザに表示されます
```

---

## 次のステップ

デプロイ確認が成功したら：

1. ✅ [トップページ](/) - メインアプリにアクセス
2. ✅ [ユーザー登録](/register) - アカウントを作成
3. ✅ [管理画面](/admin) - 問題データを管理
4. ✅ [STATUS.md](STATUS.md) - 実装済み機能を確認

---

## よくある質問

**Q: `/deploy-check`と`/health`の違いは？**

A: 
- `/deploy-check` - ブラウザで見やすい確認ページ（人間用）
- `/health` - JSON形式のAPI（システム監視用）

**Q: 本番環境でもこのページは使える？**

A: はい！むしろ本番環境でこそ重要です。デプロイ後の確認に便利です。

**Q: セキュリティは大丈夫？**

A: はい。これらのページは公開情報のみを表示し、認証不要で安全です。

---

**🎉 Happy Deploying!**

問題があれば [Issues](https://github.com/d01ki/FE-Master-AWS/issues) でお知らせください。
