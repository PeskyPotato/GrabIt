import urllib.request, json

gif = "https://gfycat.com/WhimsicalLongHerculesbeetle"
tag = gif.rsplit('/', 1)[-1]
link = "http://gfycat.com/cajax/get/" + tag
try:
    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode())
        print (data['gfyItem']['gifUrl'])
        #print (data)
except ConnectionResetError:
    print("There seems to be an issue. Please try again.")
