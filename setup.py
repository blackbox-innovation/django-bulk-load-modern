import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

__version__ = "2.0.0"

setuptools.setup(
    name="django-bulk-load-modern",
    version=__version__,
    author="Blackbox Innovation",
    author_email="dev@blackbox.ai",
    license="MIT",
    description="Modern fork of django-bulk-load with psycopg3 support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blackbox-innovation/django-bulk-load-modern",
    project_urls={
        "Original Project": "https://github.com/cedar-team/django-bulk-load",
        "Bug Tracker": "https://github.com/blackbox-innovation/django-bulk-load-modern/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    python_requires=">=3.12",
    install_requires=[
        "django>=2.2",
        "psycopg>=3.2.9"
    ],
    extras_require={
        'test': []
    },
)
