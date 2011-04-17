from distutils.core import setup
setup(name='sample-dht',
      version='0.1',
      description='A Simple DHT implementation that can run on N nodes',
      author='Eli Ezeugoh',
      author_email='cezeugoh@gmail.com',
      py_modules=['dhtclient','dhtnodeserver'],
      packages=[''],
      package_dir={'': ''},
      package_data={'': ['logging.conf']}
      )