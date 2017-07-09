from urllib import parse
from getpass import getpass
import os
import sys
import shutil

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import fire
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader, PdfFileWriter

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


OUTPUT_FOLDER = 'to_print'


class PrinterUtil:
    def print(self,
              nusp: str,
              senha: str=None,
              pasta: str=OUTPUT_FOLDER,
              arquivo: str=None,
              copias: str="1"):

        if arquivo is None:
            all_files = list(f for f in sorted(os.listdir(pasta))
                             if f.lower().endswith('.pdf'))
            if len(all_files) == 0:
                raise ValueError(f'A pasta "{pasta}" não contém arquivos PDF')
        elif not arquivo.lower().endswith('.pdf'):
            raise ValueError('"arquivo" deve ser um arquivo PDF')
        else:
            all_files = [arquivo]

        if senha is None:
            senha = getpass('Digite a sua senha aqui: ')

        s = requests.Session()

        r = s.get('https://printer.icmc.usp.br/index.php/login/login_usp',
                  verify=False)

        if not r.ok:
            raise ValueError('Problema ao abrir a página de Login')

        token = parse.parse_qs(parse.urlparse(r.url).query)['oauth_token']

        data = {
            "loginUsuario": nusp,
            "senhaUsuario": senha,
            "oauth_token": token,
        }

        r = s.post(r.url, data=data, verify=False)

        if not r.ok:
            raise ValueError('Problema ao fazer Login')

        for filename in all_files:

            filepath = f'{pasta}/{filename}'
            filesize = os.path.getsize(filepath)

            if filesize >= 10485760:  # 10MB
                print(f'Ignorando {filename} ... Arquivo maior do que 10 MB')
                continue

            soup = BeautifulSoup(r.content, 'html.parser')
            csrf = soup.find('input',
                             type='hidden',
                             attrs={'name': 'csrf_ICMC_name'})

            data = {
                "csrf_ICMC_name": csrf.attrs['value'],
                "impr": "gc1",
                "campoCopias": copias,
                "campoPaginas": "",
                "submit": "Imprimir",
            }

            files = {
                "campoArquivo": open(filepath, "rb")
            }

            print(f'Imprimindo {filename} ... ', end='')
            r = s.post('https://printer.icmc.usp.br/index.php/inicio',
                       data=data, files=files, verify=False)
            if not r.ok:
                raise ValueError('Problema ao submeter o form de impressão')
            r = s.get('https://printer.icmc.usp.br/index.php/inicio',
                      verify=False)
            if not r.ok:
                raise ValueError('Problema ao retornar à página inicial')
            print('OK')

    def split(self, arquivo: str, destino: str=OUTPUT_FOLDER):
        if not arquivo.lower().endswith('.pdf'):
            raise ValueError('"arquivo" deve ser um arquivo PDF')

        if os.path.exists(destino):
            shutil.rmtree(destino)
        os.makedirs(destino)

        inputpdf = PdfFileReader(open(arquivo, "rb"))
        for i in range(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            with open("%s/%04d.pdf" % (destino, int(i)), "wb") as outputStream:
                output.write(outputStream)

    def help(self):
        this_filename = sys.argv[0]
        print(f"""
Como usar:
    python {this_filename} help
    
    python {this_filename} split ARQUIVO [DESTINO]
    python {this_filename} split --arquivo ARQUIVO [--destino DESTINO]
    
    python {this_filename} print NUSP [SENHA] [PASTA] [ARQUIVO] [COPIAS]
    python {this_filename} print NUSP [--senha SENHA] [--pasta PASTA] [--arquivo ARQUIVO] [--copias COPIAS]
    python {this_filename} print --nusp NUSP [--senha SENHA] [--pasta PASTA] [--arquivo ARQUIVO] [--copias COPIAS]

help - Ajuda
    Exibe esse texto

split - Divide arquivo PDF:
    Esta função separa o arquivo PDF em vários arquivos, cada um contendo
    apenas 1 página. Esses arquivos são colocados em `DESTINO`, que por
    padrão é "{OUTPUT_FOLDER}"

print - Imprime arquivo(s) PDF:
    Esta função simula chamadas à interface do printer.icmc.usp.br .
    
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
""")

if __name__ == '__main__':
    fire.Fire(PrinterUtil)
