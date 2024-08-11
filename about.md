---
layout: page
title: What is the Sand Atlas?
image: assets/images/pic01.jpg
nav-menu: true
---

The Sand Atlas is an effort to collate data describing the shape and morphology of a wide range of sand grains. This data can be viewed online and downloaded for free.

# Technical details
For all images, the original source data is a micro-CT scan of an assembly of particles. These particles are individually labelled by the researcher who has submitted the data to The Sand Atlas. At this stage, a quality check is performed. To generate particle information consistently, particle surface meshes and level sets are produced using [openVDB](https://www.openvdb.org/). The meshes are passed through [SHaPE](https://www.sciencedirect.com/science/article/pii/S0010465521000953) to produce the shape descriptors. The data is then uploaded to the website and made available for download.

# Steering Committee

This community effort is run by:

- [Benjy Marks](www.benjymarks.com)
- Baozhong Chen
- [Edward Andò](https://people.epfl.ch/edward.ando?lang=en)
- [Max Wiebicke](https://scholar.google.com/citations?user=h-57EAgAAAAJ)
- [Giulia Guida](https://people.utwente.nl/g.guida)
- [Erika Tudisco](https://portal.research.lu.se/en/persons/erika-tudisco)
- [Mohammad Saadatfar](https://www.sydney.edu.au/engineering/about/our-people/academic-staff/mohammad-saadatfar.html)
- [Ilija Vego](https://orcid.org/0000-0003-4426-3382)

# Developers

The website and processing pipeline is maintained by [Benjy Marks](www.benjymarks.com) and [Ilija Vego](https://orcid.org/0000-0003-4426-3382).