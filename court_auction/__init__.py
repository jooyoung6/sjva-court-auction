import os
import sys
from framework import app, logger

# 플러그인 고유 ID 정의
package_name = 'court_auction'

# 필요한 필수 라이브러리 자동 설치 및 로드
try:
    from pywebpush import webpush, WebPushException
except ImportError:
    try:
        os.system(f"{sys.executable} -m pip install pywebpush")
        from pywebpush import webpush, WebPushException
    except Exception as e:
        logger.error(f"[{package_name}] 라이브러리 설치 실패: {str(e)}")

# SJVA 핵심 설정 로드
try:
    from .setup import plugin_load, plugin_unload
except ImportError:
    pass
