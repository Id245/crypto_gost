import argparse
from pathlib import Path

from GOST2012 import gost
from gostcrypto import gosthash


parser = argparse.ArgumentParser(description="Сравнение GOST2012.py и gostcrypto")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--text", help="Строка для сравнения")
group.add_argument("--file", type=Path, help="Файл для сравнения")
parser.add_argument("--size", type=int, choices=(256, 512), default=512)
args = parser.parse_args()

data = args.text.encode("utf-8") if args.text is not None else args.file.read_bytes()
algo = "streebog512" if args.size == 512 else "streebog256"

mine = gost(data, args.size).hex()
ref = gosthash.new(algo, data=data).hexdigest()

print(f"Mine     : {mine}")
print(f"Reference: {ref}")
print("OK" if mine == ref else "MISMATCH")
