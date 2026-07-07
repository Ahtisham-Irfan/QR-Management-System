import qrcode
from PIL import Image
import os
import uuid

def generate_qr_code(data, fill_color="#000000", back_color="#FFFFFF", logo_path=None, size=10):
    """
    Generates a customized QR code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGB')

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path)
        
        # Calculate logo size (max 20% of QR code size)
        qr_width, qr_height = img.size
        logo_max_size = int(qr_width * 0.2)
        logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
        
        # Position logo in the center
        logo_pos = (
            (qr_width - logo.size[0]) // 2,
            (qr_height - logo.size[1]) // 2
        )
        
        # Paste logo onto QR code
        img.paste(logo, logo_pos)

    # Save image
    filename = f"{uuid.uuid4()}.png"
    save_dir = os.path.join('static', 'qr_codes')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    file_path = os.path.join(save_dir, filename)
    img.save(file_path)
    
    return filename

def format_qr_content(qr_type, data):
    """
    Formats data based on QR type (WiFi, vCard, etc.)
    """
    if qr_type == "WiFi":
        return f"WIFI:S:{data.get('ssid','')};T:{data.get('security','WPA')};P:{data.get('password','')};;"
    elif qr_type == "vCard":
        return f"BEGIN:VCARD\nVERSION:3.0\nN:{data.get('name','')}\nTEL:{data.get('phone','')}\nEMAIL:{data.get('email','')}\nEND:VCARD"
    elif qr_type == "Email":
        return f"mailto:{data.get('email','')}?subject={data.get('subject','')}&body={data.get('body','')}"
    elif qr_type == "SMS":
        return f"smsto:{data.get('phone','')}:{data.get('message','')}"
    elif qr_type == "Phone":
        return f"tel:{data.get('phone','')}"
    elif qr_type == "WhatsApp":
        return f"https://wa.me/{data.get('phone','')}?text={data.get('message','')}"
    elif qr_type == "Maps":
        return f"https://www.google.com/maps/search/?api=1&query={data.get('lat','')},{data.get('lng','')}"
    # Default for URL and Text
    return data.get('content', '')
