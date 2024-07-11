from setuptools import find_packages, setup

setup(
    name="alpha_gomoku",
    version="0.1",
    packages=find_packages(where="alphagomoku"),
    package_dir={"": "alphagomoku"},
    install_requires=[
        'debugpy',
        'matplotlib',
        'numpy',
        'pandas',
        'seaborn',
        'torch',
        'torchvision',
        'torchaudio',
        'pytorch-lightning',
        'pytest',
        'wandb',
    ],
)
