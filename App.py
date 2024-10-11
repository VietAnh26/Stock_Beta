import streamlit as st
import pandas as pd
import numpy as np
from vnstock3 import Vnstock
from datetime import datetime, timedelta

# Thiết lập theme bằng streamlit config
st.logo('logo.jpg',size='large')
st.title('🌾Lúa Hóa Chứng Khoán')

# Thiết lập theme bằng streamlit config

col1 = st.sidebar
with col1:
    st.image('ava.jpg')
    st.sidebar.markdown("<h3 style='color: blue;'>Nguyễn Việt Hùng - Trưởng phòng tư vấn đầu tư SSI</h3>", unsafe_allow_html=True)
    st.write('📞SĐT : 0986206379')
    st.write('Facebook : https://www.facebook.com/hungnv1203')
    st.write('Zalo : http://zaloapp.com/qr/p/1sm2m48ieznom')
    st.write('Nhóm cộng đồng lúa hóa : https://zalo.me/g/loktls600')
    
ck = st.text_input('Mã Chứng Khoán',value='ACB').upper()
stock = Vnstock().stock(symbol=str(ck), source='VCI')
company = Vnstock().stock(symbol=str(ck), source='TCBS').company
name = company.profile()['company_name'].iloc[0]
a = stock.listing.symbols_by_industries()
b = stock.quote.intraday(symbol=ck, show_log=False)

ggs = pd.read_csv('Cau_truyen.csv')
ggs = pd.DataFrame(ggs)
danh_gia = ggs['Đánh giá'][ggs['Cổ Phiếu'] == str(ck)]

# Tính khối lượng trung bình 15 ngày
today = datetime.today()
yesterday = today - timedelta(days=1)
start = today - timedelta(days=30)
val = stock.quote.history(start=str(start.date()),end=str(yesterday.date()))
vol_ave = val['volume'].iloc[7:]

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
    
# Tính ROE
roe = stock.finance.ratio(period='quarter', lang='vi')['Chỉ tiêu khả năng sinh lợi','ROE (%)'].iloc[0] * 100
    
# Tính ROA
roa = stock.finance.ratio(period='quarter', lang='vi')['Chỉ tiêu khả năng sinh lợi','ROA (%)'].iloc[0] * 100
    
# Lợi nhuận thuần
rev = stock.finance.income_statement(period='quarter', lang='vi')['Lợi nhuận thuần'].iloc[0]

ha = pd.read_csv('Ha.csv')
ha = pd.DataFrame(ha)


st.markdown(f'<span style="color:green; font-weight:bold;">{name}</span>', unsafe_allow_html=True)
st.metric(f'{ck} stock', value = current/1000, delta = f'{change}%')
#if change >= 0:
    #st.markdown(f"<p style='color:green;'>{change}%</p>", unsafe_allow_html=True)
#else:
    #st.markdown(f"<p style='color:red;'>🔻{change}%</p>", unsafe_allow_html=True)

box = st.selectbox('Danh mục',['Thông tin cơ bản','Chu trình kinh doanh','Ban lãnh đạo','Cổ đông','Công ty con, liên kết','Sự kiện','Tin tức'],index=0)
if box == 'Thông tin cơ bản':
    st.write('Ngành : ',a['icb_name2'][a['symbol'] == ck].iloc[0])
    if str(ck) in list(ggs['Cổ Phiếu']):
        st.write('Đánh giá ngắn hạn : ',danh_gia.iloc[0])
    st.write('Giá hiện tại : ',int(b['price'].iloc[-1]),'vnđ')

    st.write('Khối lượng trung bình 15 ngày : ',round(vol_ave.mean(),0))

    st.write('Sức mạnh giá : ',rsi)

    st.write('ROE(Q) : ',roe,'%')

    st.write('ROA(Q) : ',roa,'%')

    st.write('Lợi nhuận thuần(Q) : ',rev,'vnđ')

elif box == 'Chu trình kinh doanh':
    if str(ck) in ha.iloc[:,0].values:
        mck = ha[ha.iloc[:,0] == str(ck)]
        for i in mck.columns[[1,3,4,5,6,7]]:  # Lặp qua các cột trong mck
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
    st.write(events[['event_name','notify_date']])
    
else:
    news = company.news()
    st.write(news[['title','publish_date']])