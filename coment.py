import random
import time
from web3 import Web3
import requests

# RPC
RPC_URL = 'https://base.llamarpc.com'
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Список контрактів
contracts = [
    '0xbFa3fF9dcdB811037Bbec89f89E2751114ECD299', #1000
    '0x8605522B075aFeD48f9987E573E0AA8E572B8452', #1000
    '0xea50e58B518435AD2CeCE84d1e099b2e0878B9cF', #1000
    '0x8e50c64310b55729F8EE67c471E052B1Cd7AF5b3', 
    '0x2a8e46E78BA9667c661326820801695dcf1c403E',
    '0xb620bEdCe2615A3F35273A08b3e45e3431229A60',
    '0x95ff853A4C66a5068f1ED8Aaf7c6F4e3bDBEBAE1',
    '0x4beAdC00E2A6b6C4fAc1a43FF340E5D71CBB9F77',
    '0x2382456097cC12ce54052084e9357612497FD6be',
    '0x146B627a763DFaE78f6A409CEF5B8ad84dDD4150',
    '0x1f006edBc0Bcc528A743ee7A53b5e3dD393A1Df6',
    '0x13fCcd944B1D88d0670cae18A00abD272256DDeE',
    '0xd1E1da0b62761b0df8135aE4e925052C8f618458',
    '0x6A3dA97Dc82c098038940Db5CB2Aa6B1541f2ebe',
    '0xEb9A3540E6A3dc31d982A47925d5831E02a3Fe1e',
    '0x892Bc2468f20D40F4424eE6A504e354D9D7E1866',
    '0x6a43B7e3ebFc915A8021dd05f07896bc092d1415',
    '0x9FF8Fd82c0ce09caE76e777f47d536579AF2Fe7C'
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

    
    
    gas_limit = int(random.uniform(180000, 300000))

    transaction_cost = gas_limit * gas_price + payable_amount
    balance = web3.eth.get_balance(account.address)

    if balance < transaction_cost:
        raise Exception(f'Insufficient funds: balance {balance}, tx cost {transaction_cost}')

    if check_balance(contract, account.address):
        print(f'Address {account.address} already has a token. Skipping minting for contract {contract_address}.')
        return None

    transaction = contract.functions.mintWithComment(account.address, quantity, '').build_transaction({
        'from': account.address,
        'value': payable_amount,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash


def main():
    private_keys = load_private_keys('wallets.txt')
    quantity = 1
    payable_amount = web3.to_wei(0.0001, 'ether')

    # Перемішати приватні ключі та контракти
    random.shuffle(private_keys)
    for private_key in private_keys:
        random.shuffle(contracts)  
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
