import os
import datetime
from flask import Flask, render_template, url_for
from pykrx.stock import get_market_ohlcv_by_date
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.font_manager as fm # <- 추가

app = Flask(__name__)

matplotlib.use('Agg')

CHART_IMAGE_FOLDER = os.path.join('static', 'images')
if not os.path.exists(CHART_IMAGE_FOLDER):
    os.makedirs(CHART_IMAGE_FOLDER)
app.config['CHART_IMAGE_FOLDER'] = CHART_IMAGE_FOLDER

# --- 폰트 설정 부분 수정 (여기만 변경하면 됩니다) ---
# 폰트 파일 경로 지정: Flask 앱의 루트 경로를 기준으로 static/fonts 폴더 내 폰트 파일 지정
FONT_PATH = os.path.join(app.root_path, 'static', 'fonts', 'NanumGothic.ttf')

# 폰트 매니저에 폰트 추가 및 설정
if os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams['font.family'] = 'NanumGothic' # 폰트 파일명에서 확장자를 제외한 이름 (폰트 속성 이름)
    print(f"DEBUG: Matplotlib font set to NanumGothic from {FONT_PATH}")
else:
    print(f"WARNING: NanumGothic.ttf not found at {FONT_PATH}. Hanja/Hangul may not display correctly.")
    # 대체 폰트 또는 기본 폰트 사용 (한글 깨질 가능성 높음)
    plt.rcParams['font.family'] = 'sans-serif' 

plt.rcParams['axes.unicode_minus'] = False
# --- 폰트 설정 부분 수정 끝 ---

# ... (나머지 app.py 코드는 동일) ...


def plot_ohlcv_chart(df, stock_name, image_filename):
    if len(df) < 2:
        print(f"차트를 그릴 데이터가 부족합니다 (최소 2일 필요): {stock_name}")
        return False

    df.index = pd.to_datetime(df.index)

    fig, ax = plt.subplots(figsize=(8, 5))
    
    last_two_days = df.tail(2)
    x_positions = np.arange(len(last_two_days))

    for i, row in last_two_days.iterrows():
        open_p = row['시가']
        close_p = row['종가']
        high_p = row['고가']
        low_p = row['저가']
        
        x_pos = x_positions[last_two_days.index.get_loc(i)]

        if close_p >= open_p:
            color = 'red'
            ax.vlines(x_pos, open_p, close_p, color=color, linewidth=5)
        else:
            color = 'blue'
            ax.vlines(x_pos, close_p, open_p, color=color, linewidth=5)
        
        ax.vlines(x_pos, low_p, high_p, color=color)

    ax.set_xticks(x_positions)
    ax.set_xticklabels([d.strftime('%m-%d') for d in last_two_days.index])
    
    ax.set_title(f'{stock_name} 최근 2일 캔들 주가', fontsize=16)
    ax.set_ylabel('가격 (원)', fontsize=12)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    ax.ticklabel_format(axis='y', style='plain', useOffset=False, useLocale=True)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    image_path = os.path.join(app.config['CHART_IMAGE_FOLDER'], image_filename)
    plt.savefig(image_path)
    plt.close(fig)
    return True

