import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFilter
import os
from typing import List, Tuple
from app.config import PDF_RENDER_SCALE, AUDIT_BOX_WIDTH, BLUR_RADIUS


def draw_audit_boxes(image_path: str, output_path: str, boxes: List[Tuple[int, int, int, int]]):
    """
    Draws RED bounding boxes around detected PII for the Audit View.
    """
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            for box in boxes:
                draw.rectangle(box, outline="red", width=AUDIT_BOX_WIDTH)
            img.save(output_path)
    except Exception as e:
        print(f"[IMAGE TOOL ERROR] Could not draw boxes: {e}")


def blur_regions(image_path: str, output_path: str, boxes: List[Tuple[int, int, int, int]]):
    """
    Applies strong Gaussian Blur to specific regions (Faces/PII) for the Safe View.
    """
    try:
        with Image.open(image_path) as img:
            blurred_img = img.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))

            for box in boxes:
                x1, y1, x2, y2 = box
                region = blurred_img.crop((x1, y1, x2, y2))
                img.paste(region, (x1, y1, x2, y2))

            img.save(output_path)
    except Exception as e:
        print(f"[IMAGE TOOL ERROR] Could not blur regions: {e}")


def convert_pdf_to_images(pdf_path: str, output_dir: str) -> List[str]:
    """
    Converts a PDF into a list of image paths using config-defined scale.
    Ensures PDF handles are closed to prevent memory leaks.
    """
    image_paths = []
    try:
        with pdfium.PdfDocument(pdf_path) as pdf:
            base_name = os.path.basename(pdf_path).split('.')[0]

            for i, page in enumerate(pdf):
                bitmap = page.render(scale=PDF_RENDER_SCALE)
                pil_image = bitmap.to_pil()

                out_name = f"{base_name}_page_{i + 1}.png"
                full_path = os.path.join(output_dir, out_name)
                pil_image.save(full_path)
                image_paths.append(full_path)
                page.close()

        return image_paths
    except Exception as e:
        print(f"[PDF ERROR] Failed to convert PDF with pypdfium2: {e}")
        return []