from setuptools import setup, find_packages
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="http_server_pro",
    version="7.2",
    description="A Local HTTP File Server with ngrok & QR support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kuldeep Singh",
    author_email="kdiitg@gmail.com",  # ← optional but good
    url="https://github.com/kdiitg/http_server_pro",  # ✅ Add this
    project_urls={  # ✅ Optional extras
        "Documentation": "https://github.com/kdiitg/http_server_pro",
        "Source": "https://github.com/kdiitg/http_server_pro",
        "Bug Tracker": "https://github.com/kdiitg/http_server_pro/issues"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Pillow",
        "qrcode",
        "requests",
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
        "Topic :: Internet :: File Transfer Protocol (FTP)",  # optional
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
