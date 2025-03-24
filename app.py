import streamlit as st

from config import BUCKET_NAME
from connection import s3_connection

# S3 설정
s3_client = s3_connection()
bucket_name = BUCKET_NAME  # S3 버킷 이름

# # PDF 파일을 S3에 업로드하고 URL 반환
# s3_url = upload_to_s3(f"./{pdf_path}", bucket_name, pdf_path)


def show_header():
    """
    모든 페이지 상단에 공통 헤더를 출력.
    헤더의 왼쪽에는 기업 로고를 표시.
    """
    # 헤더 영역을 columns를 사용해 좌우로 나눕니다.
    header_cols = st.columns([1, 4])
    with header_cols[0]:
        # 로고 이미지: 로고 파일 경로("logo.png")를 실제 파일 경로로 수정하세요.
        st.image("./src/imgs/logo.svg", width=80)


def main():
    # 페이지 기본 설정
    st.set_page_config(
        page_title="CarbonLink 활동데이터 입력",
        page_icon=":earth_americas:",
        layout="wide",
    )

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
            padding: 1rem 2rem;
        }
    /* 본문 영역 높이 120px, 가로·세로 중앙 정렬 */
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
        /* 헤더의 높이 100px로 설정 */
        .streamlit-header {
            height: 60px;
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
            width: 100px;
            margin: 0 auto;
            display: block;
            color: #
        }
        </style>
    """, unsafe_allow_html=True)

    # 각 페이지별 내용을 함수로 분리

    # 1) 첫 페이지 (인트로 페이지)
    def show_intro_page():
        st.markdown("<h1 class='centered-content title'>안녕하세요!</h1>",
                    unsafe_allow_html=True)
        st.markdown(
            "<h2 class='centered-content subtitle'>탄소 배출 관리 서비스 CarbonLink입니다.</h2>", unsafe_allow_html=True)
        st.markdown("""
            <p class="centered-content description">
            본 입력 양식은 SK에너지의 Scope 1, 2 탄소 배출량을 관리하기 위해 제공됩니다.<br>
            각 지사의 활동데이터 담당자분들께서는 매월 관리하시는 활동데이터를 입력해 주시면 됩니다.<br>
            이용에 어려움이 있으시다면 언제든 고객지원센터로 연락해 주세요.
            </p>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("계속하기"):
            st.session_state['page'] = '2nd_page'

    # 2) 두 번째 페이지 (기본정보 확인 페이지)
    def show_2nd_page():
        st.markdown("<h3 class='centered-content subtitle'>기본정보를 확인하겠습니다.</h3>",
                    unsafe_allow_html=True)
        st.markdown("""<div class="centered-content">
            <p class="description">
            아래 내용을 확인 후 이상이 없다면 <strong>'예'</strong>, 사실과 다르다면 <strong>'아니오'</strong>를 선택해 주세요.<br><br>
            1. 법인명: SK에너지(주) <br>
            2. 사업장: 울산지사<br><br>
            담당자분이 속한 법인명과 사업장 목록이 맞나요?
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

    # 3) 세 번째 페이지 ()

    def show_3rd_page():
        st.title("결과 페이지")
        carbon = st.session_state.get('carbon_amount', None)
        if carbon:
            st.write(f"입력하신 탄소 배출량은 **{carbon} kg** 입니다.")
        else:
            st.write("탄소 배출량이 입력되지 않았습니다.")

        if st.button("처음으로"):
            # 모든 상태 초기화 후 처음 페이지로 돌아가거나
            # 필요한 값만 초기화할 수도 있음
            st.session_state['page'] = 'intro'
            st.session_state['carbon_amount'] = None

        # 2-1) 두 번째 페이지 (문의 페이지)
    def show_inqury_page():
        st.markdown("<h3 class='subtitle'>문의 사항이 있으신가요?</h3>",
                    unsafe_allow_html=True)
        st.markdown("""
            <p class="description">
            문의 사항이 있으시면 아래 연락처로 문의해 주세요.<br><br>
            고객지원센터: 02-6207-5532<br>
            이메일:
            </p>
        """, unsafe_allow_html=True)

        # '뒤로가기' 버튼 추가 -> 바로 이전 페이지로 이동
        if st.button("뒤로가기"):
            st.session_state['page'] = '2nd_page'

    # 현재 page 상태에 따라 각 페이지 함수를 호출
    if st.session_state['page'] == 'intro':
        show_intro_page()
    elif st.session_state['page'] == '2nd_page':
        show_2nd_page()
    elif st.session_state['page'] == '3rd_page':
        show_3rd_page()
    elif st.session_state['page'] == 'inqury':
        show_inqury_page()
    elif st.session_state['page'] == 'result':
        show_result_page()


if __name__ == "__main__":
    main()
