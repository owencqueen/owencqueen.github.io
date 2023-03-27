---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

This page is currently a work in progress. In the meantime, you can find my publications on [my Google Scholar profile](https://scholar.google.com/citations?user=ID2aN3QAAAAJ&hl=en).

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
