# Alrite Django Backend

## Getting Started

To get started, clone the repository with `git clone --recurse-submodules`, the install the following dependencies:

```
pip install django
pip install django-cors-headers
pip install djangorestframework
pip install django-import-export
pip install django-crispy-forms
pip install BeautifulSoup4
pip install whitenoise
```

Or, if you've already cloned the project and did not use `--recurse-submodules`, run the following command to initialize the submodule:

```
git submodule update --init --recursive
```

## Serving Locally

Run the following command in the root directory to serve the server locally:

```
python .\manage.py runserver
```