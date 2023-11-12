#https://www.itjobs.pt/api/docs
import requests
import sys
import os
import json
import html
import re
import datetime


r=requests.get(url='https://api.itjobs.pt/job/get.json') # get json
#print(r) #Response [403]
#O código de status HTTP 403 indica que você não tem permissão para acessar o recurso solicitado na API

url = 'https://api.itjobs.pt/job/list.json?api_key=147c9727c329bd78b2f9944b5797bf8e&limit=5'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
response = requests.get(url, headers=headers)
json_result=response.json()

print('Olá, isso é uma API com pesquisas sobre vagas de emprego\n')

def csv_(dic):
     print(dic)
     nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv'
     if arquivo_existe(nome_arquivo_csv):
            novo_csv=str(input(f"O arquivo '{nome_arquivo_csv}' já existe. Deseja criar outro?(s/n): "))
            if novo_csv == 's':
                nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' 
                while arquivo_existe(nome_arquivo_csv):
                     nome_arquivo_csv = str(input('Arquivo existente.Insira outro nome: ')) + '.csv'
                adiciona_csv(dic,nome_arquivo_csv)
           
            elif novo_csv == 'n':
                 print('Será adicionado ao arquivo existente'.upper())
                 existentente_csv(dic,nome_arquivo_csv)
     else:
          adiciona_csv(dic,nome_arquivo_csv)

def adiciona_csv(dic,nome_arquivo_csv):
    with open(nome_arquivo_csv, 'w', newline='', encoding='utf-8') as arquivo_csv:
        arquivo_csv.write('titulo;empresa;descrica;data_p;salario;localizacao\n')
        for job in dic['filtros']:
            titulo = job['title']
            empresa = job['company']['name']
            if 'description' in job['company']:
                descricao = job['company']['description']
            data_p = job['publishedAt']
            if 'wage' in job:
                salario = job['wage']
            if 'locations' in job:
                localizacoes = ', '.join([local['name'] for local in job['locations']])

            descricao = descricao.replace(';', ',')  # Remover ponto e vírgula da descrição
            if 'locations' not in job:
                linha = f'{titulo};{empresa};"{descricao}";{data_p};{salario};{None}\n'
            elif 'description' not in job['company']:
                 linha=f'{titulo};{empresa};{None};{data_p};{salario};{localizacoes}\n'
            elif 'wage' not in job:
                 linha=f'{titulo};{empresa};"{descricao}";{data_p};{None};{localizacoes}\n'
            else:
                linha=f'{titulo};{empresa};"{descricao}";{data_p};{salario};{localizacoes}\n'
            arquivo_csv.write(linha)

def existentente_csv(dic,nome_arquivo_csv):
     with open(nome_arquivo_csv, 'a', encoding='utf-8') as arquivo_csv:
    # Seu código para escrever ou ler do arquivo aqui
        for job in dic['filtros']:
            titulo = job['title']
            empresa = job['company']['name']
            if 'description' in job['company']:
                descricao = job['company']['description']
            data_p = job['publishedAt']
            if 'wage' in job:
                salario = job['wage']
            if 'locations' in job:
                localizacoes = ', '.join([local['name'] for local in job['locations']])

            descricao = descricao.replace(';', ',')  # Remover ponto e vírgula da descrição
            if 'locations' not in job:
                linha = f'{titulo};{empresa};"{descricao}";{data_p};{salario};{None}\n'
            elif 'description' not in job['company']:
                 linha=f'{titulo};{empresa};{None};{data_p};{salario};{localizacoes}\n'
            elif 'wage' not in job:
                 linha=f'{titulo};{empresa};"{descricao}";{data_p};{None},{localizacoes}\n'
            else:
                linha=f'{titulo};{empresa};"{descricao}";{data_p};{salario};{localizacoes}\n'
            arquivo_csv.write(linha)

              

def arquivo_existe(nome_arquivo):
    return os.path.exists(nome_arquivo)

