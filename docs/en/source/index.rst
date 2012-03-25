===================================
django-newauth Documentation
===================================

django-newauth (newauth for short) is a Django application developed at
`BeProud Inc. <http://www.beproud.jp/>`_ that implements authentication the
right way. With newauth you can make user models that look like this:

.. code-block:: python

    from django.db import models

    from newauth.api import UserBase

    class User(UserBase):
        full_name = models.CharField(u"Full Name", max_length=255)
        email = models.EmailField('Email Address')
        profile = models.TextField('Profile Bio', blank=True, null=True)
        avatar = models.ImageField('Avatar', upload_to='profileimg/', blank=True, null=True)

        def get_display_name(self):
            return self.full_name

        class Meta:
            db_table = 'my_user_table'
            verbose_name = u"Djangonaut"
            verbose_name_plural = u"Djangonaut"

Table of contents:

.. toctree::
  :maxdepth: 1

  overview
  install

.. toctree::
  :maxdepth: 2

  tutorial/index

.. toctree::
  :maxdepth: 1

  backends
  forms
  third_party
  reference/index
  settings

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

