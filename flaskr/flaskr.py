from flask import Flask, request, make_response, redirect
import re
import string
import requests
import psycopg2

try:
	import simplejson as json
except ImportError:
	import json

app = Flask(__name__)
app.debug = True

LEN4 = len(string.ascii_letters)**4
LENA = len(string.ascii_letters)


def str4(num):
	a = []
	if num >= LEN4 : return None
	
	for _ in range(4):
		mod = num%LENA
		num = int(num/LENA)
		a.append(string.ascii_letters[mod])
	
	return "".join(a[::-1])


def int4(s):
	if not s or len(s) != 4 or not re.match("[a-z]{4,4}", s, re.I) : return -1
	a = 0
	for c in s:
		a *= LENA
		a += string.ascii_letters.index(c)
	
	return a
	

def ret(error, error_code, **kwargs):
	app.logger.info(repr(kwargs))
	if error:
		d = {"response":{"error_code":error_code, "error":error}}
	else:
		d = {"response":{"error_code":error_code}}
	
	for k,v in kwargs.items():
		d["response"][k] = v 
	r = make_response(json.dumps(d), error_code)
	r.headers["Content-Type"] = "application/json"
	return r


def init_db():
	return psycopg2.connect("""dbname='goodsound_db' user='goodsound' host='localhost' password='goodsound'""")


@app.route('/key', methods=['GET'])
def key():
	try:
		conn = init_db()
	except Exception as msg:
		app.logger.error(repr(msg))
		return ret("Неизвестная ошибка", 404)
	
	cur = conn.cursor()
	cur.execute("""INSERT INTO key_tbl (key_f) SELECT COUNT(*) from key_tbl returning key_f""")
	conn.commit()
	num = cur.fetchone()[0]
	key = str4(num)
	
	if key:
		return ret("", 200, key=key)
	else:
		return ret("Использован лимит ключей", 404)


@app.route('/count', methods=['GET'])
def count():
	try:
		conn = init_db()
	except Exception as msg:
		app.logger.error(repr(msg))
		return ret("Неизвестная ошибка", 404)
	
	cur = conn.cursor()
	cur.execute("""select count(*) from key_tbl;""")
	num = max(0, LEN4-cur.fetchone()[0])
	return ret("", 200, count=num)


@app.route('/info', methods=['GET'])
def info():
	key = request.args.get("key", "").strip()
	num = int4(key)
	if num == -1:
		return ret("Неверный формат ключа", 404)
	
	try:
		conn = init_db()
	except Exception as msg:
		app.logger.error(repr(msg))
		return ret("Неизвестная ошибка", 404)
	
	cur = conn.cursor()
	cur.execute("""select expire_f from key_tbl where key_f = %d""" % num)
	row = cur.fetchone()
	if not row:
		return ret("", 200, key=key, status="free")
	elif row[0]:
		return ret("", 200, key=key, status="expired")
	else:
		return ret("", 200, key=key, status="busy")


@app.route('/expire', methods=['GET'])
def expire():
	key = request.args.get("key", "").strip()
	num = int4(key)
	if num == -1:
		return ret("Неверный формат ключа", 404)
	
	try:
		conn = init_db()
	except Exception as msg:
		app.logger.error(repr(msg))
		return ret("Неизвестная ошибка", 404)
	
	cur = conn.cursor()
	cur.execute("""update key_tbl set expire_f = true where key_f = %d and expire_f = false""" % num)
	if cur.rowcount:
		conn.commit()
		return ret("", 200, key=key)
	else:
		return ret("Невозможно погасить ключ", 201, key=key)


if __name__ == '__main__':
	app.run()


#CREATE SEQUENCE key_ids;

#CREATE TABLE key_tbl (id INTEGER PRIMARY KEY DEFAULT COUNT('key_ids'), key_f integer, expire_f BOOL default false);
