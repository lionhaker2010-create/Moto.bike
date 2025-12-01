"""
imghdr moduli uchun patch - Python 3.13 da olib tashlangan
"""
import os
from PIL import Image

def what(file, h=None):
    """
    imghdr.what() funksiyasining o'rnini bosadi
    """
    if not os.path.exists(file):
        return None
    
    try:
        with Image.open(file) as img:
            return img.format.lower()
    except Exception:
        pass
    
    # Qo'shimcha tekshirishlar
    if h is not None:
        # Heade rga asoslangan tekshirish
        if h.startswith(b'\xff\xd8'):
            return 'jpeg'
        elif h.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif h.startswith(b'GIF87a') or h.startswith(b'GIF89a'):
            return 'gif'
        elif h.startswith(b'BM'):
            return 'bmp'
    
    return None

def test(file, h=None):
    """imghdr.test() funksiyasining o'rnini bosadi"""
    return what(file, h)