try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup

setup(
        name="magicbox",
        version="0.1",
        description="A not so magical repository pattern with support for Django, SQLAlchemy (coming soon). And some pre-built middleware to make it ready out of the box.",
        long_description="A not so magical repository pattern with support for Django, SQLAlchemy (coming soon). And some pre-built middleware to make it ready out of the box.",
        author="Kirill Fuchs",
        author_email="kfuchs@fuzzproductions.com",
        license="MIT License",
        packages=[
            "magicbox",
        ],
        include_package_data=True,
        tests_require=[
            "nose",
            "coverage",
        ],
        zip_safe=False,
        test_suite="tests.runtests.start",
        classifiers=[
            "Operating System :: OS Independent",
            "Development Status :: 2 - Pre-Alpha",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ]
)
