from PIL import Image, ImageDraw, ImageFont

# 画像サイズ
width, height = 1280, 720

# 背景色と画像を生成
background_color = (135, 206, 250)  # 空色
image = Image.new("RGB", (width, height), background_color)

# 描画用のオブジェクトを作成
draw = ImageDraw.Draw(image)

# フォントを設定（WindowsやMacに応じてフォントパスを変更）
font = ImageFont.truetype("arial.ttf", 50)  # 50ポイントのフォント

# テキストを描画
text = "Hello, Flask Calendar!"
text_color = (255, 255, 255)  # 白色
text_width, text_height = draw.textsize(text, font=font)
text_position = ((width - text_width) // 2, (height - text_height) // 2)
draw.text(text_position, text, fill=text_color, font=font)

# 画像を保存
image.save("static/background.jpg")
print("背景画像が作成されました: static/background.jpg")
