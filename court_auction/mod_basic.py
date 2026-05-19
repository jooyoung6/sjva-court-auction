import requests
from bs4 import BeautifulSoup
from framework import db
from plugin import PluginPageBase
from .model import ModelCourtAuctionItem

class ModBasic(PluginPageBase):
    def __init__(self, P):
        super(ModBasic, self).__init__(P, child_name='basic')
        self.search_url = "https://madangs.com/search?g_use_type=1005&use_type=1005&state=10&share=2&g_share=2&sort=view_desc&page=1"

    def crawl_auction(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(self.search_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 목록에서 m_code 추출 생략 (이전 설계와 동일하게 매물 코드 수집 후 루프 진입)
        m_codes = self.get_m_codes_from_list(soup)

        for m_code in m_codes:
            exist = db.session.query(ModelCourtAuctionItem).filter_by(m_code=m_code).first()
            if exist:
                continue

            detail_url = f"https://madangs.com/caview?m_code={m_code}"
            detail_res = requests.get(detail_url, headers=headers)
            detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
            
            page_text = detail_soup.get_text()
            
            # 본문에 '태양광'이 포함된 경우에만 수집 진행
            if "태양광" in page_text:
                try:
                    # 1. 사건번호 및 타이틀 추출
                    case_number = detail_soup.find('span', {'class': 'case-number'}).text.strip() if detail_soup.find('span', {'class': 'case-number'}) else "사건번호 없음"
                    title = detail_soup.find('h1', {'class': 'title'}).text.strip() if detail_soup.find('h1', {'class': 'title'}) else "태양광 발전소 매물"
                    
                    # 2. 대표 이미지 URL 추출
                    img_tag = detail_soup.find('img', {'class': 'main-thumb'})
                    img_url = img_tag['src'] if img_tag else ""

                    # 3. 금액 정보 파싱 (감정가, 최저가)
                    appraisal_price = "정보 없음"
                    lowest_price = "정보 없음"
                    price_table = detail_soup.find('table', {'class': 'price-info'})
                    if price_table:
                        rows = price_table.find_all('tr')
                        for row in rows:
                            if "감정" in row.text:
                                appraisal_price = row.find_all('td')[-1].text.strip()
                            if "최저" in row.text:
                                lowest_price = row.find_all('td')[-1].text.strip()

                    # 4. 입찰 날짜 및 유찰 횟수 추출
                    auction_date = "일정 확인 필요"
                    times_failed = 0
                    date_tag = detail_soup.find('span', {'class': 'auction-date'})
                    if date_tag:
                        auction_date = date_tag.text.strip()
                        
                    failed_tag = detail_soup.find('span', {'class': 'failed-count'})
                    if failed_tag:
                        # 텍스트 내에서 숫자만 추출 (예: "2회 유찰" -> 2)
                        times_failed = int(''.join(filter(str.isdigit, failed_tag.text)))

                    # 데이터베이스 저장
                    new_item = ModelCourtAuctionItem(
                        m_code=m_code, case_number=case_number, title=title, url=detail_url, img_url=img_url,
                        appraisal_price=appraisal_price, lowest_price=lowest_price, auction_date=auction_date, times_failed=times_failed
                    )
                    db.session.add(new_item)
                    db.session.commit()
                    
                    # 브라우저 푸시 전송 (생략)
                    self.send_browser_push(case_number, detail_url)
                except Exception as e:
                    self.P.logger.error(f"매물 파싱 중 에러 발생 ({m_code}): {str(e)}")

    # 사용자가 웹 화면에서 매물 링크를 클릭했을 때 '내가 본 매물'로 업데이트해주는 AJAX 처리 함수
    def process_ajax(self, sub, req):
        if sub == 'mark_read':
            m_code = req.form['m_code']
            item = db.session.query(ModelCourtAuctionItem).filter_by(m_code=m_code).first()
            if item:
                item.is_read = True  # 읽음 상태로 변경
                db.session.commit()
                return jsonify({'result': 'success'})
            return jsonify({'result': 'fail'})