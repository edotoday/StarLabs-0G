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


@retry_async(default_value=False)
async def mint_token(
    account_index: int,
    web3: Web3Custom,
    wallet: Account,
    token_name: str,
    contract_address: str,
    config: Config,
) -> bool:
    try:
        logger.info(f"{account_index} | Starting {token_name} token mint...")

        contract = web3.web3.eth.contract(
            address=web3.web3.to_checksum_address(contract_address), abi=MINT_ABI
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

        mint_tx = await contract.functions.mint().build_transaction(tx_params)

        try:
            estimated_gas = await web3.estimate_gas(mint_tx)
            mint_tx["gas"] = estimated_gas
        except Exception as e:
            raise Exception(f"Error estimating gas: {e}")

        tx_hash = await web3.execute_transaction(
            mint_tx,
            wallet=wallet,
            chain_id=CHAIN_ID,
            explorer_url=EXPLORER_URL_0G,
        )

        if tx_hash:
            logger.success(f"{account_index} | Successfully minted {token_name} token")
            return True

        raise Exception(f"Failed to mint {token_name} token")

    except Exception as e:
        if "Wait 24 hours" in str(e):
            logger.success(
                f"{account_index} | Faucet already requested today. Wait 24 hours before requesting again."
            )
            return True
        
        random_pause = random.randint(
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
            config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
        )
        logger.error(
            f"{account_index} | Failed to mint {token_name} token: {str(e)}. Sleeping {random_pause} seconds..."
        )
        await asyncio.sleep(random_pause)
        raise


async def jaine_faucet(
    account_index: int,
    session: primp.AsyncClient,
    web3: Web3Custom,
    config: Config,
    wallet: Account,
):
    try:
        logger.info(f"{account_index} | Starting token faucets...")

        balance = await web3.get_balance(wallet.address)
        if balance.ether < 0.00001:
            raise Exception(f"Insufficient A0GI balance for gas fees")

        success_count = 0
        
        for token_name, contract_address in TOKEN_CONTRACTS.items():
            try:
                success = await mint_token(
                    account_index,
                    web3,
                    wallet,
                    token_name,
                    contract_address,
                    config,
                )
                if success:
                    success_count += 1
                    logger.success(f"{account_index} | Successfully minted {token_name}")
                else:
                    logger.error(f"{account_index} | Failed to mint {token_name}")
            except Exception as e:
                logger.error(f"{account_index} | Error minting {token_name}: {str(e)}")
                continue
            finally:
                random_pause = random.randint(
                    config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                    config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                )
                logger.info(
                    f"{account_index} | Sleeping {random_pause} seconds after attempting {token_name}..."
                )
                await asyncio.sleep(random_pause)

        if success_count >= 1:
            logger.success(f"{account_index} | Successfully completed token faucets ({success_count}/3)")
            return True
        else:
            logger.warning(f"{account_index} | All token faucets failed")
            return False

    except Exception as e:
        logger.error(f"{account_index} | Token faucets error: {e}")
        return False
