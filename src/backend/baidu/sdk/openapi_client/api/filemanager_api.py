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


class FilemanagerApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.filemanagercopy_endpoint = _Endpoint(
            settings={
                'response_type': (dict,),
                'auth': [],
                'endpoint_path': '/rest/2.0/xpan/file?method=filemanager&opera=copy&openapi=xpansdk',
                'operation_id': 'filemanagercopy',
                'http_method': 'POST',
                'servers': [
                    {
                        'url': "https://pan.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'access_token',
                    '_async',
                    'filelist',
                    'ondup',
                ],
                'required': [
                    'access_token',
                    '_async',
                    'filelist',
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
                    'access_token':
                        (str,),
                    '_async':
                        (int,),
                    'filelist':
                        (str,),
                    'ondup':
                        (str,),
                },
                'attribute_map': {
                    'access_token': 'access_token',
                    '_async': 'async',
                    'filelist': 'filelist',
                    'ondup': 'ondup',
                },
                'location_map': {
                    'access_token': 'query',
                    '_async': 'form',
                    'filelist': 'form',
                    'ondup': 'form',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [],
                'content_type': [
                    'application/x-www-form-urlencoded'
                ]
            },
            api_client=api_client
        )
        self.filemanagerdelete_endpoint = _Endpoint(
            settings={
                'response_type': (dict,),
                'auth': [],
                'endpoint_path': '/rest/2.0/xpan/file?method=filemanager&opera=delete&openapi=xpansdk',
                'operation_id': 'filemanagerdelete',
                'http_method': 'POST',
                'servers': [
                    {
                        'url': "https://pan.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'access_token',
                    '_async',
                    'filelist',
                    'ondup',
                ],
                'required': [
                    'access_token',
                    '_async',
                    'filelist',
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
                    'access_token':
                        (str,),
                    '_async':
                        (int,),
                    'filelist':
                        (str,),
                    'ondup':
                        (str,),
                },
                'attribute_map': {
                    'access_token': 'access_token',
                    '_async': 'async',
                    'filelist': 'filelist',
                    'ondup': 'ondup',
                },
                'location_map': {
                    'access_token': 'query',
                    '_async': 'form',
                    'filelist': 'form',
                    'ondup': 'form',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [],
                'content_type': [
                    'application/x-www-form-urlencoded'
                ]
            },
            api_client=api_client
        )
        self.filemanagermove_endpoint = _Endpoint(
            settings={
                'response_type': (dict,),
                'auth': [],
                'endpoint_path': '/rest/2.0/xpan/file?method=filemanager&opera=move&openapi=xpansdk',
                'operation_id': 'filemanagermove',
                'http_method': 'POST',
                'servers': [
                    {
                        'url': "https://pan.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'access_token',
                    '_async',
                    'filelist',
                    'ondup',
                ],
                'required': [
                    'access_token',
                    '_async',
                    'filelist',
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
                    'access_token':
                        (str,),
                    '_async':
                        (int,),
                    'filelist':
                        (str,),
                    'ondup':
                        (str,),
                },
                'attribute_map': {
                    'access_token': 'access_token',
                    '_async': 'async',
                    'filelist': 'filelist',
                    'ondup': 'ondup',
                },
                'location_map': {
                    'access_token': 'query',
                    '_async': 'form',
                    'filelist': 'form',
                    'ondup': 'form',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [],
                'content_type': [
                    'application/x-www-form-urlencoded'
                ]
            },
            api_client=api_client
        )
        self.filemanagerrename_endpoint = _Endpoint(
            settings={
                'response_type': (dict,),
                'auth': [],
                'endpoint_path': '/rest/2.0/xpan/file?method=filemanager&opera=rename&openapi=xpansdk',
                'operation_id': 'filemanagerrename',
                'http_method': 'POST',
                'servers': [
                    {
                        'url': "https://pan.baidu.com",
                        'description': "No description provided",
                    },
                ]
            },
            params_map={
                'all': [
                    'access_token',
                    '_async',
                    'filelist',
                    'ondup',
                ],
                'required': [
                    'access_token',
                    '_async',
                    'filelist',
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
                    'access_token':
                        (str,),
                    '_async':
                        (int,),
                    'filelist':
                        (str,),
                    'ondup':
                        (str,),
                },
                'attribute_map': {
                    'access_token': 'access_token',
                    '_async': 'async',
                    'filelist': 'filelist',
                    'ondup': 'ondup',
                },
                'location_map': {
                    'access_token': 'query',
                    '_async': 'form',
                    'filelist': 'form',
                    'ondup': 'form',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [],
                'content_type': [
                    'application/x-www-form-urlencoded'
                ]
            },
            api_client=api_client
        )

    def filemanagercopy(
        self,
        access_token,
        _async,
        filelist,
        **kwargs
    ):
        """filemanagercopy  # noqa: E501

        filemanager copy  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.filemanagercopy(access_token, _async, filelist, async_req=True)
        >>> result = thread.get()

        Args:
            access_token (str):
            _async (int): async
            filelist (str): filelist

        Keyword Args:
            ondup (str): ondup. [optional]
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
            None
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
        kwargs['access_token'] = \
            access_token
        kwargs['_async'] = \
            _async
        kwargs['filelist'] = \
            filelist
        return self.filemanagercopy_endpoint.call_with_http_info(**kwargs)

    def filemanagerdelete(
        self,
        access_token,
        _async,
        filelist,
        **kwargs
    ):
        """filemanagerdelete  # noqa: E501

        filemanager delete  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.filemanagerdelete(access_token, _async, filelist, async_req=True)
        >>> result = thread.get()

        Args:
            access_token (str):
            _async (int): async
            filelist (str): filelist

        Keyword Args:
            ondup (str): ondup. [optional]
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
            None
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
        kwargs['access_token'] = \
            access_token
        kwargs['_async'] = \
            _async
        kwargs['filelist'] = \
            filelist
        return self.filemanagerdelete_endpoint.call_with_http_info(**kwargs)

    def filemanagermove(
        self,
        access_token,
        _async,
        filelist,
        **kwargs
    ):
        """filemanagermove  # noqa: E501

        filemanager move  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.filemanagermove(access_token, _async, filelist, async_req=True)
        >>> result = thread.get()

        Args:
            access_token (str):
            _async (int): async
            filelist (str): filelist

        Keyword Args:
            ondup (str): ondup. [optional]
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
            None
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
        kwargs['access_token'] = \
            access_token
        kwargs['_async'] = \
            _async
        kwargs['filelist'] = \
            filelist
        return self.filemanagermove_endpoint.call_with_http_info(**kwargs)

    def filemanagerrename(
        self,
        access_token,
        _async,
        filelist,
        **kwargs
    ):
        """filemanagerrename  # noqa: E501

        filemanager rename  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.filemanagerrename(access_token, _async, filelist, async_req=True)
        >>> result = thread.get()

        Args:
            access_token (str):
            _async (int): async
            filelist (str): filelist

        Keyword Args:
            ondup (str): ondup. [optional]
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
            None
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
        kwargs['access_token'] = \
            access_token
        kwargs['_async'] = \
            _async
        kwargs['filelist'] = \
            filelist
        return self.filemanagerrename_endpoint.call_with_http_info(**kwargs)

