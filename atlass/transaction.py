from django.conf import settings
import requests
from django.http import JsonResponse
from paystack.resource import TransactionResource
import random
import string


class Paystack:
    PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY
    base_url = "https://api.paystack.co/"

    def verify_payment(self, ref, *args, **kwargs):
        path = f'transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']

        response_data = response.json()

        return response_data['status'], response_data['message']

def transfer_cash(amount, account_number):
    transfer_url = 'https://api.paystack.co/transfer'

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type':'application/json'
    }

    payload = {
        'source': 'balance',
        'reason': 'Being payment for hostel fee',
        'amount': amount,
        'recipient': "RCP_gx2wn530m0i3w3m"
    }

    try:
        response = requests.post(transfer_url, headers=headers, json=payload)
        data = response.json()
        s = f'Inside{data}status{response.status_code}'
        print(s)
        if response.status_code == 200:
            transfer_code = data['data']['transfer_code']
            finalize_url = f'https://api.paystack.co/transfer/finalize_transaction/{transfer_code}'
            response = requests.post(finalize_url, headers=headers)
            data = response.json()
            if response.status_code == 200:
                return JsonResponse({'message':'Transfer complete'})
        error_message = data['message'] if 'message' in data else 'Transfer could not be completed successfully'
        return JsonResponse({'error':error_message})

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error':str(e)})


def transfer_libiri(amount, account_number):
    key = settings.PAYSTACK_SECRET_KEY
    paystack_api = paystack.Paystack(secret_key=key)
    payload = {
        'source': 'balance',
        'reason': 'Being payment for hostel fee',
        'amount': amount,
        'recipient': "RCP_gx2wn530m0i3w3m"
    }

    trans_response = paystack_api.transfer.create(**payload)
    if trans_response['status']:
        print(success)
    else:
        print('Running post moterm')

def charge_money(amount, email):
        ref = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
        key = settings.PAYSTACK_SECRET_KEY
        plan = 'Basic'

        client = TransactionResource(key, ref)
        response = client.initialize(amount, email, plan)
        print(response)
        client.authorize()
        verify = client.verify()
        print(verify)
        print(client.charge())
