from setuptools import setup
import sys
import json

with open("metadata.json") as fp:
    metadata = json.load(fp)

setup(
    name="lexibank_chaconbaniwa",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_chaconbaniwa"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "lexibank.dataset": ["chaconbaniwa=lexibank_chaconbaniwa:Dataset"]
    },
    install_requires=["pylexibank>=2.1"],
)
