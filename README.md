# dpd-client-info-service-api-python
Python API Client Library for DPD Info and Client service in Poland.  It allows parcel / shipping label generation and parcel tracking.


### Installation
```
pip install  dpd_info_client_api
```

### Setup and usage with Django

Define following variables in your project settings:

For e-nadawca:
* DPD_API_USERNAME
* DPD_API_PASSWORD
* DPD_API_FID

* DPD_API_SANDBOX_USERNAME
* DPD_API_SANDBOX_PASSWORD
* DPD_API_SANDBOX_FID


After that - use as follows:

```
from dpd_info_client_api.api import DPDAPI

DPD_ApiInstance = DPDAPI()
```

### Setup and usage rest of the world :)

```
from dpd_info_client_api.api import DPDAPI
from dpd_info_client_api.settings import DPDSettingsObject


DPDApiSettings = DPDSettingsObject()
DPDApiSettings.DPD_API_USERNAME = 'foo'
DPDApiSettings.DPD_API_PASSWORD = 'bar'
DPDApiSettings.DPD_API_FID = '1234'

DPDApiSettings.DPD_API_SANDBOX_USERNAME = 'foo'
DPDApiSettings.DPD_API_SANDBOX_PASSWORD = 'bar'
DPDApiSettings.DPD_API_SANDBOX_FID = '4321'

DPD_ApiInstance = DPDAPI(settings=DPDApiSettings) #we're not executing default init

```
That should be working at this moment.


### What's going on around here ?
Generally DPD API is preety complicated in compatision do various other API's so i've done most of the gorund work for you.
Two most often used methods are prewrapped and ready to go.
- generateSingleParcelShipment
- generateSpedLabels

### Dude - i need something to paste ...
```

```

## Where is the factory and service ?!

If you insist they're avaliable as .service and .factory on instances.

BUT

Factory is exposed directly as dictionary on the API instance. It's avaliable after execution of init_zeep.

```
DPD_ApiInstance['sessionDSPV1']
DPD_ApiInstance['packageOpenUMLFeV3']
DPD_ApiInstance['serviceSelfColOpenUMLFeV1']
```

I get an error like XXXX takes exactly 1 argument (0 given). Simple types expect only a single value argument

```
DPD_ApiInstance.get_from_factory('sessionTypeDSPEnumV1')(propertyValue)
```

Service methods are also avaliable DIRECTLY on instance. They're rewired after execution of init_zeep.
WARNING ! Example below does not work it only shows few simple calls.

```
DPD_ApiInstance.findPostalCode("00-999")
```

### I want testing Enviroment ...

Class init uses following key arguments:
DPDAPI(useTest=False, useLabs=False, initZeep=True)

* useTest (default -> False) - run the calls against sandbox credentials and WSDL
* initZeep (default -> True) - initialize zeep on init.


### I need to debug zeep ...
```
DPD_ApiInstance.enable_zeep_debug()
```

## Few examples of init: 

#### If you need the test enviroment:
```
DPD_ApiInstance = DPDAPI(useTest=True)
```
