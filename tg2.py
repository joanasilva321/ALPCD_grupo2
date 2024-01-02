
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
import csv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import requests 
import typer
import json
import os
import time
from selenium import webdriver

#criação de aplicativo de linha de comando
# app=typer.Typer()

#confere se já existe um arquivo csv com o nome escolhido e direciona para a função escrever_csv
def csv_(dic):
     #print(dic)
     nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' #input nome.csv
     if arquivo_existe(nome_arquivo_csv): #chama a função que verifica a existência dos arquivos
            novo_csv=str(input(f"O arquivo '{nome_arquivo_csv}' já existe. Deseja criar outro?(s/n): "))
            while novo_csv != 's' and novo_csv != 'n':
                novo_csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))
            if novo_csv == 's':
                nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' 
                while arquivo_existe(nome_arquivo_csv):
                     nome_arquivo_csv = str(input('Arquivo existente.Insira outro nome: ')) + '.csv'
                escrever_csv2(dic,nome_arquivo_csv,'w') #funçao que cria csv
            elif novo_csv == 'n':
                 print('Será adicionado ao arquivo existente'.upper())
                 escrever_csv2(dic,nome_arquivo_csv,'a') # função que adiciona csv
     else:
          escrever_csv2(dic,nome_arquivo_csv,'w')

def escrever_csv2(data, nome_arquivo_csv, tipo):
    with open(nome_arquivo_csv, tipo, encoding='utf-8', errors='replace') as arquivo_csv:
        if tipo == 'w':
            if isinstance(data, dict):
                headers = ','.join(data[next(iter(data))].keys())
                arquivo_csv.write(f'{headers}\n')
            elif isinstance(data, list) and data:
                headers = ','.join(data[0].keys())
                arquivo_csv.write(f'{headers}\n')

        if isinstance(data, dict):
            for key, values in data.items():
                row = ','.join(str(value) for value in values.values())
                arquivo_csv.write(f'{row}\n')
        elif isinstance(data, list):
            for dic in data:
                dic['comments']=len(dic['comments'])
                row = ','.join(str(value) for value in dic.values())
                arquivo_csv.write(f'{row}\n')


#função que verifica os nomes dos csvs na pasta      
def arquivo_existe(nome_arquivo):
    return os.path.exists(nome_arquivo)

#para que o cliente use a função
# @app.command()

# #só foi usado para testar o typer, depois que adicionado mais funções para o cliente apaga-se
# @app.command()
def teste(nome: str):
    print(nome)

#correr o typer
# if __name__=='__main__':
#     app()
############################## Elisa
    
def info_comment(coment, lista,include_score = True): # PARA CADA COMENTÁRIO INDIVIDUAL
    autor = coment.find('div', class_='flex flex-row items-center overflow-hidden').text.strip()
    if autor != '[deleted]' :
        dici = {}
        texto = coment.find('div', slot='comment')
        if texto is not None:
            texto = texto.text.strip()
        dici['autor'] = autor
        dici['comentario'] = texto
        resposta = coment.find('div', slot='children')
        if resposta is not None:
            lista_resposta = response_comment(resposta.find_all('div', id='-post-rtjson-content'))
            dici['resposta'] = lista_resposta
        if include_score:
            sc=coment.find('shreddit-comment-action-row')
            score=sc['score']
            dici['score']=score
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
    
from urllib.parse import urljoin

def top(num: int, include_score = False):
    top={}
    soup = carregar_mais_posts(20,'https://www.reddit.com/r/popular/')
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
#######################################################################################################

#def carrega_topicos():
    driver = webdriver.Chrome()
    driver.get('https://www.reddit.com/')
    wait = WebDriverWait(driver, 4)
    soup = None # assegurar que começa com valor antes 
    try:
        load_more_button1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@source="nav"]/faceplate-tracker/div[0]/button')))
        load_more_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@noun="topics_menu_see_less"]/faceplate-tracker/div[2]/button')))
        load_more_button1.click()
        load_more_button2.click()
    except TimeoutException:
        print("No more clickable buttons. Exiting the loop.")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        time.sleep(1)
    driver.quit()
    return soup

