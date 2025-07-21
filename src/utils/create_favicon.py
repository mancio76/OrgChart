# Script per generare favicon basic (da eseguire una volta)
from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    """Crea una favicon basic con le iniziali OM"""
    # Assicurati che la directory static esista
    os.makedirs('src/web/static', exist_ok=True)
    
    # Crea immagine 32x32
    size = (32, 32)
    img = Image.new('RGB', size, color='#2563eb')
    draw = ImageDraw.Draw(img)
    
    # Aggiungi testo OM
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((8, 10), "OM", fill='white', font=font)
    
    # Salva come ICO
    img.save('src/web/static/favicon.ico', format='ICO')
    
    # Salva versioni PNG
    img.save('src/web/static/favicon-32x32.png')
    
    # Crea versione 16x16
    img_small = img.resize((16, 16))
    img_small.save('src/web/static/favicon-16x16.png')
    
    print("✅ Favicon create in src/web/static/")

if __name__ == "__main__":
    create_favicon()