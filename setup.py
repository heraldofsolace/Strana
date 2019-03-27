from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Strana',
    version='0.0.3',
    packages=['Strana'],
    url='https://github.com/i-abh-esc-wq/Strana',
    license='GNU General Public License v3',
    author='Aniket Bhattacharyea',
    author_email='i_abh_esc_wq@protonmail.com',
    description='Strana is a templating engine inspired by Jinja2',
    long_description=long_description,
    long_description_content_type="text/markdown",
    #install_requires = ['functools','regex','inspect','os','collections','copy','uuid'],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    keywords='templating engine'
)
