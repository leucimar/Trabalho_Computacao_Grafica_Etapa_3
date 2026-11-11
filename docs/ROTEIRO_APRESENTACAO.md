# Roteiro de apresentação — 10 minutos

Antes de começar: teste no Windows com antecedência, abra `main.py` e deixe os arquivos de shader disponíveis no editor. Use `C` para recuperar a câmera, `R` para iniciar a missão e `H` para alternar a ajuda. Não precisa esperar mais de um ciclo de 35 segundos para mostrar a ação completa.

## 0:00–1:00 — Proposta

“Meu trabalho individual autorizado combina os temas 15, escavadeira de brinquedo, e 18, rover explorador. A cena é um terreno de testes: o rover encontra uma obstrução, solicita apoio e aguarda a escavadeira liberar o caminho. Depois retoma a exploração.”

Mostre ambos na tela e o título da missão. Informe o auxílio de ChatGPT Work/Codex em implementação e documentação, com revisão e responsabilidade acadêmicas do aluno. Não atribua a si os componentes externos do professor.

## 1:00–2:30 — Formas e hierarquia

Pause com Espaço e aproxime a câmera. Mostre caixas, cilindros, rodas, sensor e caçamba aberta. Abra `models/excavator.py` e indique os pivôs `shoulder`, `elbow` e `bucket`. Explique que a matriz mundial do filho inclui a do pai. A torre gira levando todo o braço; o cotovelo gira levando a caçamba.

A escala está nas malhas finais. O código combina translação, rotação e escala; não usa modelos 3D prontos baixados.

## 2:30–4:30 — Ação conjunta e tempo

Retome e use `R`. Aponte o estado exibido no topo. Mostre `State`, `DURATIONS` e `Mission.update` em `scene/animation.py`. O rover só volta a andar no estado `ROVER_RESUMES`, depois de `EXCAVATOR_CLEAR`. A base da escavadeira só avança após o pedido.

Explique: `dt` vem de `pygame.time.Clock.tick / 1000`. As durações são em segundos. Tempo que sobra ao terminar um estado passa para o seguinte. A rocha segue a matriz da caçamba durante a coleta. O alcance é geométrico, sem simulação física.

## 4:30–5:30 — Câmera e pausa

Durante a pausa, mova com WASD e oriente com as setas. Demonstre o botão direito do mouse. Use `C` para restaurar o enquadramento. Explique que câmera e renderização recebem atualizações mesmo quando o relógio da missão está pausado.

## 5:30–7:00 — Imagens, normais e luz

Aproxime o chão e o painel solar. Mostre os PNGs em `assets/textures`, a UV e `uvRepeat` no shader. As superfícies têm normais; a inversa transposta da matriz model mantém a normal correta quando há escala não uniforme.

A luz direcional usa raios paralelos. `dot(normal, light)` determina o difuso; um termo ambiente evita preto total. O sinalizador altera cor e emissão local. A cena HDR alimenta a extração e o desfoque de brilho para produzir bloom (F1). Demonstre também o bump nas superfícies (F2), tone mapping/gama (F3) e o painel de métricas (F4). GPU sem fonte disponível aparece como N/D.

## 7:00–8:30 — Sombra projetada

Pressione L para mostrar a diferença com/sem sombra. A iluminação das faces continua ativa. Abra `Renderer.draw`: primeira passagem renderiza profundidade vista pela luz; segunda renderiza a câmera e compara com a textura.

Mostre `depth.vert`, `depth.frag`, `scene.vert` e `scene.frag:shadowVisibility`. Explique bias, mapa 2048² e PCF 3×3. A matriz mundial atualizada alimenta as duas passagens; por isso a sombra acompanha os modelos. Não há círculo preto ou decalque.

## 8:30–10:00 — Evidências e perguntas

Mostre `docs/evidencias/resultado.json` e o registro dos testes. Informe que os testes de desenvolvimento foram em Linux/Mesa por software. Só declare testes no Windows que você realmente fez. Mostre a atribuição dos componentes da disciplina e a ressalva sobre a confirmação docente de sua aceitação como framework do livro.

### Respostas curtas para treinar

- **Por que dt?** Para medir o avanço em segundos em vez de depender do número de quadros.
- **O que é hierarquia?** Um filho herda a transformação mundial do pai, mantendo sua transformação local.
- **Shading × shadow?** Aparência iluminada da superfície × oclusão da luz por outra superfície.
- **Onde estão os shaders?** Em `shaders/`; scene ilumina, depth grava profundidade e hud desenha a legenda.
- **Attributes?** `vertexPosition`, `vertexNormal` e `vertexUV`; o HUD tem `position` e `texcoord`.
- **Uniforms principais?** `modelMatrix`, `viewMatrix`, `projectionMatrix`, `lightSpaceMatrix`, `colorTexture`, `shadowMap`, `baseColor` e `lightDirection`.
- **Como a sombra acompanha o braço?** O mapa de profundidade é refeito com as matrizes mundiais atuais das articulações.
- **Por que não há física?** O enunciado permite uma sequência coordenada e não exige colisão ou simulação física.
- **Qual framework?** Subconjunto didático do professor, que segue o livro; sua origem está documentada. Não o apresente como pacote oficial integral.
- **Por que a normal usa inversa transposta?** Para continuar perpendicular à superfície após a escala não uniforme.
- **Por que ortográfica para a luz?** A luz direcional tem raios paralelos; sua projeção não precisa de perspectiva.
- **O que o bias faz?** Evita auto-sombreamento numérico; valores excessivos descolam a sombra.

Não decore nomes sem abrir os arquivos. Consiga apontar um atributo, uma matriz, uma textura, o estado que libera o rover e as duas passagens da sombra no código real.
