# Registro de testes — 10/11/2026

## Ambiente efetivamente utilizado

Linux, Python 3.12.14, Pygame 2.6.1, SDL 2.28.4, PyOpenGL 3.1.10, NumPy 2.3.5. Contexto **OpenGL 4.5 Core / Mesa 25.0.7**, renderer **llvmpipe (LLVM 19.1.7, 256 bits)**. Renderização real por software, sem GPU física e sem interface no computador do aluno. Para SDL offscreen, foi necessário selecionar a plataforma EGL do PyOpenGL.

A instalação também foi repetida em um ambiente virtual limpo, seguida dos mesmos testes de lógica, sintaxe e renderização, com os mesmos resultados.

## Resultado reproduzível

| Verificação | Resultado | Evidência |
|---|---|---|
| Sintaxe Python | PASSOU | `python -m compileall -q core geometry models rendering scene tools tests main.py` |
| Máquina de estados/câmera | PASSOU, 7 testes | `python -m unittest discover -s tests -v` |
| Avanço equivalente a 20/30/60/144 FPS | PASSOU | Mesmo estado, pose e ciclos após 82 s simulados |
| Pausa, retomada, câmera durante pausa | PASSOU na lógica | Missão congelada por 120 updates; câmera desloca e gira |
| Orientação por mouse | PASSOU na lógica | Controlador muda direção com deslocamento simulado |
| Dois ciclos gráficos completos | PASSOU | 142 quadros renderizados com passo simulado de 0,5 s |
| Shaders / link / FBO | PASSOU | Instanciados e usados em OpenGL real; FBO completo |
| Depth map válido | PASSOU | Mínimo 0,2905836403; máximo 1,0 |
| Depth map dinâmico | PASSOU | Até 9.221 pixels de profundidade alterados entre quadros |
| Efeito da sombra na imagem | PASSOU | 32.359 pixels com diferença > 5 ao alternar sombra, na amostra de 960×540 |
| Alinhamento de coleta | PASSOU | Centro da carga coincide com (0,38; 0,52; 0,05), tolerância 1e−5 |
| Rocha acompanha a caçamba | PASSOU | Matriz mundial altera posição durante transporte |
| Capturas reais / inspeção visual | PASSOU | Explorando, coletando, transportando e passagem; amostra preservada em `evidencias/cena.jpg` |
| Erros OpenGL | PASSOU | `GL_NO_ERROR` em todos os quadros verificados |
| Janela, GPU, mouse e teclado físicos no Windows do aluno | NÃO TESTADO | Exige execução no computador de apresentação |
| Desempenho em hardware do aluno | NÃO TESTADO | Não há promessa de FPS |

Os números são do ambiente/resolução citados, não medições universais. O JSON bruto está em `docs/evidencias/resultado.json`.

## Executar a verificação

Windows, depois de instalar as dependências:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools\verify_graphics.py
```

A verificação gráfica cria uma janela, executa quadros acelerados e salva capturas/JSON em `capturas/verificacao`. Esse teste não tem duração real de 71 segundos: usa passo de 0,5 s para cobrir estados mais rapidamente.

Linux sem display, no ambiente utilizado:

```bash
PYOPENGL_PLATFORM=egl SDL_VIDEODRIVER=offscreen SDL_AUDIODRIVER=dummy python tools/verify_graphics.py
```

Não configure `SDL_VIDEODRIVER=dummy`: esse driver não oferece contexto OpenGL. No Windows normal não use as variáveis EGL/offscreen.

## Roteiro manual obrigatório antes da apresentação

1. Inicie `main.py`; confira ambos os veículos e o chão texturizado.
2. Observe um ciclo: rover para e sinaliza, escavadeira aproxima, coleta, deposita e recua; só então o rover retoma. Aguarde outra repetição.
3. Pause no meio da coleta. Confira que modelos ficam parados, mas WASD, setas, Q/E e mouse continuam funcionando. Solte o botão direito e confirme que o cursor fica livre.
4. Retome; reinicie com R; restaure a câmera com C.
5. Compare sombras usando L. As faces continuam respondendo à luz sem sombra projetada; ao ativar L novamente a sombra deve acompanhar a posição atual.
6. Aproxime a câmera da caçamba e do painel solar; confira UV, textura e ausência de auto-sombra excessiva. Se necessário reduza o mapa com `--shadow-size 1024`.
7. Use H, F12 e Esc; confira o PNG salvo em `capturas`.
8. Registre versão de Python, placa/driver, erros e conclusão desse teste. Não marque como executado antes de fazê-lo.

## Limites conhecidos

Cena demonstrativa com trajetórias programadas. Não há colisão, transparência de vidro, sombras em cascata, bloom, bump mapping ou luz pontual. O mapa usa frustum fixo adequado ao terreno; detalhes finos podem apresentar aliasing. A deposição é simbólica e a rocha repousa em altura definida; não é simulação física. A janela não possui modo de redimensionamento.

A aceitação do subconjunto didático da disciplina como framework do livro depende de confirmação docente. O teste comprova execução, não essa decisão acadêmica.
