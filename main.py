import os
import subprocess
from PIL import Image

# Function to extract frames from video using ffmpeg
def extract_frames_from_video(video_path, output_dir, frame_rate=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extract frames from the video
    subprocess.call([
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={frame_rate}',
        f'{output_dir}/frame_%03d.bmp'
    ])

# Function to convert BMP to C array
def bmp_to_c_array(image_path, array_name):
    image = Image.open(image_path)
    image = image.convert('1')  # Convert to monochrome
    image = image.resize((32, 32))  # Resize to 32x32 pixels

    pixels = list(image.getdata())
    width, height = image.size
    array = []

    for y in range(height):
        for x in range(0, width, 8):
            byte = 0
            for bit in range(8):
                if x + bit < width:
                    byte |= (1 if pixels[y * width + x + bit] == 0 else 0) << (7 - bit)
            array.append(byte)

    c_array = [f'static const unsigned char {array_name}[] U8X8_PROGMEM = {{']
    c_array.extend(f'0x{byte:02X},' for byte in array)
    c_array.append('};\n')

    return '\n'.join(c_array)

# Function to convert all BMP frames to C arrays
def convert_all_bmp_to_c(directory):
    c_arrays = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".bmp"):
            array_name = os.path.splitext(filename)[0]
            image_path = os.path.join(directory, filename)
            c_array_code = bmp_to_c_array(image_path, array_name)
            c_arrays.append(c_array_code)
    return c_arrays

# Main function to handle the conversion
def main(video_path, output_dir):
    extract_frames_from_video(video_path, output_dir)

    c_arrays = convert_all_bmp_to_c(output_dir)

    with open("frames.h", "w") as f:
        for c_array in c_arrays:
            f.write(c_array)
    
    print("Conversion complete. The frames have been saved to frames.h")

# Example usage
video_path = 'video.mp4'  # Replace with your video file path
output_dir = 'frames'

main(video_path, output_dir)
