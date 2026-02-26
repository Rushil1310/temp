from PIL import Image
import numpy as np

# Character ramps (dark → light)
# More characters = more detail levels
CHARSET_DETAILED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
CHARSET_SIMPLE = "@%#*+=-:. "

def image_to_ascii(input_path, output_path, width=100):
    img = Image.open(input_path)
    
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    
    w_in, h_in = img.size
    aspect_ratio = h_in / w_in
    h_out = int(width * aspect_ratio * 0.55)  # 0.55 is a good approximation for terminal font aspect
    
    img = img.resize((width, h_out))

    gray = img.convert('L')
    # TODO: Implement rest of the function

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Image to ASCII Art")
    parser.add_argument("image", nargs="?", default="input_meme.jpg", help="Input image")
    parser.add_argument("-o", "--output", default="output_art.txt", help="Output file")
    parser.add_argument("-w", "--width", type=int, default=100, help="Width in characters")
    args = parser.parse_args()
    
    result = image_to_ascii(args.image, args.output, args.width)
    print(result)
    print(f"\nSaved to {args.output}")