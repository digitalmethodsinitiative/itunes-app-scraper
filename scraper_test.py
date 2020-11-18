from itunes_app_scraper.scraper import AppStoreScraper
import pytest

def test_term_no_exception():
    scraper = AppStoreScraper()
    results = scraper.get_app_ids_for_query("mindful", country="gb", lang="en")
    assert len(results) > 0

def test_no_term_gives_exception():
    scraper = AppStoreScraper()
    with pytest.raises('AppStoreException'):
        scraper.get_app_ids_for_query("", country="gb", lang="en")