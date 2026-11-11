# Guia técnico — Operação Rover

## Pipeline e divisão de tarefas

Pygame cria janela, contexto, eventos, relógio e superfícies de texto. OpenGL rasteriza os modelos 3D e a legenda. A cena não é desenhada por `pygame.draw`: essas funções aparecem somente no painel 2D de ajuda, que é enviado como textura a um quad OpenGL.

Componentes usados do material da disciplina: `Object3D` organiza pais/filhos; `Matrix` fornece matrizes; `Geometry` armazena atributos; `Attribute` cria VBOs; `Mesh` cria VAOs e associa atributos ao programa; `Uniform` envia as matrizes à GPU. `BoxGeometry` constrói posições e UV de caixas. `LitBoxGeometry` adiciona normais a essas caixas; cilindros, cones truncados e rochas são extensões de `Geometry`.

O quadro segue a ordem: eventos → câmera com `dt` real → missão com `dt` quando não pausada → atualização de transformações → passagem de profundidade → cena iluminada em HDR → extração/desfoque de bloom → composição final → HUD → troca de buffers. Pausar evita só `Mission.update`; não interrompe eventos, câmera, renderização ou atualização do mapa.

## Transformações e hierarquia

Vetores-coluna: `clip = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition,1)`.

`modelMatrix` é a transformação mundial retornada por `Object3D.getWorldMatrix()`: matriz do pai multiplicada pela local do filho. `models/common.py:transform` compõe `T @ Ry @ Rx @ Rz @ S`. A escala fica normalmente nas malhas finais, para não aumentar involuntariamente o deslocamento dos pivôs filhos.

Escavadeira: raiz → torre → base do braço → ombro → cotovelo → caçamba → ponto de carga. Rover: raiz → pivô de roda → pneus/calotas; raiz → antena → sensor. As rodas giram em função do deslocamento dividido pelo raio. O sensor varre o ambiente em função do tempo acumulado.

A coleta usa cinemática inversa planar de dois segmentos em `scene/animation.py:pickup_angles`; é uma fórmula geométrica para alcançar a posição conhecida da rocha. Não há solver físico nem detecção de colisão. Durante o transporte, `Environment.animate` aplica à rocha a matriz mundial de `Excavator.load`, mantendo a composição real das articulações. Ao largar, a matriz final é calculada analiticamente mesmo se um `dt` grande saltar a coleta inteira.

## Máquina de estados e tempo

| Estado | Duração | Dependência |
|---|---:|---|
| ROVER_EXPLORING | 6 s | Aproxima o rover da área de atendimento |
| ROVER_DETECTED_BLOCKAGE | 2 s | Para e sinaliza; sensor se orienta para a escavadeira |
| EXCAVATOR_APPROACH | 4 s | Só começa após a solicitação |
| EXCAVATOR_WORKING | 10 s | Alcança, ergue, gira e deposita a rocha |
| EXCAVATOR_CLEAR | 4 s | Recolhe braço e retira base da área de trabalho |
| ROVER_RESUMES | 7 s | Só retoma depois da liberação |
| RESET | 2 s | Transição escura antes de restaurar a cena |

A função `smooth` interpola com `3t²−2t³`; velocidades começam e terminam suavemente. `Mission.update` retém tempo excedente ao passar de estado, inclusive se atravessar vários estados em um quadro. Uma tolerância de `1e-10` evita diferenças de estado em fronteiras de ponto flutuante. O teste compara os mesmos 82 segundos a 20, 30, 60 e 144 FPS simulados.

## Shaders e entradas reais

| Programa | Vertex shader | Fragment shader | Uso |
|---|---|---|---|
| Cena | `shaders/scene.vert` | `shaders/scene.frag` | Transformação, UV, luz local e comparação de sombra |
| Profundidade | `shaders/depth.vert` | `shaders/depth.frag` | Renderização do ponto de vista da luz, escrevendo a profundidade |
| Extração de brilho | `shaders/post.vert` | `shaders/extract.frag` | Pixels com algum canal HDR acima de 1,12 |
| Desfoque | `shaders/post.vert` | `shaders/blur.frag` | Seis passagens gaussianas alternando os eixos em meia resolução |
| Composição | `shaders/post.vert` | `shaders/compose.frag` | Bloom, exposição, tone mapping e gama |
| HUD | `shaders/hud.vert` | `shaders/hud.frag` | Texto, ajuda e transição escura |

