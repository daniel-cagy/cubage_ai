# Cubage AI

Projeto Python para estimar dimensões e peso de produtos a partir de uma imagem,
uma descrição textual e, opcionalmente, medidas conhecidas informadas pelo usuário,
usando a OpenAI Responses API.

A imagem deve representar o item que será medido. Quando o produto estiver na
embalagem, as estimativas consideram o conjunto embalado exatamente como aparece
na foto.

O projeto hoje possui três partes principais:

- um núcleo Python em `product_estimator/`, responsável por chamar a OpenAI, processar imagem, validar resposta e calcular métricas logísticas;
- um backend FastAPI em `api.py`, usado pela interface web;
- uma interface web estática em `index.html` e `static/`, com upload de imagem, descrição, medidas conhecidas, configurações avançadas e exportação de resultado.

## O Que O Sistema Retorna

A resposta final é um dicionário com a resposta do modelo e dados adicionados no
pós-processamento local. Os principais campos são:

- `resposta`: JSON estruturado retornado pelo modelo;
- `resposta.produto`: dimensões estimadas em centímetros e peso estimado em quilogramas;
- `resposta.nivel_confianca`: confiança binária, `alto` ou `baixo`;
- `validacao`: status, erros e alertas detectados localmente;
- `metricas_logisticas`: volume, densidade, peso cubado, peso cobrável e fator de cubagem usado;
- `medidas_conhecidas_informadas`: medidas passadas pelo usuário, quando houver;
- `modo_processamento_imagem`: `original`, `resized` ou `quantized`;
- `modelo_utilizado`: modelo enviado para a OpenAI;
- `uso_de_tokens`: tokens de entrada, saída e total, quando retornados pela API.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sua_chave_aqui"
```

Opcionalmente, defina o modelo padrão usado pelo backend:

```bash
export OPENAI_MODEL="gpt-5.4-mini"
```

## Uso

### Interface Web

Inicie o backend FastAPI:

```bash
python3 -m uvicorn api:app --reload
```

Abra a interface em:

```text
http://localhost:8000
```

A documentação interativa da API fica em:

```text
http://localhost:8000/docs
```

A interface permite:

- enviar uma imagem do produto;
- informar uma descrição textual;
- adicionar medidas conhecidas de comprimento, largura, altura ou peso;
- escolher o modelo de IA por preset ou texto livre;
- escolher o fator de cubagem usado no cálculo do peso cubado;
- escolher o tratamento da imagem: original, redimensionada ou quantizada;
- exportar o resultado em JSON ou CSV.

### API

O endpoint principal é:

```text
POST /estimate
```

Ele recebe `multipart/form-data` com:

- `image`: arquivo de imagem;
- `description`: descrição textual do produto;
- `known_measures`: JSON com medidas conhecidas, opcional;
- `image_processing_mode`: `original`, `resized` ou `quantized`;
- `model`: nome do modelo OpenAI;
- `cubage_factor`: fator de cubagem numérico, maior que zero.

### CLI

```bash
python cli.py ./imagem.jpg "Caixa de papelão com notebook Dell, modelo Inspiron 15, embalagem original lacrada"
```

Para salvar o JSON em arquivo:

```bash
python cli.py ./imagem.jpg "Caixa de papelão com notebook Dell, modelo Inspiron 15, embalagem original lacrada" --output resultado.json
```

Para informar outro modelo na execução:

```bash
python cli.py ./imagem.jpg "Produto de exemplo" --model gpt-5.4-mini
```

## Estrutura Do Projeto

```text
.
├── api.py
├── cli.py
├── index.html
├── requirements.txt
├── README.md
├── product_estimator/
│   ├── constants.py
│   ├── estimate_product.py
│   ├── image_processing.py
│   ├── post_processing.py
│   ├── prompt.py
│   └── schema.py
├── static/
│   ├── app.js
│   ├── styles.css
│   └── js/
│       ├── dom.js
│       ├── exportResults.js
│       ├── format.js
│       ├── knownMeasures.js
│       ├── render.js
│       ├── settings.js
│       └── upload.js
└── tests/
    ├── README.md
    ├── analyze_results.py
    ├── run_tests.py
    ├── images/
    ├── results/
    └── samples/
```

## Arquivos Principais

`api.py` expõe o backend FastAPI, serve a interface web e valida os dados recebidos pelo formulário.

`cli.py` é o ponto de entrada por terminal para executar uma estimativa sem usar a interface web.

`index.html` contém a estrutura da interface.

`static/styles.css` contém os estilos da interface, incluindo responsividade para celular.

`static/app.js` orquestra os módulos do frontend e envia os dados para `/estimate`.

`static/js/dom.js` centraliza referências aos elementos do DOM.

`static/js/upload.js` controla upload, preview e remoção de imagem.

`static/js/knownMeasures.js` controla a adição de medidas conhecidas.

`static/js/settings.js` controla configurações avançadas: modelo, fator de cubagem e modo de imagem.

`static/js/render.js` renderiza resultado, métricas logísticas, confiança e alertas.

`static/js/exportResults.js` exporta o resultado em JSON ou CSV.

`static/js/format.js` concentra funções pequenas de formatação e escape de HTML.

`product_estimator/estimate_product.py` contém a integração com a OpenAI Responses API e monta a resposta final usada pela CLI e pela API.

`product_estimator/image_processing.py` prepara a imagem antes do envio ao modelo. Os modos disponíveis são:

- `original`: envia a imagem original;
- `resized`: redimensiona e comprime a imagem;
- `quantized`: redimensiona e aplica quantização de cores.

`product_estimator/post_processing.py` valida a resposta do modelo e calcula métricas logísticas, como volume, peso cubado e peso cobrável.

`product_estimator/constants.py` guarda constantes e estruturas compartilhadas, como `FATOR_CUBAGEM`, chaves de dimensão e a classe `Objeto`.

`product_estimator/prompt.py` guarda o prompt de sistema enviado ao modelo.

`product_estimator/schema.py` guarda o JSON Schema exigido da resposta do modelo.

## Avaliação Experimental

A pasta `tests/` concentra os scripts usados para comparar modelos e modos de processamento de imagem.

O fluxo é:

```bash
python tests/run_tests.py
python tests/analyze_results.py tests/results/arquivo_de_resultado.csv
```

`tests/run_tests.py` executa chamadas reais à OpenAI para cada combinação de produto, modelo, modo de imagem e repetição.

`tests/analyze_results.py` lê o CSV gerado, calcula métricas de erro, taxa de acerto de intervalo, custo estimado e gera resumos, gráficos e relatório.

Os casos de teste ficam em `tests/samples/`, as imagens em `tests/images/` e os resultados em `tests/results/`.

A metodologia detalhada fica em `tests/README.md`.

## Observações

As medidas retornadas são estimativas. Sem escala explícita na imagem ou medidas
conhecidas confiáveis, o resultado deve ser tratado como aproximação para triagem
logística, comparação entre alternativas ou apoio operacional, não como medição
exata.

O fator de cubagem afeta apenas as métricas logísticas calculadas localmente. Ele
não muda a estimativa do modelo para dimensões e peso; muda o cálculo de peso
cubado e peso cobrável.
