import asyncio
import base64
import hashlib
import random
import secrets
import string
from urllib.parse import unquote
from loguru import logger
from eth_account import Account
from src.model.help.captcha import NoCaptcha, Solvium
from src.model.onchain.web3_custom import Web3Custom
from src.model.projects.others.puzzlemania import constants

from datetime import datetime, timezone
import primp
from eth_account.messages import encode_defunct
from src.utils.decorators import retry_async
from src.utils.config import Config
from src.utils.constants import EXPLORER_URL_0G
from src.utils.client import create_twitter_client


class Puzzlemania:
    def __init__(
        self,
        account_index: int,
        session: primp.AsyncClient,
        web3: Web3Custom,
        config: Config,
        wallet: Account,
        proxy: str,
        private_key: str,
        twitter_token: str,
    ):
        self.account_index = account_index
        self.session = session
        self.web3 = web3
        self.config = config
        self.wallet = wallet
        self.proxy = proxy
        self.private_key = private_key
        self.twitter_token = twitter_token

        self.login_tokens = {
            "bearer_token": "",
            "privy_access_token": "",
            "refresh_token": "",
            "identity_token": "",
            "userLogin": "",
        }

    @retry_async(default_value=False)
    async def login(self):
        try:
            nonce = await self._get_nonce()

            current_time = (
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            )

            signature_text = f"puzzlemania.0g.ai wants you to sign in with your Ethereum account:\n{self.wallet.address}\n\nBy signing, you are proving you own this wallet and logging in. This does not initiate a transaction or cost any fees.\n\nURI: https://puzzlemania.0g.ai\nVersion: 1\nChain ID: 42161\nNonce: {nonce}\nIssued At: {current_time}\nResources:\n- https://privy.io"
            signature = await self.get_signature(signature_text, self.private_key)

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "privy-app-id": "clphlvsh3034xjw0fvs59mrdc",
                "privy-client": "react-auth:2.4.1",
                "referer": "https://puzzlemania.0g.ai/",
            }

            json_data = {
                "message": signature_text,
                "signature": "0x" + signature,
                "chainId": "eip155:42161",
                "walletClientType": "metamask",
                "connectorType": "injected",
                "mode": "login-or-sign-up",
            }

            response = await self.session.post(
                "https://auth.privy.io/api/v1/siwe/authenticate",
                headers=headers,
                json=json_data,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to login: {response.status_code} | {response.text}"
                )

            if response.status_code != 200:
                raise Exception(f"failed to login: {response.text}")

            data = response.json()

            self.login_tokens["bearer_token"] = data["token"]
            self.login_tokens["privy_access_token"] = data["privy_access_token"]
            self.login_tokens["refresh_token"] = data["refresh_token"]
            self.login_tokens["identity_token"] = data["identity_token"]

            self.session.headers.update(
                {"authorization": f"Bearer {self.login_tokens['bearer_token']}"}
            )

            if data["is_new_user"]:
                logger.success(
                    f"{self.wallet.address} | Successfully registered new account!"
                )
            else:
                logger.success(f"{self.wallet.address} | Successfully logged in!")

            headers = {
                "accept": "*/*",
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "referer": "https://puzzlemania.0g.ai/",
                "x-apollo-operation-name": "UserLogin",
            }

            json_data = {
                "operationName": "UserLogin",
                "variables": {
                    "data": {
                        "externalAuthToken": self.login_tokens["bearer_token"],
                    },
                },
                "query": "mutation UserLogin($data: UserLoginInput!) {\n  userLogin(data: $data)\n}",
            }

            response = await self.session.post(
                "https://api.deform.cc/", headers=headers, json=json_data
            )

            if response.status_code != 200:
                raise Exception(f"failed to UserLogin: {response.text}")

            self.login_tokens["userLogin"] = response.json()["data"]["userLogin"]

            if data["user"]["has_accepted_terms"]:
                logger.success(f"{self.wallet.address} | Terms already accepted!")
                return True
            else:
                result = await self._accept_terms()
                if result:
                    return True
                else:
                    logger.error(f"{self.wallet.address} | Failed to accept terms!")
                    return False

        except Exception as e:
            random_pause = random.randint(
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(
                f"{self.account_index} | Puzzlemania login error: {e}. Sleeping {random_pause} seconds..."
            )
            await asyncio.sleep(random_pause)
            raise

    async def process(self):
        success = True

        if not await self.login():
            return False

        if not await self.__is_twitter_connected():
            if not await self._connect_twitter():
                logger.error(
                    f"{self.wallet.address} | Unable to connect twitter. Account may be blocked etc."
                )
                return False

        tasks = await self.__get_tasks(tasks_only=True)
        if not tasks:
            return False

        for task in tasks:
            if task["title"] in [
                "Use a friend's referral code",
                "Refer a friend",
            ]:
                continue

            records = task["records"]
            if records and len(records) > 0:
                last_record = records[len(records) - 1]

                if last_record["status"] == "COMPLETED":
                    logger.success(
                        f'{self.wallet.address} | Task "{task["title"]}" already completed!'
                    )
                    continue

            status = await self.__do_task(task)
            if not status:
                success = False

            pause = random.randint(
                self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
            )
            logger.info(
                f"{self.wallet.address} | Sleeping for {pause} seconds between actions..."
            )
            await asyncio.sleep(pause)

        
        if self.config.PUZZLEMANIA.COLLECT_REFERRAL_CODE:
            await self.__collect_referral_code()
            
        return success

    @retry_async(default_value=False)
    async def __get_tasks(self, tasks_only: bool = False):
        try:
            headers = {
                "authorization": f"Bearer {self.login_tokens['userLogin']}",
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "referer": "https://puzzlemania.0g.ai/",
                "x-apollo-operation-name": "Campaign",
            }

            response = await self.session.post(
                "https://api.deform.cc/", headers=headers, json=constants.ALL_TASKS_INFO
            )

            if response.status_code != 200:
                raise Exception(f"failed to get tasks: {response.text}")

            data = response.json()
            if tasks_only:
                return data["data"]["campaign"]["activities"]
            else:
                return data

        except Exception as err:
            logger.error(f"{self.wallet.address} | Error puzzlemania tasks: {err}")
            raise err

    @retry_async(default_value=False)
    async def _connect_twitter(self):
        try:
            state_code = "".join(
                random.choice(string.ascii_letters + string.digits + "-_")
                for _ in range(43)
            )
            characters = (
                "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_~."
            )
            code_verifier = "".join(secrets.choice(characters) for _ in range(43))

            input_bytes = code_verifier.encode("utf-8")
            sha256_hash = hashlib.sha256(input_bytes).digest()
            code_challenge = base64.b64encode(sha256_hash).decode("utf-8")

            code_challenge = (
                code_challenge.replace("+", "-").replace("/", "_").replace("=", "")
            )

            headers = {
                # "cookie": cookies_headers,
                "accept": "application/json",
                "authorization": f'Bearer {self.login_tokens["bearer_token"]}',
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "privy-app-id": "clphlvsh3034xjw0fvs59mrdc",
                "referer": "https://puzzlemania.0g.ai/",
            }

            json_data = {
                "provider": "twitter",
                "redirect_to": "https://puzzlemania.0g.ai/",
                "code_challenge": code_challenge,
                "state_code": state_code,
            }

            response = await self.session.post(
                "https://auth.privy.io/api/v1/oauth/init",
                headers=headers,
                json=json_data,
            )

            # ++++++++++ #

            url = response.json()["url"]
            twitter_client = await create_twitter_client(self.proxy, self.twitter_token)

            headers = {
                "accept": "*/*",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en",
            }

            params = {
                "client_id": "QzU1Y3VrM0xUaHdROWNJeGRZbkE6MTpjaQ",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "redirect_uri": "https://auth.privy.io/api/v1/oauth/callback",
                "response_type": "code",
                "scope": "users.read tweet.read offline.access",
                "state": state_code,
            }

            response = await twitter_client.get(
                "https://x.com/i/api/2/oauth2/authorize",
                params=params,
                headers=headers,
            )

            if "Could not authenticate you" in response.text:
                raise Exception(
                    "twitter token is invalid. Please check your twitter token!"
                )

            auth_code = response.json()["auth_code"]

            ct0 = twitter_client.headers.get("x-csrf-token")

            twitter_client.cookies.clear()
            twitter_client.cookies.update(
                {
                    "auth_token": self.twitter_token,
                    "ct0": ct0,
                }
            )

            headers = {
                "x-twitter-auth-type": "OAuth2Session",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "content-type": "application/x-www-form-urlencoded",
            }

            data = {
                "approval": "true",
                "code": auth_code,
            }

            response = await twitter_client.post(
                "https://x.com/i/api/2/oauth2/authorize", headers=headers, data=data
            )
            url = response.json()["redirect_uri"]

            # ++++++++++ #

            headers = {
                "referer": "https://x.com/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            }

            params = {
                "state": state_code,
                "code": auth_code,
            }

            response = await twitter_client.get(
                "https://auth.privy.io/api/v1/oauth/callback",
                params=params,
                headers=headers,
            )

            url_data = unquote(str(response.url))

            privy_oauth_state = url_data.split("privy_oauth_state=")[1].split("&")[0]
            privy_oauth_code = url_data.split("privy_oauth_code=")[1].strip()

            headers = {
                "sec-ch-ua-platform": '"Windows"',
                "authorization": f'Bearer {self.login_tokens["bearer_token"]}',
                "privy-client": "react-auth:2.4.1",
                "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                "sec-ch-ua-mobile": "?0",
                "privy-app-id": "clphlvsh3034xjw0fvs59mrdc",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "accept": "application/json",
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "sec-fetch-storage-access": "active",
                "referer": "https://puzzlemania.0g.ai/",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "priority": "u=1, i",
            }

            json_data = {
                "authorization_code": privy_oauth_code,
                "state_code": privy_oauth_state,
                "code_verifier": code_verifier,
            }

            response = await self.session.post(
                "https://auth.privy.io/api/v1/oauth/link",
                headers=headers,
                json=json_data,
            )

            if response.status_code == 429:
                logger.error(
                    f"{self.account_index} | Rate limit exceeded... Please try again later!"
                )
                return False

            if response.status_code != 200:
                raise Exception(f"link request failed: {response.text}")
            else:
                data = response.json()
                for account in data["linked_accounts"]:
                    if account["type"] == "twitter_oauth":
                        logger.success(
                            f"{self.wallet.address} | Twitter account @{account['username']} connected!"
                        )
                        return True
                logger.error(
                    f"{self.wallet.address} | No twitter account found in the response!"
                )
                return False

        except Exception as e:
            random_pause = random.randint(
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(
                f"{self.account_index} | Puzzlemania connect twitter error: {e}. Sleeping {random_pause} seconds..."
            )
            await asyncio.sleep(random_pause)
            raise

    async def get_signature(self, message: str, private_key: str):
        encoded_msg = encode_defunct(text=message)
        signed_msg = self.web3.web3.eth.account.sign_message(
            encoded_msg, private_key=private_key
        )
        signature = signed_msg.signature.hex()

        return signature

    @retry_async(default_value=None)
    async def _get_nonce(self):
        try:
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "privy-app-id": "clphlvsh3034xjw0fvs59mrdc",
                "privy-client": "react-auth:2.4.1",
                "referer": "https://puzzlemania.0g.ai/",
            }

            json_data = {
                "address": self.wallet.address,
            }

            response = await self.session.post(
                "https://auth.privy.io/api/v1/siwe/init",
                headers=headers,
                json=json_data,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to get nonce: {response.status_code} | {response.text}"
                )

            return response.json()["nonce"]

        except Exception as e:
            random_pause = random.randint(
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(
                f"{self.account_index} | Puzzlemania get nonce error: {e}. Sleeping {random_pause} seconds..."
            )
            await asyncio.sleep(random_pause)
            raise

    @retry_async(default_value=None)
    async def __is_twitter_connected(self) -> bool:
        try:
            response = await self.session.post(
                "https://auth.privy.io/api/v1/sessions",
                headers={
                    "authorization": f"Bearer {self.login_tokens['bearer_token']}",
                    "origin": "https://puzzlemania.0g.ai",
                    "privy-app-id": "clphlvsh3034xjw0fvs59mrdc",
                    "referer": "https://puzzlemania.0g.ai/",
                },
                json={"refresh_token": self.login_tokens["refresh_token"]},
            )
            if response.status_code != 200:
                raise Exception(f"{response.text}")

            for item in response.json()["user"]["linked_accounts"]:
                if item["type"] == "twitter_oauth":
                    logger.success(
                        f"{self.wallet.address} | Twitter account @{item['username']} already connected!"
                    )
                    return True

            return False

        except Exception as err:
            logger.error(
                f"{self.wallet.address} | Failed to get connected twitter info: {err}"
            )
            raise err

    @retry_async(default_value=None)
    async def __do_task(self, task: dict):
        try:
            task_name = task["title"]

            logger.info(f'{self.wallet.address} | Trying to do task "{task_name}"...')

            match task_name:
                case "Campaign Registration":
                    if self.config.PUZZLEMANIA.USE_REFERRAL_CODE:
                        # Find and get referral code
                        async with self.config.lock:
                            with open(
                                "data/referral_codes.txt", "r", encoding="utf-8"
                            ) as f:
                                referral_lines = f.readlines()

                            # Get random number of required invites from config
                            required_invites = random.randint(
                                self.config.PUZZLEMANIA.INVITES_PER_REFERRAL_CODE[0],
                                self.config.PUZZLEMANIA.INVITES_PER_REFERRAL_CODE[1],
                            )

                            # Find first referral code with less than required invites
                            found_code = None
                            updated_lines = []

                            for line in referral_lines:
                                address, ref_code, invites = line.strip().split(":")
                                invites = int(invites)

                                if not found_code and invites < required_invites:
                                    found_code = ref_code
                                    # We'll increment the counter only after successful registration

                                updated_lines.append(
                                    f"{address}:{ref_code}:{invites}\n"
                                )

                            if found_code:
                                body = constants.get_verify_activity_json(found_code)
                                logger.info(
                                    f"{self.wallet.address} | Using referral code: {found_code}"
                                )

                            else:
                                body = constants.get_verify_activity_json()
                    else:
                        body = constants.get_verify_activity_json()

                case "Follow Michael Heinrich - CEO, 0G Labs":
                    body = constants.FOLLOW_MICHAEL_HEINRICH_CEO_0G_LABS

                case "Follow Ming Wu - CTO, 0G Labs":
                    body = constants.FOLLOW_MING_WU_CEO_0G_LABS

                case "Follow 0G Foundation":
                    body = constants.FOLLOW_0G_FOUNDATION

                case "Follow 0G Labs":
                    body = constants.FOLLOW_0G_LABS

                case "Follow One Gravity - the first NFT collection on 0G":
                    body = constants.FOLLOW_ONE_GRAVITY_THE_FIRST_NFT_COLLECTION_ON_0G

                case "Follow AI Verse - coming soon.":
                    body = constants.FOLLOW_AI_VERSE_COMING_SOON

                case "Follow Battle of Agents - coming soon.":
                    body = constants.FOLLOW_BATTLE_OF_AGENTS_COMING_SOON

                case "Daily check-in":
                    body = constants.DAILY_CHECK_IN

                case "Like: Hype up Guild on 0G projects!":
                    body = constants.LIKE_HYPE_UP_GUILD_ON_0G_PROJECTS

                case "RT: Hype up Guild on 0G projects!":
                    body = constants.RT_HYPE_UP_GUILD_ON_0G_PROJECTS

                case "Like: Support One Gravity":
                    body = constants.LIKE_SUPPORT_ONE_GRAVITY

                case "RT: Support One Gravity":
                    body = constants.RT_SUPPORT_ONE_GRAVITY

                case "Like: You Need Decentralized AI":
                    body = constants.LIKE_YOU_NEED_DECENTRALIZED_AI
                
                case "RT: You Need Decentralized AI":
                    body = constants.RT_YOU_NEED_DECENTRALIZED_AI

                case "Like: Battle of Agents is coming soon.":
                    body = constants.LIKE_BATTLE_OF_AGENTS_IS_COMING_SOON

                case "RT: Battle of Agents is coming soon.":
                    body = constants.RT_BATTLE_OF_AGENTS_IS_COMING_SOON

                case "Like: Guild on 0G with Michael!":
                    body = constants.LIKE_GUILD_ON_0G_WITH_MICHAEL

                case "RT: Guild on 0G with Michael!":
                    body = constants.RT_GUILD_ON_0G_WITH_MICHAEL

                case "Like: Learn from Ming":
                    body = constants.LIKE_LEARN_FROM_MING

                case "RT: Learn from Ming":
                    body = constants.RT_LEARN_FROM_MING
                    
                case _:
                    logger.warning(f"{self.wallet.address} | Unknown task: {task_name}")
                    return True

            headers = {
                "accept": "*/*",
                "authorization": f'Bearer {self.login_tokens["userLogin"]}',
                "content-type": "application/json",
                "origin": "https://puzzlemania.0g.ai",
                "referer": "https://puzzlemania.0g.ai/",
                "x-apollo-operation-name": "VerifyActivity",
            }

            response = await self.session.post(
                "https://api.deform.cc/", headers=headers, json=body
            )

            if "User has already completed the activity" in response.text:
                logger.success(
                    f"{self.wallet.address} | Task {task_name} already completed!"
                )
                return True

            if response.status_code != 200:
                raise Exception(f"{response.text}")
            else:
                if (
                    response.json()["data"]["verifyActivity"]["record"]["status"]
                    == "COMPLETED"
                ):
                    if task["title"] == "Campaign registration":
                        if self.config.PUZZLEMANIA.USE_REFERRAL_CODE and found_code:
                            async with self.config.lock:
                                # Re-read the file to get the latest state
                                with open(
                                    "data/referral_codes.txt", "r", encoding="utf-8"
                                ) as f:
                                    referral_lines = f.readlines()

                                updated_lines = []
                                for line in referral_lines:
                                    address, ref_code, invites = line.strip().split(":")
                                    invites = int(invites)

                                    if ref_code == found_code:
                                        invites += 1

                                    updated_lines.append(
                                        f"{address}:{ref_code}:{invites}\n"
                                    )

                                with open(
                                    "data/referral_codes.txt", "w", encoding="utf-8"
                                ) as f:
                                    f.writelines(updated_lines)

                    logger.success(
                        f"{self.wallet.address} | Task {task_name} completed!"
                    )
                    return True
                else:
                    raise Exception(f"{response.text}")

        except Exception as err:
            logger.error(
                f"{self.wallet.address} | Error do task {task['title']}: {err}"
            )
            raise err

    @retry_async(default_value=False)
    async def _accept_terms(self):
        try:
            headers = {
                "accept": "application/json",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "authorization": f'Bearer {self.login_tokens["bearer_token"]}',
                "origin": "https://puzzlemania.0g.ai",
                "priority": "u=1, i",
                "privy-app-id": "clphlvsh3034xjw0fvs59mrdc",
                "privy-client": "react-auth:2.4.1",
                "referer": "https://puzzlemania.0g.ai/",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "sec-fetch-storage-access": "active",
            }

            json_data = {}

            response = await self.session.post(
                "https://auth.privy.io/api/v1/users/me/accept_terms",
                headers=headers,
                json=json_data,
            )

            if response.status_code == 200 and response.json()["has_accepted_terms"]:
                logger.success(f"{self.wallet.address} | Terms accepted!")
                return True
            else:
                raise Exception(f"{response.text}")

        except Exception as err:
            logger.error(f"{self.wallet.address} | Error accept terms: {err}")
            raise err

    async def __collect_referral_code(self):
        try:
            referral_code = await self.__get_user_info(collect_referral_code=True)
            if not referral_code:
                logger.error(f"{self.wallet.address} | No referral code found")
                return

            async with self.config.lock:
                # First check if the code already exists
                try:
                    with open("data/referral_codes.txt", "r", encoding="utf-8") as f:
                        existing_codes = f.readlines()
                        for line in existing_codes:
                            if referral_code in line:
                                logger.info(
                                    f"{self.wallet.address} | Referral code {referral_code} already exists in file"
                                )
                                return
                except FileNotFoundError:
                    # If file doesn't exist, we'll create it
                    pass

                # If code doesn't exist, write it
                with open("data/referral_codes.txt", "a", encoding="utf-8") as f:
                    f.write(f"{self.wallet.address}:{referral_code}:0\n")
                    logger.success(
                        f"{self.wallet.address} | New referral code {referral_code} added to file"
                    )

        except Exception as err:
            logger.error(f"{self.wallet.address} | Error collect referral code: {err}")
            raise err

    @retry_async(default_value=False)
    async def __get_user_info(self, collect_referral_code: bool = False):
        try:
            response = await self.session.post(
                "https://api.deform.cc/",
                headers={
                    "x-apollo-operation-name": "UserMe",
                    "authorization": f"Bearer {self.login_tokens['userLogin']}",
                },
                json=constants.USER_INFO,
            )
            if response.status_code != 200:
                raise Exception(f"{response.text}")

            if response.json().get("data"):
                total_points = response.json()["data"]["userMe"]["campaignSpot"][
                    "points"
                ]
                referral_code = response.json()["data"]["userMe"]["campaignSpot"][
                    "referralCode"
                ]

                logger.info(
                    f"{self.wallet.address} | Total points: {total_points} | Referral code: {referral_code}"
                )

                if collect_referral_code:
                    return referral_code
                else:
                    return response.json()

            else:
                raise Exception(f"{response.text}")

        except Exception as err:
            logger.error(f"{self.wallet.address} | Error get user info: {err}")
            raise err
