CREATE TABLE IF NOT EXISTS "divisa"(
    "id"        TEXT UNIQUE NOT NULL,
    "simbolo"   TEXT UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    "id_tipo"   TEXT,
    CONSTRAINT divisaPK PRIMARY KEY ("id"),
    CONSTRAINT divisaFK1 FOREIGN KEY ("id_tipo") REFERENCES "tipo"("id") ON UPDATE CASCADE MATCH [FULL]
);

CREATE TABLE IF NOT EXISTS "tipo"(
    "id"        TEXT UNIQUE NOT NULL,
    "nome"      TEXT UNIQUE NOT NULL,
    CONSTRAINT tipoPK PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "prezo"(
    "id"                    TEXT UNIQUE NOT NULL,
    "valor"                 INTEGER UNIQUE NOT NULL,
    "data"                  INTEGET NOT NULL,
    "id_divisa"             TEXT NOT NULL,
    "id_divisa_referencia"  TEXT NOT NULL,
    CONSTRAINT prezoPK PRIMARY KEY ("id"),
    CONSTRAINT prezoFK1 FOREIGN KEY ("id_divisa") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL],
    CONSTRAINT prezoFK2 FOREIGN KEY ("id_divisa_referencia") REFERENCES "divisa"("id") ON UPDATE CASCADE MATCH [FULL]
);
