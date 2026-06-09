#!/usr/bin/env python3
import sys
try:
    import config
    import pymysql
    from app import create_app
except Exception as e:
    print('Import error:', type(e).__name__, e)
    sys.exit(2)

print('Using config file:', config.__file__)
print('DB settings:', config.MYSQL_HOST,
      config.MYSQL_USER, '****', config.MYSQL_DATABASE)
try:
    conn = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER,
                           password=config.MYSQL_PASSWORD, database=config.MYSQL_DATABASE)
    conn.close()
    print('DB connection: OK')
except Exception as e:
    print('DB connection error:', type(e).__name__, e)

app = create_app()
app.testing = True
client = app.test_client()
resp = client.post('/login', data={'email': 'nonexistent@example.com',
                   'password': 'x'}, headers={'X-Requested-With': 'XMLHttpRequest'})
print('login status', resp.status_code)
print('login content-type', resp.headers.get('Content-Type'))
print('login body:', resp.get_data(as_text=True))
