#https://www.itjobs.pt/api/docs
import requests # para a url
import sys # arguementos no terminal
import os # função arquivo_existes
import json # para por em formato json
import html # função markdown
import re # para utilizar expressoes regulares
import datetime # para datas


r=requests.get(url='https://api.itjobs.pt/job/get.json') # get json
#print(r) #Response [403]
#O código de status HTTP 403 indica que você não tem permissão para acessar o recurso solicitado na API

url = 'https://api.itjobs.pt/job/list.json?api_key=147c9727c329bd78b2f9944b5797bf8e&limit=1600'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
response = requests.get(url, headers=headers)
json_result=response.json()

#menu
def menu():
    print('bem-vindo!isso é uma API com pesquisas sobre empregos.\n'.upper())
    print('Funcionalidades:\n'.upper())
    print('1:Trabalhos mais recentes: \npython alpcdTP1.py top<nº de empregos>\n')
    print('2:Trabalho com filtro(empresa,localidade): \npython alpcdTP1.py search <localidade> <nome empresa> <nº de empregos>\n')
    print('3:Pesquisa de IDS dos empregos: \npython alpcdTP1.py pesquisa_id\n')
    print('4:Pesquisa do salário com base no id do emprego: \npython alpcdTP1.py salary <id>\n')
    print('5:Trabalhos com filtro de skills exigidas e com filtro de período de data publicação: \npython alcdTP1gr2.py job_skills <skill 1>,<skill n> <data início aaaa-mm-dd> data fim aaaa-mm-dd\n')
    print('6:Transformar as informações de um ID(emprego) em markdown e guardar em um ficheiro: \npython alpcdTP1gr2.py markdown <id> <caminho do ficheiro>\n')
    print('7:As informações filtradas das funcionalidades 1,2 e 5 podem ser guardadas em csv!\n')

#confere se já existe um arquivo csv com o nome escolhido e direciona para as funções adiciona_csv ou existente_csv
def csv_(dic):
     print(dic)
     nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' #input nome.csv
     if arquivo_existe(nome_arquivo_csv): #chama a função que verifica a existência dos arquivos
            novo_csv=str(input(f"O arquivo '{nome_arquivo_csv}' já existe. Deseja criar outro?(s/n): "))
            if novo_csv == 's':
                nome_arquivo_csv = str(input('Qual será o nome do arquivo? ')) + '.csv' 
                while arquivo_existe(nome_arquivo_csv):
                     nome_arquivo_csv = str(input('Arquivo existente.Insira outro nome: ')) + '.csv'
                adiciona_csv(dic,nome_arquivo_csv) #funçao que cria csv
           
            elif novo_csv == 'n':
                 print('Será adicionado ao arquivo existente'.upper())
                 existentente_csv(dic,nome_arquivo_csv) # função que adiciona csv
     else:
          adiciona_csv(dic,nome_arquivo_csv)
# função que cria um novo csv
def adiciona_csv(dic,nome_arquivo_csv):
    with open(nome_arquivo_csv, 'w', newline='', encoding='utf-8') as arquivo_csv: 
        arquivo_csv.write('titulo;empresa;descrica;data_p;salario;localizacao\n') #cabeçalho e dados das colunas separados por ';'
        for job in dic['filtros']: #para cada id 
            titulo = job['title']
            empresa = job['company']['name']
            data_p = job['publishedAt']
            salario = job['wage']

            if  'locations' not in job and 'description' not in job: # se essas chaves não estiverem presentes para um certo id
                linha=f'{titulo};{empresa};"{None}";{data_p};{salario};{None}\n' # registro
            elif 'locations' not in job: # têm ids que não contém localização ou descrição
                descricao = job['company']['description']
                descricao = descricao.replace(';', ',')
                linha = f'{titulo};{empresa};"{descricao}";{data_p};{salario};{None}\n'# registro
            elif 'description' not in job['company']:
                 localizacoes = ', '.join([local['name'] for local in job['locations']])
                 linha=f'{titulo};{empresa};{None};{data_p};{salario};{localizacoes}\n' #registro
            else:
                descricao = job['company']['description']
                descricao = descricao.replace(';', ',') # substitui todas ';' do texto da descrição por ',' para não causar problema na hora de separar os dados nas colunas
                localizacoes = ', '.join([local['name'] for local in job['locations']]) # o value da chave 'locations' é uma lista, para pegar cada value de cada dici da lista cuja chave é 'name'
                linha=f'{titulo};{empresa};"{descricao}";{data_p};{salario};{localizacoes}\n' # registro
            arquivo_csv.write(linha) # escrever a 'linha' em cada registro no arquivo
