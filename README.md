# Printer ICMC Terminal
Utilize o terminal para enviar arquivos PDF para a impressora GC1 do ICMC

### Como usar

    python printer.py help

    python printer.py split ARQUIVO [DESTINO]
    python printer.py split --arquivo ARQUIVO [--destino DESTINO]

    python printer.py print NUSP [SENHA] [PASTA] [ARQUIVO] [COPIAS]
    python printer.py print NUSP [--senha SENHA] [--pasta PASTA] [--arquivo ARQUIVO] [--copias COPIAS]
    python printer.py print --nusp NUSP [--senha SENHA] [--pasta PASTA] [--arquivo ARQUIVO] [--copias COPIAS]

### help - Ajuda

Exibe uma cópia desse README

### split - Divide arquivo PDF:

Esta função separa o arquivo PDF em vários arquivos, cada um contendo
apenas 1 página. Esses arquivos são colocados em `DESTINO`, que por
padrão é "to_print"

### print - Imprime arquivo(s) PDF:

Esta função simula chamadas à interface do
[printer.icmc.usp.br](https://printer.icmc.usp.br/).

É possível passar OU um arquivo PDF, OU uma pasta com arquivos PDF. Se
ambos os argumentos forem passados, apenas o argumento `ARQUIVO` será
impresso.

A função itera sobre os arquivos de `PASTA`, enviando um por um para a
impressora. Ao combinar isso com a função de `split` (acima), é possível
imprimir um arquivo utilizando apenas um dos lados da folha.

A opção `COPIAS` é aplicada em todas as chamadas de impressão (cuidado,
saiba o que você está fazendo).

O `NUSP` é obrigatório, porém `SENHA` pode ser inserida de duas formas:
Através da linha de comando (inseguro, porque qualquer um vai poder ler),
ou de forma interativa (que não imprime os caracteres na tela). Para usar
o modo interativo basta omitir o argumento `SENHA`, e o programa irá pedir
que ela seja digitada durante a execução.

Essa função NÃO verifica se o usuário tem cota de impressão, não verifica
se a cota é suficiente para imprimir os arquivos desejados, e nem se a
cota se esgotou durante o processo de impressão. Estes casos não foram
testados, portanto podem ocorrer comportamentos inesperados.