#encoding:utf-8
from flask import Blueprint
bp=Blueprint("common", __name__)

@bp.route("/common")
def index():
    return "這是公共部分首頁!"