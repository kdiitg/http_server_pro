from setuptools import setup, find_packages

setup(
    name="http_server_pro",
    version="7.2",
    description="A Local HTTP Server with ngrok & QR support",
    author="Kuldeep Singh",
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
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
