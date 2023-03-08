
import requests

while True :
    # Send another GET request to verify the updated status
    response = requests.get('http://mdakk072.pythonanywhere.com/status')
    print(response.json(),"                                                  ",end="\r")  # {'places': 150, 'empty': 75, 'full': 75}