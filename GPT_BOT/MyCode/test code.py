import ImageEnhance
from PIL import Image

def image_to_rgb_list(image_path):
    # Open an image file
    with Image.open(image_path) as img:
        # Convert the image to RGB if it's not
        img = img.convert('RGB')

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(5.0)

        # Extract RGB tuples into a list
        rgb_list_inside = []
        pixels = img.load()
        width, height = img.size
        for i in range(height):
            row = []
            for j in range(width):
                row.append(pixels[j, i])
            rgb_list_inside.append(row)

    return rgb_list_inside


# Specify the path to your image file
image_path = r'C:\Users\Sam Eppstein\Desktop\TEST_IMAGE_3.png'  # Replace with your image file path
rgb_list = image_to_rgb_list(image_path)

# Optionally, print the RGB list to see the output
print(rgb_list)



def create_image_from_rgb(rgb_list, filename):
    # Get the dimensions of the rgb_list
    height = len(rgb_list)
    width = len(rgb_list[0]) if height > 0 else 0

    # Create a new image with RGB mode
    image = Image.new("RGB", (width, height))

    # Load the image's pixel map
    pixels = image.load()

    # Iterate over the rgb_list to set pixels
    for i in range(height):
        for j in range(width):
            # Set the colour accordingly
            pixels[j, i] = rgb_list[i][j]

    # Save the image to a file
    image.save(filename)


# Define your RGB tuples list
image_data = rgb_list
# Create and save the image

create_image_from_rgb(image_data, 'test_image_4.png')
