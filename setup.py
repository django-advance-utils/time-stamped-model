import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="time-stamped-model",
    version="0.2.9",
    author="Tom Turner",
    description="Django app to add created and modified",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/django-advance-utils/time-stamped-model",
    include_package_data=True,
    packages=['time_stamped_model'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