`rendering/renderer.py:program` compila os shaders, verifica o link e fixa localizações compatíveis entre cena e profundidade. Os shaders usam **GLSL 330 core**.

| Attribute `in` | Localização | Tipo | Significado |
|---|---:|---|---|
| vertexPosition | 0 | vec3 | Posição local; cena e profundidade |
| vertexNormal | 1 | vec3 | Normal local; cena |
| vertexUV | 2 | vec2 | Coordenada da imagem; cena |
| position | 0 | vec2 | Posição do quad da legenda em NDC; HUD |
| texcoord | 1 | vec2 | UV da legenda; HUD |

Os atributos de cena são vinculados por `Attribute.associateVariable` dentro de `Mesh`; o shader de profundidade lê a mesma posição no mesmo VAO. O HUD possui seu próprio VAO/VBO. Uma normal por face plana evita suavizar os cantos das caixas; cilindros têm normais radiais nas laterais e ±Y nas tampas.

| Uniform | Tipo | Programa | Origem / finalidade |
|---|---|---|---|
| modelMatrix | mat4 | cena, profundidade | Matriz mundial de cada malha |
| viewMatrix | mat4 | cena | Inversa da pose da câmera, por `look_at` |
| projectionMatrix | mat4 | cena | Perspectiva de 48°, near 0,1 e far 120 |
| lightSpaceMatrix | mat4 | cena, profundidade | Projeção ortográfica × visão da luz |
| uvRepeat | vec2 | cena | Repetição de UV por malha |
| colorTexture | sampler2D | cena | Imagem PNG na unidade 0 |
| shadowMap | sampler2D | cena | Textura de profundidade na unidade 1 |
| baseColor | vec3 | cena | Cor do material multiplicada pela imagem |
| lightDirection | vec3 | cena | Direção normalizada em que a luz viaja |
| cameraPosition | vec3 | cena | Posição mundial para brilho e névoa suave |
| emission | float | cena | Termo aditivo local usado no sinalizador/faróis |
| shadowsEnabled | bool | cena | Comparação com/sem sombras pela tecla L |
| bumpEnabled / bumpStrength | bool / float | cena | Controle F2 e intensidade por malha |
| sourceTexture | sampler2D | pós-processamento | Cena HDR ou passagem anterior |
| bloomTexture | sampler2D | composição | Brilho desfocado na unidade 1 |
| useBloom / usePost | bool | composição | Controles F1 e F3 |
| exposure | float | composição | Exposição 1,10 |
| horizontal | bool | desfoque | Eixo do filtro gaussiano |
| hudTexture | sampler2D | HUD | Textura RGBA do painel na unidade 0 |
| fade | float | HUD | Opacidade da transição escura sobre o cenário |

Não há uniform `time`, `deltaTime`, `normalMatrix` ou luz pontual: o tempo altera matrizes na CPU e a matriz normal é calculada no vertex shader. Não se deve citar nomes inexistentes na apresentação.

## Texturas, luz e materiais

As quatro imagens são carregadas de `assets/textures` por Pygame e enviadas com `glTexImage2D`, mipmaps e `GL_REPEAT`. `sand.png` aparece no chão e no caminho; `solar.png` no painel do rover; `hazard.png` nas plataformas e na escavadeira; `white.png` mantém o mesmo pipeline nas peças de cor sólida. A imagem só é o resultado final da geração programática: ela é carregada como PNG real e amostrada com UV.

