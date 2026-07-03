import sys
import io
#import os
from datetime import datetime
import json

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import speech_recognition as sr
from pydantic import BaseModel
from google import genai
from google.genai import types

# =====================================================================
# 納入縣市名稱，方便 Playwright 先點擊縣市
# =====================================================================
class BookingInfo(BaseModel):
    start_county: str   # 出發站所屬縣市 (例如: 臺北市, 苗栗縣市, 新竹縣市)
    start_station: str  # 出發站名稱 (例如: 臺北, 竹南, 苗栗)
    end_county: str     # 目的地所屬縣市
    end_station: str    # 目的地站名稱
    ride_date: str      # 乘車日期，格式 YYYY/MM/DD
    raw_time_desc: str  # 時間描述

def listen_to_speech():
    """透過麥克風錄音並轉換為繁體中文字串"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[語音] 正在調節環境噪音，請稍候...", flush=True)
        r.adjust_for_ambient_noise(source, duration=1)
        print("[語音] 請開始說話（例如：『幫我訂明天早上八點從竹南到台北的火車』）...", flush=True)
        
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=15)
            print("[語音] 錄音結束，正在識別中...", flush=True)
            
            text = r.recognize_google(audio, language="zh-TW")
            print(f"[語音結果]：\"{text}\"", flush=True)
            return text
        except sr.WaitTimeoutError:
            print("[語音錯誤] 偵測超時，您好像沒有說話。", flush=True)
            return None
        except sr.UnknownValueError:
            print("[語音錯誤] 抱歉，我聽不懂您說的話，請再試一次。", flush=True)
            return None
        except Exception as e:
            print(f"[語音錯誤] 發生其他錯誤: {e}", flush=True)
            return None

def analyze_intent_with_gemini(user_prompt):
    """呼叫 Gemini API 將語意分析為結構化的訂票 JSON"""
    client = genai.Client(api_key="輸入使用者gemini api")
    current_date = datetime.now().strftime("%Y/%m/%d")
    current_weekday = datetime.now().strftime("%A")

    # =====================================================================
    #在系統指令中，嚴格規範台鐵官方的縣市分類名稱
    # =====================================================================
    sys_instruction = f"""
    你是一個台鐵訂票語意分析助手。
    今天日期是 {current_date} ({current_weekday})。
    請分析使用者的口語化訂票需求，並嚴格轉換為指定的 JSON 格式。
    
    時間轉換規則範例（以今天為基準）：
    - 如果說「明天」，日期請帶入明天的日期。
    
    台鐵車站與縣市分類對照規則（必須嚴格遵守）：
    1. 站名請統一轉換為台鐵官方標準名稱（如「台北」轉成「臺北」、「新竹」就是「新竹」）。
    2. 如果使用者沒提到出發站，請預設 start_county 為「臺北市」，start_station 為「臺北」。
    3. 必須準確判斷車站屬於哪一個台鐵官方網頁分類縣市（填入 county 欄位）：
       - 臺北、萬華、松山、南港 -> 臺北市
       - 板橋、樹林、汐止、鶯歌 -> 新北市
       - 基隆、七堵、八堵 -> 基隆市
       - 桃園、中壢、內壢 -> 桃園市
       - 新竹、竹北、竹東 -> 新竹縣市
       - 竹南、苗栗、豐富、造橋、後龍 -> 苗栗縣市
       - 台中、新烏日、豐原 -> 臺中市
       - 彰化、員林 -> 彰化縣
       - 嘉義、民雄 -> 嘉義縣市
       - 台南、新營 -> 臺南市
       - 高雄、新左營、鳳山 -> 高雄市
       - 花蓮、玉里 -> 花蓮縣
       - 台東、知本 -> 臺東縣
       - 宜蘭、羅東、礁溪 -> 宜蘭縣
    """

    print("[Gemini] 正在進行語意分析與時間換算...", flush=True)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                response_mime_type="application/json",
                response_schema=BookingInfo,
                temperature=0.1
            ),
        )
        return response.text
    except Exception as e:
        print(f"[Gemini 錯誤] 呼叫 API 失敗: {e}", flush=True)
        return None

def get_booking_data():
    """供外部腳本 import 呼叫的主函數"""
    voice_text = listen_to_speech()
    if not voice_text:
        return None
        
    json_str = analyze_intent_with_gemini(voice_text)
    
    if json_str:
        # 將 JSON 字串轉成 Python 字典回傳
        return json.loads(json_str)
    return None

# 檔案單獨單獨執行測試
if __name__ == "__main__":
    data = get_booking_data()
    print("測試輸出：", data)