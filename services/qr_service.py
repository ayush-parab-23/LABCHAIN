import qrcode
import io
import base64

def generate_report_qr_base64(report_id, host_url=""):
    """
    Generates a base64-encoded QR code containing the secure verification URL.
    This can be rendered directly in HTML templates.
    """
    verification_url = f"{host_url}/verify/{report_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
