"""
QR Studio — Local network QR code generator
Run: uvicorn main:app --host 0.0.0.0 --port 8042
Access from any device on your network: http://<your-pc-ip>:8042
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from pathlib import Path
import qrcode
import qrcode.image.svg
from io import BytesIO

app = FastAPI(title="QR Studio")

# Error correction mapping
EC_LEVELS = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


@app.get("/", response_class=HTMLResponse)
async def index():
    return Path("templates/index.html").read_text()


@app.get("/generate/png")
async def generate_png(
        data: str = Query(..., description="Content to encode"),
        ec: str = Query("M", description="Error correction: L, M, Q, H"),
        fg: str = Query("#1a1a2e", description="Foreground hex color"),
        bg: str = Query("#ffffff", description="Background hex color"),
        box_size: int = Query(20, ge=5, le=50, description="Module pixel size"),
        border: int = Query(4, ge=0, le=10, description="Border modules"),
):
    qr = qrcode.QRCode(
        version=None,
        error_correction=EC_LEVELS.get(ec.upper(), qrcode.constants.ERROR_CORRECT_M),
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fg, back_color=bg)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="qr-code.png"'},
    )


@app.get("/generate/svg")
async def generate_svg(
        data: str = Query(..., description="Content to encode"),
        ec: str = Query("M", description="Error correction: L, M, Q, H"),
        fg: str = Query("#1a1a2e", description="Foreground hex color"),
        bg: str = Query("#ffffff", description="Background hex color"),
        border: int = Query(4, ge=0, le=10, description="Border modules"),
):
    qr = qrcode.QRCode(
        version=None,
        error_correction=EC_LEVELS.get(ec.upper(), qrcode.constants.ERROR_CORRECT_M),
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    factory = qrcode.image.svg.SvgPathImage
    img = qr.make_image(image_factory=factory, fill_color=fg, back_color=bg)

    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    return Response(
        content=buf.getvalue(),
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'attachment; filename="qr-code.svg"'},
    )


@app.get("/preview")
async def preview(
        data: str = Query(..., description="Content to encode"),
        ec: str = Query("M"),
        fg: str = Query("#1a1a2e"),
        bg: str = Query("#ffffff"),
        border: int = Query(4, ge=0, le=10),
):
    """Returns a PNG for the live preview (smaller box_size for speed)."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=EC_LEVELS.get(ec.upper(), qrcode.constants.ERROR_CORRECT_M),
        box_size=12,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fg, back_color=bg)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")