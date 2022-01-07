
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eego2lsl", # Replace with your own username
    version="0.1.0",
    author="Johan Medrano",
    author_email="johan.medrano@umontpellier.fr",
    description="A driver to connect the EEGO devices to the LabStreamingLayer.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    
    entry_points = {
        'console_scripts': [
            'eego2lsl=eego2lsl.eego2lsl:main'
        ]
    }, 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pylsl'
    ],
    python_requires='>=2.7',
)
