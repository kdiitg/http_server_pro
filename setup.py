from setuptools import setup, find_packages
import pathlib

# Read version from __version__.py
version_ns = {}
exec((pathlib.Path("http_server_pro") / "__version__.py").read_text(), version_ns)
version = version_ns["__version__"]

# Load README.md for PyPI
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    license="MIT",
    name="http_server_pro",
    version=version,
    description="A Local HTTP File Server with ngrok & QR support",
    keywords="http server local file-sharing ngrok QR tkinter gui",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kuldeep Singh",
    url="https://github.com/kdiitg/http_server_pro",
    project_urls={
        "Documentation": "https://github.com/kdiitg/http_server_pro",
        "Source": "https://github.com/kdiitg/http_server_pro",
        "Bug Tracker": "https://github.com/kdiitg/http_server_pro/issues"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Pillow~=11.2.1",
        "qrcode~=8.2",
        "requests~=2.32.4",
    ],
    entry_points={
        'console_scripts': [
            'http_server_pro=http_server_pro.main:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
