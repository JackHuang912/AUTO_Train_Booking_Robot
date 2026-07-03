# import tkinter as tk
# from tkinter import messagebox, ttk
# import asyncio
# import threading
# from test import fetch_train_data, get_booking_data
# from predict_vcode import get_captcha_text
# class TrainApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("台鐵語音智慧查票助手")
#         self.root.geometry("750x650")
        
#         # 儲存 Playwright 相關物件，避免被垃圾回收
#         self.page = None
#         self.browser = None
#         self.playwright_instance = None
        
#         # 全局事件循環，專門在背景線程處理 Playwright
#         self.bg_loop = None
#         self.bg_thread = None
        
#         self.create_widgets()
#         self.start_background_loop()

#     def start_background_loop(self):
#         """在程式啟動時，就在背景準備好一個乾淨且持續運作的 asyncio 事件循環"""
#         def _run_loop():
#             self.bg_loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(self.bg_loop)
#             self.bg_loop.run_forever()
            
#         self.bg_thread = threading.Thread(target=_run_loop, daemon=True)
#         self.bg_thread.start()

#     def create_widgets(self):
#         # 頂部狀態列與啟動按鈕
#         top_frame = tk.Frame(self.root, pady=10)
#         top_frame.pack(fill="x")
        
#         self.start_btn = tk.Button(top_frame, text="🎙️ 啟動查票 (導入語音資料)", font=("Microsoft JhengHei", 12, "bold"), bg="#4CAF50", fg="white", command=self.start_fetching_thread)
#         self.start_btn.pack(pady=5)
        
#         self.status_label = tk.Label(top_frame, text="狀態: 等待啟動...", font=("Microsoft JhengHei", 10))
#         self.status_label.pack()

#         # 下方大容器（用來放自強和區間）
#         main_frame = tk.Frame(self.root, padx=10, pady=10)
#         main_frame.pack(fill="both", expand=True)

#         # 1. 自強號家族區塊
#         self.express_lf = tk.LabelFrame(main_frame, text=" 自強號 (可點選訂票) ", font=("Microsoft JhengHei", 11, "bold"), fg="#D32F2F")
#         self.express_lf.pack(fill="both", expand=True, pady=5)
        
#         self.express_canvas = tk.Canvas(self.express_lf)
#         self.express_frame = tk.Frame(self.express_canvas)
#         self.express_scroll = tk.Scrollbar(self.express_lf, orient="vertical", command=self.express_canvas.yview)
#         self.express_canvas.configure(yscrollcommand=self.express_scroll.set)
        
#         self.express_scroll.pack(side="right", fill="y")
#         self.express_canvas.pack(side="left", fill="both", expand=True)
#         self.express_canvas.create_window((0,0), window=self.express_frame, anchor="nw")
#         self.express_frame.bind("<Configure>", lambda e: self.express_canvas.configure(scrollregion=self.express_canvas.bbox("all")))

#         # 2. 區間車家族區塊
#         self.local_lf = tk.LabelFrame(main_frame, text="  區間車 (現場購票) ", font=("Microsoft JhengHei", 11, "bold"), fg="#1976D2")
#         self.local_lf.pack(fill="both", expand=True, pady=5)
        
#         self.local_canvas = tk.Canvas(self.local_lf)
#         self.local_frame = tk.Frame(self.local_canvas)
#         self.local_scroll = tk.Scrollbar(self.local_lf, orient="vertical", command=self.local_canvas.yview)
#         self.local_canvas.configure(yscrollcommand=self.local_scroll.set)
        
#         self.local_scroll.pack(side="right", fill="y")
#         self.local_canvas.pack(side="left", fill="both", expand=True)
#         self.local_canvas.create_window((0,0), window=self.local_frame, anchor="nw")
#         self.local_frame.bind("<Configure>", lambda e: self.local_canvas.configure(scrollregion=self.local_canvas.bbox("all")))

#     def start_fetching_thread(self):
#         """觸發查票：安全的將 async 工作指派給背景的事件循環執行"""
#         self.start_btn.config(state="disabled")
#         self.status_label.config(text="狀態: 正在執行語音辨識與瀏覽器自動化撈取中...")
        
#         # 清空舊資料畫面
#         for widget in self.express_frame.winfo_children(): widget.destroy()
#         for widget in self.local_frame.winfo_children(): widget.destroy()
        
