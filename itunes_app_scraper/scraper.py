"""
iTunes App Store Scraper
"""
import requests
import json
import re

from urllib.parse import quote_plus
from itunes_app_scraper.util import AppStoreException, AppStoreCollections, AppStoreCategories, AppStoreMarkets


class AppStoreScraper:
	"""
	iTunes App Store scraper

	This class implements methods to retrieve information about iTunes App
	Store apps in various ways. The methods are fairly straightforward. Much
	has been adapted from the javascript-based app-store-scraper package, which
	can be found at https://github.com/facundoolano/app-store-scraper.
	"""

	def get_app_ids_for_query(self, term, num=50, page=1, country="nl", lang="nl"):
		"""
		Retrieve suggested app IDs for search query

		:param str term:  Search query
		:param int num:  Amount of items to return per page, default 50
		:param int page:  Amount of pages to return
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of App IDs returned for search query
		"""
		url = "https://search.itunes.apple.com/WebObjects/MZStore.woa/wa/search?clientApplication=Software&media=software&term="
		url += quote_plus(term)

		amount = int(num) * int(page)

		country = self.get_store_id_for_country(country)
		headers = {
			"X-Apple-Store-Front": "%s,24 t:native" % country,
			"Accept-Language": lang
		}

		try:
			result = requests.get(url, headers=headers).json()
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		return [app["id"] for app in result["bubbles"][0]["results"][:amount]]

	def get_app_ids_for_collection(self, collection="", category="", num=50, country="nl"):
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

		:return:  List of App IDs in collection.
		"""
		if not collection:
			collection = AppStoreCollections.TOP_FREE_IOS

		country = self.get_store_id_for_country(country)
		params = (collection, category, num, country)
		url = "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/ws/RSS/%s/%s/limit=%s/json?s=%s" % params

		try:
			result = requests.get(url).json()
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		return [entry["id"]["attributes"]["im:id"] for entry in result["feed"]["entry"]]

	def get_app_ids_for_developer(self, developer_id, country="nl"):
		"""
		Retrieve App IDs linked to given developer

		:param int developer_id:  Developer ID
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.

		:return list:  List of App IDs linked to developer
		"""
		url = "https://itunes.apple.com/lookup?id=%s&country=%s&entity=software" % (developer_id, country)

		try:
			result = requests.get(url).json()
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		if "results" in result:
			return [app["trackId"] for app in result["results"] if app["wrapperType"] == "software"]
		else:
			# probably an invalid developer ID
			return []

	def get_similar_app_ids_for_app(self, app_id, country="nl", lang="nl"):
		"""
		Retrieve list of App IDs of apps similar to given app

		This one is a bit special because the response is not JSON, but HTML.
		We extract a JSON blob from the HTML which contains the relevant App
		IDs.

		:param app_id:  App ID to find similar apps for
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of similar app IDs
		"""
		url = "https://itunes.apple.com/us/app/app/id%s" % app_id

		country = self.get_store_id_for_country(country)
		headers = {
			"X-Apple-Store-Front": "%s,32" % country,
			"Accept-Language": lang
		}

		result = requests.get(url, headers=headers).text
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

	def get_app_details(self, app_id, country="nl", flatten=True):
		"""
		Get app details for given app ID

		:param app_id:  App ID to retrieve details for. Can be either the
		                numerical trackID or the textual BundleID.
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param bool flatten: The App Store response may by multi-dimensional.
		                     This makes it hard to transform into e.g. a CSV,
		                     so if this parameter is True (its default) the
		                     response is flattened and any non-scalar values
		                     are removed from the response.

		:return dict:  App details, as returned by the app store. The result is
		               not processed any further, unless `flatten` is True
		"""
		try:
			app_id = int(app_id)
			id_field = "id"
		except ValueError:
			id_field = "bundleId"

		url = "https://itunes.apple.com/lookup?%s=%s&country=%s&entity=software" % (id_field, app_id, country)

		try:
			result = requests.get(url).json()
		except json.JSONDecodeError:
			raise AppStoreException("Could not parse app store response")

		try:
			app = result["results"][0]
		except IndexError:
			raise AppStoreException("No app found with ID %s" % app_id)

		# 'flatten' app response
		# responses are at most two-dimensional (array within array), so simply
		# join any such values
		if flatten:
			for field in app:
				if isinstance(app[field], list):
					app[field] = ",".join(app[field])

		return app

	def get_multiple_app_details(self, app_ids, country="nl"):
		"""
		Get app details for a list of app IDs

		:param list app_id:  App IDs to retrieve details for
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.

		:return generator:  A list (via a generator) of app details
		"""
		for app_id in app_ids:
			yield self.get_app_details(app_id)

	def get_store_id_for_country(self, country):
		"""
		Get store ID for country code

		:param str country:  Two-letter country code
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		"""
		default_store = 143452
		country = country.upper()
		return getattr(AppStoreMarkets, country) if hasattr(AppStoreMarkets, country) else default_store
