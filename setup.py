from setuptools import setup, find_packages

setup(
    name='ckanext-lire',
    version=__version__,
    description='CKAN extension for GUI managing of dataset relationships',
    long_description='',
    classifiers=[],
    keywords='',
    author='Petar Milic',
    author_email='milicpetar86@gmail.com',
    url='http://ckan.org/wiki/Extensions',
    license='mit',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.lire'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # requirements defined in pip-requirements.txt
    ],
    entry_points='''
    [ckan.plugins]
    lire=ckanext.lire.plugin:LIREPlugin
    ''',
)
