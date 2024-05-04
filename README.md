# Page analizer

### About
**Page analizer** is a web application whose purpose is to check websites for SEO compatibility and see the main info (title, main header, description) they give in response with some other info. You can try it by using the link below or deploying and running it on any hosting (check guide below).

### Deployed project link
*https://python-project-83-0fbn.onrender.com*

### Hexlet tests and linter status, CI status, CodeClimate Maintainability:
[![Actions Status](https://github.com/NMorphey/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/NMorphey/python-project-83/actions) [![CI](https://github.com/NMorphey/python-project-83/actions/workflows/CI.yml/badge.svg?event=push)](https://github.com/NMorphey/python-project-83/actions/workflows/CI.yml) [![Maintainability](https://api.codeclimate.com/v1/badges/f874dc84c273c4132ab0/maintainability)](https://codeclimate.com/github/NMorphey/python-project-83/maintainability)

### How to deploy
**Package can be installed with following command:**
>
> pip install --user git+https://github.com/NMorphey/python-project-83.git  
>
Use `make build` to configure the environment and `make start` to switch everything on.  
To run this app, you must set 2 enironment variables: `SECRET_KEY` and `DATABASE_URL`.  
🔴 **BE AWARE:** All SQL queries are written for PostgreSQL. You may need to slightly change them if you use another DB. 🔴
