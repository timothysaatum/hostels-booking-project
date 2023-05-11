import base64
import requests
import uuid

primary_key = 'd84a6ccb46e24ad2b800b528763cdb45'
#secondary_key = aba2eae9b77446a7ab4425846c1094e2

def get_access_token(api_key, api_secret):
	'''
	join api key and api secret separated by :
	'''

	auth_string = f'{api_key}:{api_secret}'

	'''
	using base64 to encode the auth string
	'''

	encoded_auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')

	'''
	setting the request headers
	'''

	headers = {
		'Authorization' : f'Basic {encoded_auth_string}', 
		'Ocp-Apim-Subscription-Key' : primary_key,
'		 Content-Type' : 'application/json',
	}

	'''
	making a request to the token endpoint
	'''

	response = requests.get('https://api.momodeveloper.mtn.com/', headers=headers)
	'''
	parsing the access token from the response
	'''
	access_token = response.json.get('access_token')

	return access_token


def make_withdrawal(amount=None, account_number=None, access_token=None):
	headers = {
		'Content-Type':'application/json',
		'Ocp-Apim-Subscription-key':primary_key
		'Ocp-Apim-Subscription-secret':'primary_key',
	}
	endpoint = 'https://api.mtn.com/collection/v1_0/requesttopay'
	payload = {
		'amount':amount,
		'currency':'EUR',
		'externalId':'123456789',
		'payer':{
			'partyIdType':'MSISDN',
			'partyId': '0594438287'
		},
		'payerMessage':'Payment for hostel fee',
		'payeeNote':'Paid to gunarcom'
	}


	response = requests.post(endpoint, json=payload, headers=headers)

	amt = response.json.get('amount')

	return amt

def initiate_payment(amount=None, account_number=None, access_token=None):
	'''
	setting the request headers
	'''

	headers = {'Authorization':f'Bearer {access_token}', 'Content-Type':'application/json'}

	'''
	setting the request headers
	'''

	data = {
		'amount':amount,
		'currency': 'CEDI',
		'externalId':'12345',
		'payer':{
			'partyIdType':'MSISDN',
			'partyId':account_number
		},
		'payerMessage':'Payment of accomodation fees',
		'payeeNote': 'Commission payment'
	}

	'''
	Make the request to the payment endpoint
	'''

	response = requests.post('https://api.momodeveloper.mtn.com/collection/', headers=headers, json=data)

	'''
	parsing the transaction ID from the response
	'''

	transaction_id = response.json.get('transactionId')

	return transaction_id

reference_id = str(uuid.uuid4())
api_key = 'aba2eae9b77446a7ab4425846c1094e2'
api_secret = reference_id
access_token = get_access_token(api_key, api_secret)

#pay_amt = 100.01
#momo_no = '0594438287'
transaction_id = initiate_payment(pay_amt, momo_no, access_token)
