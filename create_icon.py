from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a white background
    size = 256
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle for the background
    circle_color = (255, 103, 0)  # MI Orange color
    draw.ellipse([10, 10, size-10, size-10], fill=circle_color)
    
    # Draw a lock symbol
    lock_color = (255, 255, 255)  # White color
    # Lock body
    draw.rectangle([size//3, size//2, 2*size//3, 3*size//4], fill=lock_color)
    # Lock top
    draw.rectangle([size//2-20, size//3, size//2+20, size//2], fill=lock_color)
    draw.ellipse([size//2-20, size//3-10, size//2+20, size//3+10], fill=lock_color)
    
    # Save as PNG
    image.save('icon.png')
    
    # Convert to ICO
    image.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    
    print("Icon created successfully!")

if __name__ == '__main__':
    create_icon() 