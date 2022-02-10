#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:18:40.139388
#+ Editado:	2022/02/10 20:32:08.567780
# ------------------------------------------------------------------------------
import os
import sqlite3
from sqlite3 import Connection, Cursor, IntegrityError
from typing import Dict, List, Union


from uteis.ficheiro import cargarJson, cargarFich
from uteis.imprimir import jprint

from coinmarketcap_scrapper import CoinMarketCap
from coingecko_api import CoinGecko


from .dtos import Divisa_Tipo, Divisa, Paxina, Top, Topx
from .excepcions import TaboaInexistenteErro, TopxNonNumeroErro, PaxinaNonExistenteErro
from .uteis_local import nulo_se_baleiro
# ------------------------------------------------------------------------------
def coller_todo_taboa(cur: Cursor, taboa: str) -> List[Union[Divisa_Tipo, Divisa, Paxina, Top, Topx]]:

    taboas = {
            'paxina': coller_todo_paxina,
            'divisa_tipo': coller_todo_divisa_tipo,
            'divisa': coller_todo_divisa
            }
    try:
        return taboas[taboa](cur)
    except KeyError:
        raise TaboaInexistenteErro
    except Exception as e:
        raise e

def coller_todo_paxina(cur: Cursor) -> List[Paxina]:
    paxinas = []
    for linha in cur.execute('select * from paxina').fetchall():
        paxinas.append(Paxina(
            id_= linha[0],
            nome= linha[1],
            ligazon = linha[2]
            ))
    return paxinas
# ------------------------------------------------------------------------------
def coller_ou_insertar_taboa(cur: Cursor, taboa: str, valores: Union[List[str], List[Dict[str, str]]]) -> List[Union[Divisa_Tipo, Divisa, Paxina]]:
    taboas = {
            'paxina': coller_ou_insertar_paxina,
            'divisa_tipo': coller_ou_insertar_divisa_tipo,
            'divisa': coller_ou_insertar_divisa
            }
    try:
        return taboas[taboa](cur, valores)
    except KeyError:
        raise TaboaInexistenteErro
    except Exception as e:
        raise e

def coller_ou_insertar_paxina(cur: Cursor, valores: List[Dict[str, str]]) -> List[Paxina]:
    paxinas = []
    for valor in valores:
        dato = cur.execute(f'''select * from paxina where nome="{valor['nome']}"''').fetchone()

        if dato:
            paxinas.append(Paxina(
                id_= dato[0],
                nome= dato[1],
                ligazon= dato[2],
                data = dato[3]
                ))
        else:
            while True:
                try:
                    nova_paxina = Paxina(
                                        nome= valor['nome'],
                                        ligazon= valor['ligazon']
                                        )
                    cur.execute('insert into paxina("nome", "ligazon", "data")'\
                            f' values("{nova_paxina.nome}", "{nova_paxina.ligazon}", "{nova_paxina.data}")')

                    nova_paxina.id_ = coller_ou_insertar_paxina(cur, [{'nome': nova_paxina.nome}])[0].id_
                except IntegrityError:
                    pass
                except Exception as e:
                    raise e
                else:
                    paxinas.append(nova_paxina)
                    break

    return paxinas

def coller_ou_insertar_divisa_tipo(cur: Cursor, nomes: List[str]) -> List[Divisa_Tipo]:
    divisa_tipos = []
    for nome in nomes:
        dato = cur.execute(f'select * from divisa_tipo where nome="{nome}"').fetchone()

        if dato:
            divisa_tipos.append(Divisa_Tipo(
                id_= dato[0],
                nome= dato[1]
                ))
        else:
            while True:
                try:
                    nova_divisa_tipo = Divisa_Tipo(nome= nome)
                    cur.execute('insert into divisa_tipo("id", "nome", "data")'\
                            f' values("{nova_divisa_tipo.id_}", "{nova_divisa_tipo.nome}", "{nova_divisa_tipo.data}")')
                except IntegrityError:
                    pass
                except Exception as e:
                    raise e
                else:
                    divisa_tipos.append(nova_divisa_tipo)
                    break

    return divisa_tipos

