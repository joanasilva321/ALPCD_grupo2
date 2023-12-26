
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
        pagina = soup.find('section', slot='page-1')
        z = pagina.find_all('article', class_='m-0')
        in_n_posts = len(z)
        time.sleep(8)
        if in_n_posts < n_posts:
            n_interacoes += 1
        else: break
    driver.quit()
    return soup
s=carregar_mais_posts(60,'https://www.reddit.com/t/kim_kardashian/')
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

def comentarios(url):
    lista_comentarios=[]
    soup=carrega_mais_comentarios(url)
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
        return lista_comentarios
#comentarios('https://www.reddit.com/r/valheim/comments/15o9jfh/shifte_chest_reason_for_removal_from_valheim/')

def alinea_b (limite,categoria):
    categoria=f_categoria(categoria)
    if categoria is not None:
        lista_b=[]
        soup=carregar_mais_posts(limite,categoria)
        pagina=soup.find('section', slot='page-1')
        z=pagina.find_all('article', class_='m-0')
        n=0
        for i in z:
            dici_post={}
            time=str(i.find('faceplate-timeago')) # data
            tempo=re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}',time)
            tempo=tempo[0]
            tempo=datetime.fromisoformat(tempo)
            titulo=i.find('a', slot='title')
            title= titulo.text.strip()# titulo
            subredit=str(i.find('shreddit-async-loader', bundlename='faceplate_hovercard')) # subreddit
            s_redit= re.findall(r'href=".*?"',subredit )
            s_redit=s_redit[0]
            s_redit=re.sub('href=','',s_redit)
            s_redit=re.sub('"','',s_redit)
            parte_central = s_redit.strip('/') # subredit
            votos=str(i.find('shreddit-post', class_='block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] px-md py-2xs my-2xs nd:visible'))
            v=re.findall(r'score=".*?"',votos)
            if len(v)>0: 
                v=v[0]
                v=re.sub(r'score="','',v)
                v=re.sub(r'"','',v)
            coment=re.findall(r'href=".*?"', str(titulo))
            coment=coment[0]
            coment=re.sub(r'href=','',coment)
            coment=re.sub(r'"','',coment)
            dici_post['title']=title
            dici_post['subreddit']=parte_central
            dici_post['score']=v
            dici_post['time']=tempo
            dici_post['x']=coment
            lista_b.append(dici_post)
        lista_ordenada = sorted(lista_b, key=lambda x: x['time'], reverse=True)
        lista_final=[]
        for j in range (limite):
            cm=lista_ordenada[j]['x']
            url=f'https://www.reddit.com{cm}'
            lista_ordenada[j]['comments']=comentarios(url)
            del lista_ordenada[j]['x']
            del lista_ordenada[j]['time']
            lista_final.append(lista_ordenada[j])
        json_string = json.dumps(lista_final, indent=2)
        return json_string
    else: 
        print('Tópico não encontrado')
        return None

def f_categoria(categoria):
    lista_cat=[]
    urlx='https://www.reddit.com/'
    driver = webdriver.Chrome()
    driver.get(urlx)
    time.sleep(5)
    #res=requests.get(urlx)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()
    topicos=soup.find('faceplate-auto-height-animator', class_='block')
    #escondido=soup.find('details', class_='p-0 m-0 bg-transparent border-none rounded-none')
    cada=topicos.find_all('left-nav-topic-tracker', noun='topic_item')
    for i in cada:
        dict={}
        t=i.find('span', class_='flex flex-col justify-center min-w-0 shrink py-[var(--rem6)]')
        t=t.text.strip()
        href=i.find('li', role='presentation')
        r=re.findall(r'href=".*?"',str(href))
        r=r[0]
        r=re.sub(r'href=','',r)
        r=re.sub(r'"','',r)
        dict['topico']=t
        dict['ref']=r
        lista_cat.append(dict)
    topicos = [dicionario['topico'].lower() for dicionario in lista_cat]
    palavra_proxima = get_close_matches(categoria.lower(), topicos)
    if palavra_proxima:
        topico=palavra_proxima[0]
        for d in lista_cat:
            if d['topico'].lower()== topico.lower():
                categoria=d['ref']
        print(categoria)
        return categoria
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

#algoritmo_c(3, 'nba')
