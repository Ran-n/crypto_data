#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:38:36.890366
#+ Editado:	2022/02/08 18:58:48.769439
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field
from datetime import datetime as dt

from .uteis_local import chave
# ------------------------------------------------------------------------------
@dataclass
class Divisa_Tipo:
    nome: str
    id_: str = field(default=chave())

@dataclass
class Divisa:
    simbolo: str
    nome: str
    siglas: str
    data: str = field(default=dt.now(), init = False)
    id_tipo: str
    id_: str = field(default=chave())

@dataclass
class Paxina:
    id_: int = field(init = False)
    nome: str
    ligazon: str

@dataclass
class Top:
    id_: int = field(init = False)
    data: str = field(default=dt.now(), init = False)
    id_paxina: int

@dataclass
class Prezo:
    id_divisa: str
    id_divisa_ref: str
    data: str = field(default=dt.now(), init = False)
    valor: float

@dataclass
class Topx:
    id_divisa: str
    id_top: int
    posicion: int
    data: str = field(default=dt.now(), init = False)
# ------------------------------------------------------------------------------
