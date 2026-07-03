import os
import sys

# 修正 Windows 環境變換與 C++ 運行庫路徑
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
if sys.platform == 'win32':
    os.environ['PATH'] = os.environ['PATH'] + r';C:\Windows\System32'

import cv2
import numpy as np
import tensorflow as tf

# =========================================================================
# 1. 基礎參數設定（與 Kaggle 完全同步）
# =========================================================================
IMG_HEIGHT = 60
IMG_WIDTH = 200      
MAX_LENGTH = 6  

CHAR_SET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BLANK_CHAR = "_"    
FULL_CHAR_SET = CHAR_SET + BLANK_CHAR
NUM_CLASSES = len(FULL_CHAR_SET)  # 自動對齊 Kaggle 的 63 類

idx_to_char = {idx: char for idx, char in enumerate(FULL_CHAR_SET)}

# =========================================================================
# 2. 精準手動重建 Kaggle 模型骨架（100% 複製你的網格結構）
# =========================================================================
MODEL_PATH = r"D:\code_test\captcha_model_3.h5"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"[Error] Can not find model file at: {MODEL_PATH}")

print("--- Rebuilding Model Structure from Kaggle Blueprint ---")

input_layer = tf.keras.layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3), name='image_input')

# Block 1: 抓取基礎邊緣 (32 channels)
x = tf.keras.layers.Conv2D(32, (3, 3), padding='same', activation='relu')(input_layer)
x = tf.keras.layers.BatchNormalization()(x)
x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# Block 2: 抓取字元局部結構 (64 channels)
x = tf.keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
x = tf.keras.layers.BatchNormalization()(x)
x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# Block 3: 辨識完整字元特徵 (128 channels)
x = tf.keras.layers.Conv2D(128, (3, 3), padding='same', activation='relu')(x)
x = tf.keras.layers.BatchNormalization()(x)
x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# Block 4 (🌟新增): 強化高階特徵與抽象化 (256 channels)
x = tf.keras.layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
x = tf.keras.layers.BatchNormalization()(x)
x = tf.keras.layers.MaxPooling2D((2, 2))(x)

# 全連接層 (🌟拓寬神經元，餵飽後面的 6 個輸出分支)
x = tf.keras.layers.Flatten()(x)
x = tf.keras.layers.Dense(1024, activation='relu')(x) # 從 256 大幅提升到 1024
x = tf.keras.layers.Dropout(0.4)(x) # 稍微提高 Dropout 防止過擬合
# 🌟 關鍵對齊：產出 char_1 ~ char_6 核心分支
outputs = []
for i in range(MAX_LENGTH):
    out = tf.keras.layers.Dense(NUM_CLASSES, activation='softmax', name=f'char_{i+1}')(x)
    outputs.append(out)

# 宣告模型
model = tf.keras.Model(inputs=input_layer, outputs=outputs)

print("--- Extracting and Injecting Weights from H5 ---")
try:
    # 略過說明的參數，直接硬抽矩陣權重塞入骨架！
    model.load_weights(MODEL_PATH)
    print("--- 🌟 Weights Loaded & Aligned Successfully! --- \n")
except Exception as e:
    print(f"\n❌ 權重載入失敗：{e}")
    print("💡 提示：請確認本地的 H5 檔案確實為 Kaggle 產出的那一個。")
    sys.exit(1)

# =========================================================================
# 3. 預測核心函式
# =========================================================================
def predict_captcha(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return f"[Error] Cannot read image: {image_path}"
    
    # 影像前處理與正規化
    img_resized = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
    img_input = img_resized.astype(np.float32) / 255.0
    img_input = np.expand_dims(img_input, axis=0)
    
    # 讓模型預測 (會吐出 6 個輸出陣列的 list)
    predictions = model.predict(img_input, verbose=0)
    
    predicted_text = ""
    # 走訪 6 個分支的預測結果
    for position_pred in predictions:
        # position_pred[0] 取得這個 batch 第一張圖（也就是唯一的一張）的 63 類機率
        best_match_idx = np.argmax(position_pred[0])
        char = idx_to_char[best_match_idx]
        
        # 遇到自動補齊的底線 "_" 直接跳過，還原出原本 5 碼或 6 碼的驗證碼
        if char != BLANK_CHAR:
            predicted_text += char
            
    return predicted_text

# 4. 本地測試執行
# =========================================================================
if __name__ == "__main__":
    test_image_name = r"D:\code_test\thickness_method_2_distance.jpg"
    
    if os.path.exists(test_image_name):
        print("Running prediction...")
        result = predict_captcha(test_image_name)
         
        print("=" * 40)
        print(f"Test Image: {test_image_name}")
        print(f"Predict Result: [ {result} ]")
        print("=" * 40)
        
        try:
            test_img = cv2.imread(test_image_name)
            window_title = f"Predict Result: {result}"
            cv2.imshow(window_title, test_img)
            print("Image window opened. Press ANY KEY on the image window to close it...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Notice: Image show failed ({e}), but prediction text is shown above.")
    else:
        print(f"[Notice] Please put a test image named 'test.jpg' inside 'D:\\vcode_test\\'.")