#         # 將協程任務安全的拋給背景循環
#         asyncio.run_coroutine_threadsafe(self.run_async_fetch_coro(), self.bg_loop)

#     async def run_async_fetch_coro(self):
#         """完全運作在背景循環中的協程，不干涉或阻塞主執行緒"""
#         booking_info = None
#         if get_booking_data:
#             try: 
#                 booking_info = get_booking_data()
#             except Exception: 
#                 pass
            
#         if not booking_info:
#             booking_info = {
#                 "start_county": "苗栗縣", "start_station": "竹南",
#                 "end_county": "臺中市", "end_station": "臺中",
#                 "ride_date": "2026/07/04"
#             }

#         try:
#             # 此處的 await 能在獨立循環中被釋放與排程
#             train_data, page, browser, p = await fetch_train_data(booking_info)
#             self.page = page
#             self.browser = browser
#             self.playwright_instance = p
            
#             # 任務完成，回到主執行緒渲染 UI
#             self.root.after(0, self.update_ui_with_data, train_data)
#         except Exception as e:
#             self.root.after(0, self.show_error, str(e))

#     def update_ui_with_data(self, train_data):
#             self.start_btn.config(state="normal")
#             self.status_label.config(text="狀態: 資料撈取完成！")

        
#             print(f"🖥️ [UI 渲染檢查] UI 收到自強號: {len(train_data['express'])} 筆 | 區間車: {len(train_data['local'])} 筆")

#             # --- 1. 渲染自強號 ---
#             # 先清空舊元件
#             for widget in self.express_frame.winfo_children():
#                 widget.destroy()

#             if not train_data["express"]:
#                 tk.Label(self.express_frame, text="此時段無自強號車次或未解析成功", font=("Microsoft JhengHei", 10)).pack(pady=5)
#             else:
#                 for idx, train in enumerate(train_data["express"]):
#                     row_frame = tk.Frame(self.express_frame, pady=4)
#                     row_frame.pack(fill="x", anchor="w")
                    
#                     display_text = f"列車 {idx+1}: {train['text'][:65]}..." if len(train['text']) > 65 else f"列車 {idx+1}: {train['text']}"
#                     lbl = tk.Label(row_frame, text=display_text, font=("Consolas", 10), anchor="w")
#                     lbl.pack(side="left", padx=5)
                    
#                     btn = tk.Button(row_frame, text="點我訂票", bg="#FF5722", fg="white", font=("Microsoft JhengHei", 9, "bold"),
#                                     command=lambda current_idx=idx: self.click_booking_button(current_idx))
#                     btn.pack(side="right", padx=10)

#             # --- 2. 渲染區間車 ---
#             # 先清空舊元件
#             for widget in self.local_frame.winfo_children():
#                 widget.destroy()

#             if not train_data["local"]:
#                 tk.Label(self.local_frame, text="此時段無區間車車次或未解析成功", font=("Microsoft JhengHei", 10)).pack(pady=5)
#             else:
#                 for idx, train in enumerate(train_data["local"]):
#                     row_frame = tk.Frame(self.local_frame, pady=4)
#                     row_frame.pack(fill="x", anchor="w")
                    
#                     #  確保顯示不會因文字太長卡死
#                     display_text = f"車次 {idx+1}: {train['text'][:70]}..." if len(train['text']) > 70 else f"車次 {idx+1}: {train['text']}"
                    
#                     lbl = tk.Label(row_frame, text=display_text, font=("Consolas", 10), anchor="w", justify="left")
#                     lbl.pack(side="left", padx=5)

#             # 強制刷新：通知 Tkinter 的 Canvas 重新計算滾動區域（Scrollregion）
#             # 因為滾動條沒有刷新，導致元件其實有長出來，但被埋在下方看不見！
#             try:
#                 self.express_canvas.configure(scrollregion=self.express_canvas.bbox("all"))
#                 self.local_canvas.configure(scrollregion=self.local_canvas.bbox("all"))
#             except AttributeError:
#                 pass

#     def click_booking_button(self, express_index):
#         """點擊訂票：利用索引值去網頁找出對應車次，點擊進入新分頁後自動填入身分證字號與驗證碼並送出"""
#         from tkinter import simpledialog, messagebox
        
