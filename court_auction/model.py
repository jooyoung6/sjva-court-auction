from framework import db
from datetime import datetime

class ModelCourtAuctionItem(db.Model):
    __tablename__ = 'plugin_court_auction_item'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.now)
    
    m_code = db.Column(db.String(50), unique=True, nullable=False)   # 경매마당 고유 코드
    case_number = db.Column(db.String(100))                         # 사건번호 (예: 2025타경30244)
    title = db.Column(db.String(255))                               # 물건명/소재지
    url = db.Column(db.String(512))                                 # 경매마당 상세 URL
    img_url = db.Column(db.String(512))                             # 매물 사진 URL
    appraisal_price = db.Column(db.String(100))                     # 감정가
    lowest_price = db.Column(db.String(100))                        # 최저입찰가
    auction_date = db.Column(db.String(100))                        # 입찰날짜
    times_failed = db.Column(db.Integer, default=0)                 # 유찰횟수
    is_read = db.Column(db.Boolean, default=False)                  # 내가 본 매물인지 여부 (True=읽음)

    def __init__(self, m_code, case_number, title, url, img_url, appraisal_price, lowest_price, auction_date, times_failed):
        self.m_code = m_code
        self.case_number = case_number
        self.title = title
        self.url = url
        self.img_url = img_url
        self.appraisal_price = appraisal_price
        self.lowest_price = lowest_price
        self.auction_date = auction_date
        self.times_failed = times_failed
        self.is_read = False