#função que adiciona os dados em um csv existente
def existentente_csv(dic,nome_arquivo_csv):
     with open(nome_arquivo_csv, 'a',newline='', encoding='utf-8') as arquivo_csv: # 'a' porque o csv já existe
        for job in dic['filtros']: #para cada id 
            titulo = job['title']
            empresa = job['company']['name']
            data_p = job['publishedAt']
            salario = job['wage']
        
            if  'locations' not in job and 'description' not in job: # se essas chaves não estiverem presentes para um certo id
                linha=f'{titulo};{empresa};"{None}";{data_p};{salario};{None}\n' #registro
            elif 'locations' not in job:
                descricao = job['company']['description']
                descricao = descricao.replace(';', ',')
                linha = f'{titulo};{empresa};"{descricao}";{data_p};{salario};{None}\n' #registro
            elif 'description' not in job['company']:
                 localizacoes = ', '.join([local['name'] for local in job['locations']])
                 linha=f'{titulo};{empresa};{None};{data_p};{salario};{localizacoes}\n' #registro
            else:
                descricao = job['company']['description']
                descricao = descricao.replace(';', ',')
                localizacoes = ', '.join([local['name'] for local in job['locations']])
                linha=f'{titulo};{empresa};"{descricao}";{data_p};{salario};{localizacoes}\n' #registro
            arquivo_csv.write(linha) # escrever a 'linha' para cada registro
#função que verifica os nomes dos csvs na pasta      
def arquivo_existe(nome_arquivo):
    return os.path.exists(nome_arquivo)
# top n jobs mais recentes
def top(n_jobs):
    recent_jobs={}

    for i in json_result['results']: # cada job na api
        job_id=i['id'] # id do job
        job_time=i['publishedAt'] # data de publicação do job

        # converter a string para formato data
        data_para_colocar = datetime.datetime.strptime(job_time, "%Y-%m-%d %H:%M:%S")
        # tendo uma infinidade de jobs, começamos por colocar os n primeiros jobs que aparecem
        # posterioremente subsituiremos os que tem data mais recente pelo que tem data mais antiga no dicionario
        recent_jobs[job_id]=data_para_colocar
    # ordena o dicionário recent_jobs pela data (key=lambda x:x[1]), mais antigo ao mais recente, usando a lista recent_jobs.items que retorna um par de valores onde x[1] é a data
    # aplicando a função para cada uma das datas no dicionário original
    recent_jobs = {k: v for k, v in sorted(recent_jobs.items(), key=lambda x: x[1])} 
    recent_jobs = list(recent_jobs.items())   # transformar em lista
    recent_jobs = recent_jobs[:n_jobs]  # poder pegar nos n primeiros

    n_recentes=[]
    for ids in recent_jobs: # ir buscar na API os jobs em especifico com o /get.json e id=ids
        url = f'https://api.itjobs.pt/job/get.json?api_key=147c9727c329bd78b2f9944b5797bf8e&id={ids[0]}'
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'})
        encontrado=res.json()
        n_recentes.append(encontrado)
        
    print(json.dumps(n_recentes, indent=2)) # match encontrados em formato JSON

    dic={'filtros': n_recentes}

    csv=str(input('Deseja inportar para formato csv(s/n)? '))

    while csv != 's' and csv != 'n':
         csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

    if csv == 's':
       csv_(dic)
#salario para um certo id
def salary(id_job):
    for item in json_result['results']: # para cada id
        if item['id'] == id_job: # se o id corresponde ao id do input
            if item.get('wage') is not None: # se o salario não é 'null':
                print(f"Salário para o ID {id_job}: {item['wage']}") #printa o salário
            else: # se o salário é 'null':
                 print('salário não encontrado'.upper())
                 print('outras informações: '.upper())
                 if 'company' in item: # se a chave company existe para o id do input
                      print('Informações sobre a empresa:'.upper())
                      if 'name' in item['company']: # se a chave 'name' existe
                           print(f'nome: {item['company']['name']}') # nome da empresa
                      if 'phone' in item['company']:
                            print(f'phone: {item['company']['phone']}') #tel da empresa
                 if 'ref' in item:
                    print(f'referencia: {item['ref']}') #nº dereferencia
                 lista=[] # lista de tipos de serviços
                 if 'types' in item: 
                    for d in item['types']: #para cada dicionario da chave type
                        lista.append(d['name'])
                    print(f'serviços: {lista}')
                 lista0=[] # lista de lugares
                 if 'locations' in item:
                      for d in item['locations']: # para cada dicionario da chave 'locations'
                           lista0.append(d['name'])
                      print(f'locais: {lista0}')
            texto=item['body'] # texto é o value da chave 'body'
            padroes_texto = re.findall(r'>[/-]{0,2}.+?[/-]{0,2}<', texto) # separar as frases do body (as frases começam > e terminam <) em elemntos de uma lista
            if 'description' in item['company']:
                texto2=item['company']['description']
                padroes_texto2 = re.findall(r'[A-Za-z].+?[.;]', texto2) # separar as frases da descrição(começa com letra maíscula ou minuscila e termina com sinal de pontuação(. ou ;)) em elentos de uma lista
                lista = padroes_texto + padroes_texto2 # jusntar as duas listas acima em uma lista
            else:
                lista = padroes_texto # de a descriçao nao existir
            pl_key=[ # palavras chaves para salário:
            "Salário", "Remuneração", "Vencimento", "Ordenado", "Rendimento", "Proventos",  
            "Salary", "Compensation", "Earnings", "Wage", "Pay", "Income" ,'trabalho','employes',
            '$','£','portunidades','oportunidade','euros','dolar'
            ]
            if 'description' in item['company']:
                print('descrição da empresa:'.upper())
                print(texto2) 
            print('Informações sobre o salário:'.upper())
            for frase in lista: #para cada frase na lista
                for palavra in pl_key: #para cada palavra na lsita de palavras chaves
                    verifica=re.search(r'\b' + re.escape(palavra) + r'\b',frase,flags=re.IGNORECASE) # verifica se a palavra chave está na frase
                    if verifica: # se estiver:
                            frase=re.sub(r'[^\w\s.,?!]','',frase) # tira o que não for letras, numeros e pontuação da frase, exemplo: <\
                            print (frase) # printa a frase
                            print('------------------------')
                            break
            break
    else:print(' id não encontardo\n consulte a lista de ids\n (python alpcdTP1gr2.py pesquisa_id())'.upper()) #input(id) inexistente
