from setuptools import setup

setup(
    name='PEng',
    version='1.0',
    packages=['PEng'],
    url='peng.github.io',
    license='GNU General Public License v3',
    author='Aniket Bhattacharyea',
    author_email='aniketmail669@gmail.com',
    description='PEng is a templating engine inspired by Jinja2',
    #install_requires = ['functools','regex','inspect','os','collections','copy','uuid'],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 4 - Alpha',
        'Intended Audience :: Developers',
        'License :: GNU General Public License v3'
    ],
    keywords='templating engine'
)
