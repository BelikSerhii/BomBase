import random
import time
from web3 import Web3
from eth_account.messages import encode_defunct

RPC_URL = 'https://base.llamarpc.com'
web3 = Web3(Web3.HTTPProvider(RPC_URL))

claim_contract_abi = [
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

comment_contract_abi = [
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

execute_contract_abi = [
    {"inputs":[],"name":"UnsuccessfulExecution","type":"error"},
    {"inputs":[],"name":"UnsuccessfulPayment","type":"error"},
    {
        "inputs":[
            {
                "components":[
                    {"internalType":"address","name":"module","type":"address"},
                    {"internalType":"bytes","name":"data","type":"bytes"},
                    {"internalType":"uint256","name":"value","type":"uint256"}
                ],
                "internalType":"struct ReservoirV6_0_1.ExecutionInfo[]",
                "name":"executionInfos",
                "type":"tuple[]"
            }
        ],
        "name":"execute",
        "outputs":[],
        "stateMutability":"payable",
        "type":"function"
    },
    {
        "inputs":[
            {
                "components":[
                    {"internalType":"address","name":"module","type":"address"},
                    {"internalType":"bytes","name":"data","type":"bytes"},
                    {"internalType":"uint256","name":"value","type":"uint256"}
                ],
                "internalType":"struct ReservoirV6_0_1.ExecutionInfo[]",
                "name":"executionInfos",
                "type":"tuple[]"
            },
            {
                "components":[
                    {"internalType":"address","name":"target","type":"address"},
                    {"internalType":"bytes","name":"data","type":"bytes"},
                    {"internalType":"uint256","name":"threshold","type":"uint256"}
                ],
                "internalType":"struct ReservoirV6_0_1.AmountCheckInfo",
                "name":"amountCheckInfo",
                "type":"tuple"
            }
        ],
        "name":"executeWithAmountCheck",
        "outputs":[],
        "stateMutability":"payable",
        "type":"function"
    },
    {"stateMutability":"payable","type":"receive"}
]

simple_mint_abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "_id", "type": "uint256"}
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
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

olimp_contract_abi = [
    {
        "inputs": [
            {"internalType": "uint32", "name": "qty", "type": "uint32"},
            {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"},
            {"internalType": "uint64", "name": "timestamp", "type": "uint64"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"}
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

def load_private_keys(file_path):
    with open(file_path, 'r') as file:
        private_keys = file.read().splitlines()
    return private_keys

def estimate_gas_with_randomization(transaction):
    estimated_gas = web3.eth.estimate_gas(transaction)
    return int(estimated_gas * random.uniform(1.1, 1.2))

def claim_tokens(private_key, contract_address, receiver, quantity, currency, price_per_token, allowlist_proof, data):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=claim_contract_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price

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
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    gas_limit = estimate_gas_with_randomization(transaction)
    transaction['gas'] = gas_limit

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash

def mint_with_comment(private_key, contract_address, quantity, payable_amount):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=comment_contract_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price

    transaction = contract.functions.mintWithComment(account.address, quantity, '').build_transaction({
        'from': account.address,
        'value': payable_amount,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    gas_limit = estimate_gas_with_randomization(transaction)
    transaction['gas'] = gas_limit

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash

def execute_function(private_key, contract_address, execution_infos):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=execute_contract_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price

    transaction = contract.functions.execute(execution_infos).build_transaction({
        'from': account.address,
        'value': sum(info['value'] for info in execution_infos),
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    gas_limit = estimate_gas_with_randomization(transaction)
    transaction['gas'] = gas_limit

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash

def mint_simple(private_key, contract_address, mint_id):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=simple_mint_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price

    transaction = contract.functions.mint(mint_id).build_transaction({
        'from': account.address,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    gas_limit = estimate_gas_with_randomization(transaction)
    transaction['gas'] = gas_limit

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash

def mint_tokens_olimp(private_key, contract_address, qty, proof, timestamp, signature, value):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(address=contract_address, abi=olimp_contract_abi)
    nonce = web3.eth.get_transaction_count(account.address)

    gas_price = web3.eth.gas_price

    transaction = contract.functions.mint(qty, proof, timestamp, signature).build_transaction({
        'from': account.address,
        'value': value,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    gas_limit = estimate_gas_with_randomization(transaction)
    transaction['gas'] = gas_limit

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash

def generate_signature(private_key, qty, timestamp):
    message = web3.solidity_keccak(
        ['uint32', 'uint64'],
        [qty, timestamp]
    )
    encoded_message = encode_defunct(message)
    signed_message = web3.eth.account.sign_message(encoded_message, private_key=private_key)
    return signed_message.signature

def main():
    private_keys = load_private_keys('wallets.txt')

    claim_contract_address = '0x6B033e8199ce2E924813568B716378aA440F4C67'
    comment_contracts = []
    execute_contract_address = '0x1aeD60A97192157fDA7fb26267A439d523d09c5e'
    simple_mint_contracts = ['0x2aa80a13395425EF3897c9684a0249a5226eA779']
    olimp_contract_address = '0xEEadefc9Df7ed4995cb93f5b5D9b923a7Dff8599'

    quantity = 1
    currency = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    price_per_token = web3.to_wei(0.0001, 'ether')
    allowlist_proof = (
        ['0x0000000000000000000000000000000000000000000000000000000000000000'],
        1157920892373161954235709850086879078532699846656403945758400791312963935,
        web3.to_wei(0.0001, 'ether'),
        '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    )
    data = b''

    comment_quantity = 1
    comment_payable_amount = web3.to_wei(0.0001, 'ether')

    functions = [
        ('claim', lambda pk: claim_tokens(pk, claim_contract_address, web3.eth.account.from_key(pk).address, quantity, currency, price_per_token, allowlist_proof, data)),
        ('comment', lambda pk: [mint_with_comment(pk, contract, comment_quantity, comment_payable_amount) for contract in comment_contracts]),
        ('execute', lambda pk: execute_function(pk, execute_contract_address, [{'module': 'module_address', 'data': 'data', 'value': 0}])),
        ('mint', lambda pk: [mint_simple(pk, contract, 1) for contract in simple_mint_contracts]),
        ('olimp', lambda pk: mint_tokens_olimp(pk, olimp_contract_address, 1, ['proof'], int(time.time()), generate_signature(pk, 1, int(time.time())), web3.to_wei(0.0001, 'ether')))
    ]

    for private_key in private_keys:
        random.shuffle(functions)
        for func_name, func in functions:
            try:
                if func_name == 'comment' or func_name == 'mint':
                    for tx_hash in func(private_key):
                        if tx_hash:
                            print(f'{func_name} transaction successful. Hash: {tx_hash.hex()}')
                        time.sleep(random.uniform(10, 30))
                else:
                    tx_hash = func(private_key)
                    if tx_hash:
                        print(f'{func_name} transaction successful. Hash: {tx_hash.hex()}')
            except Exception as e:
                print(f'{func_name} transaction failed: {e}')
            time.sleep(random.uniform(10, 30))
        time.sleep(random.uniform(60, 100))

if __name__ == '__main__':
    main()
