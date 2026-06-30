import urllib.request, json, http.client, traceback

# Login
data = json.dumps({'email': 'admin@sms.com', 'password': 'SuperAdminSecurePassword123!'}).encode()
r = urllib.request.urlopen(urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'}), timeout=5)
token = json.loads(r.read())['data']['access_token']
print('Login OK')

# Test users
conn = http.client.HTTPConnection('localhost', 8000, timeout=10)
conn.request('GET', '/api/v1/users', headers={'Authorization': 'Bearer ' + token})
resp = conn.getresponse()
body = resp.read().decode()
print('Users Status:', resp.status)
print('Users Headers:', dict(resp.getheaders()))
print('Users Body:', body[:1000])
conn.close()
