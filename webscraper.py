from lxml.html import parse
from lxml.etree import tostring
import urllib.request
import sqlite3
from sqlite3 import Error

#cambio de user agent
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)
GENEROS = 2

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def obtener_links_a_novelas(paginasAIterar: int = 20) -> list:
	links = []
	for pagina in range(0, paginasAIterar):
		start = f"https://www.readwn.com/list/all/all-onclick-{pagina}.html"
		response = urllib.request.urlopen(start)
		pagina = parse(response)
		links.extend(pagina.xpath("//*[@class = 'novel-item']/a/@href"))
	return ['https://www.readwn.com' + link for link in links]


def obtener_autor_de_pagina_principal(doc):
	posicion_autor = doc.xpath("//*[@itemprop = 'author']/text()")
	if(posicion_autor):
		return posicion_autor[0]
	else:
		return "No author"

def obtener_titulo_de_pagina_principal(doc):
	return doc.xpath("//*[@class = 'novel-title text2row']/text()")[0]	

def obtener_generos_de_pagina_principal(doc):
	return doc.xpath("//*[@class = 'property-item']/text()")

def obtener_resumen_de_pagina_principal(doc):
	return ''.join(list(doc.xpath("//*[@class = 'content']")[0].itertext()))

def obtener_links_de_10_capitulos_de_pagina_principal(doc):
	incomplete_links = doc.xpath("//*[@class = 'chapter-list']/li/a/@href")[:10]
	return ['https://www.readwn.com'+link for link in incomplete_links]

def obtener_texto_de_capitulo(link_a_capitulo):
	response = urllib.request.urlopen(link_a_capitulo)
	capitulo = parse(response)
	p_tags = capitulo.xpath("//*[@class = 'chapter-content']/p[text()]")
	return ''.join([p.text + '\n' for p in p_tags if p.text])

def obtener_texto_de_primeros_10_capitulos(doc):
	return list(map(obtener_texto_de_capitulo, obtener_links_de_10_capitulos_de_pagina_principal(doc)))

def obtener_datos_de_novelas(link_a_novela):
	response = urllib.request.urlopen(link_a_novela)
	novela = parse(response)
	titulo = str(obtener_titulo_de_pagina_principal(novela))
	autor = str(obtener_autor_de_pagina_principal(novela))
	generos_como_lista = obtener_generos_de_pagina_principal(novela)
	generos = str(generos_como_lista).lstrip('[').rstrip(']')
	resumen = str(obtener_resumen_de_pagina_principal(novela))
	capitulos = str(obtener_texto_de_primeros_10_capitulos(novela))
	return [titulo,autor,generos,resumen,capitulos], generos_como_lista

def actualizar_database_con_nueva_novela(link_a_novela, id, conn):
	datos, generos = obtener_datos_de_novelas(link_a_novela)
	cur = conn.cursor()
	statement_novelas = "INSERT INTO novelas(id, title, author, genres, summary, first_ten_chapters_text) VALUES(?, ?, ?, ?, ?, ?)"
	for genero in generos:
		statement_novelas_y_categorias = "INSERT INTO novelas_y_categorias(id_novela, genre) VALUES(?, ?)"
		cur.execute(statement_novelas_y_categorias, [id, genero])
	cur.execute(statement_novelas, [id] + datos)
	conn.commit()

def cargar_datos_en_sqlite(conn, novelaDesdeDondeEmpezar: int = 1):
	id = novelaDesdeDondeEmpezar - 1
	links_a_novelas = obtener_links_a_novelas()[(novelaDesdeDondeEmpezar - 1):]
	for link in links_a_novelas:
		actualizar_database_con_nueva_novela(link, id, conn)
		id += 1

conn = create_connection(r"/home/usuario/Repo/webScraping/novelassql.db")

statement_novelas = """CREATE TABLE IF NOT EXISTS novelas (
	id integer PRIMARY KEY,
	title TEXT UNIQUE NOT NULL,
	author TEXT,
	genres TEXT,
	summary TEXT,
	first_ten_chapters_text TEXT
	);"""

statement_novelas_y_categorias = """ CREATE TABLE IF NOT EXISTS novelas_y_categorias (
	id_novela integer,
	genre TEXT NOT NULL,
	FOREIGN KEY (id_novela) REFERENCES novela (id)
	);
	"""

create_table(conn, statement_novelas)
create_table(conn, statement_novelas_y_categorias)

cargar_datos_en_sqlite(conn, 1)
conn.close()