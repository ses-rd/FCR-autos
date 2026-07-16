# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_128 = fields.Binary(string="Image")

    @api.onchange('product_id')
    def onchange_sale_product_image(self):
        for line in self:
            if line.product_id.image_128:
                line.image_128 = line.png_to_jpeg_white_bg(line.product_id.image_128)
            else:
                line.image_128 = False

    def png_to_jpeg_white_bg(self, image_bytes: bytes) -> bytes:
        if not image_bytes:
            return image_bytes

        if isinstance(image_bytes, str):
            image_bytes = image_bytes.encode("utf-8")

        try:
            from PIL import Image, UnidentifiedImageError
        except ImportError:
            return image_bytes

        try:
            raw_image = base64.b64decode(image_bytes)
            if not raw_image:
                return image_bytes

            image = Image.open(io.BytesIO(raw_image))
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if image.mode in ("RGBA", "LA"):
                    alpha = image.getchannel("A") if image.mode in ("RGBA", "LA") else None
                    if alpha is not None:
                        background.paste(image, mask=alpha)
                    else:
                        background.paste(image)
                else:
                    background.paste(image)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            output = io.BytesIO()
            image.save(output, format="JPEG", quality=90)
            return base64.b64encode(output.getvalue())
        except (UnidentifiedImageError, OSError, ValueError):
            return image_bytes
        except Exception:
            _logger.exception("Unable to convert product image to JPEG; keeping the original image bytes.")
            return image_bytes
