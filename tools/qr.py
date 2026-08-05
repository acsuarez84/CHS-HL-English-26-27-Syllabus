"""A small QR encoder — byte mode, versions 1–10, EC levels L/M/Q/H."""
import struct, zlib

# ---- Galois field ------------------------------------------------------
EXP = [0] * 512
LOG = [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def gmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def gen_poly(n):
    p = [1]
    for i in range(n):
        p = poly_mul(p, [1, EXP[i]])
    return p


def poly_mul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, av in enumerate(a):
        for j, bv in enumerate(b):
            r[i + j] ^= gmul(av, bv)
    return r


def rs_encode(data, nsym):
    gen = gen_poly(nsym)
    res = list(data) + [0] * nsym
    for i in range(len(data)):
        c = res[i]
        if c:
            for j in range(1, len(gen)):
                res[i + j] ^= gmul(gen[j], c)
    return res[len(data):]


# ---- capacity / block tables (versions 1–10) ---------------------------
# version: {ec: (total_codewords_per_block_info)}
# (ec_codewords_per_block, num_blocks_g1, data_cw_g1, num_blocks_g2, data_cw_g2)
BLOCKS = {
 1:  {"L": (7, 1, 19, 0, 0),  "M": (10, 1, 16, 0, 0), "Q": (13, 1, 13, 0, 0), "H": (17, 1, 9, 0, 0)},
 2:  {"L": (10, 1, 34, 0, 0), "M": (16, 1, 28, 0, 0), "Q": (22, 1, 22, 0, 0), "H": (28, 1, 16, 0, 0)},
 3:  {"L": (15, 1, 55, 0, 0), "M": (26, 1, 44, 0, 0), "Q": (18, 2, 17, 0, 0), "H": (22, 2, 13, 0, 0)},
 4:  {"L": (20, 1, 80, 0, 0), "M": (18, 2, 32, 0, 0), "Q": (26, 2, 24, 0, 0), "H": (16, 4, 9, 0, 0)},
 5:  {"L": (26, 1, 108, 0, 0), "M": (24, 2, 43, 0, 0), "Q": (18, 2, 15, 2, 16), "H": (22, 2, 11, 2, 12)},
 6:  {"L": (18, 2, 68, 0, 0), "M": (16, 4, 27, 0, 0), "Q": (24, 4, 19, 0, 0), "H": (28, 4, 15, 0, 0)},
 7:  {"L": (20, 2, 78, 0, 0), "M": (18, 4, 31, 0, 0), "Q": (18, 2, 14, 4, 15), "H": (26, 4, 13, 1, 14)},
 8:  {"L": (24, 2, 97, 0, 0), "M": (22, 2, 38, 2, 39), "Q": (22, 4, 18, 2, 19), "H": (26, 4, 14, 2, 15)},
 9:  {"L": (30, 2, 116, 0, 0), "M": (22, 3, 36, 2, 37), "Q": (20, 4, 16, 4, 17), "H": (24, 4, 12, 4, 13)},
 10: {"L": (18, 2, 68, 2, 69), "M": (26, 4, 43, 1, 44), "Q": (24, 6, 19, 2, 20), "H": (28, 6, 15, 2, 16)},
}

ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
         6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}

ECBITS = {"L": 0b01, "M": 0b00, "Q": 0b11, "H": 0b10}


def capacity(ver, ec):
    e, b1, d1, b2, d2 = BLOCKS[ver][ec]
    return b1 * d1 + b2 * d2


def choose_version(n, ec):
    for v in range(1, 11):
        cc = 8 if v < 10 else 16
        if capacity(v, ec) * 8 >= 4 + cc + n * 8:
            return v
    raise ValueError("data too long for versions 1–10")


def encode_data(text, ver, ec):
    data = text.encode("utf-8")
    cc = 8 if ver < 10 else 16
    bits = []

    def put(val, n):
        for i in range(n - 1, -1, -1):
            bits.append((val >> i) & 1)

    put(0b0100, 4)              # byte mode
    put(len(data), cc)
    for b in data:
        put(b, 8)
    total = capacity(ver, ec) * 8
    put(0, min(4, total - len(bits)))          # terminator
    while len(bits) % 8:
        bits.append(0)
    pad = [0xEC, 0x11]
    i = 0
    while len(bits) < total:
        put(pad[i % 2], 8)
        i += 1
    cws = [int("".join(str(b) for b in bits[i:i + 8]), 2)
           for i in range(0, len(bits), 8)]

    # split into blocks, add EC
    e, b1, d1, b2, d2 = BLOCKS[ver][ec]
    blocks, ecs, p = [], [], 0
    for _ in range(b1):
        blocks.append(cws[p:p + d1]); p += d1
    for _ in range(b2):
        blocks.append(cws[p:p + d2]); p += d2
    for blk in blocks:
        ecs.append(rs_encode(blk, e))
    out = []
    for i in range(max(len(b) for b in blocks)):
        for b in blocks:
            if i < len(b):
                out.append(b[i])
    for i in range(e):
        for b in ecs:
            out.append(b[i])
    return out


