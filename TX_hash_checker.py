from datetime import datetime
import requests
from requests.exceptions import RequestException
"""This program checks the sender and receiver of the transaction in TRC20 network USDT"""
# Define the USDT contract address on TRON network
usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

# Define the base URL for TRONSCAN API
base_url = "https://apilist.tronscan.org/api"
    
def get_tx_info(tx_hash, wallet_customer, wallet_bugs):
    try: 
        # Get the transaction details by hash
        tx_url = base_url + "/transaction-info?hash=" + tx_hash
        # tx_response = requests.get(tx_url).json()
        tx_response = requests.get(tx_url)

         # Check if the response status code is 200
        if tx_response. status_code != 200:
            return {'status': False, 'msg': f"Error: Received non-200 status code: {tx_response.status_code}"}

        # Check if the content type is application/json
        if not tx_response.headers["content-type"].strip().startswith("application/json"):
            return {'status': False, 'msg': "Error: Received non-JSON content type"}

        tx_data = tx_response.json()
        # print(tx_data)
        
        if not tx_data["contractRet"] == "SUCCESS":
            return {'status': False, 'msg': "The transaction didn't complete curractly(FAILED)."}
        
        confirmations = tx_data["confirmations"]
        min_confirmations = 20 # Change this to your desired number
        if confirmations < min_confirmations:
            return {'status': False, 'msg': "Warning: The transaction is not confirmed by enough blocks."}
        
        sender = tx_data["ownerAddress"]
        if not wallet_customer == sender:
            return {'status': False, 'msg': "The sender of the amount is not authrized. please double check the TX"}

        receiver = tx_data['trc20TransferInfo'][0]['to_address']
        if not receiver == wallet_bugs:
            return {'status': False, 'msg': "The reciever wallet doesn't belong to us. Please double-check the TX."}
        
        contract_type = tx_data["contract_type"]
        if not contract_type == "trc20":
            return {'status': False, 'msg': "The format of the TX is not trc20. Please double-check the TX."}
        
        revert = tx_data["revert"]
        if revert == True:
            return {'status': False, 'msg': "revert happened. probably your money will come back to your wallet."}
        # below here is accepted tx.
        time = tx_data["timestamp"]
        timestamp = time / 1000 
        date_time = datetime.fromtimestamp(timestamp)
        # Get the amount of USDT transferred (in sun, need to divide by 10**6)
        amount = int(tx_data["trigger_info"]["parameter"]["_value"]) / 10**6
        return {'status': True, 'msg': "TX was successfully added", 'time': date_time, 'amount': amount}
        
    except RequestException as e:
        return {'status': False, 'msg': f"Request error: {e}"}
    except Exception as e:
        return {'status': False, 'msg': f"TX checker has error: {e}"}
