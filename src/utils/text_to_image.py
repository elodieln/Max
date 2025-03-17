from PIL import Image, ImageDraw, ImageFont
import io
import base64

def text_to_image(text: str, width: int = 800, height: int = 600, font_size: int = 20) -> str:
    """
    Convertit du texte en image et renvoie l'image encodée en base64.
    
    Args:
        text: Le texte à convertir.
        width: Largeur de l'image.
        height: Hauteur de l'image.
        font_size: Taille de la police.
    
    Returns:
        Une chaîne base64 représentant l'image au format JPEG.
    """
    # Créer une image blanche
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Charger une police par défaut
    try:
        # Vous pouvez fournir le chemin d'une police TTF si vous en avez une spécifique
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Dessiner le texte (vous pouvez ajuster l'alignement et le wrapping)
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    
    # Sauvegarder l'image dans un buffer en JPEG
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str
