#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:18:40.139388
#+ Editado:	2022/02/08 20:31:19.215859
# ------------------------------------------------------------------------------
import os
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Dict, List, Union

from uteis.ficheiro import cargarJson, cargarFich
from coinmarketcap_scrapper import CoinMarketCap
from coingecko_api import CoinGecko

from .dtos import Divisa_Tipo, Divisa, Paxina, Top, Prezo, Topx
from .excepcions import TaboaInexistenteErro
# ------------------------------------------------------------------------------
def coller_todo_taboa(cur: Cursor, taboa: str) -> List[Union[Paxina, Topx]]:

    taboas = {
            'paxina': coller_todo_paxina
            }
    try:
        return taboas[taboa](cur)
    except KeyError:
        raise TaboaInexistenteErro

def coller_todo_paxina(cur: Cursor) -> List[Paxina]:
    paxinas = []
    for linha in cur.execute('select * from paxina').fetchall():
        paxinas.append(Paxina(
            id_= linha[0],
            nome= linha[1],
            ligazon = linha[2]
            ))
    return paxinas

def coller_ou_insertar_taboa(cur: Cursor, taboa: str, valores: List[str]) -> List[Union[Paxina, Topx]]:
    taboas = {
            'paxina': coller_ou_insertar_paxina
            }
    try:
        return taboas[taboa](cur, valores)
    except KeyError:
        raise TaboaInexistenteErro

def coller_ou_insertar_paxina(cur: Cursor, nomes: List[str]) -> List[Paxina]:
    paxinas = []
    for nome in nomes:
        dato = cur.execute(f'select * from paxina where nome="{nome}"').fetchone()

        if dato:
            paxinas.append(Paxina(
                id_= dato[0],
                nome= dato[1],
                ligazon= dato[2]
                ))
        else:
            nova_paxina = Paxina(
                        nome= nome,
                        ligazon= input(f'\n> Ligazón de {nome}: ')
                    )
            cur.execute('insert into paxina("nome", "ligazon")'\
                    f' values("{nova_paxina.nome}", "{nova_paxina.ligazon}")')
            paxinas.append(nova_paxina)

    return paxinas
# ------------------------------------------------------------------------------
def sair(con: Connection) -> None:
    con.commit()
    con.close()
# ------------------------------------------------------------------------------
def main_aux(RAIZ: str, cur: Cursor, cnf: Dict[str, str]) -> None:
    cur.executescript(''.join(cargarFich(os.path.join(RAIZ, cnf['script_creacion_db']))))

    cmc = CoinMarketCap()
    cg = CoinGecko()

    moedas = cnf['moedas']
    divisas = cnf['divisas']

    paxinas = coller_ou_insertar_taboa(cur, 'paxina', cnf['paxinas'])

    print(paxinas[0].nome)


def main(RAIZ: str, DEBUG: bool) -> None:
    cnf = cargarJson('.cnf')
    con = sqlite3.connect(os.path.join(RAIZ, cnf['db']))

    try:
        cur = con.cursor()
        main_aux(RAIZ, cur, cnf)
    except KeyboardInterrupt:
        print()
        if DEBUG: print('* Saíndo do programa.')
    finally:
        sair(con)
# ------------------------------------------------------------------------------
