#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:18:40.139388
#+ Editado:	2022/03/08 08:15:14.564822
# ------------------------------------------------------------------------------
import os
import sqlite3
from sqlite3 import Connection, Cursor, IntegrityError
from typing import Dict, List, Union
from halo import Halo
from tqdm import tqdm


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

                    while True:
                        # se non hai devolve none
                        if cur.execute(f'select * from divisa_tipo where id="{nova_divisa_tipo.id_}"').fetchone():
                            nova_divisa_tipo.reset_id()
                        else:
                            break

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
        if valor['nome'] == 'BNB':
            valor['nome'] = 'Binance Coin'
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

                    while True:
                        # se non hai devolve none
                        if cur.execute(f'select * from divisa where id="{nova_divisa.id_}"').fetchone():
                            nova_divisa.reset_id()
                        else:
                            break

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
        sentenza = 'insert into topx(id_divisa, id_top, data, posicion, prezo, id_divisa_ref,'\
                'market_cap, fully_diluted_valuation, total_volume, max_24h, min_24h, '\
                'price_change_24h, price_change_pctx_24h, circulating_supply, total_supply, '\
                'max_supply, ath, ath_change_pctx, data_ath, atl, atl_change_pctx, data_atl, '\
                'price_change_pctx_1h_divisa_ref, price_change_pctx_24h_divisa_ref, '\
                f'price_change_pctx_7d_divisa_ref) values("{topx.id_divisa}", "{topx.id_top}", '\
                f'"{topx.data}", ?, ?, "{topx.id_divisa_ref}", ?, ?, ?, ?, ?, ?, ?, ?, ?,'\
                '?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(sentenza, (topx.posicion, topx.prezo, topx.market_cap, topx.fully_diluted_valuation,
            topx.total_volume, topx.max_24h, topx.min_24h, topx.price_change_24h, topx.price_change_pctx_24h,
            topx.circulating_supply, topx.total_supply, topx.max_supply, topx.ath, topx.ath_change_pctx,
            topx.data_ath, topx.atl, topx.atl_change_pctx, topx.data_atl, topx.price_change_pctx_1h_divisa_ref,
            topx.price_change_pctx_24h_divisa_ref, topx.price_change_pctx_7d_divisa_ref))
    except IntegrityError:
        print(f'Duplicado {topx}')
        pass
    return -1
# ------------------------------------------------------------------------------
def __mais_menos(valor: str) -> str:
    """
    """

    valor = str(valor)

    if valor.startswith('-'):
        return valor
    else:
        return '+'+valor

