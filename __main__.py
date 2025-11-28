"""
Entry point

"""

import uvicorn

from back_chat import API_IP, API_PORT, APP, LOG_CONFIG, LOGGER

if __name__ == "__main__":
    LOGGER.debug("Starting...")
    uvicorn.run(
        APP, host=API_IP, port=API_PORT, reload=False, log_config=LOG_CONFIG
    )
    LOGGER.debug("Ending.")