def carregar_mais_posts(n_posts,url):
    # Configurando o WebDriver (certifique-se de ter o chromedriver ou geckodriver instalado)
    driver = webdriver.Chrome()  # ou webdriver.Firefox()

    # Abra a página do Reddit
    driver.get(url)
    n_interacoes = 1
    while n_interacoes < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        z = soup.find_all('a', class_='absolute inset-0')
        if len(z) == 0:
            tudo=soup.find('shreddit-feed', class_='nd:visible')
            z=tudo.find_all('article', class_='m-0')
        in_n_posts = len(z)
        time.sleep(5)
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


#carrega_mais_comentarios('https://www.reddit.com/r/CasualPT/comments/18vxgaj/quem_%C3%A9_que_tamb%C3%A9m_faz_isto/')

def comet(url):
    lista_comentarios=[]
    soup=carrega_mais_comentarios(url)
    x=soup.find('shreddit-post', class_='block xs:mt-xs xs:-mx-xs xs:px-xs xs:rounded-[16px] pt-xs nd:pt-xs bg-[color:var(--shreddit-content-background)] box-border mb-xs nd:visible nd:pb-2xl')
    score=re.findall(r'score=".*?"',str(x))
    if len(score) >0:
        score=score[0]
        score=re.sub(r'score=','',score)
        score=re.sub(r'"','',score)
    else: score = 0
    todos = soup.find('faceplate-batch', target='#comment-tree')
    if todos:
        cada=todos.find_all('shreddit-comment', class_='pt-md px-md xs:px-0')
        if cada:
            for coment in cada:
                dici={}
                texto=coment.find('div', slot='comment')
                autor=coment.find('div',class_='flex flex-row items-center overflow-hidden').text.strip()
                if texto is not None:
                    texto=texto.text.strip()
                dici['autor']=autor
                dici['comentario']=texto
                resposta=coment.find('div', slot='children')
                if resposta is not None:
                    lista_resposta=[]
                    resposta_texto=resposta.find_all('div', id='-post-rtjson-content')
                    #print('Respostas ao comentário:')
                    for c in resposta_texto:
                        lista_resposta.append(c.text.strip())
                        #print(c.text)
                    dici['resposta']=lista_resposta
                lista_comentarios.append(dici)
                #print('----------------')
            #print(lista_comentarios)
            return lista_comentarios, score
    else : return [], score

def alinea_b (limite,categoria):
    categoria=f_categoria(categoria)
    if categoria is not None:
        lista_b=[]
        soup=carregar_mais_posts(limite,categoria)
        z = soup.find_all('a', class_='absolute inset-0')
        times=soup.find_all('span', class_='flex items-center text-neutral-content-weak text-12')
        n=0
        for i in range(limite):
            dici_post={}
            titulo=re.findall(r'aria-label=".*?"',str(z[i]))
            if len(titulo)>0:
                titulo=titulo[0]
                titulo=re.sub(r'aria-label=','',titulo)
                titulo=re.sub(r'"','',titulo)
            subredit=re.findall(r'href=".*?/comments/',str(z[i]))
            if len(subredit)>0:
                subredit=subredit[0]
                subredit=re.sub(r'href="','',subredit)
                subredit=re.sub(r'/comments/','',subredit)
            comentarios=re.findall(r'href=".*?"',str(z[i]))
            if len(comentarios)>0:
                comentarios=comentarios[0]
                comentarios=re.sub(r'href=','',comentarios)
                comentarios=re.sub(r'"','',comentarios)
                url=f'https://www.reddit.com{comentarios}'
                lista,score=comet(url)
            else: 
                lista= []
                score = None
            tempo = re.findall(r'faceplate-timeago ts=".*?"',str(times[i]))
            if len(tempo)>0:
                tempo=tempo[0]
                tempo=re.sub(r'faceplate-timeago ts=','',tempo)
                tempo=re.sub(r'"','',tempo)
                data_hora_objeto = datetime.strptime(tempo, "%Y-%m-%dT%H:%M:%S.%f%z")
                data_hora_formatada = data_hora_objeto.strftime("%Y:%m:%d %H:%M:%S")
            else: data_hora_formatada= None
            dici_post['title']=titulo
            dici_post['subreddit']=subredit
            dici_post['comments']=lista
            dici_post['score']=score
            dici_post['time']=data_hora_formatada
            lista_b.append(dici_post)
        json_string = json.dumps(lista_b,indent=2)
        #print(json_string)

        # csv=str(input('Deseja inportar para formato csv(s/n)? '))
        # while csv != 's' and csv != 'n':
        #     csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))
        # if csv == 's':
        #     csv_(lista_b)

        return json_string

        #
    else: 
        print('Tópico não encontrado')
        return None
    
            