def top(n_jobs):
    recent_jobs={}

    for i in json_result['results']:
        job_id=i['id']
        job_time=i['publishedAt']

        # converter a string para formato data
        data_para_colocar = datetime.datetime.strptime(job_time, "%Y-%m-%d %H:%M:%S")
        # tendo uma infinidade de jobs, começamos por colocar os n primeiros jobs que aparecem
        # posterioremente subsituiremos os que tem data mais recente pelo que tem data mais antiga no dicionario
        if len(recent_jobs)<n_jobs:
            print(data_para_colocar)
            recent_jobs[job_id]=data_para_colocar
        else:

            # ordena o dicionário recent_jobs pela data (key=lambda x:x[1]), mais antigo ao mais recente, usando a lista recent_jobs.items que retorna um par de valores onde x[1] é a data
            # aplicando a função para cada uma das datas no dicionário original
            recent_jobs = {k: v for k, v in sorted(recent_jobs.items(), key=lambda x: x[1])} 
        
            for job, data_no_dicionario in recent_jobs.items():
                
                if data_no_dicionario < data_para_colocar: # verificar se é necessário substituir
                    recent_jobs[job_id] = recent_jobs.pop(f'{job}', None)
                    recent_jobs[job] = data_para_colocar          

                    break # se já substitui o valor mais antigo do dic

        lista_mais_recentes=[] # lista com as info sobre os n jobs mais recentes
        
        for ids in recent_jobs: # ir buscar na API os jobs em especifico com o /get.json e id=ids
            url = f'https://api.itjobs.pt/job/get.json?api_key=147c9727c329bd78b2f9944b5797bf8e&id={ids}'
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'})
            encontrado=res.json()
            lista_mais_recentes.append(encontrado)
            
    print(json.dumps(lista_mais_recentes, indent=2)) # match encontrados em formato JSON

    dic={'filtros': lista_mais_recentes}

    csv=str(input('Deseja inportar para formato csv(s/n)? '))

    while csv != 's' and csv != 'n':
         csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

    if csv == 's':
       csv_(dic)

def salary(id_job):
    for item in json_result['results']:
        if item['id'] == id_job:
            print(item)
            if item.get('wage') is not None:
                print(f"Salário para o ID {id_job}: {item['wage']}")
            else:
                 print('salário não encontrado'.upper())
                 print('outras informações: '.upper())
                 if 'company' in item:
                      print('Informações sobre a empresa:'.upper())
                      if 'name' in item['company']:
                           print(f'nome: {item['company']['name']}')
                      if 'phone' in item['company']:
                            print(f'phone: {item['company']['phone']}')
                 if 'ref' in item:
                    print(f'referencia: {item['ref']}')
                 lista=[]
                 if 'types' in item:
                    for d in item['types']:
                        lista.append(d['name'])
                    print(f'serviços: {lista}')
                 lista0=[]
                 if 'locations' in item:
                      for d in item['locations']:
                           lista0.append(d['name'])
                      print(f'locais: {lista0}')
            texto=item['body']
            texto2=item['company']['description']
            #print(texto2)
            padroes_texto = re.findall(r'>[/-]{0,2}.+?[/-]{0,2}<', texto)
            padroes_texto2 = re.findall(r'[A-Za-z].+?[.!?:;]', texto2)
            lista = padroes_texto + padroes_texto2
            pl_key=[
            "Salário", "Remuneração", "Vencimento", "Ordenado", "Rendimento", "Proventos",  
            "Salary", "Compensation", "Earnings", "Wage", "Pay", "Income" ,'trabalho','employes',
            'opportunities','opportunitie','oportunidade','oportunidades','benefício','benefícios'
            ]
            print('descrição da empresa:'.upper())
            print(texto2)
            print('Informações sobre o salário:'.upper())
            for frase in lista:
                for palavra in pl_key:
                    verifica=re.search(r'\b' + re.escape(palavra) + r'\b',frase,flags=re.IGNORECASE)
                    if verifica:
                            frase=re.sub(r'[^\w\s.,?!]','',frase)
                            print (frase)
                            print('------------------------')
                            break
        else:print(' id não encontardo\n consulte a lista de ids\n (python alpcdTP1gr2.py pesquisa_id())'.upper())
        break
            
def pesquisa_id():
        print('id e respectivo título:')
        print('-------------------------------')
        for item in json_result['results']:
            print(item['id'],item['title'])
        print('-------------------------------')

def search(local: str,empresa: str,n: int):
    print(local,empresa,n)
    lista_jobs = []
    for i in json_result["results"]:
        if 'locations' in i:
            for location in i['locations']:
                if location['name'] == local and i["company"]["name"] == empresa.strip():
                    if 'types' in i:
                        for job_type in i['types']:
                            if job_type['name'] == 'Full-time':
                                lista_jobs.append(i)
                                if len(lista_jobs) == n:
                                    break
        if len(lista_jobs) == n:
                                    break
    dic={
        'filtros':lista_jobs
    }
    csv=str(input('Deseja inportar para formato csv(s/n)? '))

    while csv != 's' and csv != 'n':
         csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

    if csv == 's':
       csv_(dic)


