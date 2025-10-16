"""
模擬試験ルート
"""
from flask import Blueprint, render_template, session
from auth import login_required

exam_bp = Blueprint('exam', __name__, url_prefix='/exam')

@exam_bp.route('/')
@login_required
def exam():
    """模擬試験（簡易版）"""
    return render_template('exam.html')
