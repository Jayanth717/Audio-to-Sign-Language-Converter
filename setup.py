import setuptools

setuptools.setup(
    name="a2sl",
    version="1.0.0",
    description="Audio to Sign Language Converter using Speech Recognition and NLP",
    author="A2SL Team",
    packages=setuptools.find_packages(),
    packages=setuptools.find_packages(), setup_requires=['nltk', 'joblib','click','regex','sqlparse','setuptools'], 
)
