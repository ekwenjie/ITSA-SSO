import jwt
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import date
import time 
import os

app = Flask(__name__)
CORS(app)

# healthcheck
@app.route("/", methods=['GET'])
def healthcheck():
    return Response("200", status=200, mimetype='application/json')

#TODO: CHANGE CALLBACK URI, REMOVE CLIENT ID/SECRET

#TODO: Change to login frontend
callback_uri="http://localhost:5555/oauth/callback"

#TODO: NEW AUTHCODE URL
@app.route("/oauth/callback", methods=['GET', 'POST'])
def access_granted():
    print('tested')
    args = request.args
    code = args.get('code')
    print(code)
    #If authcode, post to get token"
    return post_access_token(code)


#To request for a token
# @app.route("/oauth/token", methods=['POST'])
def post_access_token(code):
    url = 'https://smurnauth-production.fly.dev/oauth/token'

    #input other details via config
    details = {"client_id": os.getenv("CLIENT_ID"), 'client_secret': os.getenv("CLIENT_SECRET"), 'redirect_uri': callback_uri, 'grant_type': "authorization_code", 'code': code }
    print(callback_uri)
    data = requests.post(url, json=details)
    data_open = data.json()
    print(data_open)
    return get_access_token(data_open)
    

def get_access_token(data):
    # Match the IDs in both access and id token, check both are not expired
    # data = request.get_json()
    public = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtbrn2Yer9wEduoEcLzZp\nWjYUJY0a5rdk03z98G8fiQVveV9/OR62DaVPLV6JDFLkESWVet/R0ZfCHsi+rR74\ny69dMOrn3wvmBR30YyOfffwRkyOMnf7Zat3NoG+F/vUlPyJxSg8SvY9TTpTPivfV\nNCQX8GkBwDQGq/DxAo8qM0Wty3dCoVewFz3QafDBcOAlAKzD7FAidl5fzRZHeFMJ\nkyefOOy7MS6Rr6jkUzTnZuYdsrnwnAm5cAf1k0KVXmCOubxPNuAVCvL0Vr7yqGcq\nPYXJgIIauhzIgo6p/sdfGpxIXmbdYZd2g32QK1CZLtxV/p7TnyYzfnMLUlADz4bP\nzwIDAQAB\n-----END PUBLIC KEY-----\n'

    #TODO: decode and check for subject, user:id
    id_token = data["id_token"]
    id_token_decoded = jwt.decode(id_token, public, algorithms=["RS256"], audience = "m2Ci-3_xMD7T5FscLL0rHVO4fbkZx3ZxhfSVVkOiQl8")
    id_to_match = id_token_decoded['sub']

    #TODO: JWT Decode and match to ID Token
    access_token = data["access_token"]
    access_token_decoded = jwt.decode(access_token, public, algorithms=["RS256"])
    access_to_match = access_token_decoded['user']['id']
    
    if access_to_match == id_to_match:
        #Check the time
        current_time = int(time.time())
        access_expiry = access_token_decoded['exp']
        id_expiry = id_token_decoded['exp']

        #Token has expired
        if (current_time > id_expiry) or (current_time > access_expiry):
            return jsonify(
                {
                    "code": 400,
                    "message": "Token expired"
                    }
            )

        #Token ok
        url = 'https://smurnauth-production.fly.dev/oauth/userinfo'
        userinfo = requests.get(url=url, params= id_to_match, headers={"Authorization": "Bearer " + access_token}).json()
        userinfo_email = userinfo["email"]
        print(userinfo_email)

        jaydentoken = requests.get("https://1xw2qgy82e.execute-api.ap-southeast-1.amazonaws.com/dev/generatetoken/" + userinfo_email).text
        print(jaydentoken)
        userinfo["token"] = jaydentoken

        return jsonify(
            {
                "code":200,
                "data": userinfo,
                "message": "Logged in via SSO successfully"
            }
        )

if __name__ == '__main__':
    #Run app on port 5555, debug mode
    app.run(debug=True, port=5555, host="0.0.0.0")
