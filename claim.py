import random
import time
from web3 import Web3

# RPC
RPC_URL = 'https://base.llamarpc.com'
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# ABI 
contract_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "_receiver", "type": "address"},
            {"internalType": "uint256", "name": "_quantity", "type": "uint256"},
            {"internalType": "address", "name": "_currency", "type": "address"},
            {"internalType": "uint256", "name": "_pricePerToken", "type": "uint256"},
            {
                "components": [
                    {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"},
                    {"internalType": "uint256", "name": "quantityLimitPerWallet", "type": "uint256"},
                    {"internalType": "uint256", "name": "pricePerToken", "type": "uint256"},
                    {"internalType": "address", "name": "currency", "type": "address"}
                ],
                "internalType": "struct IDrop.AllowlistProof",
                "name": "_allowlistProof",
                "type": "tuple"
            },
            {"internalType": "bytes", "name": "_data", "type": "bytes"}
        ],
        "name": "claim",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]


def load_private_keys(file_path):
    with open(file_path, 'r') as file:
        private_keys = file.read().splitlines()
    return private_keys


def claim_tokens(private_key, contract_address, receiver, quantity, currency, price_per_token, allowlist_proof, data):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price
    gas_limit = int(random.uniform(180000, 300000))

    transaction = contract.functions.claim(
        receiver, 
        quantity, 
        currency, 
        price_per_token, 
        allowlist_proof, 
        data
    ).build_transaction({
        'from': account.address,
        'value': price_per_token * quantity,
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
    currency = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    price_per_token = web3.to_wei(0, 'ether')

    allowlist_proof = (
        ['0x0000000000000000000000000000000000000000000000000000000000000000'],
        1,
        web3.to_wei(0, 'ether'),
        '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    )

    data = b''

    for private_key in private_keys:
        account = web3.eth.account.from_key(private_key)
        receiver = account.address

        try:
            tx_hash = claim_tokens(private_key, '0x0821D16eCb68FA7C623f0cD7c83C8D5Bd80bd822', receiver, quantity, currency, price_per_token, allowlist_proof, data)
            if tx_hash:
                print(f'Transaction successful. Hash: {tx_hash.hex()}')
        except Exception as e:
            print(f'Transaction failed: {e}')

        mint_pause = random.uniform(1, 3)
        print(f'Pausing for {mint_pause} seconds between executions...')
        time.sleep(mint_pause)

        wallet_pause = random.uniform(5, 10)
        print(f'Pausing for {wallet_pause} seconds before using a new wallet...')
        time.sleep(wallet_pause)

if __name__ == '__main__':
    main()
