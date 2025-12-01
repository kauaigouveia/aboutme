# Lanchonete Manager

Aplicativo simples de linha de comando para controlar estoque, comandas de pedidos, clientes e fechamento de caixa de uma lanchonete.

## Como usar

1. Instale Python 3.9+.
2. Rode o aplicativo:

```bash
python app.py
```

## Funcionalidades principais

- **Cadastro e atualização de estoque:** informe item, quantidade, unidade e custo unitário.
- **Receitas com ficha técnica:** já inclui a receita padrão de **Sanduíche de Frango** (80g frango, 1 presunto, 1 queijo, 1 hambúrguer, 1 ovo, alface e tomate). Você pode cadastrar novas receitas.
- **Controle de produção:** calcula quantas unidades de uma receita podem ser feitas com o estoque atual e, ao registrar uma venda, baixa cada ingrediente individualmente.
- **Cadastro de clientes:** armazena nome e contato para associar vendas.
- **Registro de vendas:** escolhe receita, quantidade, preço de venda e cliente opcional.
- **Fechamento de caixa:** mostra receita total, custo de ingredientes, lucro bruto e lucro líquido descontando despesas do dia.

## Fluxo sugerido

1. **Cadastre o estoque inicial.** Ex.: frango 1000 g a R$0,05/g; hambúrguer 20 un a R$2,00/un; etc.
2. **Confira a capacidade de produção** em "Ver quantas unidades posso produzir" para saber quantos sanduíches podem ser vendidos com o estoque atual.
3. **Registre vendas** informando quantidade e preço. O sistema baixa os ingredientes correspondentes.
4. **Feche o caixa** ao fim do dia, informando despesas adicionais para obter lucro bruto e líquido.

Todos os dados ficam em memória durante a execução; ao reiniciar, cadastre novamente ou adapte o código para persistência conforme necessário.
