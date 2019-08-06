import re
import zeep
import logging.config
from decimal import Decimal


try:
    from django.conf import settings as django_settings
except:
    django_settings = None


class DPDInfoAPI(object):
    '''
        Class running DPD WSDL INFO WebApi.
    '''

    PROD_API_WSDL_XML = 'https://dpdinfoservices.dpd.com.pl/DPDInfoServicesXmlEventsService/DPDInfoServicesXmlEvents?wsdl'
    PROD_API_WSDL_OBJ = 'https://dpdinfoservices.dpd.com.pl/DPDInfoServicesObjEventsService/DPDInfoServicesObjEvents?wsdl'
    PROD_USERNAME = None
    PROD_PASSWORD = None

    client = None
    service = None
    factory = None

    def __init__(self, initZeep=True, settings=django_settings, xmlMode=False):
        
        #sorry for that but i liked it from JS 
        self.xmlMode = xmlMode
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

        self.check_config()

    def check_config(self):
        '''
            Are we setup ?
        '''
    
        if self.PROD_USERNAME is None:
            raise UnboundLocalError('Production username is not defined')

        if self.PROD_PASSWORD is None:
            raise UnboundLocalError('Production password is not defined')

    def init_zeep(self):
        '''
            Initialize ZEEP objects and attach service method references directly to instance.
        '''

        #are the credentials here
        self.check_config()

        #wrapped client
        self.client = zeep.Client(self.PROD_API_WSDL_XML if self.xmlMode else self.PROD_API_WSDL_OBJ)
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
    
    @property
    def authPayload(self):
        '''
            Grabs the method from factory and sets the auth variables.
        '''
        authPayload = self['authDataV1']
        authPayload.login = self.PROD_USERNAME
        authPayload.password = self.PROD_PASSWORD
        authPayload.channel = 'clientChannel'
        return authPayload

    def getEventsForCustomer(self, limit=100, language='PL'):

        return self.getEventsForCustomerV4(
            limit, language, self.authPayload
        )
    
    def getEventsForWaybill(self, waybill, getAll=True, language='PL'):

        eventsSelectTypePayload = self.get_from_factory('eventsSelectTypeEnum')('ALL' if getAll else 'ONLY_LAST')

        return self.getEventsForWaybillV1(
            waybill, eventsSelectTypePayload, language, self.authPayload
        )
    
    def confirmEventRecieved(self, eventId):

        return self.markEventsAsProcessedV1(
            eventId , self.authPayload
        )
