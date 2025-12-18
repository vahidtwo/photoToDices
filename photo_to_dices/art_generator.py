import logging
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ArtGenerator:
    DICE_IMAGE_SIZE_THRESHOLD = 20
    DEFAULT_DICE_WIDTH = 300

    def __init__(self, output_dir_path="~/tmp/"):
        self.output_dir = Path(output_dir_path).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory set to: {self.output_dir}")

    def _get_dice_images(self, dice_size):
        package_directory = Path(__file__).parent
        dice_images = []
        for i in range(1, 7):
            dice_path = package_directory / "dice" / f"{i}.png"
            logging.debug(f"Loading dice image: {dice_path}")  # Changed to debug
            dice_image = Image.open(dice_path)
            dice_image = dice_image.resize((dice_size, dice_size), Image.Resampling.LANCZOS)
            dice_images.append(dice_image)
        return dice_images

    def convert_to_dice_art(self, image_path, scale=1, dice_width=DEFAULT_DICE_WIDTH, progress_callback=None):
        logging.info(f"Starting dice art conversion for: {image_path}")
        try:
            input_image = Image.open(image_path)
        except FileNotFoundError:
            logging.error(f"Image not found at: {image_path}")
            return None, None

        image_name = Path(image_path).name

        dice_size = int(input_image.width / dice_width)
        if dice_size < self.DICE_IMAGE_SIZE_THRESHOLD:
            dice_size = self.DICE_IMAGE_SIZE_THRESHOLD
        logging.info(f"Calculated dice size: {dice_size}")

        dice_faces = self._get_dice_images(dice_size)

        processed_image = ImageOps.grayscale(input_image)
        processed_image = ImageOps.equalize(processed_image)

        if scale > 1:
            logging.info(f"Scaling image by a factor of {scale}")
            processed_image = processed_image.resize(
                (processed_image.width * scale, processed_image.height * scale), Image.Resampling.LANCZOS
            )

        # Convert processed image to numpy array for faster pixel access
        processed_array = np.array(processed_image)

        dice_art_image = Image.new("L", (processed_image.width, processed_image.height), "white")
        logging.info("Created a new blank image for the dice art.")

        total_dice_count = 0
        total_rows = (processed_image.height - dice_size) // dice_size

        for y_step, y in enumerate(range(0, processed_image.height - dice_size, dice_size)):
            for x in range(0, processed_image.width - dice_size, dice_size):
                # Extract the current block using NumPy slicing
                block = processed_array[y : y + dice_size, x : x + dice_size]
                average_sector_color = np.mean(block)  # Calculate mean directly

                dice_number = int((255 - average_sector_color) * 6.0 / 255 + 1)
                dice_number = max(1, min(6, dice_number))

                box = (x, y, x + dice_size, y + dice_size)
                dice_art_image.paste(dice_faces[dice_number - 1], box)
                total_dice_count += 1

            if progress_callback and total_rows > 0:  # Avoid ZeroDivisionError
                progress = int((y_step / total_rows) * 100)
                progress_callback(progress)

        if progress_callback:
            progress_callback(100)

        logging.info(f"Total dice used: {total_dice_count}")
        output_file_path = self.output_dir / f"dice-{image_name}"
        dice_art_image.save(output_file_path, "JPEG")
        logging.info(f"Dice art saved to: {output_file_path}")
        return str(output_file_path), total_dice_count
