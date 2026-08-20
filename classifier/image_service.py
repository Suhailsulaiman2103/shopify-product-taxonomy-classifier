from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image


class ImageService:
    """Safely validate and inspect product images."""

    REQUEST_TIMEOUT = 5

    COLOR_REFERENCES = {
        "Black": (25, 25, 25),
        "White": (235, 235, 235),
        "Gray": (128, 128, 128),
        "Red": (190, 55, 55),
        "Green": (65, 130, 75),
        "Blue": (60, 90, 170),
        "Brown": (120, 80, 55),
        "Beige": (205, 190, 160),
        "Yellow": (210, 185, 60),
        "Orange": (210, 120, 55),
        "Pink": (210, 135, 155),
        "Purple": (120, 80, 145),
    }

    def get_image_analysis(self, product):
        """Return availability plus lightweight visual information."""

        image_url = self._first_image_url(product)

        if not image_url:
            return self._failure(
                None,
                "missing",
                "No product image was provided.",
            )

        if not self._is_valid_url(image_url):
            return self._failure(
                image_url,
                "invalid",
                "Image URL is not valid.",
            )

        try:
            response = requests.get(
                image_url,
                timeout=self.REQUEST_TIMEOUT,
                allow_redirects=True,
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type",
                "",
            ).lower()

            if not content_type.startswith("image/"):
                return self._failure(
                    image_url,
                    "invalid_content",
                    "URL did not return image content.",
                )

            image = Image.open(
                BytesIO(response.content)
            ).convert("RGB")

            inferred_color = (
                self._infer_visual_color(image)
            )

            return {
                "available": True,
                "url": image_url,
                "status": "available",
                "reason": None,
                "width": image.width,
                "height": image.height,
                "visual_color": inferred_color,
            }

        except (
            requests.RequestException,
            OSError,
        ) as exc:
            return self._failure(
                image_url,
                "error",
                str(exc),
            )

    def get_image_status(self, product):
        """Backward-compatible image status helper."""

        return self.get_image_analysis(product)

    def _infer_visual_color(self, image):
        """
        Estimate a dominant non-background color.

        Very bright near-white pixels are ignored because many
        e-commerce product images use white backgrounds.
        """

        sample = image.copy()
        sample.thumbnail((80, 80))

        pixels = []

        for red, green, blue in sample.getdata():
            # Ignore near-white background pixels.
            if (
                red > 235
                and green > 235
                and blue > 235
            ):
                continue

            pixels.append((red, green, blue))

        if not pixels:
            return None

        average = tuple(
            sum(pixel[index] for pixel in pixels)
            // len(pixels)
            for index in range(3)
        )

        return min(
            self.COLOR_REFERENCES,
            key=lambda name: self._color_distance(
                average,
                self.COLOR_REFERENCES[name],
            ),
        )

    @staticmethod
    def _color_distance(first, second):
        return sum(
            (first[index] - second[index]) ** 2
            for index in range(3)
        )

    @staticmethod
    def _failure(url, status, reason):
        return {
            "available": False,
            "url": url,
            "status": status,
            "reason": reason,
            "width": None,
            "height": None,
            "visual_color": None,
        }

    @staticmethod
    def _first_image_url(product):
        for image_url in [
            product.image_1,
            product.image_2,
            product.image_3,
            product.image_4,
            product.image_5,
        ]:
            if image_url and str(image_url).strip():
                return str(image_url).strip()

        return None

    @staticmethod
    def _is_valid_url(url):
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )