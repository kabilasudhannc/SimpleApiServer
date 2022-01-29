from flask import Flask, render_template, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
import requests as req
import random
import string

app = Flask(__name__)
api = Api(app)


@app.route('/login', methods=['GET', 'POST'])
def login_required():
    if request.method == 'POST':
        tokens = pd.read_csv('users.csv')
        alphabets = string.ascii_letters
        numbers = string.digits
        pasw = alphabets + numbers

        token = ''
        for _ in range(15):
            token += random.choice(pasw)

        data = pd.DataFrame({
            'token': token
        }, index=[1])
        tokens = tokens.append(data, ignore_index=True)
        tokens.to_csv('users.csv', index=False)
        print(token)
        return render_template('login.html', token=token)

    return render_template('login.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get('Activate') == 'Activate':
            token = request.form.get('token')
            country = request.form.get('vpn')
            print(country)
            operation = 'enable'
            params = {
                'token': token,
                'country': country,
                'operation': operation
            }
            response = req.put(url='http://192.168.0.107:8000/users', json=params)
            print(response.status_code)

        if request.form.get('Deactivate') == 'Deactivate':
            token = request.form.get('token')
            country = request.form.get('vpn')
            operation = 'disable'
            params = {
                'token': token,
                'country': country,
                'operation': operation
            }
            response = req.put(url='http://192.168.0.107:8000/users', json=params)
            print(response.status_code)
        return render_template('home.html')

    if request.method == 'GET':
        return render_template('home.html')


class Users(Resource):

    @staticmethod
    def get():
        parser = reqparse.RequestParser()
        parser.add_argument('token', required=True)
        args = parser.parse_args()
        data = pd.read_csv('users.csv')
        if args['token'] in list(data['token']):
            return data[data['token'] == args['token']].to_dict('records'), 200

        else:
            return {
                       'message': 'Token is Invalid.'
                   }, 404

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('token', required=True)
        parser.add_argument('country', required=True)
        parser.add_argument('operation', required=True)
        args = parser.parse_args()

        data = pd.read_csv('users.csv')

        for token in list(data['token']):
            if args['token'] in token:
                return {
                           'message': f"'{args['token']}' already exists."
                       }, 409
        else:
            new_data = pd.DataFrame({
                'token': [args['token']],
                'country': [args['country']],
                'operation': [args['operation']],
            })
            data = data.append(new_data, ignore_index=True)
            data.to_csv('users.csv', index=False)
            return 200

    @staticmethod
    def put():
        parser = reqparse.RequestParser()
        parser.add_argument('token', required=True)
        parser.add_argument('country', required=True)
        parser.add_argument('operation', required=True)
        args = parser.parse_args()

        data = pd.read_csv('users.csv')

        if args['token'] in list(data['token']):
            data.loc[data['token'] == args['token'], 'country'] = args['country']
            data.loc[data['token'] == args['token'], 'operation'] = args['operation']

            # save back to CSV
            data.to_csv('users.csv', index=False)
            return 200

        else:
            return {
                       'message': f"'{args['token']}' not found."
                   }, 404

    @staticmethod
    def delete():
        parser = reqparse.RequestParser()
        parser.add_argument('token', required=True)
        args = parser.parse_args()

        data = pd.read_csv('users.csv')

        for token in list(data['token']):
            if args['token'] in token:
                data = data[data['token'] != args['token']]

                data.to_csv('users.csv', index=False)
                return 200

        else:
            return {
                       'message': f"'{args['token']}' not found."
                   }, 404


api.add_resource(Users, '/users')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
