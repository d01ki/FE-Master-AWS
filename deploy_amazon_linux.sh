#!/bin/bash

# FE-Master AWS EC2 自動デプロイスクリプト (Amazon Linux 2/2023対応)

set -e  # エラーが発生したら停止

echo "========================================="
echo "  FE-Master AWS EC2 デプロイスクリプト"
echo "  (Amazon Linux対応版)"
echo "========================================="
echo ""

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 現在のディレクトリを保存
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$SCRIPT_DIR"

echo -e "${GREEN}✓${NC} スクリプトディレクトリ: $APP_DIR"

# root権限チェック
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}✗${NC} このスクリプトはroot権限で実行する必要があります"
    echo "  sudo ./deploy_amazon_linux.sh を実行してください"
    exit 1
fi

# .envファイルの存在確認
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}⚠${NC}  .envファイルが見つかりません"
    echo "  .env.exampleをコピーして.envを作成してください:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# 環境変数の読み込み
export $(grep -v '^#' "$APP_DIR/.env" | xargs)

# SECRET_KEYとADMIN_PASSWORDのチェック
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-change-this-in-production-use-random-string" ]; then
    echo -e "${RED}✗${NC} SECRET_KEYが設定されていません"
    echo "  python3 -c \"import secrets; print(secrets.token_hex(32))\" で生成してください"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ] || [ "$ADMIN_PASSWORD" = "your-secure-admin-password-here" ]; then
    echo -e "${RED}✗${NC} ADMIN_PASSWORDが設定されていません"
    exit 1
fi

echo -e "${GREEN}✓${NC} 環境変数の確認完了"
echo ""

# ステップ1: システムパッケージの更新とインストール
echo "========================================="
echo "ステップ 1/7: システムパッケージの更新"
echo "========================================="

# Amazon Linuxのバージョン確認
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS: $NAME $VERSION"
fi

# Python3のインストール確認
if ! command -v python3 &> /dev/null; then
    echo "Python3をインストール中..."
    yum install -y python3 python3-pip
else
    echo "Python3は既にインストールされています"
fi

# python3-develのインストール（psycopg2のビルドに必要）
yum install -y python3-devel gcc

echo -e "${GREEN}✓${NC} システムパッケージのインストール完了"
echo ""

# ステップ2: Python仮想環境のセットアップ
echo "========================================="
echo "ステップ 2/7: Python仮想環境のセットアップ"
echo "========================================="
cd "$APP_DIR"

# 既存の仮想環境を削除（クリーンインストール）
if [ -d "venv" ]; then
    echo "既存の仮想環境を削除中..."
    rm -rf venv
fi

# 新しい仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓${NC} Python仮想環境のセットアップ完了"
echo ""

# ステップ3: 必要なディレクトリの作成
echo "========================================="
echo "ステップ 3/7: ディレクトリの作成"
echo "========================================="
mkdir -p uploads
mkdir -p json_questions
mkdir -p static/images
mkdir -p logs

# 適切な権限を設定
chown -R ec2-user:ec2-user "$APP_DIR"

echo -e "${GREEN}✓${NC} ディレクトリの作成完了"
echo ""

# ステップ4: データベースの初期化
echo "========================================="
echo "ステップ 4/7: データベースの初期化"
echo "========================================="
echo "データベースは初回起動時に自動的に初期化されます"
echo -e "${GREEN}✓${NC} データベース設定確認完了"
echo ""

# ステップ5: systemdサービスファイルの作成
echo "========================================="
echo "ステップ 5/7: systemdサービスの設定"
echo "========================================="

# サービスファイルを動的に生成
cat > /etc/systemd/system/fe-master.service <<EOF
[Unit]
Description=FE-Master Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# サービスの再読み込みと有効化
systemctl daemon-reload
systemctl enable fe-master

echo -e "${GREEN}✓${NC} systemdサービスの設定完了"
echo ""

# ステップ6: ファイアウォールの設定
echo "========================================="
echo "ステップ 6/7: ファイアウォールの設定"
echo "========================================="

# Amazon Linuxのファイアウォール設定
# AWSセキュリティグループで管理することが多いため、ローカルのfirewalldは無効化することが多い
if systemctl is-active --quiet firewalld; then
    echo "firewalldが実行中です"
    read -p "ポート5002を開放しますか？ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        firewall-cmd --permanent --add-port=5002/tcp
        firewall-cmd --reload
        echo -e "${GREEN}✓${NC} ファイアウォールの設定完了"
    fi
else
    echo "firewalldは実行されていません（AWSセキュリティグループで管理してください）"
fi
echo ""

# ステップ7: アプリケーションの起動
echo "========================================="
echo "ステップ 7/7: アプリケーションの起動"
echo "========================================="

# サービスの停止（既に起動している場合）
systemctl stop fe-master 2>/dev/null || true

# サービスの起動
systemctl start fe-master

# 起動確認
sleep 3
if systemctl is-active --quiet fe-master; then
    echo -e "${GREEN}✓${NC} アプリケーションが正常に起動しました"
else
    echo -e "${RED}✗${NC} アプリケーションの起動に失敗しました"
    echo "ログを確認してください: sudo journalctl -u fe-master -n 50"
    exit 1
fi

echo ""
echo "========================================="
echo "  デプロイ完了！"
echo "========================================="
echo ""

# パブリックIPの取得（Amazon Linux EC2の場合）
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo "アプリケーション情報:"
echo "  - ローカルアクセス: http://localhost:5002"
if [ ! -z "$PUBLIC_IP" ]; then
    echo "  - 外部アクセス: http://${PUBLIC_IP}:5002"
fi
echo ""
echo "便利なコマンド:"
echo "  - サービス状態確認: sudo systemctl status fe-master"
echo "  - ログ表示: sudo journalctl -u fe-master -f"
echo "  - 再起動: sudo systemctl restart fe-master"
echo "  - 停止: sudo systemctl stop fe-master"
echo ""
echo -e "${GREEN}デプロイが正常に完了しました！${NC}"
echo ""
echo "⚠️  重要: AWSセキュリティグループでポート5002を開放してください"