#comet('https://www.reddit.com/r/nba/comments/18rneko/highlight_cole_anthony_with_a_3pointer_wedgie/')

def f_categoria(categoria):
    lista_cat=[]
    soup=carregar_mais_posts(1,'https://www.reddit.com/')
    topicos=soup.find('faceplate-auto-height-animator', class_='block')
    cada=topicos.find_all('left-nav-topic-tracker', noun='topic_item')
    for i in cada:
        t=i.find('span', class_='flex flex-col justify-center min-w-0 shrink py-[var(--rem6)]')
        t=t.text.strip()
        lista_cat.append(t.lower())
    print(lista_cat)
    # palavra_proxima = get_close_matches(categoria.lower(), lista_cat)
    # if palavra_proxima:
    #     topico=palavra_proxima[0]
    #     cat=f'https://www.reddit.com/search/?q={topico}&sort=new'
    #     print(cat)
    #     return cat
    # else:
    #     return None 
#f_categoria('nba')

def algoritmo_c(limite, categoria):
    resultado_alinea_b = alinea_b(limite,categoria)
    try:
        resultado_alinea_b = json.loads(resultado_alinea_b)
        if resultado_alinea_b:
            data_atual = datetime.now()
            for post in range(len(resultado_alinea_b)):
                score = resultado_alinea_b[post].get('score', 'N/A') # score
                comment=resultado_alinea_b[post].get('comments', 'N/A')
                time=resultado_alinea_b[post].get('time', 'N/A')
                if time is not None:
                    time = datetime.strptime(time, '%Y:%m:%d %H:%M:%S')
                    dif_tempo= abs((data_atual - time).total_seconds())
                else: dif_tempo = 100000
                #print(dif_tempo)
                n_comment=len(comment) # num de comentarios
                num_resposta=0
                if n_comment >0:
                    for k in comment:
                        resposta = k.get('resposta')
                        if resposta:
                            num_resposta+=len(resposta) # quantas respostas para cada comentario
                resultado_alinea_b[post]['relevancia']= (0.5*int(score)+0.4*n_comment+0.1*num_resposta)+100
                #print(resultado_alinea_b[post]['relevancia'])
                while dif_tempo > 60: # mais de 1 minuto
                    dif_tempo= dif_tempo-60
                    resultado_alinea_b[post]['relevancia']= resultado_alinea_b[post]['relevancia']-1
            json_relevancia =sorted(resultado_alinea_b, key=lambda x: x.get('relevancia', 0), reverse=True)
            json_relevancia=json.dumps(json_relevancia, indent=2)
            print(json_relevancia)

            csv=str(input('Deseja inportar para formato csv(s/n)? '))
            while csv != 's' and csv != 'n':
                csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))
            if csv == 's':
                csv_(resultado_alinea_b)

    except json.JSONDecodeError:
        print("A função alinea_b retornou uma string inválida.")

# categoria=f_categoria('valein')
# carregar_mais_posts(3,categoria)
#algoritmo_c(1,'valein')
#alinea_b(1,'nba')
#top(3)


