import re
import zeep
import logging.config
from decimal import Decimal


try:
    from django.conf import settings as django_settings
except:
    django_settings = None


class DPDAPI(object):
    '''
        Class running DPD WSDL WebApi.
    '''

    PROD_API_WSDL = 'https://dpdservices.dpd.com.pl/DPDPackageObjServicesService/DPDPackageObjServices?WSDL'
    PROD_USERNAME = None
    PROD_PASSWORD = None
    PROD_FID = None

    SANDBOX_API_WSDL = 'https://dpdservicesdemo.dpd.com.pl/DPDPackageObjServicesService/DPDPackageObjServices?WSDL'
    SANDBOX_USERNAME = None
    SANDBOX_PASSWORD = None
    SANDBOX_FID = None

    client = None
    service = None
    factory = None
    generation_policy = 1
    pickup_address = None

    def __init__(self, useTest=False, initZeep=True, settings=django_settings):
        self.useTest = useTest
        
        #sorry for that but i liked it from JS 
        settings and self.set_config(settings)
        initZeep and self.init_zeep()

    def __getitem__(self, key):
        '''
            Shortcut to get_from_factory.
            Use: your_instance['addressType']
        '''

        return self.get_from_factory(key)()
    
    def __attach_service_refs(self):
        '''
            Attach service methods DIRECTLY to class instance
        '''

        for service_name in self.service.__dir__():
            #skip magic
            if service_name.startswith('__'):
                continue

            service_method = self.service_get(service_name)

            #double check
            if type(service_method) is zeep.proxy.OperationProxy:
                setattr(self, service_name, service_method)

    def set_config(self, settings):
        '''
            We can set the config here by passing a proper object.
        '''

        self.PROD_USERNAME = getattr(settings, 'DPD_API_USERNAME', None)
        self.PROD_PASSWORD = getattr(settings, 'DPD_API_PASSWORD', None)
        self.PROD_FID = getattr(settings, 'DPD_API_FID', None)

        self.SANDBOX_USERNAME = getattr(settings, 'DPD_API_SANDBOX_USERNAME', None)
        self.SANDBOX_PASSWORD = getattr(settings, 'DPD_API_SANDBOX_PASSWORD', None)
        self.SANDBOX_FID = getattr(settings, 'DPD_API_SANDBOX_FID', None)

        self.check_config()

    def check_config(self):
        '''
            Are we setup ?
        '''

        if self.useTest:
            if self.SANDBOX_USERNAME is None:
                raise UnboundLocalError('TEST Mode is active - Sandbox username is not defined')

            if self.SANDBOX_PASSWORD is None:
                raise UnboundLocalError('TEST Mode is active - Sandbox password is not defined')
            
            if self.SANDBOX_FID is None:
                raise UnboundLocalError('TEST Mode is active - Sandbox FID is not defined')
        else:
            if self.PROD_USERNAME is None:
                raise UnboundLocalError('Production username is not defined')

            if self.PROD_PASSWORD is None:
                raise UnboundLocalError('Production password is not defined')
            
            if self.PROD_FID is None:
                raise UnboundLocalError('Production FID is not defined')

    @property
    def API_USERNAME(self):
        return self.SANDBOX_USERNAME if self.useTest else self.PROD_USERNAME
    
    @property
    def API_PASSWORD(self):
        return self.SANDBOX_PASSWORD if self.useTest else self.PROD_PASSWORD
    
    @property
    def API_FID(self):
        return self.SANDBOX_FID if self.useTest else self.PROD_FID

    @property
    def wsdl_url(self):
        if self.useTest:
            return self.SANDBOX_API_WSDL

        return self.PROD_API_WSDL

    def init_zeep(self):
        '''
            Initialize ZEEP objects and attach service method references directly to instance.
        '''

        #are the credentials here
        self.check_config()

        #wrapped client
        self.client = zeep.Client(self.wsdl_url)
        self.factory = self.client.type_factory('ns0')

        self.s = self.client.service
        self.service = self.s
        self.__attach_service_refs()

    def enable_zeep_debug(self):
        '''
            Enable verbose ZEEP debugging.
        '''

        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'verbose': {
                    'format': '%(name)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
            },
            'loggers': {
                'zeep.transports': {
                    'level': 'DEBUG',
                    'propagate': True,
                    'handlers': ['console'],
                },
            }
        })

    def get_from_factory(self, object_type):
        '''
            Grab fresh type from factory.
        '''

        if not type(object_type) is type(str('')):
            raise TypeError('Object type is required to be string')

        assert self.factory, "Type Factory is unavaliable, please provide valid settings via .set_config(settings) and run .init_zeep() on instance"

        return getattr(self.factory, object_type)

    def service_get(self, method):
        '''
            That's preety much proxy get.
        '''

        assert self.s, "Service is unavaliable, please provide valid settings via .set_config(settings) and run .init_zeep() on instance"

        service_method = getattr(self.s, method, None)

        if not service_method:
            raise ('Service does not provide the %s method' % method)

        return service_method

    def service_call_auth_proxy(self, method, *args):
        '''
            That's preety much proxied call.
        '''
        
        any(args) and args.append(self.authPayload)
        return self.service_get(method)(*args)
    
    def __validateFunctionArgs(self, valid_args, kwargs):
        
        VALID_ARGS = [k for k,v in valid_args.items()]
        
        for k,v in kwargs.items():
            if k not in VALID_ARGS:
                raise AttributeError(
                    '%s if not a valid argument for this function, valid arguments are: %s' % (k, VALID_ARGS)
                )
            
            if type(v) not in valid_args[k]:
                raise TypeError('%s should be type %s - found %s' % (k, valid_args[k], type(v)))
    
    GP_VALUES = {
        1: "STOP_ON_FIRST_ERROR",
        2: "IGNORE_ERRORS",
        3: "ALL_OR_NOTHING"
    }

    def setGenerationPolicy(self, generation_policy):
        '''
            1 - Generation stops on first error - but leaves the packages that worked.
            2 - Hold my beer mode :D We ignore the errors ....
            3 - All or nothing - a stunning full success is required.
        '''

        if generation_policy not in self.GP_VALUES:
            gp = ", ".join('%s - %s' % (p,v) for p,v in self.GP_VALUES.items())
            raise ValueError('Pick valid generation policy - choices are: %s' % gp)

        self.generation_policy = generation_policy
    
    def setPickupAddress(self, pickup_address):
        '''
            Set parcel pickup address for all requests.
        '''
        self.pickup_address = self.getAdressPayload(**pickup_address)
        return self.pickup_address

    @property
    def authPayload(self):
        '''
            Grabs the method from factory and sets the auth variables.
        '''
        authPayload = self['authDataV1']
        authPayload.login = self.API_USERNAME
        authPayload.password = self.API_PASSWORD
        authPayload.masterFid = self.API_FID
        return authPayload

    @property
    def generationPolicyPayload(self):
        return self.get_from_factory('pkgNumsGenerationPolicyV1')(self.GP_VALUES[self.generation_policy])
    
    def validateZipCode(self, zipCode, countryCode='PL'):
        '''
            Polish ZipCode validator - add other countries as well.
            Will raise exception if code is not valid.
        '''

        if countryCode == 'PL':
            zipCode = zipCode.replace('-','')

            if not re.match('^\d\d\d\d\d$', zipCode):
                raise ValueError('Post code should be in XX-XXX or XXXXX format')
            
            return zipCode
        
        return zipCode

    def findPostalCode(self, zipCode, countryCode='PL'):

        zipCode = self.validateZipCode(zipCode, countryCode)

        postCodePayload = self['postalCodeV1']
        postCodePayload.countryCode = countryCode
        postCodePayload.zipCode = zipCode

        return self.findPostalCodeV1(postCodePayload, self.authPayload)
    
    def getCourierOrderAvailability(self, zipCode, countryCode='PL'):

        zipCode = self.validateZipCode(zipCode, countryCode)

        senderPlacePayload = self['senderPlaceV1']
        senderPlacePayload.countryCode = countryCode
        senderPlacePayload.zipCode = zipCode

        return self.getCourierOrderAvailabilityV1(senderPlacePayload, self.authPayload)
    
    def getPackagePayload(self, **kwargs):
        '''
            <xs:complexType name="parcelOpenUMLFeV1">
                <xs:sequence>
                    <xs:element name="content" type="xs:string" minOccurs="0"/>
                    <xs:element name="customerData1" type="xs:string" minOccurs="0"/>
                    <xs:element name="customerData2" type="xs:string" minOccurs="0"/>
                    <xs:element name="customerData3" type="xs:string" minOccurs="0"/>
                    <xs:element name="reference" type="xs:string" minOccurs="0"/>
                    <xs:element name="sizeX" type="xs:int" minOccurs="0"/>
                    <xs:element name="sizeY" type="xs:int" minOccurs="0"/>
                    <xs:element name="sizeZ" type="xs:int" minOccurs="0"/>
                    <xs:element name="weight" type="xs:double" minOccurs="0"/>
                </xs:sequence>
            </xs:complexType>
        '''

        ARG_VALIDATE = {
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

        self.__validateFunctionArgs(ARG_VALIDATE, kwargs)

        parcelPayload = self['parcelOpenUMLFeV1']

        for k,v in kwargs.items():
            setattr(parcelPayload, k, v)

        return parcelPayload
    
    def getAdressPayload(self, **kwargs):
        '''
            <xs:complexType name="packageAddressOpenUMLFeV1">
                <xs:sequence>
                    <xs:element name="address" type="xs:string" minOccurs="0"/>
                    <xs:element name="city" type="xs:string" minOccurs="0"/>
                    <xs:element name="company" type="xs:string" minOccurs="0"/>
                    <xs:element name="countryCode" type="xs:string" minOccurs="0"/>
                    <xs:element name="email" type="xs:string" minOccurs="0"/>
                    <xs:element name="fid" type="xs:int" minOccurs="0"/>
                    <xs:element name="name" type="xs:string" minOccurs="0"/>
                    <xs:element name="phone" type="xs:string" minOccurs="0"/>
                    <xs:element name="postalCode" type="xs:string" minOccurs="0"/>
                </xs:sequence>
            </xs:complexType>
        '''

        ARG_VALIDATE = {
            'address': [str],
            'city': [str],
            'company': [str],
            'countryCode': [str],
            'email': [str],
            'fid': [str],
            'name': [str],
            'phone': [str],
            'postalCode': [str]
        }

        self.__validateFunctionArgs(ARG_VALIDATE, kwargs)

        #fix postal code
        if 'postalCode' in kwargs and '-' in kwargs['postalCode']:
            kwargs['postalCode'] = kwargs['postalCode'].replace('-', '')

        addressPayload = self['packageAddressOpenUMLFeV1']

        for k,v in kwargs.items():
            setattr(addressPayload, k, v)

        return addressPayload
    
    def getServicesPayload(self, 
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
        ):

        servicesPayload = self['servicesOpenUMLFeV4']

        if carryIn:
            servicesPayload.carryIn = self['serviceCarryInOpenUMLFeV1']
        
        if cod:
            codPayload = self['serviceCODOpenUMLFeV1']
            codPayload.amount = cod
            codPayload.currency = codCurrency
            servicesPayload.cod = codPayload
        
        if cud:
            servicesPayload.cud = self['serviceCUDOpenUMLeFV1']

        if declaredValue:
            dvPayload = self['serviceDeclaredValueOpenUMLFeV1']
            dvPayload.amount = declaredValue
            dvPayload.currency = declaredValueCurrency
            servicesPayload.declaredValue = dvPayload
        
        if dedicatedDelivery:
            servicesPayload.dedicatedDelivery = self['serviceDedicatedDeliveryOpenUMLFeV1']
        
        if documentsInternational:
            servicesPayload.documentsInternational = self['serviceFlagOpenUMLF']
        
        if dox:
            servicesPayload.dox = self['servicePalletOpenUMLFeV1']
        
        if duty:
            dutyPayload = self['serviceDutyOpenUMLeFV2']
            dutyPayload.amount = duty
            dutyPayload.currency = dutyCurrency
            servicesPayload.duty = serviceDutyOpenUMLeFV2           
        
        if dpdExpress:
            servicesPayload.dpdExpress = self['serviceFlagOpenUMLF']
        
        if dpdPickup:
            pudoPayload = self['serviceDpdPickupOpenUMLFeV1']
            pudoPayload.pudo = dpdPickup
            servicesPayload.dpdPickup = pudoPayload

        if guarantee:
            serviceGuaranteeTypeEnumOpenUMLFeV1 = [
                'TIME0930',
                'TIME1200',
                'B2C',
                'TIMEFIXED',
                'SATURDAY',
                'INTER',
                'DPDNEXTDAY'
            ]

            if guarantee not in serviceGuaranteeTypeEnumOpenUMLFeV1:
                raise ValueError(
                    'servicesPayload guarantee should be on of: %s' % 
                    ",".join(serviceGuaranteeTypeEnumOpenUMLFeV1)
                )

            if guarantee == 'TIMEFIXED' and not guaranteeValue:
                raise ValueError('TIMEFIXED guarantee should also set guaranteeValue')

            sgPayload = self['serviceGuaranteeOpenUMLFeV1']
            sgPayload.guarantee = self.get_from_factory(
                'serviceGuaranteeTypeEnumOpenUMLFeV1')(guarantee)
            
            if guaranteeValue:
                sgPayload.value = guaranteeValue
            
            servicesPayload.guarantee = sgPayload
        
        if inPers:
            servicesPayload.inPers = self['serviceInPersOpenUMLFeV1']  

        if pallet:
            servicesPayload.pallet = self['servicePalletOpenUMLFeV1']  
        
        if privPers:
            servicesPayload.privPers = self['servicePrivPersOpenUMLFeV1']  
        
        if rod:
            servicesPayload.rod = self['serviceRODOpenUMLFeV1']  
        
        if selfCol:
            if selfCol not in ['PRIV', 'COMP']:
                raise ValueError('servicesPayload selfCol should be either PRIV or COMP')

            scPayload = self['serviceSelfColOpenUMLFeV1']
            sgPayload.reciever = self.get_from_factory(
                'serviceSelfColReceiverTypeEnumOpenUMLFeV1')(selfCol)

            servicesPayload.selfCol = scPayload

        if tires:
            servicesPayload.tires = self['serviceTiresOpenUMLFeV1']  
        
        if tiresExport:
            servicesPayload.tiresExport = self['serviceTiresExportOpenUMLFeV1']  

        return servicesPayload

    PAYER_TYPE = ['SENDER', 'RECEIVER', 'THIRD_PARTY']

    def GenerateSingleParcelShipment(self, 
            packageData, 
            recieverData, 
            servicesData, 
            senderData = None,
            payerType = 'SENDER',
            ref1 = None,
            ref2 = None,
            ref3 = None,
            reference = None,
            thirdPartyFID = None,
            langCode = 'PL',
            returnPayload = False
        ):

        if payerType not in self.PAYER_TYPE:
            raise ValueError('payerType should be one of %s' % ",".join(self.PAYER_TYPE))

        openUMLFeV3 = self['openUMLFeV3']

        packageOpenUMLFeV3 = self['packageOpenUMLFeV3']

        packageOpenUMLFeV3.parcels = self.getPackagePayload(**packageData)
        packageOpenUMLFeV3.receiver = self.getAdressPayload(**recieverData)
        packageOpenUMLFeV3.services = self.getServicesPayload(**servicesData)
        
        if senderData:
            packageOpenUMLFeV3.sender = self.getAdressPayload(**senderData)
        else:
            if not self.pickup_address:
                raise UnboundLocalError('Sender address is not defined, either provide senderData argument or setPickupAddress')

            packageOpenUMLFeV3.sender = self.pickup_address

        packageOpenUMLFeV3.payerType = self.get_from_factory('payerTypeEnumOpenUMLFeV1')(payerType)

        ref1 and setattr(packageOpenUMLFeV3, 'ref1', ref1)
        ref2 and setattr(packageOpenUMLFeV3, 'ref2', ref2)
        ref3 and setattr(packageOpenUMLFeV3, 'ref3', ref3)

        reference and setattr(packageOpenUMLFeV3, 'reference', reference)
        thirdPartyFID and setattr(packageOpenUMLFeV3, 'thirdPartyFID', thirdPartyFID)

        openUMLFeV3.packages = [packageOpenUMLFeV3]

        if returnPayload:
            return [openUMLFeV3, self.generationPolicyPayload, langCode, self.authPayload]

        return self.generatePackagesNumbersV4(
            openUMLFeV3, self.generationPolicyPayload,
            langCode, self.authPayload
        )

    def generateSpedLabels(self, 
            packageId=None,
            reference=None,
            waybill=None,
            sessionType='DOMESTIC',
            senderData=None,
            outputDocFormat='PDF',
            docPageFormat='LBL_PRINTER',
            outputLabelType='BIC3',
            labelVariant=None,
            returnPayload=False
        ):
        
        if not packageId and not reference and not waybill:
            raise AttributeError('One of packageId, reference or waybill is required !')

        dpdServicesParamsPayload = self['dpdServicesParamsV1']
        dpdServicesParamsPayload.policy = self.generationPolicyPayload

        if senderData:
            dpdServicesParamsPayload.pickupAddress = self.getAdressPayload(**senderData)
        else:
            if not self.pickup_address:
                raise UnboundLocalError('Sender address is not defined, either provide senderData argument or setPickupAddress')

            dpdServicesParamsPayload.pickupAddress = self.pickup_address
        
        SESSION_TYPES = ['DOMESTIC', 'INTERNATIONAL']
        if sessionType not in SESSION_TYPES:
            raise ValueError('sessionType should be one of: %s' % ",".join(SESSION_TYPES))

        sessionPayload = self['sessionDSPV1']
        sessionPayload.sessionType = self.get_from_factory('sessionTypeDSPEnumV1')(sessionType)

        packagePayload = self['packageDSPV1']

        if packageId:
            packagePayload.packageId = packageId
        
        if reference:
            packagePayload.reference = reference
        
        if waybill:
            parcelPayload = self['parcelDSPV1']
            parcelPayload.waybill = waybill
            packagePayload.parcels.append(parcelPayload)

        sessionPayload.packages = packagePayload
        
        dpdServicesParamsPayload.session = sessionPayload

        OUTPUT_DOC = ['PDF', 'TIFF', 'PS', 'EPL', 'ZPL']
        if outputDocFormat not in OUTPUT_DOC:
            raise ValueError('outputDocFormat should be one of: %s' % ",".join(OUTPUT_DOC))

        outputDocFormatDSPEnumPayload = self.get_from_factory('outputDocFormatDSPEnumV1')(outputDocFormat)

        PAGE_FORMATS = ['A4' ,'LBL_PRINTER']
        if docPageFormat not in PAGE_FORMATS:
            raise ValueError('docPageFormat should be one of: %s' % ",".join(PAGE_FORMATS))

        outputDocPageFormatDSPEnumPayload = self.get_from_factory('outputDocPageFormatDSPEnumV1')(docPageFormat)

        OUTPUT_TYPES = ['BIC3' ,'EXTENDED']
        if outputLabelType not in OUTPUT_TYPES:
            raise ValueError('outputLabelType should be one of: %s' % ",".join(OUTPUT_TYPES))

        outputLabelTypePayload = self.get_from_factory('outputLabelTypeEnumV1')(outputLabelType)

        LABEL_VARIANTS = [None, 'APOLLO', 'RUCH']
        if labelVariant not in LABEL_VARIANTS:
            raise ValueError('labelVariant should be one of: %s' % ",".join(LABEL_VARIANTS))

        if returnPayload:
            return [
                dpdServicesParamsPayload, 
                outputDocFormatDSPEnumPayload,
                outputDocPageFormatDSPEnumPayload,
                outputLabelTypePayload,
                labelVariant,
                self.authPayload
            ]

        return self.generateSpedLabelsV4(
            dpdServicesParamsPayload,
            outputDocFormatDSPEnumPayload,
            outputDocPageFormatDSPEnumPayload,
            outputLabelTypePayload,
            labelVariant,
            self.authPayload
        )