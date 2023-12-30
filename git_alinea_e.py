from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
from datetime import datetime
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from difflib import get_close_matches
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


def carrega_mais_comentarios(url):
    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    n_interacoes = 7
    soup = None # assegurar que começa com valor antes 
    while n_interacoes > 0:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            load_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="comment-tree"]/faceplate-partial/div[1]/button')))
            load_more_button.click()
        except TimeoutException:
            print("No more clickable buttons. Exiting the loop.")
            break
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        time.sleep(1)
        n_interacoes -= 1
    driver.quit()
    return soup

print(carrega_mais_comentarios('https://www.reddit.com/r/portugal/comments/18udyh9/director_da_emel_ameaca_developers_que_fizeram/'))

def info_comment(coment, lista,include_score = True): # PARA CADA COMENTÁRIO INDIVIDUAL
    autor = coment.find('div', class_='flex flex-row items-center overflow-hidden').text.strip()
    # print(autor)
    if autor != '[deleted]' :
        dici = {}
        texto = coment.find('div', slot='comment')
        if texto is not None:
            texto = texto.text.strip()
        dici['autor'] = autor
        dici['comentario'] = texto
        resposta = coment.find('div', slot='children')
        # print(resposta)
        if resposta is not None:
            lista_resposta = response_comment(resposta.find_all('div', id='-post-rtjson-content'))
            dici['resposta'] = lista_resposta
        if include_score:
            sc=coment.find('shreddit-comment-action-row')
            score=sc['score']
            dici['score']=score
            # print(score)
        lista.append(dici)
    
def response_comment(resposta_texto, include_score = False):  # ? FAZER O SCORE PARA RESPOSTAS ?
    lista_resposta = []
    for c in resposta_texto:
        lista_resposta.append(c.text.strip())
    return lista_resposta

def extract_comments(url):
    lista_comentarios = []
    soup = carrega_mais_comentarios(url)
    if soup is not None:
        x = soup.find('shreddit-post', class_='block xs:mt-xs xs:-mx-xs xs:px-xs xs:rounded-[16px] pt-xs nd:pt-xs bg-[color:var(--shreddit-content-background)] box-border mb-xs nd:visible nd:pb-2xl')
        if x is not None:
            score = re.findall(r'score=".*?"', str(x))
            score = re.sub(r'score=|"', '', score[0]) if score else None
            todos = soup.find('faceplate-batch', target='#comment-tree')
            if todos is not None:
                cada = todos.find_all('shreddit-comment', class_='pt-md px-md xs:px-0')
                if cada:
                    for coment in cada:
                        info_comment(coment, lista_comentarios)
                    return lista_comentarios, score
                else:
                    print("No 'shreddit-comment' elements found.")
                    return [], None
            else:
                print("Element 'faceplate-batch' not found.")
                return [], None
        else:
            print("Element 'shreddit-post' not found.")
            return [], None
    else:
        print("Soup object is None. Unable to proceed.")
        return [], None


# url = 'https://www.reddit.com/r/nba/comments/18rpl9y/with_their_27th_straight_loss_the_detroit_pistons/'
# url='https://www.reddit.com/r/portugal/comments/18t4c0a/qual_a_vossa_opini%C3%A3o/'
# comments, score = extract_comments(url)
# print(score)
# json_str = json.dumps(comments,ensure_ascii=False, indent=2)
# print(comments)
# json.dumps(comments,ensure_ascii=False, indent=2)

# sorted_list = sorted(comments, key=lambda x: int(x['score']), reverse=True)
# first_N_elements = sorted_list[:N]

# print(json.dumps(sorted_list,ensure_ascii=False, indent=2))

# sorted_list = sorted(comments, key=lambda x: x['score'], reverse=True)

# for i in comments:
#     print(type(i))
#     print(i)

# Take the first two elements
# first_two_elements = sorted_list[:2]

# print(sorted_list)
    

from urllib.parse import urljoin

def top(num: int, include_score = False):
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
                    n+=1
                    if include_score:
                        base_url = "https://www.reddit.com"
                        pl = p.find('a', slot='full-post-link')
                        post_link = pl['href']
                        if not re.match(r'^https://www\.reddit\.com', post_link):                            
                            url = urljoin(base_url, post_link)
                        else:
                            url = post_link
                        print(url)
                        comment_w_score, scor = extract_comments(url)
                        if comment_w_score != []:

                            sorted_list = sorted(comment_w_score, key=lambda x: int(x['score']), reverse=True)
                            sort_n = sorted_list[:5]
                            # sort_n = json.dumps(sorted_list,ensure_ascii=False, indent=2)
                            top[n]={'titulo':titulo,
                                'subreddit':subreddit,
                                'score POST':score,
                                'comment':sort_n,
                                }
                        else:
                            top[n]={'titulo':titulo,
                                'subreddit':subreddit,
                                'score POST':score,
                                'comment': 'indisponível',
                                }
                    else: 
                        top[n]={'titulo':titulo,
                              'subreddit':subreddit,
                              'score POST':score,
                              'comment':coment}
                        
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
        
top(3, include_score=True)