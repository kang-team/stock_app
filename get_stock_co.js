const axios = require('axios');

const SERVICE_KEY = 'mxw0YlGZCzHXFx6TOizB9tpLSv0fqSIyrVDCfmkBXktLR4oyuBfsNb1PdSUIMJUkVXlQ1HfFTxeTQ5qqLaeTIA==';
const STOCK_CODE = '003230'; // 삼양식품 종목 코드
const BASE_URL = 'http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo';

function formatDateToYYYYMMDD(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}

async function getStockPrice() {
    const MAX_DAYS = 7;

    for (let i = 0; i < MAX_DAYS; i++) {
        const targetDate = new Date();
        targetDate.setDate(targetDate.getDate() - i);
        const basDt = formatDateToYYYYMMDD(targetDate);

        console.log(`📌 ${basDt} 날짜의 주가 정보를 시도 중...`);

        try {
            const response = await axios.get(BASE_URL, {
                params: {
                    serviceKey: SERVICE_KEY,
                    numOfRows: 1,
                    pageNo: 1,
                    resultType: 'json',
                    basDt: basDt,
                    isinCd:'KR7003230000'			
                }
            });

            console.log(`🔍 API 원본 응답 데이터:`);
            console.log(JSON.stringify(response.data, null, 2)); // 응답 데이터 전체 출력

            const data = response.data;

            if (data?.response?.body?.items?.item?.length > 0) {
                const stockInfo = data.response.body.items.item[0];

                console.log(`\n✅ 삼양식품 (${stockInfo.itmsNm}) 주가 정보 (${stockInfo.basDt})`);
                console.log(`📌 종가: ${stockInfo.clpr}원`);
                console.log(`📌 시가: ${stockInfo.mkp}원`);
                console.log(`📌 고가: ${stockInfo.hipr}원`);
                console.log(`📌 저가: ${stockInfo.lopr}원`);
                console.log(`📌 거래량: ${stockInfo.trqu}주`);
                console.log(`📌 전일 대비: ${stockInfo.vs}원`);
                console.log(`📌 등락률: ${stockInfo.fltRt}%`);
                console.log('=================================');
                return;
            } else {
                console.log(`🚫 ${basDt} 날짜에 주가 정보가 없습니다. 다음 날짜를 시도합니다.`);
            }

        } catch (error) {
            console.error(`❌ API 요청 오류 (${basDt}):`, error.message);
        }
    }

    console.log('\n🔎 최근 7일간 삼양식품의 주가 정보를 찾을 수 없습니다. 다시 시도해 주세요.');
}

getStockPrice();
