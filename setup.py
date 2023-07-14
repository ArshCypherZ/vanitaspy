import setuptools

with open("README.md", "r") as txt:
    long_description = txt.read()

setuptools.setup(
    name='vanitas-antispam',
    version='1.0.0',
    description='AntiSpam Wrapper for Vanitas',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='License :: OSI Approved :: MIT License',
    author='ArshCypherZ',
    author_email='weebarsh@protonmail.com',
    url='https://github.dev/ArshCypherZ/vanitaspy.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_requires= ['requests'],
    python_requires='>=3.6'
)
