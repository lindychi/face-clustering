from app import app, db
from app.models import User
import face_recognition
from flask import request, jsonify

# 라우트 및 뷰 함수