def plot_weekly_line_chart(df, stock_name, image_filename):
    if df.empty:
        print(f"일주일 종가 선 그래프를 그릴 데이터가 없습니다: {stock_name}")
        return False

    df_plot = df.copy()
    df_plot.index = pd.to_datetime(df_plot.index)

    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(df_plot.index, df_plot['종가'], marker='o', linestyle='-', color='green', linewidth=2)

    ax.set_xticks(df_plot.index)
    ax.set_xticklabels([d.strftime('%m-%d') for d in df_plot.index], rotation=45, ha='right')

    ax.set_title(f'{stock_name} 최근 {len(df_plot)}거래일 종가 추이', fontsize=16)
    ax.set_ylabel('종가 (원)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    ax.ticklabel_format(axis='y', style='plain', useOffset=False, useLocale=True)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    image_path = os.path.join(app.config['CHART_IMAGE_FOLDER'], image_filename)
    plt.savefig(image_path)
    plt.close(fig)
    return True


@app.route("/")
def home():
    now_kst = datetime.datetime.now() # 현재 시간 (한국 시간으로 가정)
    
    # 한국 주식 시장 개장 시간 (평일 오전 9시 ~ 오후 3시 30분)
    market_open_time = now_kst.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close_time = now_kst.replace(hour=15, minute=30, second=0, microsecond=0)

    is_trading_day = True
    # 주말 (토=5, 일=6) 확인
    if now_kst.weekday() in [5, 6]: 
        is_trading_day = False
    
    # 공휴일은 pykrx가 내부적으로 처리하므로 별도 판단 로직은 넣지 않음.
    # pykrx가 데이터를 못 가져오면 자동으로 이전 영업일 데이터를 가져오게 됨.


    price_message = "주가 정보를 가져올 수 없습니다."
    change_info = ""
    display_date = "알 수 없음"
    chart_2day_image_url = None
    chart_weekly_image_url = None

    current_price = None
    daily_change = 0
    change_rate = 0.0

    start_date_for_ohlcv = (now_kst - datetime.timedelta(days=7)).strftime("%Y%m%d")
    end_date_for_ohlcv = now_kst.strftime("%Y%m%d")

    df_ohlcv_range = get_market_ohlcv_by_date(start_date_for_ohlcv, end_date_for_ohlcv, "003230")

    if not df_ohlcv_range.empty:
        latest_day_data = df_ohlcv_range.iloc[-1]
        
        actual_trade_date_dt = datetime.datetime.strptime(latest_day_data.name.strftime("%Y%m%d"), "%Y%m%d")
        display_date = actual_trade_date_dt.strftime("%Y년 %m월 %d일")
        current_price = int(latest_day_data['종가'])

        if len(df_ohlcv_range) >= 2:
            previous_day_data = df_ohlcv_range.iloc[-2]
            previous_day_price = int(previous_day_data['종가'])
            
            daily_change = current_price - previous_day_price
            
            if previous_day_price != 0:
                change_rate = (daily_change / previous_day_price) * 100
            else:
                change_rate = 0.0
        else:
            daily_change = 0
            change_rate = 0.0

        # --- 메시지 생성 로직 변경 ---
        price_type_text = "종가" # 기본값은 종가

        # 1. 오늘이 영업일이고, 장이 열려있는 시간이라면 "현재가"로 표시
        #    단, pykrx가 오늘 날짜 데이터를 가져왔을 때만 해당 (ex. 공휴일인데 장중시간이면 제외)
        if is_trading_day and \
           market_open_time <= now_kst <= market_close_time and \
           actual_trade_date_dt.date() == now_kst.date():
            price_type_text = "현재가"
        # 2. 장 마감 후이거나, 주말/공휴일인데 가장 최신 데이터가 오늘 날짜이면 "종가"
        elif actual_trade_date_dt.date() == now_kst.date():
             price_type_text = "종가"
        # 3. 그 외 (주말/공휴일인데 가장 최신 데이터가 어제 날짜인 경우)
        else:
            price_type_text = "종가" # 이 경우는 이전 영업일의 종가

        price_message = f"{display_date} {price_type_text}: {current_price:,}원"
        # --- 메시지 생성 로직 변경 끝 ---
        
        if len(df_ohlcv_range) >= 2:
            change_sign = ""
            color = "black"
            if daily_change > 0:
                change_sign = "▲"
                color = "red"
            elif daily_change < 0:
                change_sign = "▼"
                color = "blue"
            
            change_info = f"<br><span style='color:{color};'>전일대비 {change_sign} {abs(daily_change):,}원 ({change_rate:.2f}%)</span>"
        else:
            change_info = "<br><span>전일 대비 정보 없음</span>"
        
        chart_2day_filename = 'samyang_stock_2day_chart.png'
        if plot_ohlcv_chart(df_ohlcv_range, '삼양식품', chart_2day_filename):
            chart_2day_image_url = url_for('static', filename=os.path.join('images', chart_2day_filename).replace('\\', '/'))
        
        chart_weekly_filename = 'samyang_stock_weekly_line_chart.png'
        if plot_weekly_line_chart(df_ohlcv_range, '삼양식품', chart_weekly_filename):
            chart_weekly_image_url = url_for('static', filename=os.path.join('images', chart_weekly_filename).replace('\\', '/'))

    return render_template("index.html", 
                           message=price_message, 
                           change_info=change_info, 
                           chart_2day_image_url=chart_2day_image_url,
                           chart_weekly_image_url=chart_weekly_image_url)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)