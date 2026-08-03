from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.scrapers.ashby import AshbyScraper
from app.services.scrapers.base import BaseScraper
from app.services.scrapers.greenhouse import GreenhouseScraper
from app.services.scrapers.lever import LeverScraper
from app.services.scrapers.smartrecruiters import SmartRecruitersScraper
from app.services.scrapers.workable import WorkableScraper


def build_scrapers() -> list[BaseScraper]:
    settings = get_settings()
    scrapers: list[BaseScraper] = []
    if settings.scraper_seed_greenhouse:
        scrapers.append(GreenhouseScraper(settings.scraper_seed_greenhouse))
    if settings.scraper_seed_lever:
        scrapers.append(LeverScraper(settings.scraper_seed_lever))
    if settings.scraper_seed_ashby:
        scrapers.append(AshbyScraper(settings.scraper_seed_ashby))
    if settings.scraper_seed_smartrecruiters:
        scrapers.append(SmartRecruitersScraper(settings.scraper_seed_smartrecruiters))
    if settings.scraper_seed_workable:
        scrapers.append(WorkableScraper(settings.scraper_seed_workable))
    return scrapers


def run_all_scrapers(db: Session) -> dict[str, int]:
    results = {}
    for scraper in build_scrapers():
        results[scraper.source_name] = scraper.run(db)
    return results
