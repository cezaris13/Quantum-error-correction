from io import BytesIO
from cairosvg import svg2png
from jupyter_compare_view import compare
import matplotlib.image as mpimg
import numpy as np
from .correct_rep_code import create_rep_code_stim_string
import stim
from PIL import Image

def svg_to_png_with_white_bg(svg_data):
    """Convert SVG to PNG and ensure a white background."""
    png_bytes = BytesIO()
    svg2png(bytestring=svg_data, write_to=png_bytes)

    # Open PNG with PIL and convert transparent background to white
    png_bytes.seek(0)
    img = Image.open(png_bytes).convert("RGBA")
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(white_bg, img).convert("RGB")  # Remove transparency

    # Save it back to BytesIO for Matplotlib compatibility
    final_png_bytes = BytesIO()
    img.save(final_png_bytes, format="PNG")
    final_png_bytes.seek(0)

    return final_png_bytes

def pad_image_to_same_size(img1, img2):
    """Pads the smaller image with white background to match the size of the larger one."""
    max_height = max(img1.shape[0], img2.shape[0])
    max_width = max(img1.shape[1], img2.shape[1])

    def pad_image(img):
        pad_height = max_height - img.shape[0]
        pad_width = max_width - img.shape[1]
        return np.pad(
            img,
            ((0, pad_height), (0, pad_width), (0, 0)),  # Pad height, width, and keep channels
            mode='constant',
            constant_values=1  # White background
        )

    return pad_image(img1), pad_image(img2)

def compare_svg_diagram(d1, d2):
    img1 = mpimg.imread(svg_to_png_with_white_bg(d1._repr_svg_()), format='png')
    img2 = mpimg.imread(svg_to_png_with_white_bg(d2._repr_svg_()), format='png')

    img1, img2 = pad_image_to_same_size(img1, img2)  # Normalize sizes

    print(f"Your circuit's diagram (left) {'IS' if img1.shape == img2.shape and np.all(img1 == img2) else 'is NOT'} \
identical to the reference one (right).")

    # Changed to height 500, since I cannot see the ids of the image.
    # For the change to take effect, restart the notebook and rerun the cells.
    return compare(img1, img2, start_mode='horizontal', height=500, display_format='png', add_controls=False)

def compare_plt_fig(fig1, filename):
    b1 = BytesIO()
    fig1.savefig(b1, format='png')
    b1.seek(0)
    img1 = b1.getvalue()
    b1.close()

    with open(filename, 'rb') as fp:
        img2 = fp.read()

    return compare(img1,
                 img2,
                 start_mode='horizontal',
                 #height=285,
                 display_format='png',
                 add_controls=False,
                 )

def compare_circuit_timelines(circuit1, circuit2):
    d1, d2 = circuit1.diagram('timeline-svg'), circuit2.diagram('timeline-svg')
    return compare_svg_diagram(d1, d2)

def compare_part1(circuit):
    return compare_circuit_timelines(circuit, stim.Circuit.from_file('dont_look/correct_part1.stim'))

def compare_part2(circuit):
    return compare_circuit_timelines(circuit, stim.Circuit.from_file('dont_look/correct_part2.stim'))

def compare_part3(circuit):
    return compare_circuit_timelines(circuit, stim.Circuit.from_file('dont_look/correct_part3.stim'))

def compare_repcode(circuit, distance, rounds, p):
    return compare_circuit_timelines(circuit, stim.Circuit(create_rep_code_stim_string(distance, rounds, p)))

def compare_repcode_plot1(fig):
    return compare_plt_fig(fig, 'dont_look/repcode_plot1.png')

def compare_repcode_plot2(fig):
    return compare_plt_fig(fig, 'dont_look/repcode_plot2.png')

def compare_repcode_plot3(fig):
    return compare_plt_fig(fig, 'dont_look/repcode_plot3.png')