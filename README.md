# django_http_orm

Http Interface over Django ORM

This library provides a simple HTTP interface over the Django ORM:

It proveds the following endpoints:

1.  https://your.server.com/orm/schema/module/[APP_NAME]

This returns a list of all the Django DB Models in APP_NAME

2.  https://your.server.com/orm/schema/[FULL_MODEL_NAME]

This returns schema information about FULL_MODEL_NAME

3.  https://your.server.com/orm/query/[FULL_MODEL_NAME]?email=[PARAMETER]&name=[PARAMETER]

This performs a search for FULL_MODEL_NAME filtering by "email" and "name"

4. PUT https://your.server.com/orm/query/[FULL_MODEL_NAME]/[ID] -d '{"first_name": "randi"}'

This performs an update on the Model instance with "ID" and updates "first_name" to "randi"

5. DELETE https://your.server.com/orm/query/[FULL_MODEL_NAME]/[id]

This performa s delete

6.  POST https://your.server.com/orm/query/[FULL_MODEL_NAME] - d '{"first_name" ...}'

This creates a FUKLL_MODEL_NAME with the attributes specified in the POST body.

INSTALLTION

You will need to include "django_http_orm" in your INSTALLED_APPS and also include "django_http_orm.urls" in your urls file.

