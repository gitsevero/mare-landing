# Maré — landing page de perfume

[![Prévia do vídeo](assets/preview.jpg)](assets/mare-notebook.mp4)

Landing page de uma marca fictícia de perfume: abertura em faixas, frasco 3D (Three.js) que gira com a rolagem, grade de destaques, carrossel horizontal preso à rolagem e letreiro correndo. É um arquivo HTML só, sem build e sem dependência instalada.

**Ao vivo:** https://gitsevero.github.io/mare-landing/

## Rodar

```bash
python3 -m http.server 8000
```

Abra http://localhost:8000.

## Como funciona

- Toda a animação sai de uma função, `tick(t, scrollY)`, chamada a cada quadro. Nada usa transição de CSS, então o mesmo tempo e a mesma rolagem sempre dão o mesmo quadro.
- O frasco é montado em código (vidro, líquido, rótulo e tampa) e desenhado num `<canvas>` fixo atrás do texto. As fotos da coleção são o mesmo frasco renderizado em outras cores quando a página carrega.
- Com `?rec=1`, a página não roda sozinha e expõe `window.__frame(t, y)`. É assim que o vídeo é gravado quadro a quadro, sem engasgo.

## Gravar o vídeo no notebook

Precisa de Node, Python 3 (Pillow e numpy) e ffmpeg.

```bash
npm install
npx playwright install chromium
python3 -m http.server 8000      # em outro terminal
npm run gravar                    # 900 quadros em video/frames
python3 video/compor.py video assets/mare-notebook.mp4
```

`compor.py` acha a tela verde da foto `assets/notebook-tela-verde.png` e encaixa cada quadro nela com perspectiva. Para usar outra foto, basta a tela estar em verde puro; ajuste o recorte (`cx`, `cy`, `cw`) no começo do script.

## Créditos

- [Three.js](https://threejs.org) (MIT), carregado do jsDelivr.
- Fontes Fraunces e Manrope (SIL Open Font License), do Google Fonts.
- Maré é uma marca fictícia, criada só para esta demonstração.

## Licença

MIT. Veja [LICENSE](LICENSE).
