# Estimador de Produtos com IA

Projeto Python para estimar dimensões e peso de produtos a partir de uma imagem
e uma descrição textual, usando a OpenAI Responses API.

O modelo retorna um JSON estruturado com:

- identificação provável do produto;
- descrição resumida do que foi observado;
- `produto`, contendo dimensões estimadas em centímetros e peso estimado em quilogramas;
- `produto_com_embalagem`, contendo dimensões estimadas da embalagem e peso bruto estimado;
- nível de confiança;
- pistas usadas na estimativa;
- fatores de incerteza;
- `validacao`, adicionada no pós-processamento, com `status`, `erros` e `alertas`.

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

```bash
python cli.py ./imagem.jpg "Suporte articulado de monitor em metal preto"
```

Para salvar o JSON em arquivo:

```bash
python cli.py ./imagem.jpg "Suporte articulado de monitor em metal preto" --output resultado.json
```

Para informar outro modelo na execução:

```bash
python cli.py ./imagem.jpg "Produto de exemplo" --model gpt-5.2
```

## Estrutura

```text
.
├── cli.py
├── product_estimator/
│   ├── estimate_product.py
│   ├── post_processing.py
│   ├── prompt.py
│   └── schema.py
├── requirements.txt
└── README.md
```

`cli.py` é o ponto de entrada por terminal.

`product_estimator/estimate_product.py` contém a integração com a OpenAI e pode
ser reaproveitado por uma API web.

`product_estimator/post_processing.py` adiciona a chave `validacao` e verifica a estrutura e a coerência logística da resposta.

`product_estimator/prompt.py` guarda o prompt de sistema.

`product_estimator/schema.py` guarda o schema JSON esperado da resposta do modelo, antes do pós-processamento.

## Observação

As medidas retornadas são estimativas. Sem escala explícita na imagem ou medidas
na descrição, o resultado deve ser tratado como aproximação para triagem ou MVP,
não como medição exata.
