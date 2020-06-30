# dpd-client-info-service-api-python
Python API Client Library for DPD Info and Client service in Poland.
It allows parcel / shipping label generation.
It's mandatory to contact your DPD representative and ask them to enable API access.

## Installation

```bash
pip install  dpd_info_client_api
```

## Setup and usage with Django

Define following variables in your project settings:

* DPD_API_USERNAME
* DPD_API_PASSWORD
* DPD_API_FID

* DPD_API_SANDBOX_USERNAME
* DPD_API_SANDBOX_PASSWORD
* DPD_API_SANDBOX_FID

After that - use as follows:

```python
from dpd_info_client_api.api import DPDAPI

DPD_ApiInstance = DPDAPI()
```

## Setup for rest of the world :)

```python
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

### I get INCORRECT_LOGIN_OR_PASSWORD

Contact your DPD representative and ask them to enable API access.

## Setting the sender address

In most use cases you will need to set shipping address. It's used in generating parcels and waybills.
You can also pass senderData to required methods if that's varying between shipments.

```python
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

## Address data formating

All addresses should be passed as a dict like below {attributeName: [type(value)]}.

```python
ADDRESS_DATA = {
    'address': 'Street Name',
    'city': 'City Name',
    'company': 'Company Name',
    'countryCode': 'PL',
    'email': 'shoe size',
    'fid': 'FID',
    'phone': 'Phone',
    'postalCode': 'zip code'
}
```

Provided dict is validated against:

```python
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

## Parcel data formating

Parcel data should be passed as a dictionary {}.
NONE of those are required. You can pass an empty dict and API is OK with that ...
It's recommended to provide AT LEAST WEIGHT:

Full blown example below:

```python
PACKAGE_DATA = {
    'content': 'Nuclear Reactor',
    'customerData1': 'VVER V-320',
    'customerData2': 'Working Condition',
    'customerData3': 'No control Rods',
    'reference': 'My reference 123',
    'sizeX': 2000,
    'sizeY': 3000,
    'sizeZ': 5000,
    'weight': 3500
}
```

That will also work...

```python
PACKAGE_DATA = {
    'weight': 3500
}
```

Provided dict is validated against:

```python
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

### How do i send something

Generally DPD API is preety complicated in comparision to various other API's so i've done most of the ground work for you.
Two most often used methods are prewrapped and ready to go.

* GenerateSingleParcelShipment
* GenerateSpedLabel

```python

SENDER_DATA = {
    'address': 'Street Name 1',
    'city': 'City Name',
    'company': 'Hal Zero Coders',
    'countryCode': 'PL',
    'email': 'office@mymail.com',
    'fid': '123123',
    'phone': 'Your Phone NO',
    'postalCode': '00-999'
}

PACKAGE_DATA = {'weight': 1}

RECIPIENT_DATA = {
    'address': 'Street Name 1',
    'city': 'City Name',
    'company': 'Hal Zero Coders',
    'countryCode': 'PL',
    'email': 'office@mymail.com',
    'phone': 'Your Phone NO',
    'postalCode': '00-999'
}

DPD_ApiInstance = DPDAPI()
DPD_ApiInstance.setPickupAddress(SENDER_DATA)

sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = PACKAGE_DATA,
    recieverData = RECIPIENT_DATA,
    servicesData = {}
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

assert sendParcelQuery.Status == 'OK', 'Wrong status response' % sendParcelQuery

PACKAGE_ID = sendParcelQuery.Packages.Package[0].PackageId

waybilPdfQuery = DPD_ApiInstance.generateSpedLabel(packageId=PACKAGE_ID)

assert waybilPdfQuery.statusInfo.status == 'OK', Wrong waybill status response: %s' % waybilPdfQuery

waybilPdfData = waybilPdfQuery.documentData
```

### Ok, i need dome fancy added services to that

If you need those, you can check out getServicesPayload. ALL of the WSDL stuff is preprogrammed there.
Check out all the service options below.

```python
getServicesPayload(self,
    carryIn = False, #carry in service - left for reference
    cod = False, codCurrency='PLN', #Cash On Delivery - specify amount
    cud = False, #Collect upon Delivery
    declaredValue = None, declaredValueCurrency='PLN', #Declared Parcel Value 
    dedicatedDelivery = False, #dedicated delivery service
    documentsInternational = False, #international documents
    dox = False, #documents shipping service (envelope up to 0.5 kg)
    dpdExpress = False,  #international air freight
    dpdPickup = False, #delivery to pickup point
    duty = None, dutyCurrency = 'PLN', #DUTY
    guarantee = False, guaranteeValue = None, #guarantee of timed delivery TIME0930, TIME1200, B2C, TIMEFIXED, SATURDAY, INTER, DPDNEXTDAY
    inPers = False, #Pickup validation - required ID
    pallet = False, #Pallet Shipment
    privPers = False, #Delivery to Private Person
    rod = False, #Return on delivery - documents ?
    selfCol = False, #Self collect in depot
    tires = False, #tires
    tiresExport = False #export tires
)
```

### Example parcel with Cash on Delivery

```python
sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = PACKAGE_DATA,
    recieverData = RECIPIENT_DATA,
    servicesData = {'cod': 12.99, 'codCurrency': 'PLN'}
)
```

### Example parcel with Declared Value

```python
sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = PACKAGE_DATA,
    recieverData = RECIPIENT_DATA,
    servicesData = {'declaredValue': 12.99, 'declaredValueCurrency': 'PLN'}
)
```

### Example pallet shipment

```python
sendParcelQuery = DPD_ApiInstance.GenerateSingleParcelShipment(
    packageData = {'weight': 120, 'sizeX': 80, 'sizeY': 120},
    recieverData = recieversData,
    servicesData = {'pallet': True}
)
```

## Where is the factory and service

If you insist they're avaliable as .service and .factory on instances.

BUT

Factory is exposed directly as dictionary on the API instance. It's avaliable after execution of init_zeep.

```python
DPD_ApiInstance['sessionDSPV1']
DPD_ApiInstance['packageOpenUMLFeV3']
DPD_ApiInstance['serviceSelfColOpenUMLFeV1']
```

I get an error like XXXX takes exactly 1 argument (0 given). Simple types expect only a single value argument
Try that instead:

```python
DPD_ApiInstance.get_from_factory('sessionTypeDSPEnumV1')(propertyValue)
```

Service methods are also avaliable DIRECTLY on instance. They're rewired after execution of init_zeep.

```python
DPD_ApiInstance.findPostalCode("00-999")
```

### I want testing Enviroment

Class init uses following key arguments:
DPDAPI(useTest=False, initZeep=True)

* useTest (default -> False) - run the calls against sandbox credentials and WSDL
* initZeep (default -> True) - initialize zeep on init.

### I need to debug zeep

```python
DPD_ApiInstance.enable_zeep_debug()
```

### If you need the test enviroment

```python
DPD_ApiInstance = DPDAPI(useTest=True)
```
