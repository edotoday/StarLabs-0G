import asyncio
import random

from eth_account import Account
from src.model.onchain.web3_custom import Web3Custom
from loguru import logger
import primp

from src.utils.decorators import retry_async
from src.utils.config import Config
from src.utils.constants import EXPLORER_URL_0G

CHAIN_ID = 16601

TOKEN_CONTRACTS = {
    "ETH": "0x0fE9B43625fA7EdD663aDcEC0728DD635e4AbF7c",
    "USDT": "0x3eC8A8705bE1D5ca90066b37ba62c4183B024ebf",
    "BTC": "0x36f6414FF1df609214dDAbA71c84f18bcf00F67d"
}

# USDT token used for staking (different from faucet USDT)
STAKING_USDT_CONTRACT = "0x217c6f12d186697b16de9e1ae9f85389b93bdb30"

MINT_ABI = [
    {
        "name": "mint",
        "type": "function",
        "inputs": [],
        "outputs": [],
        "payable": True,
        "signature": "0x1249c58b",
        "stateMutability": "payable",
    }
]

TRADEGPT_ABI = [
    {
        "name": "requestTokens",
        "type": "function",
        "inputs": [],
        "outputs": [],
        "payable": False,
        "signature": "0x359cf2b7",
        "stateMutability": "nonpayable",
    }
]

TRADEGPT_CONTRACT = "0x75d4225b61324EA006582456F3871A6c16e99034"
STAKING_CONTRACT = "0x3bE9d3C9d313B580d0157Bf0B10fFCB8B92F04D4"

