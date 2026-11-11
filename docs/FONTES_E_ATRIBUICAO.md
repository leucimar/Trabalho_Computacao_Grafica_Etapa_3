# Fontes e atribuição

## Material utilizado diretamente

Repositório da disciplina do professor Rodrigo Fernandes dos Santos: <https://github.com/rodrygofesantos/pygame>, commit `bcc4079703c5947556563c4f2a558064e12b7242`, consultado em 10/11/2026. O README original relevante está preservado em `docs/README_ORIGINAL_FRAMEWORK.md`.

Copiados **sem alteração** de `Aula_Texturas/alunos/`:

- `core/__init__.py`, `core/attribute.py`, `core/matrix.py`, `core/object3D.py`, `core/mesh.py`, `core/uniform.py`;
- `geometry/__init__.py`, `geometry/geometry.py`, `geometry/boxGeometry.py`.

`geometry/primitives.py` estende as classes `Geometry` e `BoxGeometry`. A composição usa `Object3D`, `Mesh`, `Matrix`, `Attribute` e `Uniform` efetivamente em execução. A câmera e o renderer são extensões locais que mantêm essa arquitetura. A matriz normal usa inversa transposta para permitir escalas diferentes por eixo.

O repositório consultado não contém um arquivo geral de licença. Nenhuma licença MIT ou outra foi presumida nem acrescentada sobre o material de terceiros. Sua origem e os créditos foram preservados para o uso acadêmico da disciplina. Para reutilização fora dela, verificar os termos com o responsável pelo material.

## Livro e relação com a implementação

STEMKOSKI, Lee; PASCALE, Michael. *Developing Graphics Frameworks with Python and OpenGL*. 1. ed. CRC Press, 2022. DOI: <https://doi.org/10.1201/9781003181378>.

Capítulos 3–5: matrizes, grafo de cena, formas geométricas, atributos, uniforms e texturas, por meio do material didático do docente. Seção 6.9: referência conceitual para projetar a cena no espaço da luz, construir um mapa de profundidade e comparar profundidades na passagem da câmera.

Os shaders `scene.*` e `depth.*`, o FBO e o filtro PCF foram desenvolvidos para esta aplicação; não são uma transcrição nem uma distribuição oficial da seção 6.9. O pacote oficial não foi obtido nesta rodada. A aceitação da versão didática da disciplina como framework do trabalho é uma pendência a confirmar com o professor.

Também foram inspecionados, mas **não incorporados**, `stemkoski/three.py` e `ax-va/PyOpenGL-Pygame-Stemkoski-Pascale-2021`. O primeiro é outro projeto dos autores; o segundo é uma implementação de terceiros. Não foram apresentados como o pacote oficial do livro.

## Recursos próprios

`assets/textures/sand.png`, `white.png`, `hazard.png` e `solar.png` são imagens produzidas por `tools/generate_textures.py`, com semente fixa e sem imagens externas. A imagem de `docs/evidencias/cena.jpg` é uma captura de renderização real desta aplicação, sem geração por IA de imagem.

O painel HUD usa a fonte padrão distribuída pelo Pygame. Pygame, PyOpenGL, NumPy e psutil são dependências instaladas separadamente e conservam suas próprias licenças; não foram incluídas como cópias no repositório.

## Enunciado e escolhas

PDF fornecido pelo aluno: `Trabalho - Computacao Grafica etapa 3.pdf`, disciplina 2026/02, requisitos na página impressa 9 e regras de entrega nas páginas 11–12. Documento de escopo: `ESCOPO_E_PROMPT_WORK_COMPUTACAO_GRAFICA_ETAPA_3.md`. A autorização do professor para trabalho individual foi informada pelo aluno.

## Assistência de IA

ChatGPT Work / Codex: auxílio em implementação, testes e documentação. Autoria e responsabilidade acadêmicas permanecem com o aluno. Não foram inventados testes manuais no Windows ou validação docente do framework.
