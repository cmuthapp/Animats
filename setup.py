from setuptools import setup

setup(
    name = 'altruism_in_animats',
    version = '0.1',
    description = 'Evolution of cooperation/altruism in a world requiring food preparation and sharing.',
    url = 'http://github.com/pranavtbhat/altruism_in_animats',
    author = 'Pranav Thulasiram Bhat(pranavtbhat) & Chidambaram Muthappan (cmuthapp)',
    author_email = 'pranavtbhat@gmail.com & cmuthapp@cs.ucla.edu',
    license = 'MIT',
    packages = ['altruism_in_animats'],
    install_requires = [
        'pybrain',
        'pygame'
    ],
    zip_safe = False
)
