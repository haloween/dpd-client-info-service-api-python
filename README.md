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

### Setup for rest of the world :)

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

DPD_ApiInstance = DPDAPI(settings=DPDApiSettings)

```
That should be working at this moment.

### Setting the sender address.
In most use cases you will need to set shipping address. It's used in generating parcels and waybills.
You can also pass senderData to required methods if that's varying between shipments.

```
DPD_ApiInstance.setPickupAddress({
    'address': 'Street Name 1',
    'city': 'City Name',
    'company': 'Hal Zero Coders',
    'countryCode': 'PL',
    'email': 'office@mymail.com',
    'fid': '123123',
    'phone': 'Your Phone NO',
    'postalCode': '00-999'
})
```

### Address data formating
Address data should be passes as a dict like below.

```
{
    'address': [str], #Street Name and Number
    'city': [str], #City name
    'company': [str], #Company name
    'countryCode': [str], #Country code - 'PL'
    'email': [str], #Sender e-mail
    'fid': [str], #FID - that's from DPD
    'name': [str], #Person "First Name Last Name"
    'phone': [str], #Phone No
    'postalCode': [str] #Postal Code
}
```

### Parcel data formating
Parcel data should be passed as a dict like below.
NONE of those are required. You can pass an empty dict and API is OK with that ....

```
{
    'content': [str],
    'customerData1': [str],
    'customerData2': [str],
    'customerData3': [str],
    'reference': [str],
    'sizeX': [int],
    'sizeY': [int],
    'sizeZ': [int],
    'weight': [int, float, Decimal]
}
```


### How do i send something ??
Generally DPD API is preety complicated in comparision to various other API's so i've done most of the gorund work for you.
Two most often used methods are prewrapped and ready to go.

- GenerateSingleParcelShipment
- GenerateSpedLabels


```
DPD_ApiInstance = DPDAPI()
DPD_ApiInstance.setPickupAddress({
    'address': 'Street Name 1',
    'city': 'City Name',
    'company': 'Hal Zero Coders',
    'countryCode': 'PL',
    'email': 'office@mymail.com',
    'fid': '123123',
    'phone': 'Your Phone NO',
    'postalCode': '00-999'
})

sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = {'weight': 1},
    recieverData = {
        'address': 'Street Name 1',
        'city': 'City Name',
        'company': 'Hal Zero Coders',
        'countryCode': 'PL',
        'email': 'office@mymail.com',
        'fid': '123123',
        'phone': 'Your Phone NO',
        'postalCode': '00-999'
    },
    servicesData={}
)

RESPONSE
{
    'Status': 'OK', #check that one it it's OK
    'SessionId': 0000000000, #session id goes here
    'BeginTime': None,
    'EndTime': None,
    'Packages': {
        'Package': [
            {
                'Status': 'OK',
                'PackageId': 0000000000, #packageId goes here
                'Reference': None,
                'ValidationDetails': None,
                'Parcels': {
                    'Parcel': [
                        {
                            'Status': 'OK',
                            'ParcelId': 0000000, #parcelId goes here
                            'Reference': None,
                            'Waybill': 'FOO FOO FOO', #Waybill goes here
                            'ValidationDetails': None
                        }
                    ]
                }
            }
        ]
    }
}

if sendParcelQuery.Status != 'OK':
    raise AssertionError('Wrong status response', sendParcelQuery)

PACKAGE_ID = sendParcelQuery.Packages.Package[0].PackageId

waybilPdfQuery = DPD_ApiInstance.generateSpedLabels(packageId=PACKAGE_ID)

if waybilPdfQuery.statusInfo.status != 'OK':
    raise AssertionError('Wrong waybill status response', waybilPdfQuery)

waybilPdfData = waybilPdfQuery.documentData
```

### Ok, i need dome fancy added services to that !
If you need those, check out parameters of getServicesPayload. ALL of the WSDL stuff is preprogrammed there.

```
recieversData = {
    'address': 'Street Name 1',
    'city': 'City Name',
    'company': 'Hal Zero Coders',
    'countryCode': 'PL',
    'email': 'office@mymail.com',
    'fid': '123123',
    'phone': 'Your Phone NO',
    'postalCode': '00-999'
}


*COD ?*
sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = {'weight': 1},
    recieverData = recieversData,
    servicesData={'cod': 12.99, 'codCurrency': 'PLN'}
)


*declaredValue ?*
sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = {'weight': 1},
    recieverData = recieversData,
    servicesData={'declaredValue': 12.99, 'declaredValueCurrency': 'PLN'}
)

*Pallet shipment*
sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = {'weight': 120, 'sizeX': 80, 'sizeY': 120},
    recieverData = recieversData,
    servicesData={'pallet': True}
)
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
