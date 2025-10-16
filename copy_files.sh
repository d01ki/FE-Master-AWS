#!/bin/bash

# FE-Master-AWS ファイルコピースクリプト
# 元のFE-masterリポジトリから必要なファイルをコピーします

set -e

echo "========================================="
echo "  FE-Master ファイルコピースクリプト"
echo "========================================="
echo ""

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 現在のディレクトリ確認
CURRENT_DIR=$(pwd)
if [[ ! "$CURRENT_DIR" =~ "FE-Master-AWS" ]]; then
    echo -e "${RED}✗${NC} このスクリプトはFE-Master-AWSディレクトリで実行してください"
    exit 1
fi

echo -e "${GREEN}✓${NC} 現在のディレクトリ: $CURRENT_DIR"
echo ""

# 元のリポジトリをクローン
TEMP_DIR="../temp-fe-master"

if [ -d "$TEMP_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} 既存の一時ディレクトリを削除中..."
    rm -rf "$TEMP_DIR"
fi

echo "元のリポジトリをクローン中..."
git clone https://github.com/d01ki/FE-master.git "$TEMP_DIR"
echo -e "${GREEN}✓${NC} クローン完了"
echo ""

# Pythonファイルをコピー
echo "========================================="
echo "Pythonファイルをコピー中..."
echo "========================================="

PYTHON_FILES=(
    "app.py"
    "database.py"
    "auth.py"
    "persistent_session.py"
    "question_manager.py"
    "achievement_system.py"
    "ranking_system.py"
    "helper_functions.py"
    "utils.py"
)

for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$TEMP_DIR/$file" ]; then
        cp "$TEMP_DIR/$file" .
        echo -e "${GREEN}✓${NC} $file をコピーしました"
    else
        echo -e "${RED}✗${NC} $file が見つかりません"
    fi
done

echo ""

# ディレクトリをコピー
echo "========================================="
echo "ディレクトリをコピー中..."
echo "========================================="

DIRECTORIES=(
    "routes"
    "templates"
    "static"
    "json_questions"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$TEMP_DIR/$dir" ]; then
        # 既存のディレクトリを削除
        if [ -d "$dir" ]; then
            rm -rf "$dir"
        fi
        cp -r "$TEMP_DIR/$dir" .
        echo -e "${GREEN}✓${NC} $dir/ をコピーしました"
    else
        echo -e "${YELLOW}⚠${NC} $dir/ が見つかりません（スキップ）"
    fi
done

echo ""

# utilsディレクトリの特別処理（ファイルとディレクトリが両方ある場合）
if [ -d "$TEMP_DIR/utils" ] && [ ! -f "utils.py" ]; then
    if [ -d "utils" ]; then
        rm -rf utils
    fi
    cp -r "$TEMP_DIR/utils" .
    echo -e "${GREEN}✓${NC} utils/ ディレクトリをコピーしました"
fi

# 不要なファイルを削除
echo ""
echo "========================================="
echo "不要なファイルを削除中..."
echo "========================================="

# Render用のファイルは不要
UNNECESSARY_FILES=(
    "build.sh"
    "app_postgresql.py"
)

for file in "${UNNECESSARY_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}✓${NC} $file を削除しました"
    fi
done

# 一時ディレクトリを削除
echo ""
echo "一時ディレクトリを削除中..."
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✓${NC} クリーンアップ完了"

echo ""
echo "========================================="
echo "  コピー完了！"
echo "========================================="
echo ""
echo "次のステップ:"
echo "  1. git status で変更を確認"
echo "  2. git add . で変更をステージング"
echo "  3. git commit -m \"アプリケーションファイルを追加\" でコミット"
echo "  4. git push origin main でプッシュ"
echo ""
echo -e "${GREEN}すべてのファイルが正常にコピーされました！${NC}"
