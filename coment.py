import random
import time
from web3 import Web3
import requests

# RPC 
RPC_URL = 'https://base.llamarpc.com'
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Контракти
contracts = [
    '0xE65dFa5C8B531544b5Ae4960AE0345456D87A47D',
    '0x13F294BF5e26843C33d0ae739eDb8d6B178740B0',
    '0xE8aD8b2c5Ec79d4735026f95Ba7C10DCB0D3732B',
    '0xb5408b7126142C61f509046868B1273F96191b6d',
    '0xC00F7096357f09d9f5FE335CFD15065326229F66',
    '0x96E82d88c07eCa6a29B2AD86623397B689380652',
    '0x955FdFdFd783C89Beb54c85f0a97F0904D85B86C',
    #'0x615194d9695d0c02Fc30a897F8dA92E17403D61B',
    '0xb0FF351AD7b538452306d74fB7767EC019Fa10CF'
]

# ABI 
contract_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "quantity", "type": "uint256"},
            {"internalType": "string", "name": "comment", "type": "string"}
        ],
        "name": "mintWithComment",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


def load_private_keys(file_path):
    with open(file_path, 'r') as file:
        private_keys = file.read().splitlines()
    return private_keys


def check_balance(contract, address):
    balance = contract.functions.balanceOf(address).call()
    return balance > 0


def mint_tokens(private_key, contract_address, quantity, payable_amount):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price

    transaction = contract.functions.mintWithComment(account.address, quantity, '').build_transaction({
        'from': account.address,
        'value': payable_amount,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    
    estimated_gas = web3.eth.estimate_gas(transaction)
    gas_limit = int(estimated_gas * random.uniform(1.1, 1.2))  

    transaction['gas'] = gas_limit

    transaction_cost = gas_limit * gas_price + payable_amount
    balance = web3.eth.get_balance(account.address)

    if balance < transaction_cost:
        raise Exception(f'Insufficient funds: balance {balance}, tx cost {transaction_cost}')

    if check_balance(contract, account.address):
        print(f'Address {account.address} already has a token. Skipping minting for contract {contract_address}.')
        return None

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash


def main():
    private_keys = load_private_keys('wallets.txt')
    quantity = 1
    payable_amount = web3.to_wei(0.0001, 'ether')

    
    random.shuffle(private_keys)
    random.shuffle(contracts)

    for private_key in private_keys:
        for contract_address in contracts:
            try:
                tx_hash = mint_tokens(private_key, contract_address, quantity, payable_amount)
                if tx_hash:
                    print(f'Transaction successful. Hash: {tx_hash.hex()}')
            except Exception as e:
                print(f'Transaction failed: {e}')

            mint_pause = random.uniform(10, 30)
            print(f'Pausing for {mint_pause} seconds between mints...')
            time.sleep(mint_pause)

        wallet_pause = random.uniform(60, 100)
        print(f'Pausing for {wallet_pause} seconds before using a new wallet...')
        time.sleep(wallet_pause)

if __name__ == '__main__':
    main()
