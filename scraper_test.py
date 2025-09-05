from itunes_app_scraper.scraper import AppStoreScraper
from itunes_app_scraper.util import AppStoreException, AppStoreCollections, AppStoreCategories, AppStoreUtils

import json
import pytest
import os

def test_term_no_exception():
    scraper = AppStoreScraper()
    results = scraper.get_app_ids_for_query("mindful", country="gb", lang="en")
    assert len(results) > 0

def test_no_term_gives_exception():
    scraper = AppStoreScraper()
    with pytest.raises(AppStoreException, match = "No term was given"):
        scraper.get_app_ids_for_query("", country="gb", lang="en")

def test_no_invalid_id_gives_exception():
    scraper = AppStoreScraper()
    with pytest.raises(AppStoreException, match = "No app found with ID 872"):
        scraper.get_app_details('872')

def test_no_invalid_id_in_multiple_is_empty():
    scraper = AppStoreScraper()
    assert len(list(scraper.get_multiple_app_details(['872']))) == 0

def test_no_invalid_id_in_multiple_writes_log():
    scraper = AppStoreScraper()
    scraper.get_multiple_app_details(['872'])
    assert os.path.exists("log/nl_log.txt")
    fh = open('log/nl_log.txt')
    assert "No app found with ID 872" in fh.read()
    fh.close()

def test_log_file_write_message():
    scraper = AppStoreScraper()
    scraper._log_error("gb","test")
    assert os.path.exists("log/gb_log.txt")
    fh = open('log/gb_log.txt')
    assert "test" in fh.read()
    fh.close()

def test_country_code_does_exist():
    scraper = AppStoreScraper()
    assert scraper.get_store_id_for_country('gb') == 143444

def test_country_code_does_not_exist():
    scraper = AppStoreScraper()
    with pytest.raises(AppStoreException, match="Country code not found for XZ"):
        scraper.get_store_id_for_country('xz')

def test_query_multiple_pages():
    query = "game"
    scraper = AppStoreScraper()
    results = set()
    for page in range(1,4):
        page_results = scraper.get_app_ids_for_query(query, country="us", lang="en", page=page)
        if page_results:
            [results.add(x) for x in page_results]
            assert len(results) > (page-1)*50
    print(f"Total results for query {query}: {len(results)}")