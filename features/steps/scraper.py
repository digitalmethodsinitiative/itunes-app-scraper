from behave import *
from itunes_app_scraper.scraper import AppStoreScraper

@given('we have itunes scraper installed')
def step_impl(context):
    context.scraper = AppStoreScraper()

@when('we search for "{search_term}"')
def step_impl(context, search_term):
    context.results = context.scraper.get_app_ids_for_query(search_term, country="gb", lang="en")

@then('the scraper will return "{text}" results')
def step_impl(context, text):
    assert len(context.results) == int(text)

@then('the results length is "{json_len}"')
def step_impl(context, json_len):
    print(context.results)
    assert len(context.results) == int(json_len)

@when('we search for result from mindful')
def step_impl(context):
    results = context.scraper.get_app_ids_for_query("mindful", country="gb", lang="en")
    context.results = context.scraper.get_similar_app_ids_for_app(results[0])

@when('we search for the topic topfreeapplications')
def step_impl(context):
    context.results = context.scraper.get_app_ids_for_collection(collection="topfreeapplications", category="", num=50, country="gb")

@when('we search for the developer 384434796')
def step_impl(context):
    context.results = context.scraper.get_app_ids_for_developer("384434796", country="gb")

@when('we search for the app with id "{app_id}"')
def step_impl(context, app_id):
    context.results = context.scraper.get_app_details(app_id, country="gb")

@when(u'we search for "{num_apps}" apps')
def step_impl(context, num_apps):
    apps = context.scraper.get_app_ids_for_query("mindful", country="gb", lang="en", num=num_apps)
    context.results = list(context.scraper.get_multiple_app_details(apps, country="gb"))

@when(u'we search for another "{num_apps}" apps')
def step_impl(context, num_apps):
    apps = context.app_id + context.scraper.get_app_ids_for_query("mindful", country="gb", lang="en", num=num_apps)
    context.results = list(context.scraper.get_multiple_app_details(apps, country="gb"))

@when(u'we define an incorrect app id "{app_id}"')
def step_impl(context, app_id):
    context.app_id = [int(app_id)]