def coller_ou_insertar_divisa(cur: Cursor, valores: List[Dict[str, str]]) -> List[Divisa]:
    divisas = []
    for valor in valores:
        dato = cur.execute(f'''select * from divisa where nomesigla="{valor['nome']+valor['siglas']}"''').fetchone()

        if dato:
            divisas.append(Divisa(
                id_= dato[0],
                simbolo= dato[1],
                nome= dato[2],
                siglas= dato[3],
                nomesigla= dato[4],
                data= dato[5],
                id_tipo= dato[6]
                ))
        else:
            while True:
                try:
                    nova_divisa = Divisa(
                                    simbolo= valor['simbolo'],
                                    nome= valor['nome'],
                                    siglas= valor['siglas'],
                                    nomesigla= valor['nome']+valor['siglas'],
                                    id_tipo = coller_ou_insertar_divisa_tipo(cur, [valor['tipo']])[0].id_
                                    )

                    cur.execute('insert into divisa("id", "simbolo", "nome", "siglas", "nomesigla", "id_tipo", "data")'\
                            f' values("{nova_divisa.id_}", ?, "{nova_divisa.nome}", "{nova_divisa.siglas}",'\
                            f' "{nova_divisa.nomesigla}", "{nova_divisa.id_tipo}", "{nova_divisa.data}")',
                            (nulo_se_baleiro(nova_divisa.simbolo),))
                except IntegrityError:
                    pass
                except Exception as e:
                    raise e
                else:
                    divisas.append(nova_divisa)
                    break

    return divisas
# ------------------------------------------------------------------------------
def insertar_taboa(cur: Cursor, clase: Union[Top, Topx]) -> int:
    taboas = {
            Top : insertar_top,
            Topx: insertar_topx
            }
    try:
        return taboas[type(clase)](cur, clase)
    except KeyError:
        raise TaboaInexistenteErro
    except Exception as e:
        print(clase)
        raise e

def insertar_top(cur: Cursor, top: Top) -> int:
    # soamente insertar
    cur.execute('insert into top(data, id_paxina) '\
            f'values("{top.data}", "{top.id_paxina}")')
    return cur.execute('select id from top order by id desc').fetchone()[0]

def insertar_topx(cur: Cursor, topx: Topx) -> int:
    try:
        cur.execute('insert into topx(id_divisa, id_top, data, posicion, prezo, id_divisa_ref) '\
            f'values("{topx.id_divisa}", "{topx.id_top}", "{topx.data}", "{topx.posicion}"'\
            f', "{topx.prezo}", "{topx.id_divisa_ref}")')
    except IntegrityError:
        print(f'Duplicado {topx}')
        pass
    return -1
# ------------------------------------------------------------------------------
def get_topx_CMC(cur: Cursor, topx: int, divisas_ref: List[Divisa], id_top: int) -> List[Topx]:
    if DEBUG: print('* Collendo o top de CoinMarketCap')
    l_topsx = []

    # este non vai utilizar o das divisas porque os prezos sempre os da en dolar
    for divisa_ref in divisas_ref:
        if divisa_ref.simbolo == '$':
            break

    for moeda in CoinMarketCap().get_top(topx):
        temp_divisa = coller_ou_insertar_divisa(cur, [{
                                        'simbolo': '',
                                        'nome': moeda['nome'],
                                        'siglas': moeda['simbolo'],
                                        'tipo': 'criptomoeda'
                                        }])[0]
        temp_topx = Topx(
            id_divisa       = temp_divisa.id_,
            id_top          = id_top,
            posicion        = moeda['posicion'],
            prezo           = moeda['prezo'].replace(',',''),
            id_divisa_ref   = divisa_ref.id_
            )

        insertar_taboa(cur, temp_topx)
        l_topsx.append(temp_topx)

    return l_topsx

