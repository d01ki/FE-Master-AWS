# FE-Master AWS EC2 デプロイ完全ガイド

このドキュメントでは、新しいリポジトリ FE-Master-AWS を使用したAWS EC2へのデプロイ手順を説明します。

## 📦 現在作成済みのファイル

✅ README.md - プロジェクト概要とクイックスタート
✅ .env.example - 環境変数サンプル  
✅ .gitignore - Git除外設定
✅ requirements.txt - Python依存パッケージ
✅ config.py - アプリケーション設定
✅ deploy.sh - 自動デプロイスクリプト
✅ deploy/nginx.conf - Nginx設定

## 🔄 残りのファイルをコピーする方法

元のリポジトリ(FE-master)から残りのファイルをコピーします。

### 方法1: ローカルでコピー（推奨）

```bash
# ローカルマシンで実行

# 1. 元のリポジトリをクローン
git clone https://github.com/d01ki/FE-master.git temp-fe-master
cd temp-fe-master

# 2. 新しいリポジトリをクローン
cd ..
git clone https://github.com/d01ki/FE-Master-AWS.git
cd FE-Master-AWS

# 3. 必要なファイルをコピー
cp ../temp-fe-master/app.py .
cp ../temp-fe-master/database.py .
cp ../temp-fe-master/auth.py .
cp ../temp-fe-master/persistent_session.py .
cp ../temp-fe-master/question_manager.py .
cp ../temp-fe-master/achievement_system.py .
cp ../temp-fe-master/ranking_system.py .
cp ../temp-fe-master/helper_functions.py .
cp ../temp-fe-master/utils.py .

# 4. ディレクトリをコピー
cp -r ../temp-fe-master/routes .
cp -r ../temp-fe-master/templates .
cp -r ../temp-fe-master/static .
cp -r ../temp-fe-master/json_questions .
cp -r ../temp-fe-master/utils .

# 5. 不要なファイルを削除（AWS用に不要）
rm -f build.sh  # Render用なので不要
rm -f app_postgresql.py  # 元のapp.pyを使用

# 6. コミットしてプッシュ
git add .
git commit -m "元のリポジトリからアプリケーションファイルを追加"
git push origin main

# 7. 一時フォルダを削除
cd ..
rm -rf temp-fe-master
```

### 方法2: EC2インスタンス上で直接コピー

```bash
# EC2インスタンスにSSH接続後

# 1. ホームディレクトリに移動
cd ~

# 2. 元のリポジトリをクローン
git clone https://github.com/d01ki/FE-master.git temp-fe-master

# 3. 新しいリポジトリに移動
cd FE-Master-AWS

# 4. ファイルをコピー（上記と同じ）
cp ../temp-fe-master/app.py .
cp ../temp-fe-master/database.py .
# ... (以下同様)

# 5. Gitにコミット・プッシュ
git add .
git commit -m "元のリポジトリからアプリケーションファイルを追加"
git push origin main
```

## 🚀 完全なデプロイ手順

### ステップ1: EC2インスタンスの準備

- インスタンスタイプ: t2.micro (無料枠)
- OS: Ubuntu 22.04 LTS
- セキュリティグループ:
  - SSH (22): 自分のIPのみ
  - Custom TCP (5002): 0.0.0.0/0

### ステップ2: SSH接続

```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### ステップ3: リポジトリのクローンとファイルコピー

```bash
# 新しいリポジトリをクローン
git clone https://github.com/d01ki/FE-Master-AWS.git
cd FE-Master-AWS

# 元のリポジトリから必要なファイルをコピー（上記参照）
```

### ステップ4: 環境変数の設定

```bash
cp .env.example .env
nano .env
```

必須項目を設定:
```env
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ADMIN_PASSWORD=your-secure-password
DATABASE_URL=sqlite:///fe_exam.db
```

### ステップ5: デプロイ実行

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### ステップ6: アクセス確認

ブラウザで `http://<EC2-PUBLIC-IP>:5002` にアクセス

## 📝 主な改善点（元のFE-masterとの違い）

1. **セッション永続化**: データベースベースのセッション管理でRenderの問題を解決
2. **systemdサービス**: EC2での自動起動・管理
3. **gunicorn**: 本番運用に適したWSGIサーバー
4. **デプロイスクリプト**: ワンコマンドでセットアップ完了
5. **nginx対応**: リバースプロキシ設定（オプション）

## 🛠️ 運用コマンド

```bash
# サービス管理
sudo systemctl status fe-master    # 状態確認
sudo systemctl restart fe-master   # 再起動
sudo systemctl stop fe-master      # 停止
sudo systemctl start fe-master     # 起動

# ログ確認
sudo journalctl -u fe-master -f    # リアルタイム
sudo journalctl -u fe-master -n 50 # 最新50行
```

## 💾 バックアップ

```bash
# データベースのバックアップ
cp fe_exam.db fe_exam_backup_$(date +%Y%m%d).db

# アップロードファイルのバックアップ
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

## 🔒 セキュリティ設定

```bash
# ファイアウォール
sudo ufw allow 22
sudo ufw allow 5002
sudo ufw enable

# 定期更新
sudo apt update && sudo apt upgrade -y
```

## 📞 サポート

問題が発生した場合は、GitHubのIssueで報告してください。

---

**リポジトリURL**: https://github.com/d01ki/FE-Master-AWS
