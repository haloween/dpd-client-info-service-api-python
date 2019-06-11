from setuptools import setup

setup(name='dpd_info_client_api',
      version='0.2',
      description='Client for DPD WSDL API.',
      url='https://github.com/haloween/dpd-client-info-service-api-python',
      keywords = "dpd, courier, api, service, info , parcel, shipping label, wsdl, api",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Framework :: Django :: 1.9',
          'Framework :: Django :: 2.0',
          'Framework :: Django :: 2.1',
          'Framework :: Django :: 2.2',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      author='Tomasz Utracki-Janeta',
      author_email='halgravity+githubrepo@gmail.com',
      license='MIT',
      zip_safe=True,
      packages=['dpd_info_client_api'],
      include_package_data=True,
      install_requires=[
          'zeep',
          'requests'
      ]
      )