# mostra os ids existentes e o nome associado          
def pesquisa_id():
        print('id e respectivo título:')
        print('-------------------------------')
        for item in json_result['results']: #para cada id
            print(item['id'],item['title']) #mostra o id e o título associado
        print('-------------------------------')
#pesquisa de trabalhos full-time associado ao local, nome da empresa
def search(local: str,empresa: str,n: int):
    lista_jobs = [] #lista dos empregos
    for i in json_result["results"]:
        if 'locations' in i: #verifica se existe localização
            for location in i['locations']:
                #verifica a localidade e a empresa
                if location['name'] == local and i["company"]["name"] == empresa.strip():
                    if 'types' in i:
                        for job_type in i['types']:
                            if job_type['name'] == 'Full-time': #verifica se são trabalhos full-time
                                lista_jobs.append(i)
                                if len(lista_jobs) == n: #adiciona só o número de empregos pedido
                                    break
        if len(lista_jobs) == n:
                                    break

    #dicionário com os empregos
    dic={
        'filtros':lista_jobs
    }
    
    print(json.dumps(lista_jobs, indent=2)) #match encontrados em formato JSON
    
    csv=str(input('Deseja inportar para formato csv(s/n)? ')) #funcionalidade 7

    while csv != 's' and csv != 'n': #verifica se o input é s ou n
         csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

    if csv == 's': #se for s cria o csv
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


    matching_jobs = []
# verificar quais os jobs que tem skills e datas requisitadas
def job_skills(skills, start_date, end_date): 

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

                # se já encontrou pelo menos um skill vai procurar nos outros jobs restantes


    print(json.dumps(matching_jobs, indent=2)) # mostrar os match em formato JSON

    dic = {'filtros': matching_jobs}

    csv=str(input('Deseja inportar para formato csv(s/n)? '))

    while csv != 's' and csv != 'n':
         csv=str(input('Insira (s) para sim ou (n) para não, minúsculo: '))

    if csv == 's':
       csv_(dic)
# markdown de um id
def markdown(jobid, caminho):
    control=False #controla a criação do markdown
    for i in json_result['results']:
        if i['id']==jobid: #verifica se o id existe
            job=i
            control=True
    if control==True: #se for True então existe o id e cria o ficheiro
        body_html=job["body"] #pega o body do trabalho
        body_text= html.unescape(body_html).replace("<p>", "").replace("</p>", "\n") #tranforma o body em texto
    
        with open(caminho,"w", encoding="utf-8") as file: #cria o ficheiro com o caminho dado
            file.write(body_text)
        print("Markdown criado com sucesso!")
    else: #se control for false, não existe o id dado
        print(f"Job com ID {jobid} não encontrado")

########################## TERMINAL:
if len(sys.argv) < 2: # se no comando o cliente escrever menos do que o padrão exigido interrompe o programa
    print('Erro\nConsulte o menu:')
    menu()
    sys.exit(1) # trava

comando=sys.argv[0] # primeiro argumento
funçao=sys.argv[1] # segundo argumento


if comando == 'alpcdTP1gr2.py':

    if funçao == 'pesquisa_id': # se a funçao for pesquisa_id:
        pesquisa_id() # chama
    elif len(sys.argv)==2: # N job mais recentes
        # nome_ficheiro topn
        # encotrar o número de trabalhos que quer com o nº colocado no final de 'top'
        match = re.search(r'\b(top)(\d+)\b', sys.argv[1]) # () para fazer grupos, ver se começa por top e acaba por um número
        if match: # se o arg começar por top e tiver numeros depois então ....
            n_jobs = int(match.group(2)) # quantidade de jobs mais recentes
            toplst=top(n_jobs)
    if funçao == 'salary': 
        id_job = int(sys.argv[2])
        salary(id_job)
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
    elif funçao == 'markdown': # se função é markdown:
         jobid=int(sys.argv[2])# id é o 2º arg
         caminho= sys.argv[3:][0] # caminho é do 3º arg ao último
         markdown(jobid,caminho) # chama
    else: print('Função inválida.Consulte o menu:'.upper()) # inseriu função inexistente
    menu()

else:
    print(f"Comando '{comando}' não reconhecido.")



    
