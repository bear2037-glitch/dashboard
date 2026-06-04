import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(page_title='홈앤쇼핑 모바일 매출일보', layout='wide', initial_sidebar_state='expanded')

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('sales_data.csv')
    df['일자'] = pd.to_datetime(df['일자'])
    return df

df = load_data()

# 차분한 톤의 색상 팔레트
colors = {
    'primary': '#4E79A7',
    'secondary': '#76B7B2',
    'accent1': '#E4AA34',
    'accent2': '#B07AA1',
    'accent3': '#F28E2B',
    'accent4': '#59A14F'
}

# 사이드바 필터
st.sidebar.title('필터')

# 1. 날짜 범위
date_range = st.sidebar.date_input(
    '날짜 범위',
    value=(df['일자'].min().date(), df['일자'].max().date()),
    min_value=df['일자'].min().date(),
    max_value=df['일자'].max().date(),
    label_visibility='collapsed'
)

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = df['일자'].min()
    end_date = df['일자'].max()

# 2. 주문채널 필터
channels = sorted(df['주문채널'].unique())
selected_channels = st.sidebar.multiselect(
    '주문채널',
    options=channels,
    default=channels,
    label_visibility='collapsed'
)

# 3. 주문영역 필터
areas = sorted(df['주문영역'].unique())
selected_areas = st.sidebar.multiselect(
    '주문영역',
    options=areas,
    default=areas,
    label_visibility='collapsed'
)

# 4. 매출 구분 필터
sales_type = st.sidebar.selectbox(
    '매출 구분',
    options=['전체', 'TV방송', '모바일'],
    label_visibility='collapsed'
)

# 필터 적용
filtered_df = df[
    (df['일자'] >= start_date) &
    (df['일자'] <= end_date) &
    (df['주문채널'].isin(selected_channels)) &
    (df['주문영역'].isin(selected_areas))
]

# 페이지 제목
st.title('홈앤쇼핑 모바일 매출일보')

# 일별 합계 데이터 생성
daily_df = filtered_df.groupby('일자')[['주문액_방송', '주문액_모바일']].sum().reset_index()
daily_df = daily_df.sort_values('일자')

if len(daily_df) >= 2:
    today = daily_df.iloc[-1]
    yesterday = daily_df.iloc[-2]

    tv_today = today['주문액_방송'] / 1_000_000
    tv_yesterday = yesterday['주문액_방송'] / 1_000_000
    tv_change = ((tv_today - tv_yesterday) / tv_yesterday * 100) if tv_yesterday != 0 else 0

    mobile_today = today['주문액_모바일'] / 1_000_000
    mobile_yesterday = yesterday['주문액_모바일'] / 1_000_000
    mobile_change = ((mobile_today - mobile_yesterday) / mobile_yesterday * 100) if mobile_yesterday != 0 else 0

    # KPI 카드 (6개)
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(label='오늘 TV매출', value=f'{tv_today:.1f}백만원', delta=None)

    with col2:
        st.metric(label='어제 TV매출', value=f'{tv_yesterday:.1f}백만원', delta=None)

    with col3:
        st.metric(label='TV 증감률', value=f'{tv_change:.1f}%', delta=None)

    with col4:
        st.metric(label='오늘 모바일매출', value=f'{mobile_today:.1f}백만원', delta=None)

    with col5:
        st.metric(label='어제 모바일매출', value=f'{mobile_yesterday:.1f}백만원', delta=None)

    with col6:
        st.metric(label='모바일 증감률', value=f'{mobile_change:.1f}%', delta=None)

st.divider()

# 선그래프: 일별 매출 추이
fig_line = go.Figure()

fig_line.add_trace(go.Scatter(
    x=daily_df['일자'],
    y=daily_df['주문액_방송'] / 1_000_000,
    mode='lines+markers',
    name='TV방송',
    line=dict(color=colors['primary'], width=3),
    marker=dict(size=8, symbol='circle')
))

fig_line.add_trace(go.Scatter(
    x=daily_df['일자'],
    y=daily_df['주문액_모바일'] / 1_000_000,
    mode='lines+markers',
    name='모바일',
    line=dict(color=colors['secondary'], width=3),
    marker=dict(size=8, symbol='circle')
))

fig_line.update_layout(
    title='일별 매출 추이',
    xaxis_title='날짜',
    yaxis_title='매출 (백만원)',
    hovermode='x unified',
    font=dict(family='Malgun Gothic', size=12),
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    height=400,
    margin=dict(l=50, r=50, t=70, b=50)
)

st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# 막대그래프와 파이그래프
col1, col2 = st.columns(2)

with col1:
    # 막대그래프: 채널별 매출
    channel_df = filtered_df.groupby('주문채널')[['주문액_방송', '주문액_모바일']].sum().reset_index()
    channel_df = channel_df.sort_values('주문액_모바일', ascending=False)

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=channel_df['주문채널'],
        y=channel_df['주문액_방송'] / 1_000_000,
        name='TV방송',
        marker_color=colors['primary']
    ))

    fig_bar.add_trace(go.Bar(
        x=channel_df['주문채널'],
        y=channel_df['주문액_모바일'] / 1_000_000,
        name='모바일',
        marker_color=colors['secondary']
    ))

    fig_bar.update_layout(
        title='채널별 매출',
        xaxis_title='주문채널',
        yaxis_title='매출 (백만원)',
        barmode='group',
        font=dict(family='Malgun Gothic', size=12),
        height=400,
        margin=dict(l=50, r=50, t=70, b=50)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # 파이그래프: 영역별 매출 비중
    area_df = filtered_df.groupby('주문영역')['주문액_모바일'].sum().reset_index()
    area_df = area_df.sort_values('주문액_모바일', ascending=False)

    fig_pie = go.Figure(data=[go.Pie(
        labels=area_df['주문영역'],
        values=area_df['주문액_모바일'] / 1_000_000,
        hole=0.35,
        marker=dict(colors=[colors['primary'], colors['secondary'], colors['accent1'],
                           colors['accent2'], colors['accent3'], colors['accent4']])
    )])

    fig_pie.update_layout(
        title='모바일 매출 영역별 비중',
        font=dict(family='Malgun Gothic', size=12),
        height=400,
        margin=dict(l=50, r=50, t=70, b=50)
    )

    st.plotly_chart(fig_pie, use_container_width=True)