#         # 1. 彈出對話框讓使用者輸入身分證字號
#         user_id = simpledialog.askstring("身分證驗證", "請輸入訂票身分證字號:", parent=self.root)
#         if not user_id:
#             print("使用者取消輸入或未填寫身分證")
#             return
#         user_id = user_id.strip()

#         self.status_label.config(text="狀態: 正在點擊車次訂票按鈕...")
#         print(f"\n💡 [階段一] 準備點擊查詢結果中的第 {express_index + 1} 個自強號...")
        
#         async def do_click():
#             try:
#                 # ====== 階段一：在車次列表頁面，找到對應的車次並點擊 ======
#                 rows = await self.page.query_selector_all("tr.trip-column")
#                 express_rows = []
#                 for row in rows:
#                     text = await row.inner_text()
#                     if any(x in text for x in ["自強", "普悠瑪", "太魯閣", "3000", "EMU3000"]):
#                         express_rows.append(row)
                
#                 if express_index >= len(express_rows):
#                     print(f" 索引值 {express_index} 超出目前的自強號總數")
#                     return

#                 target_row = express_rows[express_index]
#                 list_btn = await target_row.query_selector("button:has-text('訂票'), a:has-text('訂票'), :text('訂票')")
                
#                 if not list_btn:
#                     print(" 找不到列表中的車次訂票按鈕，嘗試點擊該列最後一個按鈕")
#                     list_btn = await target_row.query_selector("button, a")

#                 if not list_btn:
#                     self.root.after(0, lambda: self.status_label.config(text="狀態: 找不到列表訂票按鈕"))
#                     return

#                 print("👉 已點擊車次，等待新訂票頁面載入...")
#                 async with self.page.expect_popup() as popup_info:
#                     await list_btn.click()
                
#                 popup_page = await popup_info.value
                
#                 # 🌟【防禦修改 1】：強迫 Playwright 等到網路請求完全靜止（確保驗證碼圖片下載完成）
#                 await popup_page.wait_for_load_state("networkidle")
#                 print(f"🎉 成功進入資料填寫頁面: {popup_page.url}")
#                 self.root.after(0, lambda: self.status_label.config(text="狀態: 進入填寫頁面，開始自動化..."))
                
#                 # ====== 階段二：在資料填寫頁面，自動化填寫（身分證 + 等待 v3 失敗後的 AI 驗證碼） ======
#                 try:
#                     # 🎯 1. 填入身分證字號
#                     id_selector = "input#pid, input[name='pid'], input[placeholder*='身分證']"
#                     await popup_page.wait_for_selector(id_selector, timeout=5000)
#                     await popup_page.fill(id_selector, user_id)
#                     print(f"🚀 [成功] 已自動填入身分證字號")
                    
#                     # 🎯 2. 處理台鐵動態驗證碼 (針對 Google v3 攔截做防禦)
#                     self.root.after(0, lambda: self.status_label.config(text="狀態: 等待 Google v3 驗證結果..."))
                    
#                     captcha_img_selector = "img#codeimg"
#                     input_captcha_selector = "input#verifyCode"
                    
#                     try:
#                         print("⏳ 正在監控網頁是否跳出『因 v3 驗證未通過』的二級圖形驗證碼...")
#                         # 確保圖片完全顯示出來 (visible)
#                         await popup_page.wait_for_selector(captcha_img_selector, state="visible", timeout=4000)
                        
#                         captcha_element = await popup_page.query_selector(captcha_img_selector)
#                         if captcha_element:
#                             self.root.after(0, lambda: self.status_label.config(text="狀態: 偵測到圖形驗證碼，AI 辨識中..."))
                            
#                             # 🌟【防禦修改 2】：直接對 DOM 元素進行畫面截圖剪貼！
#                             img_bytes = await captcha_element.screenshot()
                            
#                             # 呼叫 AI 模型預測 
#                             print(" 正在透過非同步執行緒呼叫 Gemini API 辨識中...")
#                             ai_predicted_code = await asyncio.to_thread(get_captcha_text, img_bytes)
#                             print(f"  [辨識成功] 預測驗證碼結果為: {ai_predicted_code}")

#                             # 自動輸入到 #verifyCode
#                             await popup_page.fill(input_captcha_selector, ai_predicted_code)
#                             # 暫停 2 秒鐘供肉眼比對驗證碼
#                             print(" 暫停 2 秒鐘供肉眼比對驗證碼...")
#                             await popup_page.wait_for_timeout(5000) 
                            
