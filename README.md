# 🎓 FE Master - AWS EC2対応版

基本情報技術者試験 学習アプリケーション（AWS EC2デプロイ最適化版）

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-black.svg)](https://flask.palletsprojects.com/)

**🔗 リポジトリ**: https://github.com/d01ki/FE-Master-AWS  
**📚 元のリポジトリ**: https://github.com/d01ki/FE-master

---

## 🌟 主な特徴

### データ永続化
- ✅ セッション情報をデータベースで管理
- ✅ サーバー再起動後もログイン状態を維持
- ✅ Renderの無料枠の制限（スリープ時のデータ消失）を完全解決

### AWS EC2最適化
- ✅ systemdサービスによる自動起動・管理
- ✅ gunicornによる本番運用対応
- ✅ nginxリバースプロキシ設定（オプション）
- ✅ 無料枠（t2.micro）で快適に動作

### 簡単デプロイ
- ✅ ワンコマンドでセットアップ完了
- ✅ 自動化されたデプロイスクリプト
- ✅ 環境変数による安全な設定管理

---

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/d01ki/FE-Master-AWS.git
cd FE-Master-AWS
```

### 2. 元のファイルをコピー

```bash
chmod +x copy_files.sh
./copy_files.sh
```

### 3. 環境変数の設定

```bash
cp .env.example .env
nano .env
```

必須設定:
```env
SECRET_KEY=<64文字のランダム文字列>
ADMIN_PASSWORD=<安全なパスワード>
DATABASE_URL=sqlite:///fe_exam.db
```

SECRET_KEY生成:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. デプロイ実行

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### 5. アクセス

ブラウザで http://<EC2のパブリックIP>:5002 にアクセス

---

## 📋 前提条件

- **AWS EC2インスタンス**: t2.micro以上（無料枠対象）
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.10以上
- **データベース**: SQLite（デフォルト）またはPostgreSQL

### セキュリティグループ設定

- SSH (22): 自分のIPのみ
- Custom TCP (5002): 0.0.0.0/0
- HTTP (80): 0.0.0.0/0（nginxを使用する場合）
- HTTPS (443): 0.0.0.0/0（SSL証明書設定後）

---

## 📁 プロジェクト構造

```
FE-Master-AWS/
├── README.md              # このファイル
├── QUICKSTART.md          # 最速デプロイガイド
├── DEPLOYMENT_GUIDE.md    # 詳細デプロイ手順
├── .env.example           # 環境変数サンプル
├── .gitignore             # Git除外設定
├── requirements.txt       # Python依存パッケージ
├── config.py              # アプリケーション設定
├── deploy.sh              # 自動デプロイスクリプト
├── copy_files.sh          # ファイルコピースクリプト
├── deploy/
│   └── nginx.conf         # nginx設定
└── (以下、copy_files.shで追加)
    ├── app.py
    ├── database.py
    ├── auth.py
    ├── persistent_session.py
    ├── routes/
    ├── templates/
    ├── static/
    └── json_questions/
```

---

## 🔧 運用コマンド

### サービス管理

```bash
# 状態確認
sudo systemctl status fe-master

# 再起動
sudo systemctl restart fe-master

# 停止
sudo systemctl stop fe-master

# 起動
sudo systemctl start fe-master

# 自動起動の有効化/無効化
sudo systemctl enable fe-master
sudo systemctl disable fe-master
```

### ログ確認

```bash
# リアルタイムログ
sudo journalctl -u fe-master -f

# 最新50行
sudo journalctl -u fe-master -n 50

# エラーログのみ
sudo journalctl -u fe-master -p err
```

### アプリケーション更新

```bash
cd ~/FE-Master-AWS
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fe-master
```

---

## 💾 データベース管理

### SQLiteバックアップ

```bash
cp fe_exam.db fe_exam_backup_$(date +%Y%m%d).db
```

### PostgreSQLへの移行

```bash
# PostgreSQLインストール
sudo apt install -y postgresql postgresql-contrib

# データベース作成
sudo -u postgres psql
CREATE DATABASE fe_exam;
CREATE USER fe_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fe_exam TO fe_user;
\q

# .env更新
nano .env
# DATABASE_URL=postgresql://fe_user:your_password@localhost:5432/fe_exam

# 再起動
sudo systemctl restart fe-master
```

---

## 🌐 nginx設定（オプション）

### インストールと設定

```bash
sudo apt install -y nginx

# 設定ファイルのパスを編集
sudo nano deploy/nginx.conf

# 適用
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fe-master
sudo ln -s /etc/nginx/sites-available/fe-master /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### SSL証明書（Let's Encrypt）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 セキュリティ設定

### ファイアウォール

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5002
sudo ufw enable
```

### 定期更新

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📊 主な機能

- 📱 **レスポンシブデザイン**: PC・スマホ・タブレット対応
- 🔒 **ユーザー認証**: 登録・ログイン・ログアウト
- 💾 **セッション永続化**: サーバー再起動後もログイン維持
- 📝 **問題演習**: ランダム、ジャンル別、模擬試験
- 📊 **学習履歴**: 詳細な進捗管理と成績分析
- 🏆 **ランキングシステム**: ユーザー間での競争
- 🎯 **実績システム**: 学習モチベーション向上
- 🖼️ **画像付き問題**: 図表を含む問題に対応
- 👑 **管理者機能**: 問題管理、ユーザー管理

---

## 🛠️ トラブルシューティング

### アプリケーションが起動しない

```bash
# ログ確認
sudo journalctl -u fe-master -n 100

# 手動起動
cd ~/FE-Master-AWS
source venv/bin/activate
python app.py
```

### ポートが使用中

```bash
# プロセス確認
sudo lsof -i :5002

# プロセス停止
sudo kill -9 <PID>
```

### データベース接続エラー

```bash
# PostgreSQL確認
sudo systemctl status postgresql

# .env確認
cat .env | grep DATABASE_URL
```

---

## 📚 ドキュメント

- [QUICKSTART.md](QUICKSTART.md) - 最速デプロイガイド
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 詳細デプロイ手順
- [元のリポジトリ](https://github.com/d01ki/FE-master) - オリジナル版

---

## 🆚 元のFE-masterとの違い

| 機能 | FE-master | FE-Master-AWS |
|------|-----------|---------------|
| デプロイ先 | Render | AWS EC2 |
| セッション管理 | ファイルシステム | データベース |
| 自動起動 | ❌ | ✅ systemd |
| サーバー | 開発用 | gunicorn（本番用） |
| データ永続化 | 不安定 | ✅ 完全対応 |
| nginx対応 | ❌ | ✅ オプション |
| デプロイスクリプト | ❌ | ✅ 自動化 |

---

## 🤝 貢献

プルリクエストを歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

---

## 📝 ライセンス

MITライセンス - 詳細は [LICENSE](LICENSE) ファイルを参照

---

## 🆘 サポート

問題が発生した場合:
1. [QUICKSTART.md](QUICKSTART.md)を確認
2. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)のトラブルシューティングを確認
3. GitHubのIssueで報告

---

## 🎯 今後の予定

- [ ] Docker対応
- [ ] CI/CD パイプライン
- [ ] 自動バックアップスクリプト
- [ ] CloudWatch監視設定
- [ ] Auto Scaling対応

---

**Made with ❤️ for AWS EC2**

⭐ このプロジェクトが役に立ったら、スターをお願いします！
