import requests
import json
import random
import re
import jwt
import pprint

class OpenidHelper :
    @staticmethod
    def get_token(openid_config, login, password):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.post('%s/api/v1/authn' % openid_config['ISSUER_URL'],
                                 json={
                                     'username': login,
                                     'password': password,
                                     'options': {
                                        'multiOptionalFactorEnroll': False,
                                        'warnBeforePasswordExpired': True
                                     }
                                 },
                                 headers=headers)

        login_response = json.loads(response.text)
        print login_response
        if login_response['status'] == 'SUCCESS':
            session_token = login_response['sessionToken']
            nonce = random.randrange(100000000, 100000000000000000, 1)
            state = random.randrange(100, 100000, 1)

            query_params = {
                'client_id': openid_config['CLIENT_ID'],
                'response_type': 'id_token',
                #'response_mode': 'fragment',
                'scope': 'openid profile',
                'nonce': nonce,
                'sessionToken': session_token,
                'state': state,
                'redirect_uri': openid_config['REDIRECT_URI']
            }
            r = requests.get('%s/oauth2/v1/authorize' % openid_config['ISSUER_URL'], allow_redirects=False, params=query_params)
            token = re.compile("#id_token=(?P<token>.*)&").search(r.headers["Location"]).group("token")
            return token

        else :
            raise Exception("InvalidOpenidResponse "+str(response.text))

    @staticmethod
    def get_claim(openid_config, login, password):
        token = OpenidHelper.get_token(openid_config, login, password)
        print token
        d= jwt.decode(token, verify=False)
        d["email"]= d["preferred_username"]
        return d


if __name__ == "__main__" :
    OPENID_CONFIG = {
        'ISSUER_URL': 'https://dev-545796.oktapreview.com',
        'CLIENT_ID': '0oafvba1nlTwOqPN40h7',
        'REDIRECT_URI': 'http://locahost/implicit/callback'
    }

    token = OpenidHelper.get_claim(OPENID_CONFIG, 'moshir.mikael@gmail.com', 'Azerty2!')
    print pprint.pformat(token)