def build(text, ec="M"):
    n = len(text.encode("utf-8"))
    ver = choose_version(n, ec)
    size = ver * 4 + 17
    m = [[None] * size for _ in range(size)]
    res = [[False] * size for _ in range(size)]

    def finder(r, c):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                rr, cc = r + dr, c + dc
                if 0 <= rr < size and 0 <= cc < size:
                    inner = (0 <= dr <= 6 and 0 <= dc <= 6)
                    v = False
                    if inner:
                        v = (dr in (0, 6) or dc in (0, 6) or
                             (2 <= dr <= 4 and 2 <= dc <= 4))
                    m[rr][cc] = v
                    res[rr][cc] = True

    finder(0, 0); finder(0, size - 7); finder(size - 7, 0)

    for i in range(8, size - 8):                       # timing
        v = (i % 2 == 0)
        m[6][i] = v; res[6][i] = True
        m[i][6] = v; res[i][6] = True

    for r in ALIGN[ver]:                               # alignment
        for c in ALIGN[ver]:
            if res[r][c]:
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    m[r + dr][c + dc] = (abs(dr) == 2 or abs(dc) == 2 or
                                         (dr == 0 and dc == 0))
                    res[r + dr][c + dc] = True

    m[size - 8][8] = True; res[size - 8][8] = True     # dark module
    for i in range(9):                                  # reserve format
        for (r, c) in ((8, i), (i, 8)):
            if 0 <= r < size and 0 <= c < size and not res[r][c]:
                res[r][c] = True; m[r][c] = False
    for i in range(8):
        for (r, c) in ((8, size - 1 - i), (size - 1 - i, 8)):
            if not res[r][c]:
                res[r][c] = True; m[r][c] = False

    cws = encode_data(text, ver, ec)
    bits = []
    for cw in cws:
        for i in range(7, -1, -1):
            bits.append((cw >> i) & 1)

    idx, up = 0, True
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if up else range(size)
        for r in rows:
            for c in (col, col - 1):
                if not res[r][c]:
                    m[r][c] = bool(bits[idx]) if idx < len(bits) else False
                    idx += 1
        up = not up
        col -= 2

    def mask_fn(k):
        return [lambda r, c: (r + c) % 2 == 0,
                lambda r, c: r % 2 == 0,
                lambda r, c: c % 3 == 0,
                lambda r, c: (r + c) % 3 == 0,
                lambda r, c: (r // 2 + c // 3) % 2 == 0,
                lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
                lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
                lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0][k]

    def penalty(g):
        p = 0
        for line in list(g) + list(map(list, zip(*g))):
            run, prev = 1, line[0]
            for v in line[1:]:
                if v == prev:
                    run += 1
                else:
                    if run >= 5: p += 3 + (run - 5)
                    run, prev = 1, v
            if run >= 5: p += 3 + (run - 5)
        for r in range(size - 1):
            for c in range(size - 1):
                if g[r][c] == g[r][c+1] == g[r+1][c] == g[r+1][c+1]:
                    p += 3
        dark = sum(sum(1 for v in row if v) for row in g)
        p += 10 * (abs(dark * 100 // (size * size) - 50) // 5)
        return p

    best, best_grid, best_k = None, None, 0
    for k in range(8):
        g = [[bool(m[r][c]) ^ (mask_fn(k)(r, c) and not res[r][c])
              for c in range(size)] for r in range(size)]
        fmt = (ECBITS[ec] << 3) | k
        d = fmt << 10
        for _ in range(5):
            if d >> 14:
                d ^= 0x537 << (d.bit_length() - 11)
        fbits = ((fmt << 10) | d) ^ 0x5412
        for i in range(15):
            b = bool((fbits >> i) & 1)
            if i < 6:   g[8][i] = b
            elif i == 6: g[8][7] = b
            elif i == 7: g[8][8] = b
            elif i == 8: g[7][8] = b
            else:        g[14 - i][8] = b
            if i < 8:    g[size - 1 - i][8] = b
            else:        g[8][size - 15 + i] = b
        g[size - 8][8] = True
        p = penalty(g)
        if best is None or p < best:
            best, best_grid, best_k = p, g, k
    return best_grid, ver, best_k


def to_png(grid, path, scale=10, quiet=4):
    n = len(grid)
    w = (n + quiet * 2) * scale
    rows = []
    for y in range(w):
        gy = y // scale - quiet
        row = bytearray([0])
        for x in range(w):
            gx = x // scale - quiet
            dark = (0 <= gy < n and 0 <= gx < n and grid[gy][gx])
            row += bytes([0, 0, 0] if dark else [255, 255, 255])
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(t, d):
        return (struct.pack(">I", len(d)) + t + d +
                struct.pack(">I", zlib.crc32(t + d) & 0xffffffff))
    png = (b"\x89PNG\r\n\x1a\n" +
           chunk(b"IHDR", struct.pack(">IIBBBBB", w, w, 8, 2, 0, 0, 0)) +
           chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(png)
    return w


def to_text(grid):
    out = []
    for r in range(0, len(grid), 2):
        line = ""
        for c in range(len(grid)):
            t = grid[r][c]
            b = grid[r + 1][c] if r + 1 < len(grid) else False
            line += "█" if t and b else "▀" if t else "▄" if b else " "
        out.append(line)
    return "\n".join(out)
