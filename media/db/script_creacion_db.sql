CREATE TABLE IF NOT EXISTS "divisa_tipo"(
    "id"        TEXT UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    "data"      TEXT UNIQUE NOT NULL,
    "borrado"   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT tipo_divisaPK PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "divisa"(
    "id"        TEXT UNIQUE NOT NULL,
    "simbolo"   TEXT UNIQUE,
    "nome"      TEXT NOT NULL,
    "siglas"    TEXT NOT NULL,
    "nomesigla" TEXT UNIQUE NOT NULL,
    "data"      TEXT NOT NULL,
    "id_tipo"   TEXT NOT NULL,
    "borrado"   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT divisaPK PRIMARY KEY ("id"),
    CONSTRAINT divisaFK1 FOREIGN KEY ("id_tipo") REFERENCES "tipo_divisa"("id") ON DELETE CASCADE ON UPDATE CASCADE MATCH [FULL]
);

CREATE TABLE IF NOT EXISTS "paxina"(
    "id"        INTEGER UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    "ligazon"   TEXT UNIQUE NOT NULL,
    "data"      TEXT UNIQUE NOT NULL,
    "borrado"   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT paxinaPK PRIMARY KEY ("id")

);

CREATE TABLE IF NOT EXISTS "top"(
    "id"        INTEGER UNIQUE NOT NULL,
    "data"      TEXT UNIQUE NOT NULL,
    "id_paxina" INTEGER NOT NULL,
    "borrado"   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT topPK PRIMARY KEY ("id"),
    CONSTRAINT divisaFK1 FOREIGN KEY ("id_paxina") REFERENCES "paxina"("id") ON UPDATE CASCADE MATCH [FULL]
);

CREATE TABLE IF NOT EXISTS "topx"(
    "id"                INTEGER NOT NULL,
    "id_divisa"         TEXT NOT NULL,
    "id_top"            INTEGER NOT NULL,
    "data"              TEXT NOT NULL,
    "posicion"          INTEGER NOT NULL,
    "prezo"             TEXT NOT NULL,
    "market_cap"                          TEXT,
    "fully_diluted_valuation"             TEXT,
    "total_volume"                        TEXT,
    "max_24h"                             TEXT,
    "min_24h"                             TEXT,
    "price_change_24h"                    TEXT,
    "price_change_pctx_24h"               TEXT,
    "circulating_supply"                  TEXT,
    "total_supply"                        TEXT,
    "max_supply"                          TEXT,
    "ath"                                 TEXT,
    "ath_change_pctx"                     TEXT,
    "data_ath"                            TEXT,
    "atl"                                 TEXT,
    "atl_change_pctx"                     TEXT,
    "data_atl"                            TEXT,
    "price_change_pctx_1h_divisa_ref"     TEXT,
    "price_change_pctx_24h_divisa_ref"    TEXT,
    "price_change_pctx_7d_divisa_ref"     TEXT,
    "id_divisa_ref"     TEXT NOT NULL,
    "borrado"           INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT topxPK PRIMARY KEY ("id"),
    CONSTRAINT topxFK1 FOREIGN KEY ("id_divisa") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL],
    CONSTRAINT topxFK2 FOREIGN KEY ("id_top") REFERENCES "top"("id") ON UPDATE CASCADE MATCH [FULL],
    CONSTRAINT topxFK3 FOREIGN KEY ("id_divisa_ref") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL]
);
