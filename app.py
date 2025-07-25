import streamlit as st

from datetime import datetime
import time
import os
import requests
import json
import uuid
from urllib import parse

from config import BUCKET_NAME
from connection import s3_connection

# 페이지 기본 설정
st.set_page_config(
    page_title="CarbonLink 활동데이터 수집",
    page_icon=":earth_americas:",
    layout="wide",
)


# S3 설정
s3_client = s3_connection()
bucket_name = BUCKET_NAME  # S3 버킷 이름


def ocr_reqeust(file_url, file_name):
    # file_url encodint
    # encoded_url = parse.urlparse(file_url)
    encoded_url = parse.quote(file_url, safe=':/&?=')

    ocr_uri = "https://cw1vu838h8.apigw.ntruss.com/custom/v1/40011/3598c637f2ca79bc3aabfdc5fb94baf268f2f0321914f80be8b8f71e43bdacb9/infer"
    headers = {
        'X-OCR-SECRET': 'SEdYam1jdlVtZGpKRU5Jc2RZclVEcUlZWFduZndtdHM=',
    }

    # fileformat을 다양하게 설정
    fileformat = file_url.split('.')[-1]
    body = {
        "images": [
            {
                "format": f'{fileformat}',
                "name": f'{file_name}',
                "url": f'{encoded_url}',
                "templateIds": [36653]
            }
        ],
        "lang": "ko",
        "requestId": str(uuid.uuid4()),
        "timestamp": int(datetime.now().timestamp()),
        "version": "V2"
    }

    # try except 추가
    try:
        response = requests.post(
            ocr_uri, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return print(response.status_code)
    except Exception as e:
        st.error(f"API 호출 실패: {e}")
        return None


def upload_to_s3(file_path, bucket_name, object_name):
    try:

        s3_client.upload_file(file_path, bucket_name,
                              f'ocr_test/{object_name}')
        s3_url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/ocr_test/{object_name}"

        st.success('File uploaded successfully')
        return s3_url
    except Exception as e:
        st.error(f"File upload failed: {e}")
        return None


base_year = datetime.now().year
base_month = datetime.now().month - 1

# year를 2025년부터 내림차순으로 정렬
year_options = [str(year) for year in range(base_year, base_year-2, -1)]
# month는 숫자로 표현
month_options = [str(month) for month in range(base_month, 0, -1)]


def show_header():
    """
    모든 페이지 상단에 공통 헤더를 출력.
    헤더의 왼쪽에는 기업 로고를 표시.
    """
    # 헤더 영역을 columns를 사용해 좌우로 나눕니다.
    header_cols = st.columns([1, 3])
    with header_cols[0]:
        # 로고 이미지: 로고 파일 경로("logo.png")를 실제 파일 경로로 수정하세요.
        st.image("./src/imgs/logo.svg", width=120)


def main():
    # 모든 페이지에 공통 헤더 표시
    show_header()

    # 세션 스테이트 초기화
    if 'page' not in st.session_state:
        st.session_state['page'] = 'intro'  # 시작 페이지 이름
    if 'carbon_amount' not in st.session_state:
        st.session_state['carbon_amount'] = None

    # 공통 CSS 스타일 (가운데 정렬, 폰트 크기 등)
    st.markdown("""
        <style>
        /* Streamlit의 기본 블록 컨테이너 최대 너비 제한 해제 */
        .main .block-container {
            max-width: 100%;
            padding: 1rem 1rem;
        }
        /* 가로·세로 중앙 정렬 */
        .page-content {
            height: 20px;
        }
        /* 가운데 정렬 */
        .centered-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        /* 헤더의 높이 40px로 설정 */
        .streamlit-header {
            height: 20px;
        }
        /* 메인 타이틀 스타일 */
        .title {
            font-size: 2em;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        /* 서브 타이틀 스타일 */
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 1.5rem;
        }
        /* 본문 설명 스타일 */
        .description {
            font-size: 1em;
            line-height: 1.6;
            margin-bottom: 2rem;
        }
        /* 안내 문구 스타일 */
        .subtext {
            font-size: 0.9em;
            color: #666;
            margin-top: 0.5rem;
        }
        /* st.button 가운데 정렬 */
        div.stButton > button {
            width: 100%;
            margin: 0 auto;
            display: block;
        }
        /* st.date_input 가운데 정렬 */
        div.stDateInput > input {
            width: 100px;
            margin: 0 auto;
            display: block;
        }
        </style>
    """, unsafe_allow_html=True)

    # 각 페이지별 내용을 함수로 분리

    # 1) 첫 페이지 (인트로 페이지)
    def show_intro_page():
        # div 태그를 사용해 가운데 정렬
        st.markdown("<h1 class='centered-content title'>안녕하세요!</h1>",
                    unsafe_allow_html=True)
        st.markdown(
            "<h2 class='centered-content subtitle'>탄소 데이터 자동수집 솔루션<br>CarbonLink 입니다.</h2>", unsafe_allow_html=True)
        st.markdown("""
                    <div class="centered-content">
            <p class="description">
            본 입력 양식은 만신홀딩스 조직경계의 Scope 1, 2 탄소 배출 데이터를 수집하기 위해 제공됩니다.<br>
            각 지사의 활동데이터 담당자분들께서는 매월 관리하시는 활동데이터를 입력해 주시면 됩니다.<br>
            이용에 어려움이 있으시다면 언제든 고객지원센터로 연락해 주세요.
            </p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 3개의 버튼을 가로로 나란히 배치하기 위해 columns 사용
        col_spacer1, col_continue, col_spacer3 = st.columns([
            1, 1, 1])
        with col_continue:
            if st.button("계속하기"):
                st.session_state['page'] = '2nd_page'

    # 2) 두 번째 페이지 (기본정보 확인 페이지)
    def show_2nd_page():
        st.markdown("<h2 class='centered-content subtitle'>기본 정보를 확인하겠습니다.</h2>",
                    unsafe_allow_html=True)
        st.markdown("""<div class="centered-content">
            <p class="description">
            아래 내용을 확인 후 이상이 없다면 <strong>'예'</strong>, 사실과 다르다면 <strong>'아니오'</strong>를 선택해 주세요.<br><br>
            1. 법인명: 만신홀딩스 <br>
            2. 사업장: 울산지사<br><br>
            담당자분이 속한 법인과 사업장이 맞나요?
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 버튼을 가로로 나란히 배치하기 위해 columns 사용
        col_spacer1, col_spacer2, col_yes, col_no, col_spacer3, colspacer4 = st.columns([
            1, 1, 1, 1, 1, 1])
        with col_yes:
            yes_btn = st.button("예")
        with col_no:
            no_btn = st.button("아니오")

        # 클릭 시 상태값 설정 후 다음 페이지로 이동
        if yes_btn:
            st.session_state['basic_info_check'] = "예"
            st.session_state['page'] = '3rd_page'
        elif no_btn:
            st.session_state['basic_info_check'] = "아니오"
            st.session_state['page'] = 'inqury'

    # 3) 세 번째 페이지 (날짜 입력 페이지)
    def show_3rd_page():
        st.markdown("<h3 class='centered-content subtitle'>기준 연월을 입력해주세요.</h3>",
                    unsafe_allow_html=True)
        st.markdown("""<div class="centered-content">
            <p class="description">
            해당 활동데이터의 적용 날짜를 선택해 주세요.<br><br>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # colmuns를 6개를 사용해 가로로 나란히 배치
        col_spacer1, year_month, col_spacer3 = st.columns(
            3)
        with year_month:
            selected_year = st.selectbox("연도 선택", year_options)
            selected_month = st.selectbox("월 선택", month_options)

        st.markdown("<br>", unsafe_allow_html=True)

        # 버튼을 가로로 나란히 배치하기 위해 columns 사용
        col_spacer1, col_spacer2, col_confirm, col_backward, col_spacer3, colspacer4 = st.columns([
            1, 1, 1, 1, 1, 1])
        with col_confirm:
            confirm_btn = st.button("확인")

        with col_backward:
            backward_btn = st.button("뒤로가기")

        # '확인' 버튼 클릭 시 선택한 날짜 저장 및 4번째 페이지로 이동
        if confirm_btn:
            st.session_state['selected_year'] = selected_year
            st.session_state['selected_month'] = selected_month
            st.session_state['page'] = '4th_page'

        # '뒤로가기' 버튼 클릭 시 이전 페이지로 이동
        if backward_btn:
            st.session_state['page'] = '2nd_page'

    # 4) 네 번째 페이지 (배출원 정보 확인)
    def show_4th_page():
        st.markdown("<h3 class='centered-content subtitle'>배출원 정보를 확인해주세요.</h3>",
                    unsafe_allow_html=True)

        st.markdown("""<div class="centered-content">
            <p class="description">
            아래 배출원 정보를 확인 후 이상이 없다면 <strong>'예'</strong>, 변경된 사항이 있다면 <strong>'아니오'</strong>를 선택해 주세요.<br><br>
            1. 포터(6169)/경유/주유비(원)<br>
            2. 그랜저(4452)/휘발유/L<br>
            <br>
            배출원 목록에 이상이 없나요?
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 버튼을 가로로 나란히 배치하기 위해 columns 사용
        col_spacer1, col_spacer2, col_yes, col_no, col_spacer3, colspacer4 = st.columns([
            1, 1, 1, 1, 1, 1])
        with col_yes:
            yes_btn = st.button("예")
        with col_no:
            no_btn = st.button("아니오")

        # 클릭 시 상태값 설정 후 다음 페이지로 이동
        if yes_btn:
            st.session_state['basic_info_check'] = "예"
            st.session_state['page'] = '5th_page'
        elif no_btn:
            st.session_state['basic_info_check'] = "아니오"
            st.session_state['page'] = 'inqury_2nd'

    # 5) 다섯 번째 페이지 (증빙자료 업로드 및 활동 데이터 확인 페이지)
    def show_5th_page():
        if 'ocr_completed' not in st.session_state:
            st.session_state['ocr_completed'] = False

        st.markdown("<h3 class='centered-content subtitle'>증빙자료를 업로드해주세요.</h3>",
                    unsafe_allow_html=True)
        st.markdown("""
            <p class="centered-content description">
            아래 버튼을 클릭하여 업로드할 증빙자료를 선택해 주세요.
            </p>
        """, unsafe_allow_html=True)

        # columns 3개를 사용해서 버튼을 가운데 정렬
        col_spacer1, file_uploader, col_spacer2 = st.columns([1, 2, 1])
        with file_uploader:
            uploaded_file = st.file_uploader(
                "증빙자료 업로드", type=['pdf', 'jpg', 'jpeg', 'png'])
            # S3에 uploaded_file 업로드
            if uploaded_file is not None:
                # 파일을 같은 경로에 저장
                # 업로드한 파일의 내용을 읽어옴 (바이너리 모드)
                file_bytes = uploaded_file.read()
                # 업로드한 파일의 이름
                file_name = uploaded_file.name

                # 현재 경로에 파일 저장 (바이너리 쓰기 모드)
                with open(f"./{file_name}", "wb") as f:
                    f.write(file_bytes)

                # 파일 이름
                # PDF 파일을 S3에 업로드하고 URL 반환
                s3_url = upload_to_s3(f"./{file_name}",
                                      bucket_name, file_name)

                st.session_state['proof_file_name'] = file_name
                st.session_state['proof_file_url'] = s3_url

                # # 작업이 끝난 후, 로컬 파일 삭제
                # if os.path.exists(f'./{file_name}'):
                #     os.remove(f'./{file_name}')

        if 'proof_file_url' in st.session_state:

            # columns 3개를 사용해서 버튼을 가운데 정렬
            col_spacer1, image_print, ocr_result, col_spacer2 = st.columns([
                1, 1, 1, 1])
            with image_print:
                # 업로드 완료후 s3 file url 출력
                # 이미지 파일이 업로드된 경우 이미지 출력
                st.image(uploaded_file, caption='Uploaded Image',
                         use_container_width=True)

            with ocr_result:
                if st.session_state['ocr_completed'] == False:
                    with st.spinner("데이터 추출 중..."):
                        time.sleep(2)
                        ocr_data = ocr_reqeust(s3_url, file_name)
                        if ocr_data is None:
                            st.error("OCR 데이터 추출에 실패했습니다. 다시 시도해 주세요.")
                            return

                        # OCR 결과를 세션 상태에 저장
                        st.session_state['ocr_data'] = ocr_data
                        # OCR 완료 상태 플래그 설정
                        st.session_state['ocr_completed'] = True

                ocr_data = st.session_state['ocr_data']
                evidence_title = ocr_data['images'][0]['title']['inferText']
                inventory_source = ocr_data['images'][0]['fields'][0]['inferText']
                inventory_name = ocr_data['images'][0]['fields'][1]['inferText']
                period = ocr_data['images'][0]['fields'][2]['inferText']
                amount = ocr_data['images'][0]['fields'][3]['inferText']

                # '데이터 추출 완료' 메시지 markdown으로 출력
                st.markdown("<h3 class='centered-content subtitle'>데이터 추출 완료</h3>",
                            unsafe_allow_html=True)

                # markdown으로 출력, 배경색상 회색
                st.markdown(f"""
                        <div class="description" style="background-color:#f0f0f0; padding: 20px; border-radius: 10px; height: 400px;">
                        <p>{evidence_title}</p>
                        <p>에너지원:<strong>{inventory_source}</strong></p>
                        <p>번호: <strong>{inventory_name}</strong></p>
                        <p>기간: <strong>{period}</strong></p>
                        <p>수량: <strong>{amount}</strong></p>
                        </div>
                    """, unsafe_allow_html=True)

                # 데이터 추출 완료 후 '제출하기' 버튼 출력
                # ocr_data가 존재하면 '제출하기' 버튼 출력
                # 'ocr_completed' 플래그가 True인 경우에만 '제출하기' 버튼 출력

                if st.session_state['ocr_completed'] == True:
                    if st.button("제출하기"):
                        st.session_state['page'] = 'final'

                    if st.button("수정하기"):
                        st.session_state['page'] = '4th_page'

                # col_submit, col_cancle = st.columns(
                #     [1, 1])
                # with col_submit:
                #     submit_btn = st.button("제출하기")
                #     if submit_btn:
                #         st.session_state['page'] = 'final'  # 결과 페이지로 이동
                # # 수정하기 클릭시 수량을 직접 입력
                # with col_cancle:
                #     cancle_btn = st.button("수정하기")

    # 6) 결과 페이지

    def show_result_page():
        st.markdown("<h3 class='centered-content subtitle'>감사합니다!</h3>",
                    unsafe_allow_html=True)
        st.markdown("""<div class="centered-content">
            <p class="description">
            활동데이터가 성공적으로 제출되었습니다.<br>
            제출하신 데이터는 만신홀딩스의 탄소배출량 계산에 활용됩니다.<br>
            </p>
            </div>
        """, unsafe_allow_html=True)

    def show_inqury_page():
        st.markdown("<h3 class='centered-contnet subtitle'>문의 사항이 있으신가요?</h3>",
                    unsafe_allow_html=True)
        st.markdown("""
                    <div class="centered-content">
            <p class="description">
            문의 사항이 있으시면 아래 연락처로 문의해 주세요.<br><br>
            고객지원센터: 02-6207-5532<br>
            이메일:
            </p>
            </div>
        """, unsafe_allow_html=True)

        # '뒤로가기' 버튼 추가 -> 바로 이전 페이지로 이동
        if st.button("뒤로가기"):
            st.session_state['page'] = '2nd_page'

    def show_2nd_inqury_page():
        st.markdown("<h3 class='centered-contnet subtitle'>문의 사항이 있으신가요?</h3>",
                    unsafe_allow_html=True)
        st.markdown("""
                    <div class="centered-content">
            <p class="description">
            문의 사항이 있으시면 아래 연락처로 문의해 주세요.<br><br>
            고객지원센터: 02-6207-5532<br>
            이메일:
            </p>
            </div>
        """, unsafe_allow_html=True)

        # '뒤로가기' 버튼 추가 -> 바로 이전 페이지로 이동
        if st.button("뒤로가기"):
            st.session_state['page'] = '4th_page'

    # 현재 page 상태에 따라 각 페이지 함수를 호출
    if st.session_state['page'] == 'intro':
        show_intro_page()
    elif st.session_state['page'] == '2nd_page':
        show_2nd_page()
    elif st.session_state['page'] == '3rd_page':
        show_3rd_page()
    elif st.session_state['page'] == '4th_page':
        show_4th_page()
    elif st.session_state['page'] == '5th_page':
        show_5th_page()
    elif st.session_state['page'] == 'inqury':
        show_inqury_page()
    elif st.session_state['page'] == 'inqury_2nd':
        show_2nd_inqury_page()
    elif st.session_state['page'] == 'final':
        show_result_page()


if __name__ == "__main__":
    main()
