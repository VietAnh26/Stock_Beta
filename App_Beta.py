import streamlit as st
import pandas as pd
import numpy as np
from vnstock3 import Vnstock
from datetime import datetime, timedelta

# Cache cho những thao tác tốn kém tài nguyên hoặc gọi API
@st.cache_data
def get_stock_data(ck):
    stock = Vnstock().stock(symbol=ck, source='VCI')
    company = Vnstock().stock(symbol=ck, source='TCBS').company
    return stock, company


def calculate_indicators(stock, ck):
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    start = today - timedelta(days=30)
    
    # Tính khối lượng trung bình 15 ngày
    val = stock.quote.history(start=str(start.date()), end=str(yesterday.date()))
    vol_ave = val['volume'].iloc[7:]

    # Tính RSI
    val['diff'] = val['close'].diff()
    rsi_data = val.iloc[8:]
    gain = rsi_data[rsi_data['diff'] > 0]
    loss = rsi_data[rsi_data['diff'] < 0]
    gain_ave = gain['diff'].sum() / 14
    loss_ave = abs(loss['diff'].sum() / 14)  # Lấy trị tuyệt đối
    rsi = 100 - (100 / (1 + (gain_ave / loss_ave)))

    # Tính ROE và ROA
    roe = stock.finance.ratio(period='quarter', lang='vi')['Chỉ tiêu khả năng sinh lợi','ROE (%)'].iloc[0] * 100
    roa = stock.finance.ratio(period='quarter', lang='vi')['Chỉ tiêu khả năng sinh lợi','ROA (%)'].iloc[0] * 100

    # Lợi nhuận thuần
    rev = stock.finance.income_statement(period='quarter', lang='vi')['Lợi nhuận thuần'].iloc[0]

    return vol_ave.mean(), rsi, roe, roa, rev

# Tải logo và thông tin cố định
st.image('logo.jpg', width=200)
st.title('🌾Lúa Hóa Chứng Khoán')

# Sidebar với thông tin cố định
col1 = st.sidebar
with col1:
    st.image('ava.jpg')
    st.sidebar.markdown("<h3 style='color: blue;'>Nguyễn Việt Hùng - Trưởng phòng tư vấn đầu tư - Công ty SSI</h3>", unsafe_allow_html=True)
    st.write('📞SĐT : 0986206379')
    st.write('Facebook : https://www.facebook.com/hungnv1203')
    st.write('Zalo : http://zaloapp.com/qr/p/1sm2m48ieznom')
    st.write('Nhóm cộng đồng lúa hóa : https://zalo.me/g/loktls600')

# Nhập mã chứng khoán
ck = st.text_input('Mã CK', value='ACB').upper()
st.info('Vui lòng nhấn enter sau khi nhập mã!')


# Lấy dữ liệu từ API và tính toán
stock, company = get_stock_data(ck)
vol_ave, rsi, roe, roa, rev = calculate_indicators(stock, ck)

# Tra cứu từ Google Sheet
ggs = pd.read_csv('Cau_truyen.csv')
danh_gia = ggs['Đánh giá'][ggs['Cổ Phiếu'] == ck]

# Dữ liệu Google Sheet (tải một lần)
ha = pd.read_csv('Ha.csv')
ha = pd.DataFrame(ha)
mck = ha[ha.iloc[:, 0] == ck]

#Tính biến động giá
today = datetime.today()
yesterday = today - timedelta(days=1)
start = today - timedelta(days=30)
current = stock.quote.intraday(symbol=ck, show_log=False).iloc[-1,1]
lag = stock.quote.history(start=str(start.date()), end=str(yesterday.date())).iloc[-1,4]*1000
change = (current - lag)/(lag)*100

# Hiển thị thông tin
st.markdown(f'<span style="color:green; font-weight:bold;">{company.profile()["company_name"].iloc[0]}</span>', unsafe_allow_html=True)
st.metric(f'{ck} stock', value = current/1000, delta = f'{round(change,2)}%')

# Lựa chọn hiển thị theo danh mục
box = st.selectbox('Danh mục', ['Thông tin cơ bản', 'Chu trình kinh doanh', 'Ban lãnh đạo', 'Cổ đông', 'Công ty con, liên kết', 'Sự kiện', 'Tin tức'], index=0)

if box == 'Thông tin cơ bản':
    st.write('Ngành : ', stock.listing.symbols_by_industries()['icb_name2'][stock.listing.symbols_by_industries()['symbol'] == ck].iloc[0])
    if ck in list(ggs['Cổ Phiếu']):
        st.write('Đánh giá ngắn hạn : ', danh_gia.iloc[0])
    st.write('Giá hiện tại : ', int(stock.quote.intraday(symbol=ck, show_log=False)['price'].iloc[-1]), 'vnđ')
    st.write('Khối lượng trung bình 15 ngày : ', round(vol_ave, 0))
    st.write('Sức mạnh giá (RSI) : ', rsi)
    st.write('ROE(Q) : ', roe, '%')
    st.write('ROA(Q) : ', roa, '%')
    st.write('Lợi nhuận thuần(Q) : ', rev, 'vnđ')

elif box == 'Chu trình kinh doanh':
    if str(ck) in mck.iloc[:,0]:
        for i in mck.columns[[1, 3, 4, 5, 6, 7]]:
            st.write(f'⁃ **{i}** : ')
            text = mck[i].iloc[0]  # Lấy giá trị từ hàng đầu tiên
            st.text(f'     {text}')
    else:
        st.write('Không có dữ liệu')

elif box == 'Ban lãnh đạo':
    st.write(company.officers())

elif box == 'Cổ đông':
    st.write(company.shareholders())

elif box == 'Công ty con, liên kết':
    st.write(company.subsidiaries())

elif box == 'Sự kiện':
    events = company.events()
    st.write(events[['event_name', 'notify_date']])

else:
    news = company.news()
    st.write(news[['title', 'publish_date']])