#                     except Exception as captcha_timeout_err:
#                         print(" 提示：未偵測到二級圖形驗證碼（可能 v3 驗證直接通過或不需驗證碼），準備直接送出表單。")
                    
#                     # 🎯 3. 精準鎖定最終的「訂票Submit按鈕」並送出
#                     final_submit_selector = "input[type='submit'], button[type='submit'], .btn-3d"
#                     final_submit_btn = await popup_page.query_selector(final_submit_selector)
                    
#                     if final_submit_btn:
#                         await final_submit_btn.click()
#                         print(" [成功] 已自動按下最終送出/訂票按鈕！")
#                         self.root.after(0, lambda: self.status_label.config(text="狀態: 已自動送出！正在等待明細頁面..."))
                        
#                         # =================================================================
#                         #等待並處理訂票成功的確認明細頁面
#                         # =================================================================
#                         try:
#                             # 1. 確保網頁完成跳轉，且新頁面的「下一步」按鈕已經跑出來
#                             next_step_selector = "button.btn-nextStep, :text('下一步')"
#                             print("⏳ 正在等待訂票成功確認頁面載入...")
#                             await popup_page.wait_for_selector(next_step_selector, timeout=7000)
#                             print("\n🎉 [階段三] 成功進入訂票成功確認頁面！")
                            
#                             # 2. 擷取訂票代碼 (從 class="font18" 提取)
#                             booking_code_el = await popup_page.query_selector(".cartlist-id span.font18")
#                             booking_code = await booking_code_el.inner_text() if booking_code_el else "未知"
                            
#                             # 3. 擷取分配到的座位 (從 class="seat" 提取)
#                             seat_info_el = await popup_page.query_selector("span.seat")
#                             seat_info = await seat_info_el.inner_text() if seat_info_el else "未知"
                            
#                             print("-" * 50)
#                             print(f"🎫 【台鐵訂票成功明細】")
#                             print(f"🔹 訂票代碼：{booking_code.strip()}")
#                             print(f"🔹 分配座位：{seat_info.strip()}")
#                             print("-" * 50)
                            
#                             # 同步更新你的 GUI 介面狀態
#                             self.root.after(0, lambda: self.status_label.config(
#                                 text=f"狀態: 訂票成功！代碼: {booking_code.strip()} | 座位: {seat_info.strip()}，準備進入下一步..."
#                             ))
                            
#                             # 4. 點擊「下一步」按鈕
#                             final_next_btn = await popup_page.query_selector(next_step_selector)
#                             if final_next_btn:
#                                 await popup_page.wait_for_timeout(500) # 稍微緩衝 0.5 秒看起來更像真人
#                                 await final_next_btn.click()
#                                 print(" [成功] 已自動點擊『下一步』按鈕！")
#                                 self.root.after(0, lambda: self.status_label.config(text="狀態: 已點擊下一步，請至網頁完成付款程序。"))
                            
#                         except Exception as page_three_err:
#                             print(f" 擷取明細或點擊下一步時失敗 (可能手動點走了): {page_three_err}")
#                         # =================================================================
                        
#                     else:
#                         print(" 找不到最終送出按鈕，請手動點擊網頁上的按鈕")
#                         self.root.after(0, lambda: self.status_label.config(text="狀態: 欄位已自動填妥，請手動點擊送出。"))
                        
#                 except Exception as inner_e:
#                     print(f" 自動化填寫流程發生錯誤: {inner_e}")
#                     self.root.after(0, lambda: self.status_label.config(text="狀態: 自動化填寫失敗。"))

#             except Exception as e:
#                 print(f" 核心流程失敗: {e}")
#                 self.root.after(0, lambda: self.status_label.config(text="狀態: 流程失敗，請查看終端機 Log"))
                
#         asyncio.run_coroutine_threadsafe(do_click(), self.bg_loop)
#     def show_error(self, err_msg):
#         self.start_btn.config(state="normal")
#         self.status_label.config(text="狀態: 執行發生錯誤。")
#         messagebox.showerror("錯誤", f"自動化過程中發生錯誤:\n{err_msg}")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TrainApp(
#         root)
#     root.mainloop()
import tkinter as tk
from tkinter import messagebox, ttk
import asyncio
import threading
from test import fetch_train_data, get_booking_data
from predict_vcode import get_captcha_text

class TrainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("台鐵語音智慧查票助手")
        self.root.geometry("800x700")
        
        # 設定全域現代風格樣式 (ttk Theme)
        self.style = ttk.Style()
        self.style.theme_use("clam")  # 使用 clam 基礎，外觀較為平整現代
        self.configure_styles()

        # 儲存 Playwright 相關物件，避免被垃圾回收
        self.page = None
        self.browser = None
        self.playwright_instance = None
        
        # 全局事件循環，專門在背景線程處理 Playwright
        self.bg_loop = None
        self.bg_thread = None
        
        self.create_widgets()
        self.start_background_loop()

    def configure_styles(self):
        """配置現代扁平化 UI 的顏色與字型樣式"""
        # 顏色定義
        self.c_primary = "#1E88E5"     # 科技藍
        self.c_success = "#4CAF50"     # 翡翠綠
        self.c_accent = "#FF5722"      # 活力橘
        self.c_bg = "#F5F7FA"          # 輕盈灰背景
        self.c_dark = "#2C3E50"        # 深藍灰文字
        
        self.root.configure(bg=self.c_bg)
        
        # 配置 Ttk 控制項樣式
        self.style.configure(".", background=self.c_bg, foreground=self.c_dark, font=("Microsoft JhengHei", 10))
        self.style.configure("TLabelframe", background=self.c_bg, bordercolor="#E0E0E0", borderwidth=1)
        self.style.configure("TLabelframe.Label", font=("Microsoft JhengHei", 11, "bold"), foreground=self.c_dark, background=self.c_bg)
        
        # 滾動條樣式扁平化
        self.style.configure("Vertical.TScrollbar", gripcount=0, background="#E0E0E0", troughcolor=self.c_bg, borderwidth=0, arrowsize=12)

    def start_background_loop(self):
        """在程式啟動時，就在背景準備好一個乾淨且持續運作的 asyncio 事件循環"""
        def _run_loop():
            self.bg_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.bg_loop)
            self.bg_loop.run_forever()
            
        self.bg_thread = threading.Thread(target=_run_loop, daemon=True)
        self.bg_thread.start()

    def create_widgets(self):
        # 頂部控制面板 (Top Action Card)
        top_card = tk.Frame(self.root, bg="white", highlightbackground="#E0E0E0", highlightthickness=1, bd=0)
        top_card.pack(fill="x", padx=15, pady=15)
        
        # 啟動按鈕現代化 (改用扁平化無邊框設計)
        self.start_btn = tk.Button(
            top_card, 
            text="🎙️  啟動查票 (導入語音資料)", 
            font=("Microsoft JhengHei", 12, "bold"), 
            bg=self.c_success, 
            fg="white", 
            activebackground="#43A047",
            activeforeground="white",
            bd=0, 
            padx=20, 
            pady=10, 
            cursor="hand2",
            command=self.start_fetching_thread
        )
        self.start_btn.pack(pady=15)
        
        # 下方車次大容器
        main_frame = tk.Frame(self.root, bg=self.c_bg)
        main_frame.pack(fill="both", expand=True, padx=15, pady=0)

        # 1. 自強號家族區塊 (改用 ttk.LabelFrame)
        self.express_lf = ttk.LabelFrame(main_frame, text="  自強號車型 (可連動自動訂票)  ")
        self.express_lf.pack(fill="both", expand=True, pady=8)
        
        # Canvas 移除老舊邊框，換成現代背景色
        self.express_canvas = tk.Canvas(self.express_lf, bg="white", bd=0, highlightthickness=0)
        self.express_frame = tk.Frame(self.express_canvas, bg="white")
        self.express_scroll = ttk.Scrollbar(self.express_lf, orient="vertical", command=self.express_canvas.yview)
        self.express_canvas.configure(yscrollcommand=self.express_scroll.set)
        
        self.express_scroll.pack(side="right", fill="y")
        self.express_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.express_canvas_window = self.express_canvas.create_window((0,0), window=self.express_frame, anchor="nw")
        
        self.express_frame.bind("<Configure>", lambda e: self.express_canvas.configure(scrollregion=self.express_canvas.bbox("all")))
        self.express_canvas.bind('<Configure>', lambda e: self.express_canvas.itemconfig(self.express_canvas_window, width=e.width))

        # 2. 區間車區塊
        self.local_lf = ttk.LabelFrame(main_frame, text="  區間車型 (現場刷卡購票)  ")
        self.local_lf.pack(fill="both", expand=True, pady=8)
        
        self.local_canvas = tk.Canvas(self.local_lf, bg="white", bd=0, highlightthickness=0)
        self.local_frame = tk.Frame(self.local_canvas, bg="white")
        self.local_scroll = ttk.Scrollbar(self.local_lf, orient="vertical", command=self.local_canvas.yview)
        self.local_canvas.configure(yscrollcommand=self.local_scroll.set)
        
        self.local_scroll.pack(side="right", fill="y")
        self.local_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.local_canvas_window = self.local_canvas.create_window((0,0), window=self.local_frame, anchor="nw")
        
        self.local_frame.bind("<Configure>", lambda e: self.local_canvas.configure(scrollregion=self.local_canvas.bbox("all")))
        self.local_canvas.bind('<Configure>', lambda e: self.local_canvas.itemconfig(self.local_canvas_window, width=e.width))

        # 底部專業狀態列 (Status Bar)
        status_bar = tk.Frame(self.root, bg="#ECEFF1", bd=1, relief="solid")
        status_bar.pack(fill="x", side="bottom")
        self.status_label = tk.Label(status_bar, text=" 狀態: 系統就緒，等待使用者操作...", font=("Microsoft JhengHei", 10), bg="#ECEFF1", fg="#546E7A", anchor="w", padx=10, pady=5)
        self.status_label.pack(fill="x")

    def start_fetching_thread(self):
        """觸發查票：安全的將 async 工作指派給背景的事件循環執行"""
        self.start_btn.config(state="disabled", bg="#B0BEC5", text="⏳ 正在處理中...")
        self.status_label.config(text=" 狀態: 正在執行語音辨識與瀏覽器自動化撈取中...")
        
        # 清空舊資料畫面
        for widget in self.express_frame.winfo_children(): widget.destroy()
        for widget in self.local_frame.winfo_children(): widget.destroy()
        
        # 將協程任務安全的拋給背景循環
        asyncio.run_coroutine_threadsafe(self.run_async_fetch_coro(), self.bg_loop)

    async def run_async_fetch_coro(self):
        """完全運作在背景循環中的協程，不干涉或阻塞主執行緒"""
        booking_info = None
        if get_booking_data:
            try: 
                booking_info = get_booking_data()
            except Exception: 
                pass
            
        if not booking_info:
            booking_info = {
                "start_county": "苗栗縣", "start_station": "竹南",
                "end_county": "臺中市", "end_station": "臺中",
                "ride_date": "2026/07/04"
            }

        try:
            train_data, page, browser, p = await fetch_train_data(booking_info)
            self.page = page
            self.browser = browser
            self.playwright_instance = p
            
            # 任務完成，回到主執行緒渲染 UI
            self.root.after(0, self.update_ui_with_data, train_data)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_ui_with_data(self, train_data):
        self.start_btn.config(state="normal", bg=self.c_success, text="🎙️  啟動查票 (導入語音資料)")
        self.status_label.config(text=" 狀態: 資料撈取完成！")

        print(f"🖥️ [UI 渲染檢查] UI 收到自強號: {len(train_data['express'])} 筆 | 區間車: {len(train_data['local'])} 筆")

        # --- 1. 渲染自強號 ---
        for widget in self.express_frame.winfo_children(): widget.destroy()

        if not train_data["express"]:
            tk.Label(self.express_frame, text="此時段無自強號車次或未解析成功", font=("Microsoft JhengHei", 10), bg="white", fg="#78909C").pack(pady=15)
        else:
            for idx, train in enumerate(train_data["express"]):
                # 卡片樣式行容器 (一條亮灰色底線做區隔)
                row_frame = tk.Frame(self.express_frame, bg="white", highlightbackground="#F0F0F0", highlightthickness=1, bd=0)
                row_frame.pack(fill="x", anchor="w", padx=8, pady=4)
                
                display_text = f"  列車 {idx+1}: {train['text']}"
                lbl = tk.Label(row_frame, text=display_text, font=("Consolas", 10), anchor="w", bg="white", fg=self.c_dark, pady=8)
                lbl.pack(side="left", fill="x", expand=True, padx=5)
                
                btn = tk.Button(
                    row_frame, 
                    text="點我訂票", 
                    bg=self.c_accent, 
                    fg="white", 
                    activebackground="#E64A19",
                    activeforeground="white",
                    font=("Microsoft JhengHei", 9, "bold"),
                    bd=0,
                    padx=12,
                    pady=4,
                    cursor="hand2",
                    command=lambda current_idx=idx: self.click_booking_button(current_idx)
                )
                btn.pack(side="right", padx=10, pady=6)

        # --- 2. 渲染區間車 ---
        for widget in self.local_frame.winfo_children(): widget.destroy()

        if not train_data["local"]:
            tk.Label(self.local_frame, text="此時段無區間車車次或未解析成功", font=("Microsoft JhengHei", 10), bg="white", fg="#78909C").pack(pady=15)
        else:
            for idx, train in enumerate(train_data["local"]):
                row_frame = tk.Frame(self.local_frame, bg="white", highlightbackground="#F0F0F0", highlightthickness=1, bd=0)
                row_frame.pack(fill="x", anchor="w", padx=8, pady=4)
                
                display_text = f"  車次 {idx+1}: {train['text']}"
                lbl = tk.Label(row_frame, text=display_text, font=("Consolas", 10), anchor="w", justify="left", bg="white", fg=self.c_dark, pady=8)
                lbl.pack(side="left", fill="x", expand=True, padx=5)

        # 強制刷新滾動區
        try:
            self.express_canvas.configure(scrollregion=self.express_canvas.bbox("all"))
            self.local_canvas.configure(scrollregion=self.local_canvas.bbox("all"))
        except AttributeError:
            pass

    def click_booking_button(self, express_index):
        """點擊訂票：利用索引值去網頁找出對應車次，點擊進入新分頁後自動填入身分證字號與驗證碼並送出"""
        from tkinter import simpledialog, messagebox
        
        user_id = simpledialog.askstring("身分證驗證", "請輸入訂票身分證字號:", parent=self.root)
        if not user_id:
            print("使用者取消輸入或未填寫身分證")
            return
        user_id = user_id.strip()

        self.status_label.config(text=" 狀態: 正在點擊車次訂票按鈕...")
        print(f"\n💡 [階段一] 準備點擊查詢結果中的第 {express_index + 1} 個自強號...")
        
        async def do_click():
            try:
                rows = await self.page.query_selector_all("tr.trip-column")
                express_rows = []
                for row in rows:
                    text = await row.inner_text()
                    if any(x in text for x in ["自強", "普悠瑪", "太魯閣", "3000", "EMU3000"]):
                        express_rows.append(row)
                
                if express_index >= len(express_rows):
                    print(f" 索引值 {express_index} 超出目前的自強號總數")
                    return

                target_row = express_rows[express_index]
                list_btn = await target_row.query_selector("button:has-text('訂票'), a:has-text('訂票'), :text('訂票')")
                
                if not list_btn:
                    print(" 找不到列表中的車次訂票按鈕，嘗試點擊該列最後一個按鈕")
                    list_btn = await target_row.query_selector("button, a")

                if not list_btn:
                    self.root.after(0, lambda: self.status_label.config(text=" 狀態: 找不到列表訂票按鈕"))
                    return

                print(" 已點擊車次，等待新訂票頁面載入...")
                async with self.page.expect_popup() as popup_info:
                    await list_btn.click()
                
                popup_page = await popup_info.value
                
                await popup_page.wait_for_load_state("networkidle")
                print(f" 成功進入資料填寫頁面: {popup_page.url}")
                self.root.after(0, lambda: self.status_label.config(text=" 狀態: 進入填寫頁面，開始自動化..."))
                
                try:
                    # 🎯 1. 填入身分證字號
                    id_selector = "input#pid, input[name='pid'], input[placeholder*='身分證']"
                    await popup_page.wait_for_selector(id_selector, timeout=5000)
                    await popup_page.fill(id_selector, user_id)
                    print(f" [成功] 已自動填入身分證字號")
                    
                    #  2. 處理台鐵動態驗證碼
                    self.root.after(0, lambda: self.status_label.config(text=" 狀態: 等待 Google v3 驗證結果..."))
                    
                    captcha_img_selector = "img#codeimg"
                    input_captcha_selector = "input#verifyCode"
                    
                    try:
                        print(" 正在監控網頁是否跳出二級圖形驗證碼...")
                        await popup_page.wait_for_selector(captcha_img_selector, state="visible", timeout=4000)
                        
                        captcha_element = await popup_page.query_selector(captcha_img_selector)
                        if captcha_element:
                            self.root.after(0, lambda: self.status_label.config(text=" 狀態: 偵測到圖形驗證碼，AI 辨識中..."))
                            
                            img_bytes = await captcha_element.screenshot()
                            
                            print(" 正在透過非同步執行緒呼叫 Gemini API 辨識中...")
                            ai_predicted_code = await asyncio.to_thread(get_captcha_text, img_bytes)
                            print(f"  [辨識成功] 預測驗證碼結果為: {ai_predicted_code}")

                            await popup_page.fill(input_captcha_selector, ai_predicted_code)
                            print(" 暫停 2 秒鐘供肉眼比對驗證碼...")
                            await popup_page.wait_for_timeout(2000) 
                            
                    except Exception as captcha_timeout_err:
                        print(" 提示：未偵測到二級圖形驗證碼，準備直接送出表單。")
                    
                    #  3. 精準鎖定最終 Submit
                    final_submit_selector = "input[type='submit'], button[type='submit'], .btn-3d"
                    final_submit_btn = await popup_page.query_selector(final_submit_selector)
                    
                    if final_submit_btn:
                        await final_submit_btn.click()
                        print(" [成功] 已自動按下最終送出/訂票按鈕！")
                        self.root.after(0, lambda: self.status_label.config(text=" 狀態: 已自動送出！正在等待明細頁面..."))
                        
                        try:
                            next_step_selector = "button.btn-nextStep, :text('下一步')"
                            print("⏳ 正在等待訂票成功確認頁面載入...")
                            await popup_page.wait_for_selector(next_step_selector, timeout=7000)
                            print("\n🎉 [階段三] 成功進入訂票成功確認頁面！")
                            
                            booking_code_el = await popup_page.query_selector(".cartlist-id span.font18")
                            booking_code = await booking_code_el.inner_text() if booking_code_el else "未知"
                            
                            seat_info_el = await popup_page.query_selector("span.seat")
                            seat_info = await seat_info_el.inner_text() if seat_info_el else "未知"
                            
                            print("-" * 50)
                            print(f"🎫 【台鐵訂票成功明細】")
                            print(f"🔹 訂票代碼：{booking_code.strip()}")
                            print(f"🔹 分配座位：{seat_info.strip()}")
                            print("-" * 50)
                            
                            self.root.after(0, lambda: self.status_label.config(
                                text=f" 狀態: 🎉 訂票成功！代碼: {booking_code.strip()} | 座位: {seat_info.strip()}，正進入下一步..."
                            ))
                            
                            final_next_btn = await popup_page.query_selector(next_step_selector)
                            if final_next_btn:
                                await popup_page.wait_for_timeout(500)
                                await final_next_btn.click()
                                print(" [成功] 已自動點擊『下一步』按鈕！")
                                self.root.after(0, lambda: self.status_label.config(text=" 狀態: 已點擊下一步，請至網頁完成付款程序。"))
                            
                        except Exception as page_three_err:
                            print(f" 擷取明細或點擊下一步時失敗: {page_three_err}")
                        
                    else:
                        print(" 找不到最終送出按鈕，請手動點擊網頁上的按鈕")
                        self.root.after(0, lambda: self.status_label.config(text=" 狀態: 欄位已自動填妥，請手動點擊送出。"))
                        
                except Exception as inner_e:
                    print(f" 自動化填寫流程發生錯誤: {inner_e}")
                    self.root.after(0, lambda: self.status_label.config(text=" 狀態: 自動化填寫失敗。"))

            except Exception as e:
                print(f" 核心流程失敗: {e}")
                self.root.after(0, lambda: self.status_label.config(text=" 狀態: 流程失敗，請查看終端機 Log"))
                
        asyncio.run_coroutine_threadsafe(do_click(), self.bg_loop)

    def show_error(self, err_msg):
        self.start_btn.config(state="normal", bg=self.c_success, text="🎙️  啟動查票 (導入語音資料)")
        self.status_label.config(text=" 狀態: 執行發生錯誤。")
        messagebox.showerror("錯誤", f"自動化過程中發生錯誤:\n{err_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainApp(root)
    root.mainloop()