from setuptools import find_packages, setup

setup(
    name="alphagomoku",
    version="0.1",
    packages=find_packages(where="alphagomoku"),
    package_dir={"": "alphagomoku"},
    install_requires=[
        "debugpy",
        "gymnasium",
        "matplotlib",
        "numpy",
        "pandas",
        "seaborn",
        "torch",
        "torchvision",
        "torchaudio",
        "pytorch-lightning",
        "pytest",
        "wandb",
    ],
)
