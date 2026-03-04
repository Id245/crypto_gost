from pathlib import Path
import re
import sys

BLOCK_SIZE = 64  
ZERO_512 = bytes(BLOCK_SIZE)
BITS_512 = (512).to_bytes(BLOCK_SIZE, "big")

PI = (
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79,
    5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31,
    235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204,
    181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135,
    21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177,
    50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87,
    223, 245, 36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3,
    224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74,
    167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65,
    173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59,
    7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137,
    225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97,
    32, 113, 103, 164, 45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82,
    89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57, 75, 99, 182,
)

TAU = (
    0, 8, 16, 24, 32, 40, 48, 56,
    1, 9, 17, 25, 33, 41, 49, 57,
    2, 10, 18, 26, 34, 42, 50, 58,
    3, 11, 19, 27, 35, 43, 51, 59,
    4, 12, 20, 28, 36, 44, 52, 60,
    5, 13, 21, 29, 37, 45, 53, 61,
    6, 14, 22, 30, 38, 46, 54, 62,
    7, 15, 23, 31, 39, 47, 55, 63,
)

A = (
    0x8E20FAA72BA0B470, 0x47107DDD9B505A38, 0xAD08B0E0C3282D1C, 0xD8045870EF14980E,
    0x6C022C38F90A4C07, 0x3601161CF205268D, 0x1B8E0B0E798C13C8, 0x83478B07B2468764,
    0xA011D380818E8F40, 0x5086E740CE47C920, 0x2843FD2067ADEA10, 0x14AFF010BDD87508,
    0x0AD97808D06CB404, 0x05E23C0468365A02, 0x8C711E02341B2D01, 0x46B60F011A83988E,
    0x90DAB52A387AE76F, 0x486DD4151C3DFDB9, 0x24B86A840E90F0D2, 0x125C354207487869,
    0x092E94218D243CBA, 0x8A174A9EC8121E5D, 0x4585254F64090FA0, 0xACCC9CA9328A8950,
    0x9D4DF05D5F661451, 0xC0A878A0A1330AA6, 0x60543C50DE970553, 0x302A1E286FC58CA7,
    0x18150F14B9EC46DD, 0x0C84890AD27623E0, 0x0642CA05693B9F70, 0x0321658CBA93C138,
    0x86275DF09CE8AAA8, 0x439DA0784E745554, 0xAFC0503C273AA42A, 0xD960281E9D1D5215,
    0xE230140FC0802984, 0x71180A8960409A42, 0xB60C05CA30204D21, 0x5B068C651810A89E,
    0x456C34887A3805B9, 0xAC361A443D1C8CD2, 0x561B0D22900E4669, 0x2B838811480723BA,
    0x9BCF4486248D9F5D, 0xC3E9224312C8C1A0, 0xEFFA11AF0964EE50, 0xF97D86D98A327728,
    0xE4FA2054A80B329C, 0x727D102A548B194E, 0x39B008152ACB8227, 0x9258048415EB419D,
    0x492C024284FBAEC0, 0xAA16012142F35760, 0x550B8E9E21F7A530, 0xA48B474F9EF5DC18,
    0x70A6A56E2440598E, 0x3853DC371220A247, 0x1CA76E95091051AD, 0x0EDD37C48A08A6D8,
    0x07E095624504536C, 0x8D70C431AC02A736, 0xC83862965601DD1B, 0x641C314B2B8EE083,
)

