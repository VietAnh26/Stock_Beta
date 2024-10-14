import streamlit as st
import pandas as pd
import numpy as np
from vnstock3 import Vnstock
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Lúa Hóa Chứng Khoán",
    page_icon="🌾",
    layout="wide",
)

if 'active_button' not in st.session_state:
    st.session_state.active_button = 'button1'
    
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.logo('logo.jpg',size='large')
st.title('🌾Lúa Hóa Chứng Khoán')
st.markdown("<h3 style='color: #ed6868; font-size: 16px;'> Lúa hóa cung cấp miễn phí platform về thông tin các mã chứng khoán giúp nhà đầu tư nhanh chóng có được đánh giá tổng quan về doanh nghiệp.<br><br> Quý nhà đầu tư có thể liên hệ trực tiếp với chuyên viên tư vấn thông qua đường link tại sidebar bên trái!</h3>", unsafe_allow_html=True)
st.write('---')
minute = datetime.today().minute

col1 = st.sidebar

button1 = col1.button('📊 Thông tin chứng khoán')
button2 = col1.button('🛠️ Quản trị viên')
col1.write('---')

if 0 <= minute <= 10 or 21 <= minute <= 30 or 41 <= minute <= 50:
    col1.image('ava.jpg')
    col1.markdown("<h3 style='color: #5793f2;'>Nguyễn Việt Hùng - Trưởng phòng Tư vấn đầu tư Công ty SSI</h3>", unsafe_allow_html=True)
    col1.write('📞SĐT : 0986206379')
    col1.write('Facebook : https://www.facebook.com/hungnv1203')
    col1.write('Zalo : http://zaloapp.com/qr/p/1sm2m48ieznom')
    col1.write('Nhóm cộng đồng lúa hóa : https://zalo.me/g/loktls600')
else:
    col1.image('Thanh.jpg')
    col1.markdown("<h3 style='color: #5793f2;'>Nguyễn Quang Thành - Chuyên viên Tư vấn đầu tư Công ty SSI</h3>", unsafe_allow_html=True)
    col1.write('📞SĐT : 0974446582')
    col1.write('Zalo : http://zaloapp.com/qr/p/rmo4vohuml4t')
    col1.write('Facebook : https://www.facebook.com/thanhnguyenssi')

if button1:
    st.session_state.active_button = 'button1'

if button2:
    st.session_state.active_button = 'button2'

