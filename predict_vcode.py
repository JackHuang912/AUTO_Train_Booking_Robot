# import os
# import sys
# import cv2
# import numpy as np
# import tensorflow as tf

# # 修正 Windows 環境變換與 C++ 運行庫路徑
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# if sys.platform == 'win32':
#     os.environ['PATH'] = os.environ['PATH'] + r';C:\Windows\System32'

# # =========================================================================
# # 1. 基礎參數設定
# # =========================================================================
# IMG_HEIGHT = 60
# IMG_WIDTH = 200      
# MAX_LENGTH = 6  

# CHAR_SET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# BLANK_CHAR = "_"    
# FULL_CHAR_SET = CHAR_SET + BLANK_CHAR
# NUM_CLASSES = len(FULL_CHAR_SET)

# idx_to_char = {idx: char for idx, char in enumerate(FULL_CHAR_SET)}

# # =========================================================================
# # 2. 建立模型並載入權重
# # =========================================================================
# MODEL_PATH = r"D:\code_test\captcha_model_3.h5"

# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(f"[Error] Can not find model file at: {MODEL_PATH}")

# print("--- Rebuilding Model Structure from Kaggle Blueprint ---")

# input_layer = tf.keras.layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3), name='image_input')
# x = tf.keras.layers.Conv2D(32, (3, 3), padding='same', activation='relu')(input_layer)
# x = tf.keras.layers.BatchNormalization()(x)
# x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# x = tf.keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
# x = tf.keras.layers.BatchNormalization()(x)
# x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# x = tf.keras.layers.Conv2D(128, (3, 3), padding='same', activation='relu')(x)
# x = tf.keras.layers.BatchNormalization()(x)
# x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# x = tf.keras.layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
# x = tf.keras.layers.BatchNormalization()(x)
# x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# x = tf.keras.layers.Flatten()(x)
# x = tf.keras.layers.Dense(1024, activation='relu')(x)
# x = tf.keras.layers.Dropout(0.4)(x)

# outputs = []
# for i in range(MAX_LENGTH):
#     out = tf.keras.layers.Dense(NUM_CLASSES, activation='softmax', name=f'char_{i+1}')(x)
#     outputs.append(out)

# model = tf.keras.Model(inputs=input_layer, outputs=outputs)

# try:
#     model.load_weights(MODEL_PATH)
#     print("--- 🌟 Weights Loaded & Aligned Successfully! --- \n")
# except Exception as e:
#     print(f"\n❌ 權重載入失敗：{e}")
#     sys.exit(1)

# =========================================================================
# 3. 供外部主程式呼叫的辨識介面 (整合「實體落地防禦」與「3WA 去噪濾鏡」🌟)
# =========================================================================
# def get_captcha_text(image_source):
#     """
#     image_source 可以是：
#     1. 圖片檔案路徑 (str) -> 供你獨立測試用
#     2. 圖片二進位數據 (bytes) -> 供 Playwright 實戰截圖用
#     """
#     os.makedirs(r"D:\code_test", exist_ok=True)
#     temp_path = r"D:\code_test\temp_screenshot.jpg"

#     if isinstance(image_source, bytes):
#         # 1. 將 Playwright 的 bytes 解碼為 OpenCV 圖片
#         nparr = np.frombuffer(image_source, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
#         if img is not None:
#             # 🎯 核心防禦：先將圖片存成實體檔案，確保實戰環境跟你在本地測試成功的載入環境 100% 相同！
#             cv2.imwrite(temp_path, img)
#             # 再從檔案讀取進來預測，徹底解決解碼維度扭曲、只吐一個 W 的問題
#             img = cv2.imread(temp_path)
#     else:
#         # 如果傳進來的是路徑字串，直接讀取
#         img = cv2.imread(image_source)
        
#     if img is None:
#         print("❌ [AI] 讀取圖片失敗！")
#         return ""
    
#     # 影像大小調整（符合你的模型規格）
#     img_resized = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
    
#     # -----------------------------------------------------------------
#     # 🌟【新增：3WA 傳統電腦視覺去噪處理】
#     # -----------------------------------------------------------------
#     # 1. 轉灰階
#     gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
#     # 2. 自適應二值化 (將雜點背景與驗證碼文字做黑白分離)
#     _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
#     # 3. 形態學去噪：使用「開運算 (Opening)」擦除比字體細的干擾線與噪點
#     kernel = np.ones((2, 2), np.uint8)
#     denoised_binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
#     # 4. 轉回 3 通道 (RGB)，因為你的 CNN 模型 input 要求 3 通道
#     processed_img = cv2.cvtColor(denoised_binary, cv2.COLOR_GRAY2BGR)
    
#     # 🌟【除錯兼確認效果】：把 AI 真正吃進去、去噪後的圖存下來
#     # 請在執行後卡住 2 秒時，去 D:\code_test\ 看 debug_ai.jpg，確認干擾線有沒有變乾淨！
#     cv2.imwrite(r"D:\code_test\debug_ai.jpg", processed_img)
#     # -----------------------------------------------------------------
    
#     # 影像正規化與餵給模型（100% 沿用你成功的寫法，只把 img_resized 換成去噪後的 processed_img）
#     img_input = processed_img.astype(np.float32) / 255.0
#     img_input = np.expand_dims(img_input, axis=0)
    
#     # 預測
#     predictions = model.predict(img_input, verbose=0)
    
#     predicted_text = ""
#     # 走訪 6 個分支的預測結果（100% 沿用你原本成功的寫法）
#     for position_pred in predictions:
#         best_match_idx = np.argmax(position_pred[0])
#         char = idx_to_char[best_match_idx]
        
#         if char != BLANK_CHAR:
#             predicted_text += char
            
#     return predicted_text
import os
import cv2
import numpy as np
import google.generativeai as genai
from PIL import Image
import io

def get_captcha_text(image_source):
    """
    將金鑰設定完全內聚在函式中，徹底解決 Playwright 異步執行緒抓不到 Key 的問題
    """
    os.makedirs(r"D:\code_test", exist_ok=True)
    temp_path = r"D:\code_test\temp_screenshot.jpg"

   
    genai.configure(api_key="輸入使用者gemini api")

    raw_image = None
    
    # 2. 解析圖片來源
    if isinstance(image_source, bytes):
        nparr = np.frombuffer(image_source, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
        if img is not None:
            cv2.imwrite(temp_path, img)
        raw_image = Image.open(io.BytesIO(image_source))
    else:
        raw_image = Image.open(image_source)
        
    if raw_image is None:
        print(" 圖片對象為空！")
        return ""

    #  呼叫 Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """
        Analyze this CAPTCHA image. It contains 5 or 6 alphanumeric characters.
        Identify the characters accurately, paying attention to case sensitivity.
        Output ONLY the characters themselves, with no spaces, no punctuation, and no extra text.
        """
        
        response = model.generate_content([prompt, raw_image])
        predicted_text = response.text.strip()
        
        print(f" Gemini API 識別成功: {predicted_text}")
        return predicted_text

    except Exception as e:
        
        print(f"呼叫失敗: {e}")
        return "ERROR_API_CRASH"