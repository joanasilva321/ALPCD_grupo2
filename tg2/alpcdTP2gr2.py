from bs4 import BeautifulSoup
import requests 
import typer
import json
import os
import time
from selenium import webdriver

#criação de aplicativo de linha de comando
app=typer.Typer()

#confere se já existe um arquivo csv com o nome escolhido e direciona para a função escrever_csv
def csv_(dic):
     print(dic)
     nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' #input nome.csv
     if arquivo_existe(nome_arquivo_csv): #chama a função que verifica a existência dos arquivos
            novo_csv=str(input(f"O arquivo '{nome_arquivo_csv}' já existe. Deseja criar outro?(s/n): "))
            while novo_csv != 's' and novo_csv != 'n':
                novo_csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))
            if novo_csv == 's':
                nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' 
                while arquivo_existe(nome_arquivo_csv):
                     nome_arquivo_csv = str(input('Arquivo existente.Insira outro nome: ')) + '.csv'
                escrever_csv(dic,nome_arquivo_csv,'w') #funçao que cria csv
            elif novo_csv == 'n':
                 print('Será adicionado ao arquivo existente'.upper())
                 escrever_csv(dic,nome_arquivo_csv,'a') # função que adiciona csv
     else:
          escrever_csv(dic,nome_arquivo_csv,'w')

# função que cria um novo csv ou escreve num existente
def escrever_csv(dic,nome_arquivo_csv, tipo):
    with open(nome_arquivo_csv, tipo, encoding='utf-8') as arquivo_csv:
        if tipo=='w':
            headers=','.join(dic[1].keys())
            arquivo_csv.write(f'{headers}\n')
        for post in dic:
            values=','.join(str(value) for value in dic[post].values())
            arquivo_csv.write(f'{values}\n')

#função que verifica os nomes dos csvs na pasta      
def arquivo_existe(nome_arquivo):
    return os.path.exists(nome_arquivo)

#função para carregar mais que 3 posts
def carregar_mais_posts(url,n_posts):
    # Configurando o WebDriver (certifique-se de ter o chromedriver ou geckodriver instalado)
    driver = webdriver.Chrome()  # ou webdriver.Firefox()
    driver.get(url)
    n_interacoes = 1
    while n_interacoes < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tudo=soup.find('shreddit-feed', class_='nd:visible')
        cada=tudo.find_all('article', class_='m-0')
        in_n_posts = len(cada)
        time.sleep(2)
        if in_n_posts < n_posts:
            n_interacoes += 1
        else: break
    driver.quit()
    return soup

#para que o cliente use a função
@app.command()
#função que pega n posts mais populares
def top(num: int):
    top={}
    soup = carregar_mais_posts('https://www.reddit.com/r/popular/',20)
    if soup:
        posts=soup.find('shreddit-feed',class_='nd:visible')
        posts_ind=posts.find_all('article',class_="m-0")
        n=0
        if len(posts_ind)==num: #mudar para < depois
            print('menor')
        else:
            for p in posts_ind:
                if n<num:
                    info=p.find('shreddit-post')
                    titulo=info['post-title']
                    subreddit=info['subreddit-prefixed-name']
                    score=info['score']
                    coment=info['comment-count']
                    top[n+1]={'titulo':titulo,
                              'subreddit':subreddit,
                              'score':score,
                              'comment':coment}
                    n+=1
                else:
                    break
        print(json.dumps(top,ensure_ascii=False, indent=2))
        
        csv=str(input('Deseja inportar para formato csv(s/n)? '))

        while csv != 's' and csv != 'n':
            csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

        if csv == 's':
            csv_(top)

    else:
        print(f'Falha ao obter a página.')

#só foi usado para testar o typer, depois que adicionado mais funções para o cliente apaga-se
@app.command()
def teste(nome: str):
    print(nome)

#correr o typer
if __name__=='__main__':
    app()