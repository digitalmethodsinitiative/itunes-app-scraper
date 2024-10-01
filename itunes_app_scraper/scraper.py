"""
iTunes App Store Scraper
"""
import requests
import json
import time
import re
import os
from datetime import datetime

from urllib.parse import quote_plus
from itunes_app_scraper.util import AppStoreException, AppStoreCollections, AppStoreCategories, AppStoreMarkets, COUNTRIES

class Regex:
	STARS = re.compile(r"<span class=\"total\">[\s\S]*?</span>")


class AppStoreScraper:
	"""
	iTunes App Store scraper

	This class implements methods to retrieve information about iTunes App
	Store apps in various ways. The methods are fairly straightforward. Much
	has been adapted from the javascript-based app-store-scraper package, which
	can be found at https://github.com/facundoolano/app-store-scraper.
	"""

	def get_app_ids_for_query(self, term, num=50, page=1, country="nl", lang="nl", timeout=None):
		"""
		Retrieve suggested app IDs for search query

		:param str term:  Search query
		:param int num:  Amount of items to return per page, default 50
		:param int page:  Amount of pages to return
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'
		:param int timeout: Seconds to wait for response before stopping.

		:return list:  List of App IDs returned for search query
		"""
		if term is None or term == "":
			raise AppStoreException("No term was given")

		url = "https://search.itunes.apple.com/WebObjects/MZStore.woa/wa/search?clientApplication=Software&media=software&term="
		url += quote_plus(term)
        
        if num is None or page is None:
            amount = None
        else:
		    amount = int(num) * int(page)

		country = self.get_store_id_for_country(country)
		headers = {
			"X-Apple-Store-Front": "%s,24 t:native" % country,
			"Accept-Language": lang
		}

		try:
			result = requests.get(url, headers=headers, timeout=timeout).json()
		except ConnectionError as ce:
			raise AppStoreException("Cannot connect to store: {0}".format(str(ce)))
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		if "bubbles" not in result or not result["bubbles"]:
			raise AppStoreException(f"No results found for search term {term} (country {country}, lang {lang})")

		return [app["id"] for app in result["bubbles"][0]["results"][:amount]]

	def get_app_ids_for_collection(self, collection="", category="", num=50, country="nl", lang="", timeout=None):
		"""
		Retrieve app IDs in given App Store collection

		Collections are e.g. 'top free iOS apps'.

		:param str collection:  Collection ID. One of the values in
		                        `AppStoreCollections`.
		:param int category:  Category ID. One of the values in
		                      AppStoreCategories. Can be left empty.
		:param int num:  Amount of results to return. Defaults to 50.
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang: Dummy argument for compatibility. Unused.
		:param int timeout: Seconds to wait for response before stopping.

		:return:  List of App IDs in collection.
		"""
		if not collection:
			collection = AppStoreCollections.TOP_FREE_IOS

		country = country.lower()
		params = (country, category, collection, num)
		url = "https://itunes.apple.com/WebObjects/MZStoreServices.woa/ws/charts?cc=%s&g=%s&name=%s&limit=%s" % params


		try:
			result = requests.get(url, timeout=timeout).json()
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		return result["resultIds"]

	def get_apps_for_developer(self, developer_id, country="nl", lang="", timeout=None):
		"""
		Retrieve Apps linked to given developer

		:param int developer_id:  Developer ID
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang: Dummy argument for compatibility. Unused.
		:param int timeout: Seconds to wait for response before stopping.

		:return list[dict]:  List of Apps linked to developer
		"""
		url = "https://itunes.apple.com/lookup?id=%s&country=%s&entity=software" % (developer_id, country)

		try:
			result = requests.get(url, timeout=timeout).json()
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		if "results" in result:
			return [app for app in result["results"] if app["wrapperType"] == "software"]
		else:
			# probably an invalid developer ID
			return []

	def get_app_ids_for_developer(self, developer_id, country="nl", lang="", timeout=None):
		"""
		Retrieve App IDs linked to given developer

		:param int developer_id:  Developer ID
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang: Dummy argument for compatibility. Unused.
		:param int timeout: Seconds to wait for response before stopping.

		:return list:  List of App IDs linked to developer
		"""
		apps = self.get_apps_for_developer(developer_id, country=country, lang=lang, timeout=timeout)
		if len(apps) > 0:
			app_ids =[app["trackId"] for app in apps["results"] if app["wrapperType"] == "software"] 
		else:
			return []
		return app_ids
		

	def get_similar_app_ids_for_app(self, app_id, country="nl", lang="nl", timeout=None):
		"""
		Retrieve list of App IDs of apps similar to given app

		This one is a bit special because the response is not JSON, but HTML.
		We extract a JSON blob from the HTML which contains the relevant App
		IDs.

		:param app_id:  App ID to find similar apps for
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang:  Language code to search with, default 'nl'
		:param int timeout: Seconds to wait for response before stopping.

		:return list:  List of similar app IDs
		"""
		url = "https://itunes.apple.com/us/app/app/id%s" % app_id

		country = self.get_store_id_for_country(country)
		headers = {
			"X-Apple-Store-Front": "%s,32" % country,
			"Accept-Language": lang
		}

		result = requests.get(url, headers=headers, timeout=timeout).text
		if "customersAlsoBoughtApps" not in result:
			return []

		blob = re.search(r"customersAlsoBoughtApps\":\s*(\[[^\]]+\])", result)
		if not blob:
			return []

		try:
			ids = json.loads(blob[1])
		except (json.JSONDecodeError, IndexError):
			return []

		return ids

	def get_app_details(self, app_id, country="nl", lang="", add_ratings=False, flatten=True, sleep=None, force=False, timeout=None):
		"""
		Get app details for given app ID

		:param app_id:  App ID to retrieve details for. Can be either the
		                numerical trackID or the textual BundleID.
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang: Dummy argument for compatibility. Unused.
		:param bool flatten: The App Store response may by multi-dimensional.
		                     This makes it hard to transform into e.g. a CSV,
		                     so if this parameter is True (its default) the
		                     response is flattened and any non-scalar values
		                     are removed from the response.
		:param int sleep: Seconds to sleep before request to prevent being
						  temporary blocked if there are many requests in a
						  short time. Defaults to None.
		:param bool force:  by-passes the server side caching by adding a timestamp
		                    to the request (default is False)
		:param int timeout: Seconds to wait for response before stopping.

		:return dict:  App details, as returned by the app store. The result is
		               not processed any further, unless `flatten` is True
		"""
		try:
			app_id = int(app_id)
			id_field = "id"
		except ValueError:
			id_field = "bundleId"

		if force:
			# this will by-pass the serverside caching
			import secrets
			timestamp = secrets.token_urlsafe(8)
			url = "https://itunes.apple.com/lookup?%s=%s&country=%s&entity=software&timestamp=%s" % (id_field, app_id, country, timestamp)
		else:
			url = "https://itunes.apple.com/lookup?%s=%s&country=%s&entity=software" % (id_field, app_id, country)

		try:
			if sleep is not None:
				time.sleep(sleep)
			result = requests.get(url, timeout=timeout).json()
		except Exception:
			try:
				# handle the retry here.
				# Take an extra sleep as back off and then retry the URL once.
				time.sleep(2)
				result = requests.get(url, timeout=timeout).json()
			except Exception:
				raise AppStoreException("Could not parse app store response for ID %s" % app_id)

		try:
			app = result["results"][0]
		except (KeyError, IndexError):
			raise AppStoreException("No app found with ID %s" % app_id)

		if add_ratings:
			try:
				ratings = self.get_app_ratings(app_id, countries=country)
				app['user_ratings'] = ratings
			except AppStoreException:
				# Return some details
				self._log_error(country, 'Unable to collect ratings for %s' % str(app_id))
				app['user_ratings'] = 'Error; unable to collect ratings'

		# 'flatten' app response
		# responses are at most two-dimensional (array within array), so simply
		# join any such values
		if flatten:
			for field in app:
				if isinstance(app[field], list):
					app[field] = ",".join(app[field])
				elif isinstance(app[field], dict):
					app[field] = ", ".join(["%s star: %s" % (key, value) for key,value in app[field].items()])

		return app

	def get_multiple_app_details(self, app_ids, country="nl", lang="", add_ratings=False, sleep=1, force=False):
		"""
		Get app details for a list of app IDs

		:param list app_id:  App IDs to retrieve details for
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang: Dummy argument for compatibility. Unused.
		:param int sleep: Seconds to sleep before request to prevent being
						  temporary blocked if there are many requests in a
						  short time. Defaults to 1.
		:param bool force:  by-passes the server side caching by adding a timestamp
		                    to the request (default is False)

		:return generator:  A list (via a generator) of app details
		"""
		for app_id in app_ids:
			try:
				yield self.get_app_details(app_id, country=country, lang=lang, add_ratings=add_ratings, sleep=sleep, force=force)
			except AppStoreException as ase:
				self._log_error(country, str(ase))
				continue

	def get_store_id_for_country(self, country):
		"""
		Get store ID for country code

		:param str country:  Two-letter country code
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		"""
		country = country.upper()

		if hasattr(AppStoreMarkets, country):
			return getattr(AppStoreMarkets, country)
		else:
			raise AppStoreException("Country code not found for {0}".format(country))

	def get_app_ratings(self, app_id, countries=None, sleep=1, timeout=None):
		"""
		Get app ratings for given app ID

		:param app_id:  App ID to retrieve details for. Can be either the
		                numerical trackID or the textual BundleID.
		:countries:     List of countries (lowercase, 2 letter code) or single country (e.g. 'de')
		                to generate the rating for
		                if left empty, it defaults to mostly european countries (see below)
		:param int sleep: Seconds to sleep before request to prevent being
						  temporary blocked if there are many requests in a
						  short time. Defaults to 1.
		:param int timeout: Seconds to wait for response before stopping.

		:return dict:  App ratings, as scraped from the app store.
		"""
		dataset = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
		if countries is None:
			countries = COUNTRIES
		elif isinstance(countries, str): # only a string provided
			countries = [countries]
		else:
			countries = countries

		for country in countries:
			url = "https://itunes.apple.com/%s/customer-reviews/id%s?displayable-kind=11" % (country, app_id)
			store_id = self.get_store_id_for_country(country)
			headers = { 'X-Apple-Store-Front': '%s,12 t:native' % store_id }

			try:
				if sleep is not None:
					time.sleep(sleep)
				result = requests.get(url, headers=headers, timeout=timeout).text
			except Exception:
				try:
					# handle the retry here.
					# Take an extra sleep as back off and then retry the URL once.
					time.sleep(2)
					result = requests.get(url, headers=headers, timeout=timeout).text
				except Exception:
					raise AppStoreException("Could not parse app store rating response for ID %s" % app_id)

			ratings = self._parse_rating(result)

			if ratings is not None:
				dataset[1] = dataset[1] + ratings[1]
				dataset[2] = dataset[2] + ratings[2]
				dataset[3] = dataset[3] + ratings[3]
				dataset[4] = dataset[4] + ratings[4]
				dataset[5] = dataset[5] + ratings[5]

        # debug
		#,print("-----------------------")
		#,print('%d ratings' % (dataset[1] + dataset[2] + dataset[3] + dataset[4] + dataset[5]))
		#,print(dataset)

		return dataset

	def _parse_rating(self, text):
		matches = Regex.STARS.findall(text)

		if len(matches) != 5:
			# raise AppStoreException("Cant get stars - expected 5 - but got %d" % len(matches))
			return None

		ratings = {}
		star = 5

		for match in matches:
			value = match
			value = value.replace("<span class=\"total\">", "")
			value = value.replace("</span>", "")
			ratings[star] = int(value)
			star = star - 1

		return ratings

	def _log_error(self, app_store_country, message):
		"""
		Write the error to a local file to capture the error.

		:param str app_store_country: the country for the app store
		:param str message: the error message to log
		"""
		log_dir = 'log/'
		if not os.path.isdir(log_dir):
			os.mkdir(log_dir)

		app_log = os.path.join(log_dir, "{0}_log.txt".format(app_store_country))
		errortime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
		fh = open(app_log, "a")
		fh.write("%s %s \n" % (errortime,message))
		fh.close()
