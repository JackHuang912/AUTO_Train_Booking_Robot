# -
本專案透過語音識別自動進行台鐵訂票功能

# 🎙️ 台鐵語音智慧查票與自動化訂票助手 (Train Booking Assistant)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Async-green.svg)
![Gemini](https://img.shields.io/badge/Gemini_API-Multimodal-orange.svg)
![Tkinter](https://img.shields.io/badge/UI-Tkinter_Ttk-lightgrey.svg)

## 簡介 (Overview)

傳統的台鐵訂票流程繁瑣，且在尖峰時段常常因為圖形驗證碼或 Google reCAPTCHA v3 驗證延遲而延誤。
本工具實現了直接透過語音輸入查票並自動從瀏覽器填入對應乘車資訊，並撈取合適的班次進行訂購**」。

## Demo
step1 於 TERMINAL 執行python ui.py 系統便自動跳出操作介面，按下啟動查票，隨後利用語音方式輸入訂票資訊。(ex:幫我訂明天早上8點苗栗竹南到台中市台中站的車票)

<img width="399" height="319" alt="image" src="https://github.com/user-attachments/assets/cbf09447-988e-4b74-aa25-6cf777f617fe" />

---
step2 程式自動分析輸入的資訊並於背景開啟台鐵網站自動填入資訊，並將合適的車班資訊回傳，此時使用者能夠按下想搭乘的自強車班按鈕程式會跳出輸入身分證號的介面，輸入後自動進行票卷的訂購。

<img width="˙300" height="311" alt="image" src="https://github.com/user-attachments/assets/09aeb949-edc6-4f7d-b5f0-306cfd073d22" />


---
在背景運作的程式結合圖像識別功能透過CNN進行識別碼的圖像辨識。
<img width="886" height="310" alt="image" src="https://github.com/user-attachments/assets/1e31f64c-252e-40e4-b048-1256a418b9dc" />


採用資料集source:https://github.com/linsamtw/TaiwanTrainVerificationCode2text 

---
⚠️ 免責聲明
本專案僅供學術研究、技術交流與個人自動化專案開發參考。請勿用於任何惡意搶票、商業牟利或破壞台鐵訂票系統公平性之行為。因使用本程式所造成之任何法律問題或訂票糾紛，本作者概不負責。
