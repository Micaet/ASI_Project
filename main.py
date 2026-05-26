import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import settings
from app.db.session import init_db
from app.ingestion.service import ingest_iss, ingest_spacex


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # wycisz nadmiernie gadatliwe loggery
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


def main() -> None:
    setup_logging()
    logger = logging.getLogger("ingestion")

    init_db()

    scheduler = BlockingScheduler()

    # ISS -- co 30 sekund
    scheduler.add_job(
        ingest_iss,
        "interval",
        seconds=settings.iss_poll_seconds,
        id="iss_poll",
        name="ISS position poll",
        max_instances=1,
    )

    # SpaceX -- co godzinę
    scheduler.add_job(
        ingest_spacex,
        "interval",
        seconds=settings.spacex_poll_seconds,
        id="spacex_poll",
        name="SpaceX launches poll",
        max_instances=1,
    )

    # pierwszy fetch od razu po starcie, nie czekając na interwał
    scheduler.add_job(ingest_iss, id="iss_init", name="ISS initial fetch")
    scheduler.add_job(ingest_spacex, id="spacex_init", name="SpaceX initial fetch")

    # graceful shutdown na SIGTERM (docker stop)
    def shutdown(signum, frame):
        logger.info("Otrzymano sygnał %s, zamykam scheduler...", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    logger.info(
        "Scheduler uruchomiony: ISS co %ds, SpaceX co %ds",
        settings.iss_poll_seconds,
        settings.spacex_poll_seconds,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
