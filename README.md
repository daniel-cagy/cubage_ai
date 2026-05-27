# projeto-si

Projeto Python para estimar dimensões e peso de um produto a partir de uma imagem
e uma descrição textual, usando a OpenAI Responses API.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sua_chave_aqui"
```

## Uso

```bash
python estimate_product.py ./imagem.jpg "Suporte articulado de monitor em metal preto"
```

Para salvar o JSON em arquivo:

```bash
python estimate_product.py ./imagem.jpg "Suporte articulado de monitor em metal preto" --output resultado.json
```

Por padrão o script usa `gpt-5.5`. Para trocar:

```bash
python estimate_product.py ./imagem.jpg "Produto de exemplo" --model gpt-5.2
```
