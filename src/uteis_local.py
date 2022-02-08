#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:39:29.474890
#+ Editado:	2022/02/08 21:54:57.476873
# ------------------------------------------------------------------------------
from secrets import token_urlsafe
from typing import Union
# ------------------------------------------------------------------------------
def chave(lonx: int = 24) -> str:
    """
    Retorna un catex aleatorio de 32(24) caracteres que se usará como id.
    """
    return token_urlsafe(lonx)
# ------------------------------------------------------------------------------
def nulo_se_baleiro(catex: str) -> Union[str, None]:
    """
    Retorna nulo se é un catex baleiro, senón devolve o catex.
    """
    if len(catex) == 0:
        return None
    return catex
# ------------------------------------------------------------------------------
