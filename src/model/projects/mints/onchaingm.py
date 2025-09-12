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

STORAGE_SCAN_CONTRACT = "0x0460aA47b41a66694c0a73f667a1b795A5ED3556"
CHAIN_ID = 16601

ONCHAINGM_CONTRACT = "0x84A2dc4fd3EFBbAcCc2f2edfC65F1067545275c8"

@retry_async(default_value=False)
async def onchaingm_gm(
    account_index: int,
    session: primp.AsyncClient,
    web3: Web3Custom,
    config: Config,
    wallet: Account,
):
    try:
        logger.info(f"{account_index} | Starting OnchainGM GM mint...")

        # Проверяем баланс нативной монеты
        balance = await web3.get_balance(wallet.address)
        if balance.ether < 0.003:  # 0.003 for mint + a little on gas
            raise Exception(f"Insufficient wallet balance: {balance.ether} A0GI")

        logger.info(f"{account_index} | Starting mint of OnchainGM GM...")

        # Стоимость минта в wei (0.00029 A0GI)
        mint_price = web3.web3.to_wei(0.00029, "ether")

        data = "0x84a3bb6b0000000000000000000000000000000000000000000000000000000000000000"

        # Получаем параметры газа
        gas_params = await web3.get_gas_params()
        if gas_params is None:
            raise Exception("Failed to get gas parameters")

        # Подготавливаем транзакцию
        tx_params = {
            "from": wallet.address,
            "to": web3.web3.to_checksum_address(ONCHAINGM_CONTRACT),
            "value": mint_price,  # 0.00029 A0GI
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
            logger.success(
                f"{account_index} | Successfully minted OnchainGM GM"
            )
            return True

        raise Exception("Failed to mint OnchainGM GM")

    except Exception as e:
        random_pause = random.randint(
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
        )
        logger.error(
            f"{account_index} | Error minting OnchainGM GM: {e}. Waiting {random_pause} seconds..."
        )
        await asyncio.sleep(random_pause)
        raise
