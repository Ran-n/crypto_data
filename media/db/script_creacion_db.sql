CREATE TABLE IF NOT EXISTS "divisa_tipo"(
    "id"        TEXT UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    CONSTRAINT tipo_divisaPK PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "divisa"(
    "id"        TEXT UNIQUE NOT NULL,
    "simbolo"   TEXT UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    "siglas"    TEXT UNIQUE,
    "data"      TEXT NOT NULL,
    "id_tipo"   TEXT NOT NULL,
    CONSTRAINT divisaPK PRIMARY KEY ("id"),
    CONSTRAINT divisaFK1 FOREIGN KEY ("id_tipo") REFERENCES "tipo_divisa"("id") ON DELETE CASCADE ON UPDATE CASCADE MATCH [FULL]
);

CREATE TABLE IF NOT EXISTS "paxina"(
    "id"        INTEGER UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    "ligazon"   TEXT UNIQUE NOT NULL,
    CONSTRAINT paxinaPK PRIMARY KEY ("id")

);

CREATE TABLE IF NOT EXISTS "top"(
    "id"        INTEGER UNIQUE NOT NULL,
    "data"      TEXT UNIQUE NOT NULL,
    "id_paxina" INTEGER NOT NULL,
    CONSTRAINT topPK PRIMARY KEY ("id"),
    CONSTRAINT divisaFK1 FOREIGN KEY ("id_paxina") REFERENCES "paxina"("id") ON UPDATE CASCADE MATCH [FULL]
);

CREATE TABLE IF NOT EXISTS "prezo"(
    "id_divisa"     TEXT NOT NULL,
    "id_divisa_ref" TEXT NOT NULL,
    "data"          TEXT UNIQUE NOT NULL,
    "valor"         FLOAT NOT NULL,
    CONSTRAINT prezoPK PRIMARY KEY ("id_divisa", "id_divisa_ref", "data"),
    CONSTRAINT prezoFK1 FOREIGN KEY ("id_divisa") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL],
    CONSTRAINT prezoFK1 FOREIGN KEY ("id_divisa_ref") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL]
);

CREATE TABLE IF NOT EXISTS "topx"(
    "id_divisa" TEXT NOT NULL,
    "id_top"    INTEGER NOT NULL,
    "posicion"  INTEGER NOT NULL,
    "data"      TEXT UNIQUE NOT NULL,
    CONSTRAINT prezoPK PRIMARY KEY ("id_divisa", "id_top"),
    CONSTRAINT prezoFK1 FOREIGN KEY ("id_divisa") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL],
    CONSTRAINT prezoFK1 FOREIGN KEY ("id_top") REFERENCES "top"("id") ON UPDATE CASCADE MATCH [FULL]
);
