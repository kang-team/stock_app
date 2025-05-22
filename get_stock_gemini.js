// 필요한 모듈을 가져옵니다. 'axios'는 HTTP 요청을 쉽게 보낼 수 있게 해주는 라이브러리입니다.
// 프로젝트 폴더에서 'npm install axios' 명령어를 실행하여 설치해야 합니다.
const axios = require('axios');

// 제공받은 API 키 (Decoding된 키를 사용합니다)
const SERVICE_KEY = 'mxw0YlGZCzHXFx6TOizB9tpLSv0fqSIyrVDCfmkBXktLR4oyuBfsNb1PdSUIMJUkVXlQ1HfFTxeTQ5qqLaeTIA==';
// 삼양식품의 종목코드 (한국거래소 기준)
const SAMYANG_FOODS_STOCK_CODE = '003230';

/**
 * 특정 날짜를 'YYYYMMDD' 형식의 문자열로 반환하는 함수
 * API 요청 시 '기준일자(basDt)' 파라미터에 사용됩니다.
 * @param {Date} date - 변환할 Date 객체
 * @returns {string} 'YYYYMMDD' 형식의 날짜 문자열
 */
function formatDateToYYYYMMDD(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}

/**
 * 금융위원회 API를 통해 삼양식품의 주가 정보를 가져오는 비동기 함수
 * 현재 날짜부터 시작하여 최대 7일 전까지 데이터를 시도합니다.
 */
async function getSamyangFoodsStockPrice() {
    // API 엔드포인트 URL
    const apiUrl = 'http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo';

    // 최대 7일 전까지 데이터를 시도합니다. (주말 및 공휴일 고려)
    const MAX_DAYS_TO_CHECK = 7;

    for (let i = 0; i < MAX_DAYS_TO_CHECK; i++) {
        const targetDate = new Date();
        targetDate.setDate(targetDate.getDate() - i); // 오늘부터 i일 전 날짜 설정
        const basDt = formatDateToYYYYMMDD(targetDate);

        console.log(`\n${basDt} 날짜의 주가 정보를 시도합니다...`);

        try {
            // axios를 사용하여 GET 요청을 보냅니다.
            // params 객체에 API에 필요한 쿼리 파라미터들을 정의합니다.
            const response = await axios.get(apiUrl, {
                params: {
                    serviceKey: SERVICE_KEY,     // API 서비스 키
                    numOfRows: 1,                // 가져올 데이터의 개수 (최신 1개만 필요)
                    pageNo: 1,                   // 페이지 번호
                    resultType: 'json',          // 응답 데이터 형식 (JSON으로 요청)
                    basDt: basDt,                // 기준일자 (현재 시도하는 날짜)
                    srtnCd: SAMYANG_FOODS_STOCK_CODE // 단축코드 (종목코드)
                }
            });

            const data = response.data; // API 응답 데이터

            // 응답 데이터 구조를 확인하고 주가 정보를 파싱합니다.
            // data.response.body.items.item 경로에 실제 데이터가 있습니다.
            if (data && data.response && data.response.body && data.response.body.items && data.response.body.items.item && data.response.body.items.item.length > 0) {
                const stockInfo = data.response.body.items.item[0]; // 첫 번째 항목 (가장 최신 데이터)

                console.log(`\n=== 삼양식품 (${stockInfo.itmsNm}) 주가 정보 (${stockInfo.basDt}) ===`);
                console.log(`종가: ${stockInfo.clpr}원`);     // 종가 (Closing Price)
                console.log(`시가: ${stockInfo.mkp}원`);     // 시가 (Opening Price)
                console.log(`고가: ${stockInfo.hipr}원`);     // 고가 (High Price)
                console.log(`저가: ${stockInfo.lopr}원`);     // 저가 (Low Price)
                console.log(`거래량: ${stockInfo.trqu}주`);   // 거래량 (Trading Volume)
                console.log(`전일 대비: ${stockInfo.vs}원`); // 전일 대비 등락액
                console.log(`등락률: ${stockInfo.fltRt}%`);  // 등락률
                console.log('=================================');
                return; // 데이터를 찾았으므로 함수 종료
            } else {
                console.log(`${basDt} 날짜에는 주가 정보가 없습니다. 다음 날짜를 시도합니다.`);
                // 데이터가 없으면 다음 날짜를 시도하기 위해 루프 계속
            }

        } catch (error) {
            // API 요청 중 오류가 발생했을 때 처리합니다.
            console.error(`API 요청 중 오류 발생 (${basDt}):`, error.message);
            if (error.response) {
                console.error('API 응답 오류 상태:', error.response.status);
                console.error('API 응답 데이터:', error.response.data);
            } else if (error.request) {
                console.error('API 응답 없음:', error.request);
            } else {
                console.error('오류 발생:', error.message);
            }
            // 오류가 발생해도 다음 날짜를 시도하기 위해 루프 계속
        }
    }
    console.log('\n최근 7일간 삼양식품의 주가 정보를 찾을 수 없습니다. 나중에 다시 시도해주세요.');
}

// 함수를 호출하여 주가 정보를 가져옵니다.
getSamyangFoodsStockPrice();
