import request

url = 'https://www.w3schools.com/python/demopage.php'
myobj = {'somekey': 'somevalue'}
x = requests.post(url, data = myobj)
print(x.text)

def send_request(url):
    if method == 'POST':
            response = requests.post(url, data=data)
        else:
            response = requests.get(url, params=data)

        return response.text