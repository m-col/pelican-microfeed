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
