"""
    xpan

    xpanapi  # noqa: E501

    The version of the OpenAPI document: 0.1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from ..api_client import ApiClient, Endpoint as _Endpoint
from ..model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from ..model.oauth_token_authorization_code_response import OauthTokenAuthorizationCodeResponse
from ..model.oauth_token_device_code_response import OauthTokenDeviceCodeResponse
from ..model.oauth_token_device_token_response import OauthTokenDeviceTokenResponse
from ..model.oauth_token_refresh_token_response import OauthTokenRefreshTokenResponse


class AuthApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.oauth_token_code2token_endpoint = _Endpoint(
            settings={
                'response_type': (OauthTokenAuthorizationCodeResponse,),
                'auth': [],
                'endpoint_path': '/oauth/2.0/token?grant_type=authorization_code&openapi=xpansdk',
                'operation_id': 'oauth_token_code2token',
                'http_method': 'GET',
                'servers': [
                    {
                        'url': "https://openapi.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'code',
                    'client_id',
                    'client_secret',
                    'redirect_uri',
                ],
                'required': [
                    'code',
                    'client_id',
                    'client_secret',
                    'redirect_uri',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'code':
                        (str,),
                    'client_id':
                        (str,),
                    'client_secret':
                        (str,),
                    'redirect_uri':
                        (str,),
                },
                'attribute_map': {
                    'code': 'code',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                    'redirect_uri': 'redirect_uri',
                },
                'location_map': {
                    'code': 'query',
                    'client_id': 'query',
                    'client_secret': 'query',
                    'redirect_uri': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json; charset=UTF-8'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.oauth_token_device_code_endpoint = _Endpoint(
            settings={
                'response_type': (OauthTokenDeviceCodeResponse,),
                'auth': [],
                'endpoint_path': '/oauth/2.0/device/code?response_type=device_code&openapi=xpansdk',
                'operation_id': 'oauth_token_device_code',
                'http_method': 'GET',
                'servers': [
                    {
                        'url': "https://openapi.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'client_id',
                    'scope',
                ],
                'required': [
                    'client_id',
                    'scope',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'client_id':
                        (str,),
                    'scope':
                        (str,),
                },
                'attribute_map': {
                    'client_id': 'client_id',
                    'scope': 'scope',
                },
                'location_map': {
                    'client_id': 'query',
                    'scope': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json; charset=UTF-8'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.oauth_token_device_token_endpoint = _Endpoint(
            settings={
                'response_type': (OauthTokenDeviceTokenResponse,),
                'auth': [],
                'endpoint_path': '/oauth/2.0/token?grant_type=device_token&openapi=xpansdk',
                'operation_id': 'oauth_token_device_token',
                'http_method': 'GET',
                'servers': [
                    {
                        'url': "https://openapi.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'code',
                    'client_id',
                    'client_secret',
                ],
                'required': [
                    'code',
                    'client_id',
                    'client_secret',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'code':
                        (str,),
                    'client_id':
                        (str,),
                    'client_secret':
                        (str,),
                },
                'attribute_map': {
                    'code': 'code',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                },
                'location_map': {
                    'code': 'query',
                    'client_id': 'query',
                    'client_secret': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json; charset=UTF-8'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.oauth_token_refresh_token_endpoint = _Endpoint(
            settings={
                'response_type': (OauthTokenRefreshTokenResponse,),
                'auth': [],
                'endpoint_path': '/oauth/2.0/token?grant_type=refresh_token&openapi=xpansdk',
                'operation_id': 'oauth_token_refresh_token',
                'http_method': 'GET',
                'servers': [
                    {
                        'url': "https://openapi.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'refresh_token',
                    'client_id',
                    'client_secret',
                ],
                'required': [
                    'refresh_token',
                    'client_id',
                    'client_secret',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'refresh_token':
                        (str,),
                    'client_id':
                        (str,),
                    'client_secret':
                        (str,),
                },
                'attribute_map': {
                    'refresh_token': 'refresh_token',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                },
                'location_map': {
                    'refresh_token': 'query',
                    'client_id': 'query',
                    'client_secret': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json; charset=UTF-8'
                ],
                'content_type': [],
            },
            api_client=api_client
        )

    def oauth_token_code2token(
        self,
        code,
        client_id,
        client_secret,
        redirect_uri,
        **kwargs
    ):
        """oauth_token_code2token  # noqa: E501

        get accesstoken by authorization code  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.oauth_token_code2token(code, client_id, client_secret, redirect_uri, async_req=True)
        >>> result = thread.get()

        Args:
            code (str):
            client_id (str):
            client_secret (str):
            redirect_uri (str):

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            OauthTokenAuthorizationCodeResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['code'] = \
            code
        kwargs['client_id'] = \
            client_id
        kwargs['client_secret'] = \
            client_secret
        kwargs['redirect_uri'] = \
            redirect_uri
        return self.oauth_token_code2token_endpoint.call_with_http_info(**kwargs)

    def oauth_token_device_code(
        self,
        client_id,
        scope,
        **kwargs
    ):
        """oauth_token_device_code  # noqa: E501

        get device code and user code  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.oauth_token_device_code(client_id, scope, async_req=True)
        >>> result = thread.get()

        Args:
            client_id (str):
            scope (str):

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            OauthTokenDeviceCodeResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['client_id'] = \
            client_id
        kwargs['scope'] = \
            scope
        return self.oauth_token_device_code_endpoint.call_with_http_info(**kwargs)

    def oauth_token_device_token(
        self,
        code,
        client_id,
        client_secret,
        **kwargs
    ):
        """oauth_token_device_token  # noqa: E501

        get access_token  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.oauth_token_device_token(code, client_id, client_secret, async_req=True)
        >>> result = thread.get()

        Args:
            code (str):
            client_id (str):
            client_secret (str):

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            OauthTokenDeviceTokenResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['code'] = \
            code
        kwargs['client_id'] = \
            client_id
        kwargs['client_secret'] = \
            client_secret
        return self.oauth_token_device_token_endpoint.call_with_http_info(**kwargs)

    def oauth_token_refresh_token(
        self,
        refresh_token,
        client_id,
        client_secret,
        **kwargs
    ):
        """oauth_token_refresh_token  # noqa: E501

        authorization code  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.oauth_token_refresh_token(refresh_token, client_id, client_secret, async_req=True)
        >>> result = thread.get()

        Args:
            refresh_token (str):
            client_id (str):
            client_secret (str):

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            OauthTokenRefreshTokenResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['refresh_token'] = \
            refresh_token
        kwargs['client_id'] = \
            client_id
        kwargs['client_secret'] = \
            client_secret
        return self.oauth_token_refresh_token_endpoint.call_with_http_info(**kwargs)