No vertex shader, `worldNormal = transpose(inverse(mat3(modelMatrix))) * vertexNormal`. Isso conserva a orientação correta da normal sob escala não uniforme. O fragment shader renormaliza a normal e calcula iluminação difusa de Lambert, um brilho Blinn–Phong discreto, termo ambiente e emissão local do sinalizador. A direção da luz é `normalize(-0.55,-1,-0.45)`. Não há luzes pontuais. A emissão alimenta a cena HDR; extração e desfoque dos pixels brilhantes em `PostProcess` produzem o halo de bloom. O bump mapping perturba as normais de areia e rochas por diferenças de altura da textura e de um padrão procedural, sem deslocar a geometria.

## Shadow mapping real em duas passagens

1. `Renderer.__init__` cria FBO com textura **GL_DEPTH_COMPONENT24**, por padrão 2048². Fixa draw/read buffers em `GL_NONE` e exige `GL_FRAMEBUFFER_COMPLETE`.
2. A luz direcional usa câmera ortográfica de −16 a +16 em X/Y, near 1 e far 60, vista de `-lightDirection * 26` para a origem. Raios paralelos combinam com a projeção ortográfica.
3. `Renderer.draw`, primeira passagem: viewport do mapa, limpeza do depth buffer, `depth.vert`, matriz mundial atual de cada objeto que projeta sombra e `glDrawArrays`. O fragment shader vazio usa a gravação de profundidade do pipeline; não existe decalque.
4. Segunda passagem: direciona a cena para o framebuffer HDR `GL_RGBA16F` com depth renderbuffer de 24 bits e viewport da janela. Cada fragmento usa sua posição no espaço da luz, divide por W e remapeia NDC de [−1,1] para [0,1].
5. `scene.frag:shadowVisibility` compara a profundidade atual, descontado o bias, com a profundidade da textura. Usa PCF de nove amostras. Fragmentos fora do frustum são tratados como iluminados; a borda da textura também é branca.
6. A sombra reduz iluminação difusa e brilho; a componente ambiente permanece. O mapa é renderizado novamente a cada quadro, acompanhando a torre, o braço, a rocha e os veículos.

Bias: `max(0.0012 * (1 − dot(normal, −lightDirection)), 0.00035)`, em coordenadas normalizadas de profundidade. Pouco bias causa *shadow acne*; muito bias descola a sombra (*peter panning*). A resolução e o frustum fixos favorecem esta pequena cena. Não há cascatas, luz móvel ou suporte a cenários ilimitados.

**Sombreamento local** calcula a aparência da superfície conforme normal, luz e material. **Sombra projetada** verifica se outro trecho da cena bloqueia a luz até a superfície. A tecla L desliga só a segunda operação: as superfícies continuam iluminadas e orientadas pela luz.

## Pós-processamento e métricas

`PostProcess.begin` aloca os framebuffers na primeira utilização ou quando a resolução muda. `end` extrai brilho, aplica três pares de desfoque e compõe no framebuffer 0. F1 controla bloom; F3 controla exposição, tone mapping e gama. O HUD é desenhado depois da composição. `--no-bloom`, `--no-bump` e `--no-post` definem os estados iniciais.

`PerformanceMonitor` coleta CPU pelo psutil e GPU pelo nvidia-smi ou contador de motor do Windows, em uma thread com consultas limitadas por timeout. A renderização apenas lê um snapshot protegido por lock. CPU mede o sistema inteiro; `GPU motor*` não é utilização global. Fonte indisponível aparece como N/D. F4 oculta o painel.

## Limites e comprovação

As capturas são renderizações reais. `tools/verify_graphics.py` verifica FBO, shaders compilados/linkados por execução, dois ciclos, mapa com profundidades válidas, mudanças no mapa e comparação de pixels com sombras on/off. `docs/evidencias/resultado.json` guarda os números. Esse JSON é do registro original com Mesa llvmpipe em Linux. A atualização de 11/11/2026 também passou em GPU Intel Iris Xe no Windows; consultar `docs/TESTES.md` e `docs/evidencias/resultado_atualizacao.json`. Teclado/mouse físicos e o roteiro manual de apresentação permanecem pendentes.

A base integrada é o subconjunto didático independente da disciplina. A conformidade formal dessa versão com a exigência do framework do livro depende de confirmação docente; consultar `FONTES_E_ATRIBUICAO.md`.
