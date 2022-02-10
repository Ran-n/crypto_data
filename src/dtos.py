#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/08 18:38:36.890366
#+ Editado:	2022/02/09 19:31:10.216034
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field
from datetime import datetime as dt

from .uteis_local import chave
# ------------------------------------------------------------------------------
@dataclass
class Divisa_Tipo:
    nome: str
    id_: str = field(default_factory=chave)
    data: str = field(default_factory=dt.now)

@dataclass
class Divisa:
    simbolo: str
    nome: str
    siglas: str
    nomesigla: str
    id_tipo: str
    id_: str = field(default_factory=chave)
    data: str = field(default_factory=dt.now)

@dataclass
class Paxina:
    nome: str
    ligazon: str
    id_: int = field(default=-1)
    data: str = field(default_factory=dt.now)

@dataclass
class Top:
    id_paxina: int
    id_: int = field(default=-1)
    data: str = field(default_factory=dt.now)

@dataclass
class Topx:
    id_divisa: str
    id_top: int
    posicion: int
    prezo: str
    id_divisa_ref: str
    data: str = field(default_factory=dt.now)
# ------------------------------------------------------------------------------
