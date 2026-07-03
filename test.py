import sys
import io
import asyncio
from playwright.async_api import async_playwright

try:
    from voice_assistant import get_booking_data
except ImportError:
    get_booking_data = None

def clean_county_for_tra(county_str):
    """
    強效清洗：確保語音辨識不論抓到「苗栗」、「苗栗縣市」還是「台中市」，
    都能精準轉換成台鐵網頁按鈕上的官方名稱。
    """
    if not county_str:
        return ""
    
    # 修正語音常出現的混淆字
    if "苗栗" in county_str: return "苗栗縣"
    if "台中" in county_str or "臺中" in county_str: return "臺中市"
    if "台北" in county_str or "臺北" in county_str: return "臺北市"
    if "新北" in county_str: return "新北市"
    if "新竹" in county_str: return "新竹市" if "市" in county_str else "新竹縣"
    
    base = county_str.replace("縣市", "")
    if not (base.endswith("縣") or base.endswith("市")):
        if base in ["彰化", "南投", "雲林", "嘉義", "屏東", "臺東", "花蓮", "宜蘭"]:
            base += "縣"
        else:
            base += "市"
    return base

async def select_station_flow(page, data_type, county, station):
    """
    精準站點選取：只尋找當前畫面上『看得見』的按鈕，避開台鐵雙彈窗的重複 ID 衝突。
    """
    # 點開文字查詢視窗
    await page.click(f"button[title='文字站點查詢'][data-type='{data_type}']")
    await page.wait_for_timeout(400) # 給予足夠的 Bootstrap 動態展開時間
    county_fixed = county.replace("台", "臺")
    # 點擊縣市
    county_btn = page.locator(f"button.tipCity:has-text('{county_fixed}'):visible")
    await county_btn.wait_for(state="visible", timeout=5000)
    await county_btn.click()
    await page.wait_for_timeout(400) # 等待右側車站面板刷新
    
    # 精準比對結尾站名（例：-竹南，避開 臺中港 衝突）
    station_locator = page.locator(f"button.tipStation[title$='-{station}']:visible")
    await station_locator.wait_for(state="visible", timeout=5000)
    await station_locator.click()

async def fetch_train_data(booking_data):
    """
    爬蟲核心：負責把資料查出來，並將按鈕與文字打包成 List 回傳給 UI
    """
    start_county = booking_data.get("start_county")
    start_station = booking_data.get("start_station")
    end_county = booking_data.get("end_county")
    end_station = booking_data.get("end_station")
    ride_date = booking_data.get("ride_date")
    
    print(f"\n [Browser] 核心開始自動填入：{ride_date} | {start_county}({start_station}) -> {end_county}({end_station})", flush=True)

    # 為了防禦意外崩潰，建立預設的回傳變數
    p = None
    browser = None
    page = None
    express_list = []
    local_list = []

    try:
        from playwright.async_api import async_playwright
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        page = await browser.new_page()
        
        print("Step 1: 連線至台鐵官網...")
        await page.goto("https://www.railway.gov.tw/tra-tip-web/tip")
        await page.wait_for_selector("#startStation")
        
        # 1. 填入出發站
        target_start_county = clean_county_for_tra(start_county)
        print(f"Step 2: 選取出發站 -> {target_start_county} 的 {start_station}")
        await select_station_flow(page, "startStation", target_start_county, start_station)
        
        # 2. 填入目的地
        target_end_county = clean_county_for_tra(end_county)
        print(f"Step 3: 選取目的地 -> {target_end_county} 的 {end_station}")
        await select_station_flow(page, "endStation", target_end_county, end_station)
        
        # --- 3. 動態填入乘車日期 ---
        print(f"Step 4: Filling Ride Date ({ride_date})...")
        date_input = page.locator("input#rideDate[type='text']:visible")
        
        await date_input.evaluate("el => el.removeAttribute('readonly')")
        await date_input.focus()
        await date_input.evaluate(f"el => {{ el.value = '{ride_date}'; el.dispatchEvent(new Event('change', {{ bubbles: true }})); el.dispatchEvent(new Event('blur', {{ bubbles: true }})); }}")
        await page.wait_for_timeout(300)
        
        # 4. 送出查詢
        print("Step 5: 送出查詢表單...")
        await page.click("#queryForm input[type='submit']")
 # 5. 撈取車次資料
        print("Step 6: 開始解析時刻表...")
        await page.wait_for_selector("tr.trip-column", timeout=15000)
        await page.wait_for_timeout(1000) 
        
        #  既然台鐵全部都用 tr.trip-column，我們就精準抓這個，速度最快最乾淨
        rows = await page.query_selector_all("tr.trip-column")
        print(f" [解析成功] 網頁上一共抓到 {len(rows)} 個車次 <tr> 標籤！")
        
        for idx, row in enumerate(rows):
            text = await row.inner_text()
            if not text or not text.strip():
                continue
                
            # 清理換行符號，轉成單行便於判斷
            clean_text = " | ".join([item.strip() for item in text.split("\n") if item.strip()])
            
            # 防禦表頭
            if "出發時間" in clean_text or "抵達時間" in clean_text:
                continue
            
            train_info = {
                "text": clean_text
            }
            
            #  依據車種關鍵字進行精準分流 (修正"區間車"為"區間")
            if any(x in clean_text for x in ["自強", "普悠瑪", "太魯閣", "3000", "EMU3000", "莒光"]):
                if train_info not in express_list:
                    express_list.append(train_info)
            elif any(x in clean_text for x in ["區間", "快車", "復興", "本地"]):
                if train_info not in local_list:
                    local_list.append(train_info)
            else:
                # 備用保險分流
                if train_info not in local_list and train_info not in express_list:
                    local_list.append(train_info)
                    
        print(f" 分流完成 -> 自強號系列: {len(express_list)} 班 | 區間車系列: {len(local_list)} 班")

    except Exception as e:
        #  完美的防禦機制，捕捉這段內部的任何錯誤
        print(f" 撈取資料時發生錯誤: {str(e)}")

    #  終極修正關鍵：不論 try 裡面成不成功，都精確回傳 4 個物件給 UI 拆解 (與函數最外層對齊)
    train_data = {
        "express": express_list,
        "local": local_list
    }
    return train_data, page, browser, p