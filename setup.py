import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="subscribe-manager",
    version="0.0.1",
    author="modestme",
    author_email="844713856@qq.com",
    description="A subscription proxy tool that unifies subscription management, regularly downloads and stores "
                "subscription information, automatically converts subscriptions, and provides proxy services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/modestme/SubscribeManager",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.115.2,<0.116.0",
        "uvicorn>=0.31.1,<0.32.0",
        "pyyaml>=6.0.2,<7.0.0",
        "requests>=2.32.3,<3.0.0",
        "apscheduler>=3.10.4,<4.0.0",
        "pydantic-settings>=2.6.0,<3.0.0",
        "loguru>=0.7.2,<0.8.0",
        "aiohttp>=3.10.10,<4.0.0",
        "nest-asyncio>=1.6.0,<2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "sbscmgr=subscribe_manager.main:main",
        ],
    },
)
