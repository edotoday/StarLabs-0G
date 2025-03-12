from functools import wraps
import asyncio
from typing import TypeVar, Callable, Any, Optional
from loguru import logger

T = TypeVar("T")


# @retry_async(attempts=3, default_value=False)
# async def deploy_contract(self):
#     try:
#         # ваш код деплоя
#         return True
#     except Exception as e:
#         # ваша обработка ошибки с паузой
#         await asyncio.sleep(your_pause)
#         raise  # это вернет управление декоратору для следующей попытки
def retry_async(
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    default_value: Any = None,
):
    """
    Async retry decorator with exponential backoff.

    Args:
        attempts (int): Maximum number of retry attempts
        delay (float): Initial delay between retries in seconds
        backoff (float): Multiplier for delay after each retry
        default_value (Any): Value to return if all retries fail
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < attempts - 1:  # Don't sleep on the last attempt
                        logger.warning(
                            f"Attempt {attempt + 1}/{attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay:.1f} seconds..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {attempts} attempts failed for {func.__name__}: {str(e)}"
                        )
                        raise e  # Re-raise the last exception

            return default_value

        return wrapper

    return decorator