def valid_date(s): # validar o formato do input da data
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date() 
        # se o input for convertido para data com sucesso ->  retorna o objeto (string) inicial com formato padrão de data para poder ser comparado com outras datas 
    except ValueError:
        print(f"Invalid date format. Please use YYYY-MM-DD.")
    
    return None

def date(current_job, start_date, end_date): # verificar se a data de publicação encontra-se entre data_inico e data_fim
    publ_at = current_job['publishedAt'] # data de publicação do job que está a ser inspecionado no loop da função job_skills
    date = publ_at.split(' ') 
    publ_at_date = date[0] # para a data só precisamos da primeira parte

    current_date = datetime.datetime.strptime(publ_at_date, "%Y-%m-%d").date() # transforma string da data de publicação para formato de data 

    if start_date <= current_date <= end_date:
        return True
    else:
        return False


def job_skills(skills, start_date, end_date): # verificar quais os jobs que tem skills e datas requisitadas

    matching_jobs = [] # lista para os match com os argumentos introduzidos

    for job in json_result['results']: # pegar nas informações de cada job no JSON da API
        body = job['body'] # texto onde procurar as skills

        ref = re.compile(r'\b(?:' + '|'.join(map(re.escape, skills)) + r')\b', re.IGNORECASE) 
        # procurar se cada skill na lista skills (?:), na sua totalidade da palavra (\b), existe no body
        # usa-se re.escape para anular qualquer significado especial numa expressão regual e re.ignorecase para considerar palavras com maiusculas e minusculas
       
        # verifica se pelo menos um dos skills encontra se no body
        if (re.search(ref, body)):        # se ref foi encontrada no texto do body
            if date(job, start_date, end_date): # verificar se cada job que respeita a condição tem data de publicação entre as datas introduzidas no terminal
                matching_jobs.append(job)

    print(json.dumps(matching_jobs, indent=2)) # mostrar os match em formato JSON

    dic = {'filtros': matching_jobs}
    
    csv=str(input('Deseja inportar para formato csv(s/n)? '))

    while csv != 's' and csv != 'n':
         csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

    if csv == 's':
       csv_(dic)

    
def markdown(jobid, caminho):
    control=False
    for i in json_result['results']:
        if i['id']==jobid:
            teste=i
            control=True
    if control==True:
        body_html=teste["body"]
        body_text= html.unescape(body_html).replace("<p>", "").replace("</p>", "\n") 
    
        with open(caminho,"w", encoding="utf-8") as file:
            file.write(body_text)
        print("Markdown criado com sucesso!")
    else:
        print(f"Job com ID {jobid} não encontrado")



########################## Argumentos:
if len(sys.argv) < 2:
    print("Uso: python alpcdTP1gr2.py <função> <input/consulte o menu para ver se tem input>")
    sys.exit(1)


comando=sys.argv[0]
funçao=sys.argv[1]


if comando == 'alpcdTP1gr2.py':
    if len(sys.argv)==2: # N job mais recentes
        # nome_ficheiro topn
        # neste caso só tem esta opção que tem len==2 as outras tem mais args
        # encotrar o número de trabalhos que quer com o nº colocado no final de 'top'
        match = re.search(r'\b(top)(\d+)\b', sys.argv[1]) # () para fazer grupos
        if match: # se o arg começar por top e tiver numeros depois então ....
            n_jobs = int(match.group(2)) # quantidade de jobs mais recentes
            toplst=top(n_jobs)
    if funçao == 'salary': 
        id_job = int(sys.argv[2])
        salary(id_job)
    if funçao =='pesquisa_id':
        pesquisa_id()
    if funçao == 'search' and len(sys.argv) >= 5:
        local=str(sys.argv[2])
        empresa_args = sys.argv[3:-1]
        empresa = ' '.join(empresa_args)
        n=int(sys.argv[-1])
        search(local,empresa,n)
    if funçao == 'skills': # nome_ficheiro nome_funcao skills data_inico data_fim
        skills=sys.argv[2] 
        skills=skills.split(', ') # criar a lista de skills , meti espaço depois de ' para não incluir o espaço no abjeto que é criado
        start_date = valid_date(sys.argv[3]) 
        if start_date is not None:
            end_date = valid_date(sys.argv[4]) 
            if end_date is not None:
                matching_jobs = job_skills(skills, start_date, end_date)        
        
    if funçao == 'markdown':
         jobid=int(sys.argv[2])
         caminho= sys.argv[3:][0]
         markdown(jobid,caminho)
    else: print('Função inválida'.upper())

else:
    print(f"Comando '{comando}' não reconhecido.")


    

