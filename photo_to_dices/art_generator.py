
from pathlib import Path
from PIL import Image, ImageOps

class ArtGenerator:
    DICE_IMAGE_SIZE_THRESHOLD = 20
    DEFAULT_DICE_WIDTH = 300

    def __init__(self, output_dir_path="~/tmp/"):
        self.output_dir = Path(output_dir_path).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_dice_images(self, dice_size):
        package_directory = Path(__file__).parent
        dice_images = []
        for i in range(1, 7):
            dice_path = package_directory / "dice" / f"{i}.png"
            dice_image = Image.open(dice_path)
            dice_image = dice_image.resize((dice_size, dice_size), Image.Resampling.LANCZOS)
            dice_images.append(dice_image)
        return dice_images

    def convert_to_dice_art(self, image_path, scale=1):
        try:
            input_image = Image.open(image_path)
        except FileNotFoundError:
            return None, None

        image_name = Path(image_path).name
        
        # Calculate dice_size based on image width and a default dice width,
        # ensuring it doesn't fall below a minimum threshold.
        dice_size = int(input_image.width / self.DEFAULT_DICE_WIDTH)
        if dice_size < self.DICE_IMAGE_SIZE_THRESHOLD:
            dice_size = self.DICE_IMAGE_SIZE_THRESHOLD

        dice_faces = self._get_dice_images(dice_size)

        # Convert to grayscale and equalize
        processed_image = ImageOps.grayscale(input_image)
        processed_image = ImageOps.equalize(processed_image)

        # Apply scaling if greater than 1
        if scale > 1:
            processed_image = processed_image.resize(
                (processed_image.width * scale, processed_image.height * scale),
                Image.Resampling.LANCZOS
            )
        
        # Create a new image for the dice art
        dice_art_image = Image.new("L", (processed_image.width, processed_image.height), "white")

        total_dice_count = 0
        for y in range(0, processed_image.height - dice_size, dice_size):
            for x in range(0, processed_image.width - dice_size, dice_size):
                # Calculate the average color of the current sector
                sector_color_sum = 0
                for dy in range(dice_size):
                    for dx in range(dice_size):
                        sector_color_sum += processed_image.getpixel((x + dx, y + dy))
                average_sector_color = sector_color_sum / (dice_size * dice_size)
                
                # Determine which dice face to use based on the average color
                # Invert color (darker becomes higher dice number)
                dice_number = int((255 - average_sector_color) * 6.0 / 255 + 1)
                
                # Ensure dice_number is within valid range [1, 6]
                dice_number = max(1, min(6, dice_number))
                
                # Paste the corresponding dice face onto the dice art image
                box = (x, y, x + dice_size, y + dice_size)
                dice_art_image.paste(dice_faces[dice_number - 1], box)
                total_dice_count += 1
        
        output_file_path = self.output_dir / f"dice-{image_name}"
        dice_art_image.save(output_file_path, "JPEG")
        return str(output_file_path), total_dice_count
