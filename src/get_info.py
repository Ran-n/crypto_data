#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:18:40.139388
#+ Editado:	2022/02/08 22:36:05.956569
# ------------------------------------------------------------------------------
import os
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Dict, List, Union

from uteis.ficheiro import cargarJson, cargarFich
from uteis.imprimir import jprint
from coinmarketcap_scrapper import CoinMarketCap
from coingecko_api import CoinGecko

from .dtos import Divisa_Tipo, Divisa, Paxina, Top, Prezo, Topx
from .excepcions import TaboaInexistenteErro, TopxNonNumeroErro
from .uteis_local import nulo_se_baleiro
# ------------------------------------------------------------------------------
def coller_todo_taboa(cur: Cursor, taboa: str) -> List[Union[Divisa_Tipo, Divisa, Paxina, Top, Prezo, Topx]]:

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

def coller_ou_insertar_taboa(cur: Cursor, taboa: str, valores: Union[List[str], List[Dict[str, str]]]) -> List[Union[Divisa_Tipo, Divisa, Paxina, Top, Prezo, Topx]]:
    taboas = {
            'paxina': coller_ou_insertar_paxina,
            'divisa_tipo': coller_ou_insertar_divisa_tipo,
            'divisa': coller_ou_insertar_divisa
            }
    try:
        return taboas[taboa](cur, valores)
    except KeyError:
        raise TaboaInexistenteErro
    except Exception as e
        raise e

def coller_ou_insertar_paxina(cur: Cursor, valores: List[Dict[str, str]]) -> List[Paxina]:
    paxinas = []
    for valor in valores:
        dato = cur.execute(f'''select * from paxina where nome="{valor['nome']}"''').fetchone()

        if dato:
            paxinas.append(Paxina(
                id_= dato[0],
                nome= dato[1],
                ligazon= dato[2]
                ))
        else:
            nova_paxina = Paxina(
                        nome= valor['nome'],
                        ligazon= valor['ligazon']
                    )
            cur.execute('insert into paxina("nome", "ligazon")'\
                    f' values("{nova_paxina.nome}", "{nova_paxina.ligazon}")')
            paxinas.append(nova_paxina)

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
            nova_divisa_tipo = Divisa_Tipo(nome= nome)

            cur.execute('insert into divisa_tipo("id", "nome")'\
                    f' values("{nova_divisa_tipo.id_}", "{nova_divisa_tipo.nome}")')
            divisa_tipos.append(nova_divisa_tipo)

    return divisa_tipos

def coller_ou_insertar_divisa(cur: Cursor, valores: List[Dict[str, str]]) -> List[Divisa]:
    divisas = []
    for valor in valores:
        dato = cur.execute(f'''select * from divisa where nome="{valor['nome']}"''').fetchone()

        if dato:
            divisas.append(Divisa(
                id_= dato[0],
                simbolo= dato[1],
                nome= dato[2],
                siglas= dato[3],
                data= dato[4],
                id_tipo= dato[5]
                ))
        else:
            nova_divisa = Divisa(
                            simbolo= valor['simbolo'],
                            nome= valor['nome'],
                            siglas= valor['siglas'],
                            id_tipo = coller_ou_insertar_divisa_tipo(cur, [valor['tipo']])[0].id_
                            )

            cur.execute('insert into divisa("id", "simbolo", "nome", "siglas", "id_tipo", "data")'\
                    f' values("{nova_divisa.id_}", ?, "{nova_divisa.nome}",'\
                    f' "{nova_divisa.siglas}", "{nova_divisa.id_tipo}", "{nova_divisa.data}")',
                    (nulo_se_baleiro(nova_divisa.simbolo),))
            divisas.append(nova_divisa)

    return divisas
# ------------------------------------------------------------------------------
def sair(con: Connection) -> None:
    con.commit()
    con.close()
# ------------------------------------------------------------------------------
def main_aux(RAIZ: str, cur: Cursor, cnf: Dict[str, str]) -> None:
    cur.executescript(''.join(cargarFich(os.path.join(RAIZ, cnf['script_creacion_db']))))

    cmc = CoinMarketCap()
    cg = CoinGecko()

    divisa_tipos = coller_ou_insertar_taboa(cur, 'divisa_tipo', cnf['tipos de divisa'])
    paxinas = coller_ou_insertar_taboa(cur, 'paxina', cnf['paxinas'])
    divisas = coller_ou_insertar_taboa(cur, 'divisa', cnf['divisas'])

    try:
        topx = int(cnf['topx'])
    except ValueError:
        raise TopxNonNumeroErro
    except Exception as e:
        raise e

    print(paxinas[0].nome)
    print(divisas[2])


def main(RAIZ: str, DEBUG: bool) -> None:
    cnf = cargarJson('.cnf')
    con = sqlite3.connect(os.path.join(RAIZ, cnf['db']))

    try:
        cur = con.cursor()
        main_aux(RAIZ, cur, cnf)
    except KeyboardInterrupt:
        print()
        if DEBUG: print('* Saíndo do programa.')
    except Exception as e:
        raise e
    finally:
        sair(con)
# ------------------------------------------------------------------------------
