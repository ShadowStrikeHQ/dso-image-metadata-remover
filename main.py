import argparse
import logging
import os
import sys

from PIL import Image
from PIL import ExifTags

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Removes metadata from image files (EXIF, IPTC, XMP).')
    parser.add_argument('input_file', help='The input image file.')
    parser.add_argument('output_file', help='The output image file (will overwrite if exists).')
    parser.add_argument('--keep-color-profile', action='store_true', help='Preserve color profile') # Feature request
    return parser


def remove_metadata(input_file, output_file, keep_color_profile=False):
    """
    Removes metadata (EXIF, IPTC, XMP) from an image file.

    Args:
        input_file (str): Path to the input image file.
        output_file (str): Path to the output image file.
        keep_color_profile (bool): Optional. if true, keeps the color profile
    """
    try:
        # Input Validation
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if not os.path.isfile(input_file):
            raise ValueError(f"Input file is not a regular file: {input_file}")


        img = Image.open(input_file)

        # Clean EXIF data
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)

        # Save the image without metadata
        # Using 'quality' to preserve image quality as much as possible for JPEGs.
        # Ensure we preserve the file format for consistency
        file_extension = os.path.splitext(input_file)[1].lower()

        save_options = {}

        if file_extension in ['.jpg', '.jpeg']:
             save_options['quality'] = 95  # Adjust as needed for quality/size trade-off
             save_options['optimize'] = True
             save_options['progressive'] = True #for jpeg images.
        if keep_color_profile:
           try:
               profile = img.info.get('icc_profile')
               if profile:
                   save_options['icc_profile'] = profile
                   logging.info("Preserving color profile")
           except Exception as e:
               logging.warning(f"Error while trying to read and perserve the color profile: {e}")


        image_without_exif.save(output_file, **save_options)

        logging.info(f"Metadata removed successfully.  Output file: {output_file}")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise # re-raise exception to be handled in main()
    except ValueError as e:
        logging.error(f"Value error: {e}")
        raise # re-raise exception to be handled in main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise # re-raise exception to be handled in main()


def main():
    """
    Main function to parse arguments and call the metadata removal function.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        remove_metadata(args.input_file, args.output_file, args.keep_color_profile)
    except Exception as e:
        logging.error(f"An unhandled error occurred during processing: {e}")
        sys.exit(1) # Exit with a non-zero code to indicate failure

    sys.exit(0)  # Exit with a zero code to indicate success


if __name__ == "__main__":
    # Example usage:
    # python dso-image-metadata-remover.py input.jpg output.jpg
    # python dso-image-metadata-remover.py input.png output.png --keep-color-profile
    main()