def get_topx_CG(cur: Cursor, topx: int, divisas_ref: List[Divisa], id_top: int) -> List[Topx]:
    if DEBUG: print('* Collendo o top de CoinGecko')
    l_topsx = []

    # xFCR: TEMPORAL
    for divisa_ref in divisas_ref:
        if divisa_ref.simbolo == '$':
            break

    lista_moedas = CoinGecko().get_coins()
    if topx != 0:
        lista_moedas = lista_moedas[:topx]

    for index, moeda in enumerate(lista_moedas, 1):
        temp_divisa = coller_ou_insertar_divisa(cur, [{
            'simbolo': '',
            'nome': moeda['name'],
            'siglas': moeda['symbol'].upper(),
            'tipo': 'criptomoeda'
        }])[0]

        temp_topx = Topx(
            id_divisa       = temp_divisa.id_,
            id_top          = id_top,
            posicion        = index,
            prezo           = moeda['market_data']['current_price']['usd'],
            id_divisa_ref   = divisa_ref.id_
        )

        insertar_taboa(cur, temp_topx)
        l_topsx.append(temp_topx)

        #for divisa_ref in divisas_ref:

    return l_topsx

def get_topsx(cur: Cursor, topx: int, paxina_nome: str, divisas_ref: List[Divisa], id_top: int) -> List[Topx]:
    '''
    os nomes deben ser iguais ós do ficheiro de configuración
    poñoo aqui porque igualmente se se quere engadir unha nova
    fai falla modificar o codigo para facer o import asi que da igual
    e se se quere eliminar unha basta con quitala da config
    '''
    apis_paxinas = {
        'CoinGecko': get_topx_CG,
        'CoinMarketCap': get_topx_CMC
    }

    try:
        return apis_paxinas[paxina_nome](cur, topx, divisas_ref, id_top)
    except KeyError:
        raise PaxinaNonExistenteErro
    except Exception as e:
        raise e
# ------------------------------------------------------------------------------
def sair(con: Connection) -> None:
    con.commit()
    con.close()
# ------------------------------------------------------------------------------
def main_aux(RAIZ: str, cur: Cursor, cnf: Dict[str, str]) -> None:
    cur.executescript(''.join(cargarFich(os.path.join(RAIZ, cnf['script_creacion_db']))))

    divisa_tipos = coller_ou_insertar_taboa(cur, 'divisa_tipo', cnf['tipos de divisa'])
    paxinas = coller_ou_insertar_taboa(cur, 'paxina', cnf['paxinas'])
    divisas = coller_ou_insertar_taboa(cur, 'divisa', cnf['divisas'])
    divisas_ref = coller_ou_insertar_taboa(cur, 'divisa', cnf['divisas_ref'])
    #divisas_todas = [*divisas, *divisas_ref]

    """
    # get id divisa fiat
    for divisa_tipo in divisa_tipos:
        if divisa_tipo.nome == 'fiat':
            id_fiat = divisa_tipo.id_
            break

    # sacar un array coas divisas fiat
    divisas_fiat = []
    for divisa in divisas:
        if divisa.id_tipo == id_fiat:
            divisas_fiat.append(divisa)
    """

    try:
        topx = int(cnf['topx'])
    except ValueError:
        raise TopxNonNumeroErro
    except Exception as e:
        raise e

    tops = []
    for paxina in paxinas:
        while True:
            try:
                top_pax = Top(id_paxina= paxina.id_)
                top_pax.id_ = insertar_taboa(cur, top_pax)
            except IntegrityError:
                raise Exception
            except Exception as e:
                raise e
            else:
                tops.append(top_pax)
                break
        # get_top da páxina
        # xFCR: mirar se se gardan máis info guai
        get_topsx(cur, topx, paxina.nome, divisas_ref, top_pax.id_)

    # gardar o prezo das divisas que non sexan fiat

def main(RAIZ: str, debug: bool) -> None:
    global DEBUG
    DEBUG = debug

    if DEBUG: print('* Comezando\n')
    cnf = cargarJson('.cnf')
    con = sqlite3.connect(os.path.join(RAIZ, cnf['db']))

    try:
        cur = con.cursor()
        main_aux(RAIZ, cur, cnf)
    except KeyboardInterrupt:
        if DEBUG: print('\n* Saíndo do programa.')
    except Exception as e:
        raise e
    finally:
        sair(con)
        if DEBUG: print('\n* Rematado')
# ------------------------------------------------------------------------------
