import requests as re
import json
import time
import pandas as pd
from tqdm import tqdm

#parâmetros para requisiçã
ano_pesquisa = int(input("Ano de pesquisa de servidores: "))
mes_pesquisa = int(input("Mês de pesquisa de servidores: "))
size_pagina = 20

#Fazendo a requisição
url= 'https://api.transparencia.rr.gov.br/api/v1/portal/transparencia/pesquisar-remuneracoes'
params = {'mes':mes_pesquisa, 'ano':ano_pesquisa, 'size':size_pagina}
resposta = re.get(url, params=params)
pagina_principal = json.loads(resposta.text)

#pegando quantidade de páginas com size = 20
nmr_page = list(range(pagina_principal["data"]["totalPages"]))

################################################################################################

df = pd.DataFrame()

#interando nas páginas
for num_pag in tqdm(nmr_page, desc="Processando páginas", leave=False):

    headers = {'accept': '*/*',}
    params_0 = {'mes': mes_pesquisa, 'ano':ano_pesquisa, 'page': num_pag, 'size':size_pagina}
    req = re.get(url, params=params_0, headers=headers)
        
    for i in range(size_pagina):
        contador = 5
        while contador > 0:
            try:
                pag = json.loads(req.text)
                elemento = pag["data"]["content"][i]
            except IndexError: # Se não houver mais elementos na página, saia do loop
                break  
            except json.JSONDecodeError as e:
                contador -= 1
                print(f'Erro {e}| retando {contador} tentativas')
                time.sleep(2)

        else:
        #declarando o dataframe secundário
            df_data = pd.DataFrame({
                'matricula': elemento["matricula"],
                'nome': elemento["nome"],
                'cpf_part': elemento["cpf"],
                'mes': elemento["mes"],
                'ano': elemento["ano"],
                'cargo': elemento["cargo"],
                'orgao': elemento["orgao"],
                'valor_bruto': elemento["remuneracaoBruta"],
                'valor_liquido': elemento["remuneracaoLiquida"]}, 
                index=[0]) 
         
        #unindo os dataframes    
        df = pd.concat([df, df_data], axis=0)     

df.to_csv(f'Bases/servidores_RR_{mes_pesquisa}{ano_pesquisa}.csv', index=False)