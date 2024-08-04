import time
import random
from web3 import Web3

# RPC
rpc_url = 'https://base.drpc.org'
web3 = Web3(Web3.HTTPProvider(rpc_url))

# ABI
contract_address = '0x204B70042E2FD080ab88bdCAcB9a557EE3da4bBc'
abi = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "account",
                "type": "address"
            },
            {
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]


contract = web3.eth.contract(address=contract_address, abi=abi)

# Шлях check.txt
wallets_file_path = 'check.txt'


with open(wallets_file_path, 'r') as file:
    wallet_addresses = [line.strip() for line in file.readlines()]


for wallet_address in wallet_addresses:
    try:
        
        checksum_address = web3.to_checksum_address(wallet_address)
        
        total_tokens = 0
        
        for token_id in range(0, 7):
            balance = contract.functions.balanceOf(checksum_address, token_id).call()
            total_tokens += balance
        
        print(f'На гаманці {checksum_address} знаходиться {total_tokens} токенів.')

        # Пауза
        pause_duration = random.uniform(1, 3)  
        time.sleep(pause_duration)
        
    except Exception as e:
        print(f'Не вдалося перевірити баланс для гаманця {wallet_address}: {e}')
