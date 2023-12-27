
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


def carregar_mais_posts(n_posts,categoria):
    # Configurando o WebDriver (certifique-se de ter o chromedriver ou geckodriver instalado)
    driver = webdriver.Chrome()  # ou webdriver.Firefox()

    # Abra a página do Reddit
    driver.get(categoria)
    n_interacoes = 1
    while n_interacoes < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        #pagina = soup.find('section', slot='page-1')
        z = soup.find_all('a', class_='absolute inset-0')
        in_n_posts = len(z)
        time.sleep(5)
        if in_n_posts < n_posts:
            n_interacoes += 1
        else: break
    driver.quit()
    return z

def carrega_mais_comentarios(url):
    driver = webdriver.Chrome()
    driver.get(url)
    n_interacoes=10
    while n_interacoes > 1:
        n_interacoes=n_interacoes-1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        time.sleep(1)
    driver.quit()
    return soup

def comet(url):
    lista_comentarios=[]
    soup=carrega_mais_comentarios(url)
    x=soup.find('shreddit-post', class_='block xs:mt-xs xs:-mx-xs xs:px-xs xs:rounded-[16px] pt-xs nd:pt-xs bg-[color:var(--shreddit-content-background)] box-border mb-xs nd:visible nd:pb-2xl')
    score=re.findall(r'score=".*?"',str(x))
    score=score[0]
    score=re.sub(r'score=','',score)
    score=re.sub(r'"','',score)
    todos = soup.find('faceplate-batch', target='#comment-tree')
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

def alinea_b (limite,categoria):
    categoria=f_categoria(categoria)
    if categoria is not None:
        lista_b=[]
        z=carregar_mais_posts(limite,categoria)
        n=0
        for i in range(limite):
            dici_post={}
            titulo=re.findall(r'aria-label=".*?"',str(z[i]))
            if len(titulo)>0:
                titulo=titulo[0]
                titulo=re.sub(r'aria-label=','',titulo)
                titulo=re.sub(r'"','',titulo)
            subredit=re.findall(r'href=".*?/comments/',str(z[i]))
            subredit=subredit[0]
            subredit=re.sub(r'href="','',subredit)
            subredit=re.sub(r'/comments/','',subredit)
            comentarios=re.findall(r'href=".*?"',str(z[i]))
            comentarios=comentarios[0]
            comentarios=re.sub(r'href=','',comentarios)
            comentarios=re.sub(r'"','',comentarios)
            dici_post['title']=titulo
            dici_post['subreddit']=subredit
            url=f'https://www.reddit.com{comentarios}'
            lista,score=comet(url)
            dici_post['comments']=lista
            dici_post['score']=score
            lista_b.append(dici_post)
        json_string = json.dumps(lista_b, indent=2)
        print(json_string)
        return json_string
    else: 
        print('Tópico não encontrado')
        return None
            
#comet('https://www.reddit.com/r/nba/comments/18rneko/highlight_cole_anthony_with_a_3pointer_wedgie/')

def f_categoria(categoria):
    lista_cat=[]
    urlx='https://www.reddit.com/'
    driver = webdriver.Chrome()
    driver.get(urlx)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()
    topicos=soup.find('faceplate-auto-height-animator', class_='block')
    cada=topicos.find_all('left-nav-topic-tracker', noun='topic_item')
    for i in cada:
        t=i.find('span', class_='flex flex-col justify-center min-w-0 shrink py-[var(--rem6)]')
        t=t.text.strip()
        lista_cat.append(t.lower())
    palavra_proxima = get_close_matches(categoria.lower(), lista_cat)
    if palavra_proxima:
        topico=palavra_proxima[0]
        cat=f'https://www.reddit.com/search/?q={topico}&sort=new'
        print(cat)
        return cat
    else:
        return None 
#f_categoria('nba')

def algoritmo_c(limite, categoria):
    resultado_alinea_b = alinea_b(limite,categoria)
    try:
        resultado_alinea_b = json.loads(resultado_alinea_b)
        if resultado_alinea_b:
            for post in range(len(resultado_alinea_b)):
                score = resultado_alinea_b[post].get('score', 'N/A') # score
                comment=resultado_alinea_b[post].get('comments', 'N/A')
                n_comment=len(comment) # num de comentarios
                num_resposta=0
                for k in comment:
                    resposta = k.get('resposta')
                    if resposta:
                        num_resposta+=len(resposta) # quantas respostas para cada comentario
                resultado_alinea_b[post]['relevancia']= 0.5*int(score)+0.4*n_comment+0.1*num_resposta
            json_relevancia =sorted(resultado_alinea_b, key=lambda x: x.get('relevancia', 0), reverse=True)
            json_relevancia=json.dumps(json_relevancia, indent=2)
            print(json_relevancia)
    except json.JSONDecodeError:
        print("A função alinea_b retornou uma string inválida.")

# categoria=f_categoria('valein')
# carregar_mais_posts(3,categoria)
#algoritmo_c(3,'nba')