def get_topx_CMC(cur: Cursor, topx: int, divisas_ref: List[Divisa], id_top: int) -> List[Topx]:
    #if DEBUG: print('* Collendo o top de CoinMarketCap')
    l_topsx = []

    # este non vai utilizar o das divisas porque os prezos sempre os da en dolar
    for divisa_ref in divisas_ref:
        if divisa_ref.simbolo == '$':
            break

    #cmc = CoinMarketCap(verbose= DEBUG)
    cmc = CoinMarketCap()

    for moeda in tqdm(cmc.get_top(topx), desc='CoinMarketCap'):
        temp_divisa = coller_ou_insertar_divisa(cur, [{
                                        'simbolo': '',
                                        'nome': moeda['nome'],
                                        'siglas': moeda['simbolo'],
                                        'tipo': 'criptomoeda'
                                        }])[0]

        try:
            info_moeda = cmc.get_moeda(moeda['ligazon'], 'ligazon')
        except Exception as e:
            print(f'Erro: {e}')
            print(moeda)
            temp_topx = Topx(
                id_divisa                           = temp_divisa.id_,
                id_top                              = id_top,
                posicion                            = moeda['posicion'],
                prezo                               = moeda['prezo'],
                market_cap                          = None,
                fully_diluted_valuation             = None,
                total_volume                        = None,
                max_24h                             = None,
                min_24h                             = None,
                price_change_24h                    = None,
                price_change_pctx_24h               = None,
                circulating_supply                  = None,
                total_supply                        = None,
                max_supply                          = None,
                ath                                 = None,
                ath_change_pctx                     = None,
                data_ath                            = None,
                atl                                 = None,
                atl_change_pctx                     = None,
                data_atl                            = None,
                price_change_pctx_1h_divisa_ref     = None,
                price_change_pctx_24h_divisa_ref    = None,
                price_change_pctx_7d_divisa_ref     = None,
                price_change_pctx_14d_divisa_ref    = None,
                price_change_pctx_30d_divisa_ref    = None,
                price_change_pctx_200d_divisa_ref   = None,
                price_change_pctx_365d_divisa_ref   = None,
                max_7d                              = None,
                min_7d                              = None,
                max_30d                             = None,
                min_30d                             = None,
                max_90d                             = None,
                min_90d                             = None,
                max_365d                            = None,
                min_365d                            = None,
                roi                                 = None,
                trading_volume_24h                  = None,
                trading_volume_change_pctx_24h      = None,
                volume_dividido_market_cap          = None,
                dominancia                          = None,
                total_value_locked                  = None,
                watchlists_stars                    = None,
                id_divisa_ref                       = divisa_ref.id_
            )
        else:
            try:
                temp_topx = Topx(
                    id_divisa                           = temp_divisa.id_,
                    id_top                              = id_top,
                    posicion                            = moeda['posicion'],
                    prezo                               = info_moeda['prezo'],
                    market_cap                          = info_moeda['market_cap'],
                    fully_diluted_valuation             = None,
                    total_volume                        = None,
                    max_24h                             = info_moeda['max_24h'],
                    min_24h                             = info_moeda['min_24h'],
                    price_change_24h                    = info_moeda['price_change_24h'],
                    price_change_pctx_24h               = info_moeda['price_change_pctx_24h'].replace('%','') if info_moeda['price_change_pctx_24h'] != None else None,
                    circulating_supply                  = info_moeda['circulating_supply'],
                    total_supply                        = info_moeda['total_supply'],
                    max_supply                          = info_moeda['max_supply'],
                    ath                                 = info_moeda['ath'],
                    ath_change_pctx                     = info_moeda['ath_change_pctx'].replace('%','') if info_moeda['ath_change_pctx'] != None else None,
                    data_ath                            = None,
                    atl                                 = info_moeda['atl'],
                    atl_change_pctx                     = info_moeda['atl_change_pctx'].replace('%','') if info_moeda['atl_change_pctx'] != None else None,
                    data_atl                            = None,
                    price_change_pctx_1h_divisa_ref     = None,
                    price_change_pctx_24h_divisa_ref    = None,
                    price_change_pctx_7d_divisa_ref     = None,
                    price_change_pctx_14d_divisa_ref    = None,
                    price_change_pctx_30d_divisa_ref    = None,
                    price_change_pctx_200d_divisa_ref   = None,
                    price_change_pctx_365d_divisa_ref   = None,
                    max_7d                              = info_moeda['max_7d'],
                    min_7d                              = info_moeda['min_7d'],
                    max_30d                             = info_moeda['max_30d'],
                    min_30d                             = info_moeda['min_30d'],
                    max_90d                             = info_moeda['max_90d'],
                    min_90d                             = info_moeda['min_90d'],
                    max_365d                            = info_moeda['max_52semanas'],
                    min_365d                            = info_moeda['min_52semanas'],
                    roi                                 = info_moeda['roi'],
                    trading_volume_24h                  = info_moeda['trading_volume_24h'],
                    trading_volume_change_pctx_24h      = info_moeda['trading_volume_change_pctx_24h'].replace('%','') if info_moeda['trading_volume_change_pctx_24h'] != None else None,
                    volume_dividido_market_cap          = info_moeda['volume_dividido_market_cap'],
                    dominancia                          = info_moeda['dominancia_mercado'],
                    total_value_locked                  = info_moeda['total_value_locked'],
                    watchlists_stars                    = info_moeda['watchlists'],
                    id_divisa_ref                       = divisa_ref.id_
                )
            except:
                print(info_moeda)
        finally:
            insertar_taboa(cur, temp_topx)
            l_topsx.append(temp_topx)

    return l_topsx

