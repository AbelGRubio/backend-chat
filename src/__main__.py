import uvicorn

from back_chat import APP, LOGGER, API_PORT, API_IP, LOG_CONFIG


if __name__ == '__main__':
    LOGGER.debug("Starting...")
    uvicorn.run(
        APP,
        host=API_IP,
        port=API_PORT,
        reload=False,
        log_config=LOG_CONFIG
    )
    LOGGER.debug("Ending.")
