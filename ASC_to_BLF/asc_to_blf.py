import can
import os

def convert_asc_to_blf(asc_path, blf_path=None):
    if not os.path.isfile(asc_path):
        print(f"[ERROR] File not found: {asc_path}")
        return False

    if not blf_path:
        blf_path = os.path.splitext(asc_path)[0] + ".blf"

    try:
        with open(asc_path, 'r') as asc_file:
            reader = can.ASCReader(asc_file)
            messages = list(reader)

        with can.BLFWriter(blf_path) as writer:
            for msg in messages:
                writer.write(msg)

        print(f"[SUCCESS] Converted to: {blf_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        return False

# Example usage:
if _name_ == "_main_":
    input_asc = "example.asc"  # Replace with your .asc file path
    convert_asc_to_blf(input_asc)
