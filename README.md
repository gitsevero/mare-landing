# Maré — landing page de perfume

Landing page de uma marca fictícia de perfume: abertura em faixas, frasco 3D (Three.js) que gira com a rolagem, grade de destaques, carrossel horizontal preso à rolagem e letreiro correndo. É um arquivo HTML só, sem build e sem dependência instalada.

## Rodar

```bash
python3 -m http.server 8000
```

Abra http://localhost:8000.

## Como funciona

- Toda a animação sai de uma função, `tick(t, scrollY)`, chamada a cada quadro; nada depende de transição de CSS.
- O frasco é montado em código (vidro, líquido, rótulo e tampa) e desenhado num `<canvas>` fixo atrás do texto. As fotos da coleção são o mesmo frasco renderizado em outras cores quando a página carrega.

## Créditos

- [Three.js](https://threejs.org) (MIT), carregado do jsDelivr.
- Fontes Fraunces e Manrope (SIL Open Font License), do Google Fonts.
- Maré é uma marca fictícia, criada só para esta demonstração.

## Licença

MIT. Veja [LICENSE](LICENSE).
