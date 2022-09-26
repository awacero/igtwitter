.. igtwitter documentation master file, created by
   sphinx-quickstart on Fri Sep 23 08:33:35 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

igtwitter's documentation!
=====================================
.. image:: epn.png
   :target: index.html
   :alt: alt text
   :class: banner
   :width: 600px
 
GDS service to publish seismic information using a twitter account. This code was previously a plugin of EQEVENTS, but that code was modified to be used with GDS.

GDS or the operator will decide wheter or not the tweet must be posted. There will be one tweet for the automatic (preliminar) event and another for the manual (revisado) event. If the event is older than hour_limit, there will be no publication.

Result:
------------------------------------

If the publication works as expected, this should be posted in the twitter account.

.. image:: tweet_example.png
   :target: index.html
   :alt: alt text
   :class: banner
   :width: 500px

.. raw:: html

    <div class="startpage">


Indices and Tables
------------------

.. hlist::

    * `Module Index <py-modindex.html>`_

      *Lists all modules*

    * `Index <genindex.html>`_

      *All functions, classes, terms*


.. raw:: html

    </div>


.. toctree::
   :maxdepth: 2
   :caption: Contentss:






