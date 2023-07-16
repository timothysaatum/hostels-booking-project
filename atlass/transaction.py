from django.conf import settings
import requests


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



class Xerxes:

    SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    RECIPIENT_CODE = None
    TRANSFER_CODE = None
    REFERENCE = None
    headers = {
            'Authorization': f'Bearer {SECRET_KEY}',
            'Content-Type':'application/json'
        }
    def __init__(self, amount=None, account_number=None):
        self.amount = amount
        self.account_number = account_number

    def create_recipient(self):
        recipient_create_url="https://api.paystack.co/transferrecipient"

        sup_bk = requests.get('https://api.paystack.co/bank?currency=GHS', headers=self.headers)
        sup_bk = sup_bk.json()
        print(sup_bk)
        

        #verif_acc = requests.post('https://api.paystack.co/bank/resolve?account_number=0594438287&bank_code=MTN', headers=self.headers)
        #print(f'code: {verif_acc}')

        data = { 
            "type": "mobile_money",
            "name": "Timoth Saatum",
            "account_number": self.account_number,
            "bank_code": "MTN",
            "currency": "GHS"
        }


        #creating a recipient
        try:
            response = requests.post(recipient_create_url, headers=self.headers, json=data)
            recipient_data =response.json()
            print(recipient_data)
            self.RECIPIENT_CODE = recipient_data['data']['recipient_code']
        except Exception as e:
            raise e



    #initiating the transfer process
    def initiate_transfer(self):

        transfer_url = "https://api.paystack.co/transfer"
        recipient = self.RECIPIENT_CODE

        data = { 
            "source": "balance", 
            "reason": "Being Payment for hostel fee", 
            "amount":self.amount, 
            "recipient": recipient
        }


        start_transfer = requests.post(transfer_url, headers=self.headers, json=data)
        transfer_data= start_transfer.json()
        print(transfer_data)
        self.TRANSFER_CODE = transfer_data['data']['transfer_code']

        if start_transfer.status_code == 200:

            transfer_code = transfer_data['data']['transfer_code']
            return transfer_code

        else:
            return 'An error occurred'


    def disable_otp(self):

        #request to disable otp
        otp_url_disable = 'https://api.paystack.co/transfer/disable_otp'
        r = requests.post(otp_url_disable, headers=self.headers)
        otp_data = r.json()
        print(otp_data)


        #finalizing the disabling of the otp
        url='https://api.paystack.co/transfer/disable_otp_finalize'

        data = {
            'otp': '806514'
        }

        res = requests.post(url, headers=self.headers, json=data)
        d = res.json()
        print(d)


    def finalize_transfer(self):
        transfer_code = self.TRANSFER_CODE
        finalize_transfer_url = 'https://api.paystack.co/transfer/finalize_transfer'

        data = { 
            "transfer_code": transfer_code, 
            "otp": "794144"
        }

        try:
            finalize_trans = requests.post(finalize_transfer_url, headers=self.headers, json=data)
            finalize_trans_data = finalize_trans.json()
            #self.REFERENCE = finalize_trans_data['data']['reference']
            print(finalize_trans_data)
        except Exception as e:
            raise e


    #perform the transfer
    def verify_transfer(self):

        ref = self.REFERENCE
        url='https://api.paystack.co/transfer/verify/{ref}'


        response = requests.get(url, headers=self.headers)
        response_data = response.json()

        if response.status_code == 200:
            return response_data['data']['account_number']

        else:
            return 'No such transaction'