STAKING_ABI = [
    {
        "name": "deposit",
        "type": "function",
        "inputs": [{"name": "amount", "type": "uint256"}],
        "outputs": [],
        "payable": False,
        "signature": "0xb6b55f25",
        "stateMutability": "nonpayable",
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]


@retry_async(default_value=False)
async def tradegpt_faucet(
    account_index: int,
    session: primp.AsyncClient,
    web3: Web3Custom,
    config: Config,
    wallet: Account,
) -> bool:
    try:
        logger.info(f"{account_index} | Starting TradeGPT faucet...")

        balance = await web3.get_balance(wallet.address)
        if balance.ether < 0.00001:
            raise Exception(f"Insufficient A0GI balance for gas fees")

        contract = web3.web3.eth.contract(
            address=web3.web3.to_checksum_address(TRADEGPT_CONTRACT), abi=TRADEGPT_ABI
        )

        gas_params = await web3.get_gas_params()
        if gas_params is None:
            raise Exception("Failed to get gas parameters")

        if "gasPrice" not in gas_params and "maxFeePerGas" not in gas_params:
            try:
                current_gas_price = await web3.web3.eth.gas_price
                gas_params["gasPrice"] = current_gas_price
                logger.info(
                    f"{account_index} | Using network gas price: {web3.web3.from_wei(gas_params['gasPrice'], 'gwei')} gwei"
                )
            except Exception as e:
                logger.error(f"{account_index} | Failed to get network gas price: {e}")
                raise Exception(f"Failed to get network gas price: {e}")

        tx_params = {
            "from": wallet.address,
            "value": 0,
            "nonce": await web3.web3.eth.get_transaction_count(
                wallet.address, "pending"
            ),
            "chainId": CHAIN_ID,
            **gas_params,
        }

        if "maxFeePerGas" in gas_params:
            tx_params["type"] = "0x2"

        request_tx = await contract.functions.requestTokens().build_transaction(tx_params)

        try:
            estimated_gas = await web3.estimate_gas(request_tx)
            request_tx["gas"] = estimated_gas
        except Exception as e:
            raise Exception(f"Error estimating gas: {e}")

        tx_hash = await web3.execute_transaction(
            request_tx,
            wallet=wallet,
            chain_id=CHAIN_ID,
            explorer_url=EXPLORER_URL_0G,
        )

        if tx_hash:
            logger.success(f"{account_index} | Successfully requested TradeGPT tokens")
            return True

        raise Exception(f"Failed to request TradeGPT tokens")

    except Exception as e:
        if "Wait 24 hours" in str(e) or "already requested" in str(e).lower():
            logger.success(
                f"{account_index} | TradeGPT faucet already requested today. Wait 24 hours before requesting again."
            )
            return True
        
        random_pause = random.randint(
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
        )
        logger.error(
            f"{account_index} | Failed to request TradeGPT tokens: {str(e)}. Sleeping {random_pause} seconds..."
        )
        await asyncio.sleep(random_pause)
        raise


@retry_async(default_value=False)
async def tradegpt_staking(
    account_index: int,
    session: primp.AsyncClient,
    web3: Web3Custom,
    config: Config,
    wallet: Account,
) -> bool:
    try:
        logger.info(f"{account_index} | Starting TradeGPT staking...")

        balance = await web3.get_balance(wallet.address)
        if balance.ether < 0.00001:
            raise Exception(f"Insufficient A0GI balance for gas fees")

        usdt_balance = await web3.get_token_balance(
            wallet.address, 
            STAKING_USDT_CONTRACT, 
            ERC20_ABI, 
            decimals=18, 
            symbol="USDT"
        )

        if usdt_balance.formatted < 1:
            logger.info(f"{account_index} | USDT balance ({usdt_balance.formatted:.6f}) is less than 1, requesting from faucet...")
            faucet_result = await tradegpt_faucet(account_index, session, web3, config, wallet)
            if not faucet_result:
                raise Exception(f"Failed to get USDT from faucet")
            
            await asyncio.sleep(5)
            
            usdt_balance = await web3.get_token_balance(
                wallet.address, 
                STAKING_USDT_CONTRACT, 
                ERC20_ABI, 
                decimals=18, 
                symbol="USDT"
            )

        if usdt_balance.formatted <= 0:
            raise Exception(f"No USDT balance found after faucet")

        deposit_percentage = random.randint(50, 90)
        deposit_amount_ether = (usdt_balance.formatted * deposit_percentage) / 100
        deposit_amount_wei = web3.convert_to_wei(deposit_amount_ether, 18)

        logger.info(f"{account_index} | USDT balance: {usdt_balance.formatted:.6f} USDT")
        logger.info(f"{account_index} | Will deposit {deposit_percentage}% ({deposit_amount_ether:.6f} USDT)")

        approve_tx_hash = await web3.approve_token(
            token_address=STAKING_USDT_CONTRACT,
            spender_address=STAKING_CONTRACT,
            amount=deposit_amount_wei,
            wallet=wallet,
            chain_id=CHAIN_ID,
            token_abi=ERC20_ABI,
            explorer_url=EXPLORER_URL_0G,
        )

        if approve_tx_hash:
            logger.success(f"{account_index} | Successfully approved USDT for staking")

        staking_contract = web3.web3.eth.contract(
            address=web3.web3.to_checksum_address(STAKING_CONTRACT), 
            abi=STAKING_ABI
        )

        gas_params = await web3.get_gas_params()
        if gas_params is None:
            raise Exception("Failed to get gas parameters")

        if "gasPrice" not in gas_params and "maxFeePerGas" not in gas_params:
            try:
                current_gas_price = await web3.web3.eth.gas_price
                gas_params["gasPrice"] = current_gas_price
                logger.info(
                    f"{account_index} | Using network gas price: {web3.web3.from_wei(gas_params['gasPrice'], 'gwei')} gwei"
                )
            except Exception as e:
                logger.error(f"{account_index} | Failed to get network gas price: {e}")
                raise Exception(f"Failed to get network gas price: {e}")

        tx_params = {
            "from": wallet.address,
            "value": 0,
            "nonce": await web3.web3.eth.get_transaction_count(
                wallet.address, "pending"
            ),
            "chainId": CHAIN_ID,
            **gas_params,
        }

        if "maxFeePerGas" in gas_params:
            tx_params["type"] = "0x2"

        deposit_tx = await staking_contract.functions.deposit(deposit_amount_wei).build_transaction(tx_params)

        try:
            estimated_gas = await web3.estimate_gas(deposit_tx)
            deposit_tx["gas"] = estimated_gas
        except Exception as e:
            raise Exception(f"Error estimating gas: {e}")

        tx_hash = await web3.execute_transaction(
            deposit_tx,
            wallet=wallet,
            chain_id=CHAIN_ID,
            explorer_url=EXPLORER_URL_0G,
        )

        if tx_hash:
            logger.success(f"{account_index} | Successfully deposited {deposit_amount_ether:.6f} USDT to TradeGPT staking")
            return True

        raise Exception(f"Failed to deposit USDT to TradeGPT staking")

    except Exception as e:
        random_pause = random.randint(
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
        )
        logger.error(
            f"{account_index} | Failed to stake USDT to TradeGPT staking: {str(e)}. Sleeping {random_pause} seconds..."
        )
        await asyncio.sleep(random_pause)
        raise
