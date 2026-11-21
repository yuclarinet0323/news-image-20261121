# News image entry: "The World Today - Saturday 21 November 2026"
# Python 3.13, standard library only. Draws a newspaper front page that sums
# up the world news of 21 November 2026 and writes it to /output/entry.png
# (or $MAKEFUN_OUTPUT_DIR/entry.png). Fully deterministic: no clocks, no
# randomness, no network, no files read. The PNG is encoded by hand
# (zlib + struct) and all text uses a bitmap font defined below.
#
# Stories (all reported on 21 Nov 2026):
#   LEAD  Russia fired 400+ drones and 110 missiles at Ukraine overnight;
#         two missiles and a suspected drone came down in Poland. NATO
#         called it a grave violation; PM Tusk called it a provocation.
#   1     Trump, Xi and Putin held a first three-way summit in Shenzhen;
#         Trump defended his ties to both at a 90-minute press conference.
#   2     The ICJ found Myanmar responsible for genocide against the
#         Rohingya - the first time it has held a state responsible.
#   3     An AI-sector sell-off pushed the S&P 500 down 3.7% into
#         correction, days after Anthropic's record IPO debut.
#   4     US-Iran talks stalled as Hormuz attacks continued; a Saudi-led
#         coalition intercepted Houthi missiles aimed at Riyadh.
#   5     COP31 in Antalya ran into overtime, deadlocked over fossil fuels.
#   Ticker: pancreatic-cancer pill daraxonrasib trial breakthrough;
#         BepiColombo reached Mercury orbit after eight years;
#         a magnitude 6.7 earthquake shook central Peru;
#         the UK and EU signed post-Brexit reset agreements.

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- canvas ---
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err, x, y = dx - dy, x0, y0
    while True:
        for a in range(t):
            for b in range(t):
                px(x + a, y + b, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
            if r - t <= d <= r:
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    lo_x, hi_x = min(x0, x1, x2), max(x0, x1, x2)
    lo_y, hi_y = min(y0, y1, y2), max(y0, y1, y2)
    for yy in range(lo_y, hi_y + 1):
        for xx in range(lo_x, hi_x + 1):
            d1 = (xx - x1) * (y0 - y1) - (x0 - x1) * (yy - y1)
            d2 = (xx - x2) * (y1 - y2) - (x1 - x2) * (yy - y2)
            d3 = (xx - x0) * (y2 - y0) - (x2 - x0) * (yy - y0)
            if (d1 >= 0 and d2 >= 0 and d3 >= 0) or (d1 <= 0 and d2 <= 0 and d3 <= 0):
                px(xx, yy, c)


# ------------------------------------------------------------------ font ---
# 5x7 bitmap font, one glyph = 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "00100", "01000"),
    ":": ("00000", "00000", "00100", "00000", "00000", "00100", "00000"),
    ";": ("00000", "00000", "00100", "00000", "00000", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def text_w(s, scale, bold=False):
    adv = 6 * scale
    return len(s) * adv - scale


def draw_text(x, y, s, scale, c, bold=False):
    adv = 6 * scale
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            for col in range(5):
                if g[r][col] == "1":
                    wdt = scale + (scale if bold else 0)
                    rect(cx + col * scale, y + r * scale, wdt, scale, c)
        cx += adv
    return cx


def centered(y, s, scale, c, bold=False):
    draw_text((W - text_w(s, scale, bold)) // 2, y, s, scale, c, bold)


# ---------------------------------------------------------------- colors ---
PAPER = (247, 243, 233)
INK = (18, 26, 38)
NAVY = (13, 30, 54)
RED = (178, 30, 38)
GOLD = (238, 190, 60)
WHITE = (255, 255, 255)
GREY = (92, 102, 116)
LIGHT = (233, 226, 208)
SKY = (16, 28, 52)
ORANGE = (240, 130, 40)
YELLOW = (250, 205, 80)
TEAL = (20, 110, 105)
GREEN = (38, 120, 62)
PURPLE = (92, 58, 140)
BROWN = (140, 84, 30)

rect(0, 0, W, H, PAPER)

# -------------------------------------------------------------- masthead ---
rect(0, 0, W, 106, NAVY)
centered(16, "THE WORLD TODAY", 10, WHITE, bold=True)
rect(0, 106, W, 36, RED)
draw_text(28, 114, "SATURDAY", 3, WHITE, bold=True)
draw_text(250, 114, "21 NOVEMBER 2026", 3, GOLD, bold=True)
draw_text(620, 114, "ONE DAY, ONE PICTURE", 3, WHITE)

# ------------------------------------------------------------- lead art ----
rect(28, 154, 968, 140, SKY)
# stars / drones
for (sx, sy) in [(80, 176), (200, 168), (330, 184), (470, 170), (610, 180),
                 (760, 168), (900, 186), (140, 200), (540, 196), (840, 204)]:
    rect(sx, sy, 4, 4, WHITE)
# missile + drone streaks
line(120, 272, 420, 182, ORANGE, 4)
line(120, 280, 430, 197, YELLOW, 3)
line(300, 282, 560, 192, ORANGE, 4)
line(700, 278, 880, 206, ORANGE, 4)
line(690, 285, 872, 219, YELLOW, 3)
tri(420, 182, 398, 188, 416, 200, YELLOW)
tri(560, 192, 538, 198, 556, 210, YELLOW)
tri(880, 206, 858, 212, 876, 224, YELLOW)
# drone silhouette
rect(208, 220, 30, 6, WHITE)
rect(194, 213, 8, 4, WHITE)
rect(232, 213, 8, 4, WHITE)
rect(194, 229, 8, 4, WHITE)
rect(232, 229, 8, 4, WHITE)
# city skyline
for (bx, bh) in [(28, 44), (108, 62), (196, 36), (268, 74), (356, 48),
                 (436, 64), (524, 40), (596, 70), (684, 46), (764, 60),
                 (852, 42), (924, 54)]:
    rect(bx, 294 - bh, 72, bh, (6, 12, 24))
    for wy in range(294 - bh + 8, 286, 14):
        for wx in range(bx + 10, bx + 60, 18):
            rect(wx, wy, 7, 8, YELLOW)
# explosion glow
disc(486, 272, 22, ORANGE)
disc(486, 272, 12, YELLOW)
disc(760, 266, 15, ORANGE)
disc(760, 266, 8, YELLOW)
rect(28, 290, 968, 4, RED)
draw_text(44, 162, "KYIV - OVERNIGHT", 3, GOLD, bold=True)

# ----------------------------------------------------------- lead story ----
draw_text(28, 302, "LEAD STORY - EUROPE", 3, RED, bold=True)
draw_text(28, 332, "RUSSIA BOMBARDS UKRAINE;", 6, INK, bold=True)
draw_text(28, 386, "MISSILES LAND IN POLAND", 6, RED, bold=True)
draw_text(28, 442, "400+ DRONES AND 110 MISSILES POUNDED KYIV OVERNIGHT.", 3, INK)
draw_text(28, 468, "TWO MISSILES AND A DRONE CAME DOWN ON POLISH SOIL.", 3, INK)
draw_text(28, 494, "NATO: GRAVE VIOLATION. TUSK: DELIBERATE PROVOCATION.", 3, INK)
rect(28, 528, 968, 3, INK)

# ------------------------------------------------------------- story grid --
def panel(x, y, w, h, cat, cat_c, head, head_c, lines):
    rect(x, y, w, h, WHITE)
    rect(x, y, w, 3, cat_c)
    rect(x, y + 3, w, 3, LIGHT)
    draw_text(x + 14, y + 12, cat, 2, cat_c, bold=True)
    hy = y + 34
    for hl in head:
        draw_text(x + 14, hy, hl, 4, head_c, bold=True)
        hy += 34
    sy = hy + 4
    for ln in lines:
        draw_text(x + 14, sy, ln, 2, GREY)
        sy += 16


PW, PH = 474, 156
panel(28, 540, PW, PH, "DIPLOMACY - SHENZHEN", TEAL,
      ["TRUMP, XI & PUTIN", "HOLD 3-WAY SUMMIT"], INK,
      ["FIRST THREE-WAY MEETING OF THE", "US, CHINESE AND RUSSIAN LEADERS.", "TRUMP DEFENDS TIES TO BOTH MEN."])
panel(522, 540, PW, PH, "JUSTICE - THE HAGUE", PURPLE,
      ["UN COURT: MYANMAR", "GUILTY OF GENOCIDE"], INK,
      ["ICJ RULES ON THE ROHINGYA CASE:", "FIRST TIME A STATE IS HELD", "RESPONSIBLE. RETURN ORDERED."])
panel(28, 704, PW, PH, "MARKETS - NEW YORK", BROWN,
      ["AI STOCKS ROUT;", "S&P IN CORRECTION"], INK,
      ["S&P 500 FALLS 3.7% AS AI AND CHIP", "STOCKS SELL OFF; NASDAQ ERASES", "2026 GAINS AFTER ANTHROPIC IPO."])
panel(522, 704, PW, PH, "MIDDLE EAST - HORMUZ", RED,
      ["IRAN TALKS STALL;", "HORMUZ ATTACKS ON"], INK,
      ["TEHRAN WANTS DIPLOMACY; TRUMP", "CALLS ITS TERMS UNACCEPTABLE.", "SAUDIS DOWN HOUTHI MISSILES."])

# ------------------------------------------------------------ COP31 strip --
rect(28, 868, 968, 68, WHITE)
rect(28, 868, 968, 3, GREEN)
draw_text(42, 876, "CLIMATE - ANTALYA, TURKIYE", 2, GREEN, bold=True)
draw_text(42, 898, "COP31 TALKS RUN INTO OVERTIME", 3, INK, bold=True)
draw_text(580, 878, "NEARLY 200 NATIONS DEADLOCKED;", 2, GREY)
draw_text(580, 894, "DRAFT DEAL SILENT ON", 2, GREY)
draw_text(580, 910, "FOSSIL FUELS.", 2, GREY)

# ---------------------------------------------------------------- ticker ---
rect(0, 940, W, 84, NAVY)
draw_text(28, 950, "ALSO TODAY", 2, GOLD, bold=True)
draw_text(28, 972, "CANCER PILL: TUMOURS VANISH IN 1 IN 12 * MERCURY PROBE ARRIVES * PERU QUAKE 6.7", 2, WHITE)
draw_text(28, 996, "UK AND EU SIGN POST-BREXIT RESET DEALS * PALISADES ARSONIST CONVICTED IN LA", 2, WHITE)

# ------------------------------------------------------------------- png ---
def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
       + chunk(b"IEND", b""))

out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "entry.png"), "wb") as f:
    f.write(png)
