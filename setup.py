from setuptools import setup

install_requires = []
with open('requirements.txt') as f:
    for line in f.readlines():
        req = line.strip()
        if not req or req.startswith(('-e', '#')):
            continue
        install_requires.append(req)

setup(
    name='jupyterhub-studipauthenticator',
    version='0.1.0',
    packages=['studipauthenticator'],
    url='https://github.com/dennis531/jupyterhub-studip-authenticator',
    license='MIT',
    author='debenz',
    author_email='debenz@uos.de',
    description='Stud.IP LTI Authenticator for Courses',
    install_requires=install_requires
)
