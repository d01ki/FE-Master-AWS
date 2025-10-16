# 🚀 FE-Master-AWS クイックスタート

AWS EC2で5分でデプロイ！

## 📋 前提条件

- AWS EC2インスタンス (t2.micro, Ubuntu 22.04 LTS)
- SSH接続可能な状態
- セキュリティグループでポート22, 5002を開放

## ⚡ 最速デプロイ（3ステップ）

### 1️⃣ リポジトリのクローンとファイルコピー

```bash
# EC2にSSH接続後
git clone https://github.com/d01ki/FE-Master-AWS.git
cd FE-Master-AWS

# 元のリポジトリからファイルをコピー
chmod +x copy_files.sh
./copy_files.sh

# 変更をコミット（後でプッシュしたい場合）
git add .
git commit -m "アプリケーションファイルを追加"
# git push origin main  # プッシュする場合
```

### 2️⃣ 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# SECRET_KEYを生成して設定
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY" >> .env
echo "ADMIN_PASSWORD=YourSecurePassword123" >> .env
echo "DATABASE_URL=sqlite:///fe_exam.db" >> .env
echo "FLASK_ENV=production" >> .env
echo "DEBUG=False" >> .env
```

または手動編集:
```bash
nano .env
```

### 3️⃣ デプロイ実行

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

## 🎉 完了！

ブラウザで以下にアクセス:
```
http://<EC2のパブリックIP>:5002
```

管理者ログイン:
- ユーザー名: `admin`
- パスワード: `.env`で設定したADMIN_PASSWORD

## 📊 サービス管理

```bash
# 状態確認
sudo systemctl status fe-master

# 再起動
sudo systemctl restart fe-master

# ログ確認
sudo journalctl -u fe-master -f
```

## 🔥 トラブルシューティング

### アプリケーションが起動しない

```bash
# ログを確認
sudo journalctl -u fe-master -n 100

# 手動起動でエラー確認
cd ~/FE-Master-AWS
source venv/bin/activate
python app.py
```

### ポート5002にアクセスできない

```bash
# セキュリティグループを確認
# AWSコンソールでポート5002が開放されているか確認

# ファイアウォール確認
sudo ufw status
sudo ufw allow 5002
```

## 📚 詳細情報

- [デプロイガイド](DEPLOYMENT_GUIDE.md) - 詳細な手順
- [README](README.md) - プロジェクト概要
- [元のリポジトリ](https://github.com/d01ki/FE-master) - オリジナル版

## 💡 ヒント

### PostgreSQLを使用する場合

```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql

# PostgreSQL内で
CREATE DATABASE fe_exam;
CREATE USER fe_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fe_exam TO fe_user;
\q

# .envを更新
nano .env
# DATABASE_URL=postgresql://fe_user:your_password@localhost:5432/fe_exam
```

### nginxでポート80を使用

```bash
sudo apt install -y nginx

# deploy/nginx.confのパスを修正
sudo nano deploy/nginx.conf

# 設定を適用
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fe-master
sudo ln -s /etc/nginx/sites-available/fe-master /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# ポート80を開放
sudo ufw allow 80
```

### SSL証明書の設定

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

**問題が発生した場合**: GitHubのIssueで報告してください
**リポジトリ**: https://github.com/d01ki/FE-Master-AWS
