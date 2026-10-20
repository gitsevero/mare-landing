# Põe os quadros do site na tela verde do notebook e codifica o MP4.
# Uso:
#   python3 video/compor.py teste video/frames/0180.png teste.png   (um quadro, para conferir)
#   python3 video/compor.py video assets/mare-notebook.mp4          (o vídeo inteiro)
# Precisa de Pillow, numpy e ffmpeg no PATH.
import sys, subprocess, glob, os, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTO = os.path.join(AQUI, '..', 'assets', 'notebook-tela-verde.png')
FRAMES = os.path.join(AQUI, 'frames')
W, H = 1920, 1080

src = Image.open(FOTO).convert('RGB')
# recorte 16:9 em volta do notebook, para a tela ficar maior no quadro (ajuste ao trocar a foto)
cx, cy, cw = 660, 372, 1090
ch = cw * 9 / 16
bg = src.crop((cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)).resize((W, H), Image.LANCZOS)
bg = bg.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
a = np.asarray(bg).astype(np.float32)

# máscara da tela: quanto o verde passa do maior entre vermelho e azul
gex = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
ys, xs = np.nonzero(gex > 90)
s, d = xs + ys, xs - ys
cantos = np.array([[xs[s.argmin()], ys[s.argmin()]], [xs[d.argmax()], ys[d.argmax()]],
                   [xs[s.argmax()], ys[s.argmax()]], [xs[d.argmin()], ys[d.argmin()]]], dtype=np.float64)
# 7 px para fora: a borda do verde não é reta e a franja antialiasada passa dos cantos
c0 = cantos.mean(0); quad = c0 + (cantos - c0) * (1 + 7 / np.linalg.norm(cantos - c0, axis=1, keepdims=True))

poli = Image.new('L', (W, H), 0); ImageDraw.Draw(poli).polygon([tuple(p) for p in quad], fill=255)
poli = np.asarray(poli).astype(np.float32) / 255
m = (np.clip((gex - 6) / 34, 0, 1) * poli)[..., None]
# tira o verde que vazou na moldura e o reflexo da tela no teclado (a planta fica como está)
desp = a.copy(); desp[..., 1] = np.minimum(a[..., 1], np.maximum(a[..., 0], a[..., 2]) + 6)
faixa = np.asarray(Image.fromarray((poli * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))[..., None] > 0
planta = np.zeros((H, W, 1), bool); planta[440:, :430] = True
base = np.where(faixa | ~planta, desp, a)

qw = int(np.linalg.norm(quad[1] - quad[0])); qh = int(np.linalg.norm(quad[3] - quad[0]))
def coef(dst, srcp):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, srcp):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A), np.array(B)).tolist()
K = coef(quad, [(0, 0), (qw, 0), (qw, qh), (0, qh)])

def quadro(path):
    site = Image.open(path).convert('RGB').resize((qw, qh), Image.LANCZOS)
    w = np.asarray(site.transform((W, H), Image.PERSPECTIVE, K, Image.BICUBIC)).astype(np.float32)
    return (base * (1 - m) + w * m).clip(0, 255).astype(np.uint8)

if sys.argv[1] == 'teste':
    Image.fromarray(quadro(sys.argv[2])).save(sys.argv[3]); sys.exit()

frames = sorted(glob.glob(os.path.join(FRAMES, '*.png')))
ff = subprocess.Popen([shutil.which('ffmpeg'), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', sys.argv[2]], stdin=subprocess.PIPE)
for i, f in enumerate(frames):
    ff.stdin.write(quadro(f).tobytes())
    if i % 150 == 0: print(i, '/', len(frames), flush=True)
ff.stdin.close(); ff.wait(); print('ok', ff.returncode)