# Xử lý nếu button1 được chọn (mặc định là button1 khi vừa vào)
if st.session_state.active_button == 'button1':
    try:
        stock = Vnstock().stock(symbol='ACB', source='VCI')
        b = stock.listing.all_symbols()['ticker'][1:]
        ck = st.selectbox(label = 'Mã Chứng Khoán',options = b).strip().upper()
        st.info('Vui lòng nhấn Enter sau khi nhập mã và chờ 20s!')
        with st.spinner("Đang tải dữ liệu chứng khoán... Vui lòng chờ!"):
            stock = Vnstock().stock(symbol=str(ck), source='VCI')
            company = Vnstock().stock(symbol=str(ck), source='TCBS').company

            bld = company.officers()
            bld.columns = ['Tên','Vị trí','Sở hữu(%)']
            bld['Sở hữu(%)'] = bld['Sở hữu(%)']*100

            cd = company.shareholders()
            cd.columns = ['Cổ đông','Sở hữu(%)']
            cd['Sở hữu(%)'] = cd['Sở hữu(%)']*100

            sub = company.subsidiaries()
            sub.columns = ['Công ty','Tỷ lệ sở hữu(%)']
            sub['Tỷ lệ sở hữu(%)'] = sub['Tỷ lệ sở hữu(%)']*100

            events = company.events()[['event_name','notify_date']]
            events.columns = ['Sự kiện','Ngày thông báo']

            news = company.news()[['title','publish_date']]
            news.columns = ['Tiêu đề','Ngày công bố']

            name = company.profile()['company_name'].iloc[0]
            a = stock.listing.symbols_by_industries()

            ggs = pd.read_csv('Cau_truyen.csv')
            ggs = pd.DataFrame(ggs)
            danh_gia = ggs['Đánh giá'][ggs['Cổ Phiếu'] == str(ck)]

            # Tính khối lượng trung bình 15 ngày
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            start = today - timedelta(days=30)
            val = stock.quote.history(start=str(start.date()),end=str(yesterday.date()))
            vol_ave = round(val['volume'].iloc[7:].mean(),0)
            vol_ave = '{:,}'.format(vol_ave)

            current = stock.quote.intraday(symbol=ck, show_log=False).iloc[-1,1]
            lag = stock.quote.history(symbol=ck,start=str(start.date()), end=str(yesterday.date())).iloc[-1,4]*1000
            change = round((current - lag)/(lag)*100,2)

            # Tính RSI
            val['diff'] = val['close'].diff()
            rsi = val.iloc[8:]
            gain = rsi[rsi['diff'] > 0]
            loss = rsi[rsi['diff'] < 0]
            gain_ave = gain['diff'].sum() / 14
            loss_ave = loss['diff'].sum() / 14
            rsi = 100 - (100/(1+(gain_ave/(-loss_ave))))
            rsi = round(rsi,2)

            # Tính ROE
            roe = stock.finance.ratio(period='quarter', lang='vi')['Chỉ tiêu khả năng sinh lợi','ROE (%)'].iloc[0] * 100
            roe = round(roe,2)

            # Tính ROA
            roa = stock.finance.ratio(period='quarter', lang='vi')['Chỉ tiêu khả năng sinh lợi','ROA (%)'].iloc[0] * 100
            roa = round(roa,2)

            # Lợi nhuận thuần
            rev = stock.finance.income_statement(period='quarter', lang='vi')['Lợi nhuận thuần'].iloc[0]
            rev = '{:,}'.format(rev)

            url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSPCc3dalt0t1wIKkZtuIZ3EezJCIKsT8FnnSI7EqUlGNnxDQ3hDJW66-VBgXd59lajDNZEt2leRveP/pub?output=csv'
            ha = pd.read_csv(url)
            ha = pd.DataFrame(ha)


            st.markdown(f'<span style="color:green; font-weight:bold;">{name}</span>', unsafe_allow_html=True)
            st.metric(f'{ck} stock', value = current/1000)
            if change >= 0:
                change = str(change)
                st.markdown(f"<p style='color:green;'>+ {change}%</p>", unsafe_allow_html=True)
            else:
                change = str(change)
                st.markdown(f"<p style='color:red;'>🔻{change}%</p>", unsafe_allow_html=True)

            t1,t2,t3,t4,t5,t6 = st.tabs(['⭐ **Thông tin cơ bản**','👨🏻‍💼 **Ban lãnh đạo**','🤝 **Cổ đông**','🏬 **Công ty con, liên kết**','📅 **Sự kiện**','📰 **Tin tức**'])
            with t1:
                st.subheader('Hình thức kinh doanh')
                st.write('⁃ **Ngành** : ',a['icb_name2'][a['symbol'] == ck].iloc[0])
                if str(ck) in list(ggs['Cổ Phiếu']):
                    st.write('⁃ **Đánh giá ngắn hạn** : ',danh_gia.iloc[0])
                if str(ck) in ha.iloc[:,0].values:
                    mck = ha[ha.iloc[:,0] == str(ck)]
                    for i in mck.columns[[1,3,4,5,6,7]]:  # Lặp qua các cột trong mck
                        st.write(f'⁃ **{i}** : ')
                        text = mck[i].iloc[0]  # Lấy giá trị từ hàng đầu tiên
                        st.text(f'     {text}')

                st.subheader('Chỉ số cơ bản')
                st.write('Giá hiện tại : ',int(current),'vnđ')

                st.write('Khối lượng trung bình 15 ngày : ',vol_ave)

                st.write('Sức mạnh giá : ',rsi)

                st.write('ROE(Q) : ',roe,'%')

                st.write('ROA(Q) : ',roa,'%')

                st.write('Lợi nhuận thuần(Q) : ',rev,'vnđ')

            t2.write(bld)

            t3.write(cd)

            t4.write(sub)

            t5.write(events)

            t6.write(news)
    except Exception as e:
        st.error(f'Không có dữ liệu cho mã chứng khoán {ck}!')

if st.session_state.active_button == 'button2':
    login_placeholder = st.empty()

    # Kiểm tra trạng thái đăng nhập
    if not st.session_state.logged_in:
        with login_placeholder.container():  # Tạo container để chứa nội dung đăng nhập
            st.warning("Vui lòng đăng nhập để truy cập Admin")

            # Nhập tài khoản và mật khẩu
            username = st.text_input("Tài khoản")
            password = st.text_input("Mật khẩu", type="password")

            # Tạo một button để xác nhận đăng nhập
            login_button = st.button("Đăng nhập")

            # Kiểm tra thông tin tài khoản
            if login_button:
                if username == "admin" and password == "123456":  # Thay bằng thông tin tài khoản thực tế
                    st.session_state.logged_in = True
                    st.success("Đăng nhập thành công!")

                    # Xóa nội dung đăng nhập sau khi đăng nhập thành công
                    login_placeholder.empty()
                else:
                    st.error("Tài khoản hoặc mật khẩu không đúng!")

    # Nếu đã đăng nhập, hiển thị nội dung Admin và xóa phần đăng nhập
    if st.session_state.logged_in:
        login_placeholder.empty()  # Xóa toàn bộ phần đăng nhập nếu đã đăng nhập thành công
        st.write("Chào mừng bạn đến trang Quản trị viên!")
        # Thêm các chức năng admin tại đây
