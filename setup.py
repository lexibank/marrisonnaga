from setuptools import setup
import json


with open("metadata.json", encoding="utf-8") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_marrisonnaga",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_marrisonnaga"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["marrisonnaga=lexibank_marrisonnaga:Dataset"]},
    install_requires=["pylexibank>=2.1", "segments>=2.0.2"],
    extras_require={"test": ["pytest-cldf"]},
)
