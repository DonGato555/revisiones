from bs4 import BeautifulSoup
import requests
import pandas as pd
pd.options.display.max_columns = None

import datetime



segundos= 60
minutos= 1
intervalo = segundos * minutos

from pytz import timezone
  
# using now() to get current time 
current_time = datetime.datetime.now(timezone('America/Bogota')) 

dia = current_time.strftime("%d")
mes = current_time.strftime("%m")
anio = current_time.strftime("%Y")

#dia='18'
##########
#VARIABLES#

fecha = anio+'-'+mes+'-'+dia

print('FECHA DE CONSULTA: ',fecha,"\n################")

zonales = ['PRONACA']
#fecha = 'day(d.dmddate)= '+dia+' and month(d.dmddate)= '+mes+' and year(d.dmddate)= '+anio+''
#fecha = anio+'-'+mes+'-'+dia

consulta = consulta = "select top(50) \
brcCode as Regional, \
sum(case when dmdCancelOrder='0' and doccode='ped' then 1 else 0 end) TotalPedidos, \
sum(case when dmdCancelOrder='0' and doccode='dev' then 1 else 0 end) TotalDevoluciones, \
sum(case when (_processMessage='-0' OR _processMessage like'%exito%') and doccode='ped' then 1 else 0 end) PedidosExito, \
sum(case when (_processMessage='-0' OR _processMessage like'%exito%') and doccode='dev' then 1 else 0 end) DevolucionesExito, \
sum(case when dmdCancelOrder='0' and dmdprocess='0' and doccode='ped' then 1 else 0 end) pSINPROCESAR, \
sum(case when dmdCancelOrder='0' and dmdprocess='0' and doccode='dev' then 1 else 0 end) dSINPROCESAR, \
sum(case when (_processMessage like'%transito%') and doccode='ped' then 1 else 0 end) PTransito, \
sum(case when (_processMessage like'%transito%') and doccode='dev' then 1 else 0 end) DTransito, \
sum(case when (_processMessage like'%soap%') and doccode='ped' then 1 else 0 end) PSoap, \
sum(case when (_processMessage like'%soap%') and doccode='dev' then 1 else 0 end) DSoap, \
sum(case when (_processMessage like'%error%') and doccode='ped' then 1 else 0 end) PErr, \
sum(case when (_processMessage like'%error%') and doccode='dev' then 1 else 0 end) DErr, \
sum(case when (_processMessage like'%existente%') and doccode='ped' then 1 else 0 end) PExistente, \
sum(case when (_processMessage like'%existente%') and doccode='dev' then 1 else 0 end) DExistente \
from demand where convert(date,dmddate,101)= '"+fecha+"' and rotcode in(select rotcode from route where rotDummy1='PDA'  and chaCode='V01' and _deleted='0' and rotInactive='0') group by brcCode"



#################################
### OBTENEMOS SESION Y COOKIES###

def obtener_sesion(zonal):    
    session = requests.Session()
    payload = {'connectionName':''+zonal+'_XSS_441_PRD'}
    s = session.get("https://prd1.xsalesmobile.net/"+zonal+"/xsm/Login/Index")
    cc = s.cookies['ASP.NET_SessionId']
    s = session.post("https://prd1.xsalesmobile.net/"+zonal+"/xsm/Login/validatedSession")
    s = session.post("https://prd1.xsalesmobile.net/"+zonal+"/xsm/Login/serverVersion")
    s = session.post("https://prd1.xsalesmobile.net/"+zonal+"/xsm/Login/DisplayDDListConnections")
    s = session.post("https://prd1.xsalesmobile.net/"+zonal+"/xsm/Login/setConnection", data=payload)
    s = session.post("https://prd1.xsalesmobile.net/"+zonal+"/xsm/Login/SetLanguage")

    return cc

#########################
### LOGEAMOS LA SESION###

def logear_sesion(cc,zonal):
    
    cookies = {
        'ASP.NET_SessionId': cc,
    }

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Referer': 'https://prd1.xsalesmobile.net/'+zonal+'/xsm/Login/Index',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': '0',
        'Origin': 'https://prd1.xsalesmobile.net',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    data = {
      'connectionName': ''+zonal+'_XSS_441_PRD',
      'username': 'Soporte.nuo',
      'password': 'Nuo2020*'
    }

    response = requests.post('https://prd1.xsalesmobile.net/'+zonal+'/xsm/Login/userLogonServer', headers=headers, cookies=cookies, data=data)


######################
### OBTENEMOS EVENT###

def obtener_event(cc,zonal):

    cookies = {
        'ASP.NET_SessionId': cc,
    }

    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://prd1.xsalesmobile.net/'+zonal+'/xsm/app/css/global.css?vcss=20191107',
        'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Origin': 'https://prd1.xsalesmobile.net',
    }

    response = requests.get('https://prd1.xsalesmobile.net/'+zonal+'/xsm/app/webForms/webTools/sqlQuery/DBQueryUI.aspx', headers=headers, cookies=cookies)

    html_brute = response.text
    soup = BeautifulSoup(html_brute, "html.parser")

    fragmentList = soup.findAll("input")
    ff = soup.find("input", {"id": "__EVENTVALIDATION"})
    ee= ff.get('value')

    return ee


#############################
### EJECUTAMOS LA CONSULTA###

def ejecutar_consulta(cc,ee,zonal):

    cookies = {
        'ASP.NET_SessionId': cc,
    }    

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://prd1.xsalesmobile.net',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.197',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://prd1.xsalesmobile.net/'+zonal+'/xsm/app/css/global.css?vcss=20191107',
        'Accept-Language': 'es-ES,es;q=0.9',
    }

    
    data = {
      '__EVENTTARGET': '',
      '__EVENTARGUMENT': '',
      '__LASTFOCUS': '',
      '__VIEWSTATE': '',
      'Ddl_BaseDatos': ''+zonal+'_XSS_441_PRD',
      'optradio': 'Rb_DecimalCo',
      'TxtSql': consulta,
      'lblBtnExecute': 'Ejecutar',
      'ddlExport': '-1',
      '__SCROLLPOSITIONX': '0',
      '__SCROLLPOSITIONY': '0',
      '__EVENTVALIDATION': ee
    }

    response = requests.post('https://prd1.xsalesmobile.net/'+zonal+'/xsm/app/webForms/webTools/sqlQuery/DBQueryUI.aspx', headers=headers, cookies=cookies, data=data)


    html_brute = response.text
    soup = BeautifulSoup(html_brute, "html.parser")
    fragmentList = soup.findAll("table")
    opciones = soup.findAll("option")
    print(zonal, " : " ,opciones[0]['value'])
    if len(fragmentList)>0:
        df_list = pd.read_html(response.text) # this parses all the tables in webpages to a list
        df = df_list[0]
        #df.head()
        print(df)
    else:
        print("No hay informacion")
    
    

def principal(zonal):
    cc = obtener_sesion(zonal)
    logear_sesion(cc,zonal)
    ee = obtener_event(cc,zonal)
    ejecutar_consulta(cc,ee,zonal)

    
for zonal in zonales:
    principal(zonal)
print("#############################")




