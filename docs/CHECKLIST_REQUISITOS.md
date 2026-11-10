# Checklist de requisitos

Fonte: enunciado do trabalho, página impressa 9. Individualidade autorizada informada pelo aluno. Resultados de desenvolvimento em 10/11/2026; teste no Windows ainda pendente.

| Requisito | Estado | Arquivo / método de evidência |
|---|---|---|
| Dois temas tridimensionais reconhecíveis | PASSOU em inspeção visual | `models/rover.py`, `models/excavator.py`, captura real |
| Cenário próprio de exploração | PASSOU | `scene/environment.py`, diorama com caminho e rochas |
| Ambos se deslocam e animam partes | PASSOU | Rodas, sensor, base, torre, braço e caçamba; teste de dois ciclos |
| Interação significativa / ação conjunta | PASSOU | Estados condicionam apoio e retomada; rover se aproxima da área da escavadeira e a reconhece com sensor |
| Movimento por tempo decorrido | PASSOU | `Clock.tick/1000`, `Mission.update`; comparação entre quatro FPS simulados |
| Translação, rotação e escala | PASSOU | `models/common.py:transform`, hierarquia `Object3D` |
| Câmera perspectiva | PASSOU | `Camera.projection`, 48°, matriz perspectiva real |
| Posição/orientação pelo teclado | PASSOU na lógica; hardware NÃO TESTADO | WASD/setas/Q/E; testes do controlador |
| Controle de mouse | PASSOU na lógica; hardware NÃO TESTADO | Botão direito e deslocamento relativo |
| Pausar/retomar mantendo visualização | PASSOU na lógica | `Mission.paused`, câmera e renderer fora da condição de pausa |
| PNG com UV visível | PASSOU | Chão/painel/plataformas, `vertexUV`, `colorTexture`, `uvRepeat` |
| Luz direcional, materiais e normais | PASSOU | `scene.*`, Lambert/Blinn–Phong, inversa transposta |
| Sombra projetada dinâmica por shadow mapping | PASSOU | FBO depth 24 bits + comparação/PCF na segunda passagem; leitura real de profundidade e diferença de pixels |
| Componentes do framework do livro | NÃO TESTADO quanto à aceitação formal | Integra versão didática independente do próprio docente; confirmar aceitação. Não foi obtido o pacote oficial integral |
| Fontes, origem e componentes identificados | PASSOU | `FONTES_E_ATRIBUICAO.md`, `README_ORIGINAL_FRAMEWORK.md`, `ORIGEM_COMPONENTES.json` |
| Shaders, attributes e uniforms explicados | PASSOU | `GUIA_TECNICO.md`, nomes reais do código |
| Dependências e instruções Windows | PASSOU na elaboração; execução Windows NÃO TESTADA | `requirements.txt`, README |
| Roteiro de 10 minutos | PASSOU na elaboração | `ROTEIRO_APRESENTACAO.md`; domínio individual ainda deve ser treinado |
| Declaração de IA e responsável individual | PASSOU | README e fontes |
| Publicação no GitHub | Verificação externa no histórico remoto | A comprovação é a árvore publicada e seus commits; este arquivo isoladamente não comprova publicação |

Bônus: não implementados. Não confundir emissão local do sinalizador com bloom/glow. Não se declara atendimento integral enquanto a ressalva do framework e a execução no ambiente de apresentação estiverem pendentes.
