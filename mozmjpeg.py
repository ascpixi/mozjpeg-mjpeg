import os
import sys
import argparse
import shutil
import subprocess
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-quality", type=int, help="Compression quality (0..100; 5-95 is most useful range, default is 75)", default=75)
parser.add_argument("-grayscale", action="store_true", help="Create monochrome JPEG files")
parser.add_argument("-rgb", action="store_true", help="Create RGB JPEG files")
parser.add_argument("-i", "--input", required=True, type=str, help="Input file path")
parser.add_argument("-o", "--output", required=True, type=str, help="Output file path (raw MJPEG stream)")


args = parser.parse_args()

binary_suffix = ".exe" if os.name == "nt" else ""

def try_get_prog(name: str) -> str:
    path = f"{name}{binary_suffix}"
    if shutil.which(path) is not None:
        return path
    
    path = f"./deps/{name}{binary_suffix}"
    if os.path.isfile(path):
        return path
    
    print(f"[-] {name} not found", file=sys.stderr)
    print(f"[-] either add it to your path environment variable, or", file=sys.stderr)
    print(f"[-] place it in {path}", file=sys.stderr)
    exit(1)

cjpeg = try_get_prog("cjpeg-static")
ffmpeg = try_get_prog("ffmpeg")

# extract all frames
if os.path.isdir("tmp"):
    if input("[?] 'tmp' folder already exists, OK to delete? [Y/N]: ").lower() != "y":
        print("[ ] aborted")
        exit(0)

    shutil.rmtree("tmp")

os.mkdir("tmp")
os.mkdir("./tmp/input")
os.mkdir("./tmp/output")
subprocess.run([ffmpeg, "-i", args.input, "./tmp/input/frame-%04d.png"])

in_frames = os.listdir("./tmp/input")
in_frames.sort()

# encode via mozjpeg
total_size = 0
for filename in in_frames:
    full_path: str = f"./tmp/input/{filename}"
    out_filename = filename.replace(".png", ".jpg")
    out_path = f"./tmp/output/{out_filename}"

    subprocess.run([
        cjpeg,
        "-quality", str(args.quality),
        "-outfile", out_path,
        full_path
    ])

    size = os.stat(out_path).st_size / 1024
    total_size += size
    print(f"[+] encoded frame {out_filename}, size {size} KiB, total: {total_size} KiB")

print(f"[+] stream encoded, total size {total_size}")
print(f"[ ] now merging...")

with open(args.output, "wb") as output:
    for filename in os.listdir("./tmp/output"):
        filepath = os.path.join("./tmp/output", filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                output.write(file.read())

print(f"[+] stream written!")