def get_topx_CG(cur: Cursor, topx: int, divisas_ref: List[Divisa], id_top: int) -> List[Topx]:
    #if DEBUG: print('* Collendo o top de CoinGecko')
    l_topsx = []

    tope = True
    if topx == 0:
        tope = False

    cpp = ['1h', '24h', '7d', '14d', '30d', '200d', '1y']
    cg = CoinGecko()

    for divisa_ref in tqdm(divisas_ref, desc='CoinGecko'):
        pax = 1
        while True:
            # a veces da erro nidea de por que xdd
            while True:
                try:
                    l_moedas_cg = cg.get_coins_markets(
                            id_moeda_vs=divisa_ref.siglas.lower(),
                            pax=pax,
                            cambio_prezo_porcentaxe = cpp
                            )
                except:
                    pass
                else:
                    break

            if len(l_moedas_cg) == 0 or (tope and topx <= 0):
                break

            if tope:
                l_moedas_cg = l_moedas_cg[:topx]
                topx -= len(l_moedas_cg)

            for moeda in l_moedas_cg:
                temp_divisa = coller_ou_insertar_divisa(cur, [{
                    'simbolo': '',
                    'nome': moeda['name'],
                    'siglas': moeda['symbol'].upper(),
                    'tipo': 'criptomoeda'
                }])[0]

                temp_topx = Topx(
                    id_divisa                           = temp_divisa.id_,
                    id_top                              = id_top,
                    posicion                            = moeda['market_cap_rank'],
                    prezo                               = moeda['current_price'],
                    market_cap                          = moeda['market_cap'],
                    fully_diluted_valuation             = moeda['fully_diluted_valuation'],
                    total_volume                        = moeda['total_volume'],
                    max_24h                             = moeda['high_24h'],
                    min_24h                             = moeda['low_24h'],
                    price_change_24h                    = __mais_menos(moeda['price_change_24h']),
                    price_change_pctx_24h               = __mais_menos(moeda['price_change_percentage_24h']),
                    circulating_supply                  = moeda['circulating_supply'],
                    total_supply                        = moeda['total_supply'],
                    max_supply                          = moeda['max_supply'],
                    ath                                 = moeda['ath'],
                    ath_change_pctx                     = __mais_menos(moeda['ath_change_percentage']),
                    data_ath                            = moeda['ath_date'],
                    atl                                 = __mais_menos(moeda['atl']),
                    atl_change_pctx                     = __mais_menos(moeda['atl_change_percentage']),
                    data_atl                            = moeda['atl_date'],
                    price_change_pctx_1h_divisa_ref     = __mais_menos(moeda['price_change_percentage_1h_in_currency']),
                    price_change_pctx_24h_divisa_ref    = __mais_menos(moeda['price_change_percentage_24h_in_currency']),
                    price_change_pctx_7d_divisa_ref     = __mais_menos(moeda['price_change_percentage_7d_in_currency']),
                    price_change_pctx_14d_divisa_ref    = __mais_menos(moeda['price_change_percentage_14d_in_currency']),
                    price_change_pctx_30d_divisa_ref    = __mais_menos(moeda['price_change_percentage_30d_in_currency']),
                    price_change_pctx_200d_divisa_ref   = __mais_menos(moeda['price_change_percentage_200d_in_currency']),
                    price_change_pctx_365d_divisa_ref   = __mais_menos(moeda['price_change_percentage_1y_in_currency']),
                    roi                                 = moeda['roi'],
                    max_7d                              = None,
                    min_7d                              = None,
                    max_30d                             = None,
                    min_30d                             = None,
                    max_90d                             = None,
                    min_90d                             = None,
                    max_365d                            = None,
                    min_365d                            = None,
                    trading_volume_24h                  = None,
                    trading_volume_change_pctx_24h      = None,
                    volume_dividido_market_cap          = None,
                    dominancia                          = None,
                    total_value_locked                  = None,
                    watchlists_stars                    = None,
                    id_divisa_ref                       = divisa_ref.id_
                )

                if temp_topx.posicion and temp_topx.prezo:
                    insertar_taboa(cur, temp_topx)
                    l_topsx.append(temp_topx)
            pax+=1

    return l_topsx

#@Halo(text='Cargando datos', spinner='dots')
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
        get_topsx(cur, topx, paxina.nome, divisas, top_pax.id_)

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
