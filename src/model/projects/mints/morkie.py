import asyncio
import random
import hashlib
import time
import os

from eth_account import Account
from src.model.help.captcha import NoCaptcha
from src.model.onchain.web3_custom import Web3Custom
from loguru import logger
import primp

from src.utils.decorators import retry_async
from src.utils.config import Config
from src.utils.constants import EXPLORER_URL_0G

CHAIN_ID = 16601

# Минимальный ABI для проверки баланса NFT
NFT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    }
]


@retry_async(default_value=False)
async def morkie_og_mint(
    account_index: int,
    session: primp.AsyncClient,
    web3: Web3Custom,
    config: Config,
    wallet: Account,
):
    try:
        MORKIE_0GOG_CONTRACT = "0x3597a99af936d4b61E8E6051D11607e60F7BC413"

        logger.info(f"{account_index} | Checking balance of Morkie 0G NFT...")

        # Проверяем баланс NFT на кошельке
        nft_contract = web3.web3.eth.contract(
            address=web3.web3.to_checksum_address(MORKIE_0GOG_CONTRACT), abi=NFT_ABI
        )

        nft_balance = await nft_contract.functions.balanceOf(wallet.address).call()

        if nft_balance > 0:
            logger.success(
                f"{account_index} | Wallet already has {nft_balance} OG (MORKIE-0G) NFT"
            )
            return True

        # Проверяем баланс нативной монеты
        balance = await web3.get_balance(wallet.address)
        if balance.ether == 0:  # 0.005 for mint + a little on gas
            raise Exception(f"Insufficient wallet balance: wallet balance is 0")

        logger.info(f"{account_index} | Starting mint of Morkie 0G NFT...")

        # Данные для вызова функции mint на основе транзакций из примера
        data = f"0x84bb1e42000000000000000000000000{wallet.address[2:].lower()}0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        # Получаем параме тры газа
        gas_params = await web3.get_gas_params()
        if gas_params is None:
            raise Exception("Failed to get gas parameters")

        # Подготавливаем транзакцию
        tx_params = {
            "from": wallet.address,
            "to": web3.web3.to_checksum_address(MORKIE_0GOG_CONTRACT),
            "value": 0,  # 0 A0GI
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
            logger.success(f"{account_index} | Successfully minted Morkie 0G NFT")
            return True

        raise Exception("Failed to mint Morkie 0G NFT")

    except Exception as e:
        random_pause = random.randint(
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
        )
        logger.error(
            f"{account_index} | Error minting Morkie 0G NFT: {e}. Waiting {random_pause} seconds..."
        )
        await asyncio.sleep(random_pause)
        raise
