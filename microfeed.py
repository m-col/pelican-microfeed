# -*- coding: utf-8 -*-
"""
microfeed - Pelican plugin
==========================

microfeeds allows for the creation of pages that each act as a feed of content separate
to the main articles. The how and what:

 - Write articles under a category that will be used to make a microfeed.
 - Create the config setting MICROFEEDS as a list of these categories.
 - Articles in these categories are extracted early in generation so they are excluded
   from any article lists used in templates.
 - A *microfeed* object is exposed to page templates via which articles can be accessed
   as microfeed.*category* or microfeed[*category*] (these are equivalent).
 - Each microfeed will also generate an ATOM/RSS feed as usual if you have set
   CATEGORY_FEED_ATOM or CATEGORY_FEED_RSS.

"""


from functools import partial

from pelican import signals


class Microfeed:
    categories = ()
    articles = {}

    def setup_dict(self):
        """
        Sets microfeed.articles to contain a key for each category, each holding an
        empty list.
        """
        for cat in self.categories:
            self.articles[cat] = []

microfeed = Microfeed()


def get_categories(pelican):
    """
    Collect the list of categories that the user wants to turn into microfeeds.
    """
    categories = pelican.settings.get('MICROFEEDS', None)
    if categories and type(categories) in (list, set, tuple):
        microfeed.categories = categories
        microfeed.setup_dict()

def collect_microfeed_articles(article_generator):
    """
    Collect the microfeed articles from the article generator and move them to the
    microfeed object for later use.
    """
    if microfeed.categories:
        microfeed.setup_dict()
        normal_articles = []
        for article in article_generator.articles:
            if article.category in microfeed.categories:
                microfeed.articles[article.category].append(article)
            else:
                normal_articles.append(article)
        article_generator.articles = normal_articles

def add_microfeed_to_context(page_generator):
    """
    Expose the microfeed object to the page generator's context for use in page
    templates'
    """
    for cat in microfeed.categories:
        setattr(microfeed, cat, microfeed.articles[cat])
    page_generator.context['microfeed'] = microfeed

def gen_microfeed_feed(article_generator, writer):
    """
    Optionally generate an ATOM/RSS feed for each microfeed.
    """
    for cat_name in microfeed.categories:
        cat = microfeed.articles[cat_name][0].category

        if article_generator.settings.get('CATEGORY_FEED_ATOM'):
            writer.write_feed(
                microfeed.articles[cat.name],
                article_generator.context,
                article_generator.settings['CATEGORY_FEED_ATOM'].format(slug=cat.slug),
                article_generator.settings.get(
                    'CATEGORY_FEED_ATOM_URL',
                    article_generator.settings['CATEGORY_FEED_ATOM']
                ).format(slug=cat.slug),
                feed_title=cat.name
            )

        if article_generator.settings.get('CATEGORY_FEED_RSS'):
            writer.write_feed(
                microfeed.articles[cat.name],
                article_generator.context,
                article_generator.settings['CATEGORY_FEED_RSS'].format(slug=cat.slug),
                article_generator.settings.get(
                    'CATEGORY_FEED_RSS_URL',
                    article_generator.settings['CATEGORY_FEED_RSS']
                ).format(slug=cat.slug),
                feed_title=cat.name,
                feed_type='rss'
            )
    if article_generator.settings.get('GENERATE_MICROFEED_POSTS', False):
        write = partial(
            writer.write_file,
            relative_urls=article_generator.settings['RELATIVE_URLS'],
        )
        for cat_name in microfeed.categories:
            article_generator.articles = microfeed.articles[cat_name]
            article_generator.generate_articles(write)

def register():
    signals.initialized.connect(get_categories)
    signals.article_generator_pretaxonomy.connect(collect_microfeed_articles)
    signals.page_generator_finalized.connect(add_microfeed_to_context)
    signals.article_writer_finalized.connect(gen_microfeed_feed)
