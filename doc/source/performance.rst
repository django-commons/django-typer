.. include:: ./refs.rst

===========
Performance
===========

Django management command startup time can be noticeably slow, especially for large projects with
many models. We can perceive time at roughly 100 ms, bare

----------------

.. raw:: html
    :file: _static/img/minimal_profile.svg

.. raw:: html
    :file: _static/img/polls_profile.svg