import os
import random

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


def generate_profile_picture(username, image_size=256, font_size=150):
    background_color = tuple(random.randint(0, 255) for _ in range(3))  # RGB

    image = Image.new("RGB", (image_size, image_size), background_color)
    draw = ImageDraw.Draw(image)
    initial = username[0].upper() if username else "?"
    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/arial.ttf')

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initial, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_position = ((image_size - text_width) // 2, (image_size - text_height) // 3.5)

    draw.text(text_position, initial, fill="white", font=font)

    filename = f"{username}_profile.png"
    file_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    image.save(file_path)

    return f"profile_images/{filename}"
