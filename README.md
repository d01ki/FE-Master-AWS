# 🎓 FE Master - AWS EC2対応版

基本情報技術者試験 学習アプリケーション(AWS EC2デプロイ最適化版)

## 🌟 主な改善点

- ✅ **データ永続化**: セッション情報をデータベースで管理し、サーバー再起動後もログイン状態を維持
- ✅ **AWS EC2最適化**: systemdサービス、nginx設定による本番運用対応
- ✅ **簡単デプロイ**: ワンコマンドでセットアップ・デプロイが完了
- ✅ **セキュリティ強化**: 環境変数による秘密情報の管理

## 📋 前提条件

- AWS EC2インスタンス(t2.micro以上推奨、無料枠対象)
- Ubuntu 22.04 LTS
- Python 3.10+
- PostgreSQL 13+(またはSQLite)

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/d01ki/FE-Master-AWS.git
cd FE-Master-AWS
```

### 2. 環境変数の設定

```bash
cp .env.example .env
nano .env  # エディタで編集
```

必須の環境変数:
```env
SECRET_KEY=<強力なランダム文字列>
ADMIN_PASSWORD=<管理者パスワード>
DATABASE_URL=sqlite:///fe_exam.db  # またはPostgreSQLのURL
```

SECRET_KEYの生成:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. 自動デプロイ

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

このスクリプトが以下を自動実行します:
- 依存パッケージのインストール
- Python仮想環境のセットアップ
- データベースの初期化
- systemdサービスの設定
- nginxの設定(オプション)
- アプリケーションの起動

### 4. アクセス

- ローカル: http://localhost:5002
- 外部: http://<EC2のパブリックIP>:5002

## 🔧 手動デプロイ(詳細)

### システムパッケージのインストール

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

### Python仮想環境のセットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### PostgreSQLのセットアップ(オプション)

```bash
# PostgreSQLユーザーとデータベース作成
sudo -u postgres psql
CREATE DATABASE fe_exam;
CREATE USER fe_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fe_exam TO fe_user;
\q

# .envファイルに設定
DATABASE_URL=postgresql://fe_user:your_password@localhost:5432/fe_exam
```

### systemdサービスの設定

```bash
sudo cp deploy/fe-master.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fe-master
sudo systemctl start fe-master
sudo systemctl status fe-master
```

### nginx設定(オプション、HTTPSおよびポート80での公開用)

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fe-master
sudo ln -s /etc/nginx/sites-available/fe-master /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📁 プロジェクト構造

```
FE-Master-AWS/
├── app.py                 # メインアプリケーション
├── config.py              # 設定管理
├── database.py            # データベース管理
├── auth.py                # 認証システム
├── persistent_session.py  # セッション永続化
├── requirements.txt       # Python依存パッケージ
├── .env.example           # 環境変数サンプル
├── deploy.sh              # 自動デプロイスクリプト
├── deploy/
│   ├── fe-master.service  # systemdサービス設定
│   └── nginx.conf         # nginx設定
├── routes/                # ルーティング
├── templates/             # HTMLテンプレート
├── static/                # CSS、JS、画像
└── json_questions/        # 問題データ(JSON形式)
```

## 🔄 デプロイ後の操作

### アプリケーションの再起動

```bash
sudo systemctl restart fe-master
```

### ログの確認

```bash
sudo journalctl -u fe-master -f
```

### アプリケーションの停止

```bash
sudo systemctl stop fe-master
```

### データベースのバックアップ(SQLiteの場合)

```bash
cp fe_exam.db fe_exam_backup_$(date +%Y%m%d).db
```

### PostgreSQLのバックアップ

```bash
pg_dump -U fe_user fe_exam > backup_$(date +%Y%m%d).sql
```

## 🔒 セキュリティのベストプラクティス

1. **ファイアウォールの設定**
```bash
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP(nginxを使用する場合)
sudo ufw allow 443     # HTTPS(SSL証明書設定後)
sudo ufw allow 5002    # アプリケーション(直接アクセスする場合)
sudo ufw enable
```

2. **SSL証明書の設定(Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **定期的なアップデート**
```bash
sudo apt update && sudo apt upgrade -y
```

## 🛠️ トラブルシューティング

### アプリケーションが起動しない

```bash
# ログを確認
sudo journalctl -u fe-master -n 50

# 手動で起動してエラーを確認
cd /path/to/FE-Master-AWS
source venv/bin/activate
python app.py
```

### データベース接続エラー

```bash
# PostgreSQLの状態確認
sudo systemctl status postgresql

# .envファイルのDATABASE_URL確認
cat .env | grep DATABASE_URL
```

### ポートが既に使用中

```bash
# ポート5002を使用しているプロセスを確認
sudo lsof -i :5002

# 必要に応じてプロセスを終了
sudo kill -9 <PID>
```

## 📊 機能

- 📱 レスポンシブデザイン(PC・スマホ対応)
- 🔒 ユーザー認証(登録・ログイン・ログアウト)
- 💾 セッション永続化(サーバー再起動後もログイン状態維持)
- 📝 問題演習(ランダム、ジャンル別、模擬試験)
- 📊 学習履歴の記録・表示
- 🏆 ランキングシステム
- 🎯 実績システム
- 🖼️ 画像付き問題対応
- 👑 管理者機能(問題管理、ユーザー管理)

## 🤝 貢献

プルリクエストを歓迎します！

## 📝 ライセンス

MITライセンス

## 🆘 サポート

Issueでお気軽にご質問ください。

---

**Made with ❤️ for AWS EC2**