C = (
    bytes.fromhex("b1085bda1ecadae9ebcb2f81c0657c1f2f6a76432e45d016714eb88d7585c4fc4b7ce09192676901a2422a08a460d31505767436cc744d23dd806559f2a64507"),
    bytes.fromhex("6fa3b58aa99d2f1a4fe39d460f70b5d7f3feea720a232b9861d55e0f16b501319ab5176b12d699585cb561c2db0aa7ca55dda21bd7cbcd56e679047021b19bb7"),
    bytes.fromhex("f574dcac2bce2fc70a39fc286a3d843506f15e5f529c1f8bf2ea7514b1297b7bd3e20fe490359eb1c1c93a376062db09c2b6f443867adb31991e96f50aba0ab2"),
    bytes.fromhex("ef1fdfb3e81566d2f948e1a05d71e4dd488e857e335c3c7d9d721cad685e353fa9d72c82ed03d675d8b71333935203be3453eaa193e837f1220cbebc84e3d12e"),
    bytes.fromhex("4bea6bacad4747999a3f410c6ca923637f151c1f1686104a359e35d7800fffbdbfcd1747253af5a3dfff00b723271a167a56a27ea9ea63f5601758fd7c6cfe57"),
    bytes.fromhex("ae4faeae1d3ad3d96fa4c33b7a3039c02d66c4f95142a46c187f9ab49af08ec6cffaa6b71c9ab7b40af21f66c2bec6b6bf71c57236904f35fa68407a46647d6e"),
    bytes.fromhex("f4c70e16eeaac5ec51ac86febf240954399ec6c7e6bf87c9d3473e33197a93c90992abc52d822c3706476983284a05043517454ca23c4af38886564d3a14d493"),
    bytes.fromhex("9b1f5b424d93c9a703e7aa020c6e41414eb7f8719c36de1e89b4443b4ddbc49af4892bcb929b069069d18d2bd1a5c42f36acc2355951a8d9a47f0dd4bf02e71e"),
    bytes.fromhex("378f5a541631229b944c9ad8ec165fde3a7d3a1b258942243cd955b7e00d0984800a440bdbb2ceb17b2b8a9aa6079c540e38dc92cb1f2a607261445183235adb"),
    bytes.fromhex("abbedea680056f52382ae548b2e4f3f38941e71cff8a78db1fffe18a1b3361039fe76702af69334b7a1e6c303b7652f43698fad1153bb6c374b4c7fb98459ced"),
    bytes.fromhex("7bcd9ed0efc889fb3002c6cd635afe94d8fa6bbbebab076120018021148466798a1d71efea48b9caefbacd1d7d476e98dea2594ac06fd85d6bcaa4cd81f32d1b"),
    bytes.fromhex("378ee767f11631bad21380b00449b17acda43c32bcdf1d77f82012d430219f9b5d80ef9d1891cc86e71da4aa88e12852faf417d5d9b21b9948bc924af11bd720"),
)

def input_processing(message: str) -> bytes:
    return message.encode("utf-8")


def bytes_xor(message1: bytes, message2: bytes) -> bytes:
    if len(message1) != len(message2):
        raise ValueError("Нужны блоки равной длины")
    return bytes(a ^ b for a, b in zip(message1, message2))


def add_mod_512(a: bytes, b: bytes) -> bytes:
    if len(a) != BLOCK_SIZE or len(b) != BLOCK_SIZE:
        raise ValueError("Оба аргумента должны иметь длину 64 байта")
    return ((int.from_bytes(a, "big") + int.from_bytes(b, "big")) & ((1 << 512) - 1)).to_bytes(BLOCK_SIZE, "big")


def s_transform(data: bytes) -> bytes:
    return bytes(PI[byte] for byte in data)


def p_transform(data: bytes) -> bytes:
    return bytes(data[index] for index in TAU)


def l_transform(data: bytes) -> bytes:
    if len(data) != BLOCK_SIZE:
        raise ValueError("Для L-преобразования нужен блок 64 байта")

    result = bytearray()
    for offset in range(0, BLOCK_SIZE, 8):
        value = int.from_bytes(data[offset:offset + 8], "big")
        mixed = 0
        for bit in range(64):
            if value & (1 << (63 - bit)):
                mixed ^= A[bit]
        result.extend(mixed.to_bytes(8, "big"))
    return bytes(result)


def lps(data: bytes) -> bytes:
    return l_transform(p_transform(s_transform(data)))


def e_transform(key: bytes, message_block: bytes) -> bytes:
    if len(key) != BLOCK_SIZE or len(message_block) != BLOCK_SIZE:
        raise ValueError("Ключ и блок должны иметь длину 64 байта")

    k = key
    state = message_block

    for const in C:
        state = lps(bytes_xor(state, k))
        k = lps(bytes_xor(k, const))

    return bytes_xor(state, k)


def g_n(h: bytes, message_block: bytes, n: bytes) -> bytes:
    key = lps(bytes_xor(h, n))
    encrypted = e_transform(key, message_block)
    return bytes_xor(bytes_xor(encrypted, h), message_block)


def _pad_last_block(tail: bytes) -> bytes:
    if len(tail) >= BLOCK_SIZE:
        raise ValueError("Хвост должен быть короче 64 байт")

    padded = bytearray(BLOCK_SIZE)
    start = BLOCK_SIZE - len(tail) - 1
    padded[start] = 1
    padded[start + 1:] = tail
    return bytes(padded)


