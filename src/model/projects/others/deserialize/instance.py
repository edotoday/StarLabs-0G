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

# Astrostake contracts - will randomly choose one
ASTROSTAKE_CONTRACTS = [
    "0x3Ec65770216a325aaB2d2bC33C375b4CA330bDB5",
    "0x2D4C1932155e0e433E6a5A1D84Cf2b38889f407D"
]

# ABI for staking function (method ID: 0x5c19a95c)
ASTROSTAKE_ABI = [
    {
        "name": "stake",
        "type": "function",
        "inputs": [{"name": "_user", "type": "address"}],
        "outputs": [],
        "payable": True,
        "signature": "0x5c19a95c",
        "stateMutability": "payable",
    }
]


@retry_async(default_value=False)
async def astrostake_staking(
    account_index: int,
    session: primp.AsyncClient,
    web3: Web3Custom,
    config: Config,
    wallet: Account,
) -> bool:
    try:
        logger.info(f"{account_index} | Starting Astrostake native token staking...")

        # Get native token balance
        balance = await web3.get_balance(wallet.address)
        logger.info(f"{account_index} | Native balance: {balance.ether:.6f} 0G")

        # Check minimum balance for gas + staking
        min_balance_for_gas = 0.00001  # Reserve for gas fees
        if balance.ether <= min_balance_for_gas:
            raise Exception(f"Insufficient balance for staking. Need more than {min_balance_for_gas} 0G")

        # Get staking percentage from config
        stake_percent_min, stake_percent_max = config.STAKING.ASTROSTAKE.BALANCE_PERCENT_TO_STAKE
        stake_percentage = random.randint(stake_percent_min, stake_percent_max)
        
        # Calculate staking amount (excluding gas reserve)
        available_for_staking = balance.ether - min_balance_for_gas
        stake_amount_ether = (available_for_staking * stake_percentage) / 100
        stake_amount_wei = web3.convert_to_wei(stake_amount_ether, 18)

        logger.info(f"{account_index} | Will stake {stake_percentage}% ({stake_amount_ether:.6f} 0G)")

        # Randomly select contract
        selected_contract = random.choice(ASTROSTAKE_CONTRACTS)
        logger.info(f"{account_index} | Selected contract: {selected_contract}")

        # Данные для вызова функции stake на основе транзакций из примера
        data = f"0x5c19a95c000000000000000000000000{wallet.address[2:].lower()}"

        # Получаем параметры газа
        gas_params = await web3.get_gas_params()
        if gas_params is None:
            raise Exception("Failed to get gas parameters")

        # Подготавливаем транзакцию
        tx_params = {
            "from": wallet.address,
            "to": web3.web3.to_checksum_address(selected_contract),
            "value": stake_amount_wei,
            "data": data,
            "nonce": await web3.web3.eth.get_transaction_count(wallet.address),
            "chainId": CHAIN_ID,
            **gas_params,
        }

        # Устанавливаем тип транзакции в зависимости от параметров газа
        if "maxFeePerGas" in gas_params:
            tx_params["type"] = "0x2"  # Use hex string format

        # Оцениваем газ динамически
        try:
            estimated_gas = await web3.estimate_gas(tx_params)
            tx_params["gas"] = estimated_gas

        except Exception as e:
            raise Exception(f"Error estimating gas: {e}")

        # Выполняем транзакцию
        tx_hash = await web3.execute_transaction(
            tx_params,
            wallet=wallet,
            chain_id=CHAIN_ID,
            explorer_url=EXPLORER_URL_0G,
        )

        if tx_hash:
            logger.success(f"{account_index} | Successfully staked {stake_amount_ether:.6f} 0G to Astrostake contract {selected_contract}")
            return True

        raise Exception(f"Failed to stake to Astrostake")

    except Exception as e:
        random_pause = random.randint(
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
        )
        logger.error(
            f"{account_index} | Failed to stake to Astrostake: {str(e)}. Sleeping {random_pause} seconds..."
        )
        await asyncio.sleep(random_pause)
        raise
