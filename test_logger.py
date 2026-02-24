from app.utils.logger import logger

def test_logging():
    logger.info("INFO: This is an info log")
    logger.warning("WARNING: This is a warning log")
    logger.error("ERROR: This is an error log")
    print("Test logs written to logs/app.log")

if __name__ == "__main__":
    test_logging()
