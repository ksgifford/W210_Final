import requests
import json

path = '/home/ubuntu/w210-img-upload/'+current_user.username+'/upload'
username = current_user.username
payload = json.dumps({'path':path, 'userId':username})

req = requests.post("http://ec2-3-87-218-106.compute-1.amazonaws.com:5000/predictFolder", json=payload)
