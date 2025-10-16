"""
ランキングルート
"""
from flask import Blueprint, render_template
from auth import login_required

ranking_bp = Blueprint('ranking', __name__, url_prefix='/ranking')

@ranking_bp.route('/')
@login_required
def ranking():
    """ランキングページ（簡易版）"""
    return render_template('ranking.html')