def _gost_core(message: bytes, hash_size: int = 512) -> bytes:
    if hash_size not in (256, 512):
        raise ValueError("Неправильный тип (выберите 256 либо 512)")

    h = bytes([1] * BLOCK_SIZE) if hash_size == 256 else ZERO_512
    n = ZERO_512
    sigma = ZERO_512

    remaining = message

    while len(remaining) >= BLOCK_SIZE:
        block = remaining[-BLOCK_SIZE:]
        remaining = remaining[:-BLOCK_SIZE]
        h = g_n(h, block, n)
        n = add_mod_512(n, BITS_512)
        sigma = add_mod_512(sigma, block)

    last_block = _pad_last_block(remaining)
    h = g_n(h, last_block, n)
    n = add_mod_512(n, (len(remaining) * 8).to_bytes(BLOCK_SIZE, "big"))
    sigma = add_mod_512(sigma, last_block)

    h = g_n(h, n, ZERO_512)
    h = g_n(h, sigma, ZERO_512)

    return h[:32] if hash_size == 256 else h


def gost(message: bytes, hash_size: int = 512) -> bytes:
    # Нормализация ориентации байтов под эталон gostcrypto.
    return _gost_core(message[::-1], hash_size)[::-1]


def gost_hex(message: bytes | str, hash_size: int = 512) -> str:
    if isinstance(message, str):
        message = input_processing(message)
    return gost(message, hash_size).hex()


def initialization(message: bytes, type: int) -> bytes:
    return gost(message, type)


def _read_file_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Не удалось прочитать файл: {path}") from exc


def _extract_hex_digest(text: str, expected_len: int) -> str:
    cleaned = text.strip().lower()
    if re.fullmatch(rf"[0-9a-f]{{{expected_len}}}", cleaned):
        return cleaned

    matches = re.findall(r"[0-9a-fA-F]+", text)
    for token in matches:
        token = token.lower()
        if len(token) == expected_len and re.fullmatch(r"[0-9a-f]+", token):
            return token

    raise ValueError("В файле не найдено корректное хэш-значение")


def hash_file(input_path: Path, output_path: Path, hash_size: int) -> str:
    message = _read_file_bytes(input_path)
    digest_hex = gost_hex(message, hash_size)

    try:
        output_path.write_text(digest_hex + "\n", encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Не удалось записать файл: {output_path}") from exc

    return digest_hex


def verify_file(input_path: Path, hash_path: Path, hash_size: int) -> tuple[bool, str, str]:
    message = _read_file_bytes(input_path)
    computed = gost_hex(message, hash_size)

    try:
        expected_text = hash_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        expected_text = _read_file_bytes(hash_path).decode("latin-1", errors="ignore")
    except OSError as exc:
        raise RuntimeError(f"Не удалось прочитать файл с хэшем: {hash_path}") from exc

    expected = _extract_hex_digest(expected_text, 64 if hash_size == 256 else 128)
    return computed == expected, computed, expected


def _prompt_path(prompt: str, must_exist: bool = True) -> Path:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Путь не может быть пустым.")
            continue

        path = Path(raw).expanduser()
        if must_exist and not path.exists():
            print(f"Файл не найден: {path}")
            continue
        return path


def _prompt_hash_size(default: int = 512) -> int:
    while True:
        raw = input(f"Размер хэша [256/512], Enter={default}: ").strip()
        if not raw:
            return default
        if raw in {"256", "512"}:
            return int(raw)
        print("Некорректный размер. Введите 256 или 512.")


def _print_menu() -> None:
    print("\nМеню проверки ГОСТ Р 34.11-2012")
    print("1. Вычислить хэш строки")
    print("2. Вычислить хэш файла")
    print("3. Проверить файл по файлу с хэшем")
    print("0. Выход")


def _run_menu() -> int:
    while True:
        _print_menu()
        choice = input("Выберите пункт: ").strip()

        try:
            if choice == "1":
                message = input("Введите строку: ")
                hash_size = _prompt_hash_size()
                print(gost_hex(message, hash_size))
            elif choice == "2":
                input_path = _prompt_path("Путь к входному файлу: ", must_exist=True)
                output_path = _prompt_path("Путь к файлу для сохранения хэша: ", must_exist=False)
                hash_size = _prompt_hash_size()
                digest = hash_file(input_path, output_path, hash_size)
                print(f"Хэш ({hash_size}) записан в {output_path}")
                print(digest)
            elif choice == "3":
                input_path = _prompt_path("Путь к проверяемому файлу: ", must_exist=True)
                hash_path = _prompt_path("Путь к файлу с ожидаемым хэшем: ", must_exist=True)
                hash_size = _prompt_hash_size()
                ok, computed, expected = verify_file(input_path, hash_path, hash_size)
                print(f"Expected: {expected}")
                print(f"Computed: {computed}")
                print("OK" if ok else "MISMATCH")
            elif choice == "0":
                print("Выход.")
                return 0
            else:
                print("Неизвестный пункт меню.")
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"Ошибка: {exc}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nОперация прервана.")
        except EOFError:
            print("\nВыход.")
            return 0


if __name__ == "__main__":
    raise SystemExit(_run_menu())
