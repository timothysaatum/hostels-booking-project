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

    headers = {
            'Authorization': f'Bearer {SECRET_KEY}',
            'Content-Type':'application/json'
        }

        
    def __init__(self, amount=None, account_number=None, account_name=None, RECIPIENT_CODE=None, TRANSFER_CODE=None, REFERENCE=None, hostel=None):
        
        self.amount = amount
        self.account_number = account_number
        self.account_name = account_name
        self.hostel = hostel
        self.TRANSFER_CODE = RECIPIENT_CODE
        self.TRANSFER_CODE = TRANSFER_CODE
        self.REFERENCE = REFERENCE

        print(self.amount)

    def create_recipient(self):
        recipient_create_url="https://api.paystack.co/transferrecipient"

        #verif_acc = requests.post('https://api.paystack.co/bank/resolve?account_number=0594438287&bank_code=MTN', headers=self.headers)
        #print(f'code: {verif_acc}')
        banks_url="https://api.paystack.co/bank"

        bank_code = requests.get(banks_url, f'Authorization: {self.SECRET_KEY}')

        print(bank_code.json())

        #BLP9yzThAkqcjN3

        data = { 
            "type": "mobile_money",
            "name": self.account_name,
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
            "reason": f"Being Payment for {self.hostel} hostel fee", 
            "amount": self.amount, 
            "recipient": recipient
        }

        try:

            start_transfer = requests.post(transfer_url, headers=self.headers, json=data)
            transfer_data= start_transfer.json()
            #print(transfer_data)
            self.TRANSFER_CODE = transfer_data['data']['transfer_code']

        except Exception as e:
            raise e



    def disable_otp(self):

        #request to disable otp
        otp_url_disable = 'https://api.paystack.co/transfer/disable_otp'
        r = requests.post(otp_url_disable, headers=self.headers)


        #finalizing the disabling of the otp
        url='https://api.paystack.co/transfer/disable_otp_finalize'
        
        data = {
            'otp': '806514'
        }

        res = requests.post(url, headers=self.headers, json=data)
        


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
            print(finalize_trans_data)
            #self.REFERENCE = finalize_trans_data['data']['reference']
        except Exception as e:
            raise e


    #perform the transfer
    def verify_transfer(self):

        ref = self.REFERENCE
        url='https://api.paystack.co/transfer/verify/{ref}'

        try:
            response = requests.get(url, headers=self.headers)
            #response_data = response.json()
        except Exception as e:

            raise e