============================================
Using User objects with third party apps
============================================

newauth has the concept of a "default" user model. This model can be imported
via the newauth.models module.

.. code-block:: python

    from django.db import models
    from newauth.models import User

    class ThirdPartyModel(models.Model):
        user = models.ForeignKey(User)
        #...
