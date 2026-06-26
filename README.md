# Estimador de Produtos com IA

Projeto Python para estimar dimensões e peso de produtos a partir de uma imagem,
uma descrição textual e, opcionalmente, medidas conhecidas informadas pelo usuário,
usando a OpenAI Responses API.

A imagem deve representar o item que será medido. Quando o produto estiver na
embalagem, as estimativas consideram o conjunto embalado exatamente como aparece
na foto.

O sistema retorna um JSON estruturado com:

- identificação provável do produto;
- descrição resumida do que foi observado;
- `produto`, contendo dimensões estimadas em centímetros e peso estimado em quilogramas do item fotografado;
- `medidas_conhecidas_informadas`, quando o usuário enviar comprimento, largura, altura ou peso conhecidos;
- nível de confiança binário: `alto` ou `baixo`;
- `validacao`, adicionada no pós-processamento, com `status`, `erros` e `alertas`;
- `metricas_logisticas`, calculadas localmente a partir da estimativa;
- exportação do resultado pela interface em JSON ou CSV.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sua_chave_aqui"
```

Opcionalmente, defina o modelo padrão:

```bash
export OPENAI_MODEL="gpt-5.5"
```

## Uso

### Interface web

Inicie o backend FastAPI:

```bash
python3 -m uvicorn api:app --reload
```

A interface permite enviar a foto, a descrição e medidas conhecidas opcionais, como comprimento, largura, altura ou peso.

Abra a interface em:

```text
http://localhost:8000
```

A documentação interativa da API fica em:

```text
http://localhost:8000/docs
```

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
python cli.py ./imagem.jpg "Produto de exemplo" --model gpt-5.2
```

## Estrutura

```text
.
├── api.py
├── cli.py
├── index.html
├── static/
│   ├── app.js
│   ├── styles.css
│   └── js/
│       ├── dom.js
│       ├── exportResults.js
│       ├── format.js
│       ├── knownMeasures.js
│       ├── render.js
│       └── upload.js
├── product_estimator/
│   ├── constants.py
│   ├── estimate_product.py
│   ├── image_processing.py
│   ├── post_processing.py
│   ├── prompt.py
│   └── schema.py
├── requirements.txt
└── README.md
```

`api.py` expõe o backend FastAPI e serve a interface web.

`index.html` contém a estrutura da interface web.

`static/styles.css` contém os estilos da interface.

`static/app.js` orquestra os módulos da interface e envia os dados para o endpoint `/estimate`.

`static/js/` contém os módulos de upload, medidas conhecidas, renderização, exportação, formatação e referências do DOM.

`cli.py` é o ponto de entrada por terminal.

`product_estimator/estimate_product.py` contém a integração com a OpenAI e pode
ser reaproveitado por uma API web.

`product_estimator/image_processing.py` redimensiona e comprime a imagem antes da chamada ao modelo.

`product_estimator/constants.py` guarda constantes operacionais, como o fator de cubagem.

`product_estimator/post_processing.py` adiciona validação e métricas logísticas à resposta.

`product_estimator/prompt.py` guarda o prompt de sistema.

`product_estimator/schema.py` guarda o schema JSON esperado da resposta do modelo, antes do pós-processamento.

## Observação

As medidas retornadas são estimativas. Sem escala explícita na imagem ou medidas
na descrição, o resultado deve ser tratado como aproximação para triagem ou MVP,
não como medição exata.
