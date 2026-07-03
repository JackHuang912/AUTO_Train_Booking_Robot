# import os
# import cv2
# import numpy as np

# def test_thickness_denoise(image_path, output_dir=r"D:\code_test"):
#     os.makedirs(output_dir, exist_ok=True)
    
#     # 1. 讀取彩色原圖 (一定要用最原始的彩色圖 temp_screenshot.jpg，特徵最完整)
#     img = cv2.imread(image_path)
#     if img is None:
#         print(f"❌ 無法讀取原始彩色圖片: {image_path}")
#         return
        
#     img_resized = cv2.resize(img, (200, 60))
#     gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
#     # 基礎二值化（切成黑底白字來處理粗細）
#     _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
#     print("\n--- 🕵️‍♂️ 啟動『筆畫粗細過濾演算法』特攻測試 ---")

#     # =========================================================================
#     # 方法一：精準黑帽運算（分離細線法）
#     # =========================================================================
#     # 建立一個 3x3 的圓形/十字形結構，這個尺寸剛好跟細斜線的寬度相當
#     kernel_fine = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
#     # 黑帽運算可以「只抓出比筆刷還要細的暗部/線條特徵」
#     fine_lines = cv2.morphologyEx(binary, cv2.MORPH_BLACKHAT, kernel_fine)
#     # 從原二值化圖中，扣除這些被抓出來的細線
#     method1_res = cv2.subtract(binary, fine_lines)
    
#     cv2.imwrite(os.path.join(output_dir, "thickness_method_1_blackhat.jpg"), cv2.bitwise_not(method1_res))
#     print("💾 已生成: thickness_method_1_blackhat.jpg (黑帽細線抽離法)")

#     # =========================================================================
#     # 方法二：先深度侵蝕（消滅細線） + 距離變換重構（還原粗字體）
#     # =========================================================================
#     # 用 3x3 矩陣用力侵蝕，因為斜線很細，侵蝕完後斜線會完全化為烏有(0)，只留下字母的中心骨架
#     eroded = cv2.erode(binary, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)
#     # 使用「距離變換」重新計算骨架到邊緣的距離，強行把字母的粗度「長回來」，而且絕對不會長出斜線
#     dist_transform = cv2.distanceTransform(eroded, cv2.DIST_L2, 5)
#     _, method2_res = cv2.threshold(dist_transform, 0.2 * dist_transform.max(), 255, cv2.THRESH_BINARY)
#     method2_res = method2_res.astype(np.uint8)
    
#     cv2.imwrite(os.path.join(output_dir, "thickness_method_2_distance.jpg"), cv2.bitwise_not(method2_res))
#     print("💾 已生成: thickness_method_2_distance.jpg (深度侵蝕與距離重構法)")

#     # =========================================================================
#     # 方法三：非對稱粗細過濾（使用 2x3 或 3x2 橢圓筆刷）
#     # =========================================================================
#     # 既然斜線細、字母粗，我們用一個橫向略寬的橢圓核心 (3, 2) 做開運算
#     kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 2))
#     opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_ellipse)
#     # 再用閉運算稍作修補
#     method3_res = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
    
#     cv2.imwrite(os.path.join(output_dir, "thickness_method_3_ellipse.jpg"), cv2.bitwise_not(method3_res))
#     print("💾 已生成: thickness_method_3_ellipse.jpg (橢圓非對稱過濾法)")

# if __name__ == "__main__":
#     target_image = r"D:\code_test\temp_screenshot.jpg"
#     test_thickness_denoise(target_image)
#     print("\n🎉 針對『筆畫粗細』的 3 大演算法測試完畢！請立刻打開 D:\\code_test\\")
#     print("檢查 thickness_method_1 到 3 的圖片。")
#     print("利用細線與粗字體的物理特徵差異，這次應該能看到非常突破性的乾淨結果！")
import os
import cv2
import numpy as np

def test_thickness_denoise(image_path, output_dir=r"D:\code_test"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 讀取彩色原圖 (一定要用最原始的彩色圖 temp_screenshot.jpg)
    img = cv2.imread(image_path)
    if img is None:
        print(f" 無法讀取原始彩色圖片: {image_path}")
        return
        
    img_resized = cv2.resize(img, (200, 60))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # 基礎二值化（切成黑底白字來處理粗細）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    print("\n--- 『筆畫粗細過濾與彩色還原』測試 ---")

    # =========================================================================
    # 方法一：精準黑帽運算（分離細線法）
    # =========================================================================
    kernel_fine = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    fine_lines = cv2.morphologyEx(binary, cv2.MORPH_BLACKHAT, kernel_fine)
    method1_res = cv2.subtract(binary, fine_lines)
    
    cv2.imwrite(os.path.join(output_dir, "thickness_method_1_blackhat.jpg"), cv2.bitwise_not(method1_res))
    print(" 已生成: thickness_method_1_blackhat.jpg (黑帽細線抽離法)")

    # =========================================================================  
    # 用 3x3 矩陣削去細斜線
    eroded = cv2.erode(binary, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)
    # 使用「距離變換」還原粗字體
    dist_transform = cv2.distanceTransform(eroded, cv2.DIST_L2, 5)
    _, mask = cv2.threshold(dist_transform, 0.2 * dist_transform.max(), 255, cv2.THRESH_BINARY)
    mask = mask.astype(np.uint8) # 這是去噪成功的純黑白遮罩 (白字黑底)
    
    # 【核心邏輯：彩色還原】
    # 利用黑白遮罩，把原始彩色圖片中字體顏色的部分挖出來
    color_restored = cv2.bitwise_and(img_resized, img_resized, mask=mask)
    
    # 建立純白畫布作為新背景
    white_background = np.full_like(img_resized, 255) 
    # 把不屬於字體的地方填滿白色
    bg_part = cv2.bitwise_and(white_background, white_background, mask=cv2.bitwise_not(mask))
    # 結合彩色字與純白背景
    method2_color_res = cv2.add(bg_part, color_restored)
    
    # 儲存彩色還原結果！
    cv2.imwrite(os.path.join(output_dir, "thickness_method_2_distance.jpg"), method2_color_res)
    print(" 已生成: thickness_method_2_distance.jpg ( 彩色還原法 )")

    # =========================================================================
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 2))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_ellipse)
    method3_res = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
    
    cv2.imwrite(os.path.join(output_dir, "thickness_method_3_ellipse.jpg"), cv2.bitwise_not(method3_res))
    print(" 已生成: thickness_method_3_ellipse.jpg (橢圓非對稱過濾法)")

if __name__ == "__main__":
    target_image = r"D:\code_test\temp_screenshot.jpg"
    test_thickness_denoise(target_image)
    print("\n 測試完畢！請立刻打開 D:\\code_test\\")
    print("檢查 thickness_method_2_distance.jpg 是否成功的變成了【乾淨、且帶有原圖色彩】的白底驗證碼圖片！")