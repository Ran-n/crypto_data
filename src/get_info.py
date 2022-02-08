#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:18:40.139388
#+ Editado:	2022/02/08 19:28:23.666437
# ------------------------------------------------------------------------------
import os
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Dict

from uteis.ficheiro import cargarJson, cargarFich
from coinmarketcap_scrapper import CoinMarketCap
from coingecko_api import CoinGecko

from .dtos import Divisa
# ------------------------------------------------------------------------------

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

    print(moedas)

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
