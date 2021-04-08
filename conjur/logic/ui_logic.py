# -*- coding: utf-8 -*-

"""
LogoutLogic module

This module is the business logic for logging out of the Conjur CLI
"""
import webbrowser
import os
from enum import Enum
import logging

from conjur.api.endpoints import ConjurEndpoint
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.data_object import ConjurrcData
from conjur.wrapper.http_wrapper import invoke_endpoint, HttpVerb


class BrowserOpenType(Enum):
    Window = 1
    Tab = 2


class NotSupportedByServerException(Exception):
    """
    Exception for when the user supplies a not complex enough password when
    attempting to change their password
    """


class TypeNotSupportedException(Exception):
    """
    Exception for when the user supplies a not complex enough password when
    attempting to change their password
    """


class BrowserNotSupportedException(Exception):
    """
    Exception for when the user supplies a not complex enough password when
    attempting to change their password
    """


class WebBrowserWrapperGeneralException(Exception):
    """
    Exception for when the user supplies a not complex enough password when
    attempting to change their password
    """


class WebBrowserWrapper:
    @staticmethod
    def is_ui_browser_exist():
        try:
            SUPPORTED_BROWSERS = ['macosx', 'chrome', 'firefox', 'safari', 'mozilla', 'netscape', 'opera',
                                  'google-chrome']
            webbrowser.get()
            browsers = [k for k, v in webbrowser._browsers.items()]
            for b in browsers:
                if b in SUPPORTED_BROWSERS:
                    return
        except Exception as err:
            raise WebBrowserWrapperGeneralException() from err
        raise BrowserNotSupportedException()

    @staticmethod
    def open(url, browser_open_type: BrowserOpenType):
        try:
            if browser_open_type == BrowserOpenType.Tab:
                webbrowser.open_new_tab(url)
                return
            if browser_open_type == BrowserOpenType.Window:
                webbrowser.open_new(url)
                return
            raise TypeNotSupportedException(f"Unknown Enum for BrowserOpenType {browser_open_type.value}")
        except Exception as err:
            raise WebBrowserWrapperGeneralException("Could not open browser.") from err


# pylint: disable=too-few-public-methods
class UiLogic:
    """
    LogoutLogic

    This class holds the business logic for logging out of Conjur
    """

    def open_new_window(self, url):
        """
        Method to remove credentials during logout
        """
        return self._open_ui(url, BrowserOpenType.Window)

    def open_new_tab(self, url):
        return self._open_ui(url, BrowserOpenType.Tab)

    def _open_ui(self, url, browser_open_type: BrowserOpenType):
        self._validate_supported_server(url)
        WebBrowserWrapper.is_ui_browser_exist()
        ui_endpoint = f"{url}/ui"
        WebBrowserWrapper.open(ui_endpoint, browser_open_type)

    @staticmethod
    def _validate_supported_server(url):
        params = {
            'url': url
        }
        conjurrc_data = ConjurrcData.load_from_file()
        # If the user provides us with the certificate path, we will use it
        # to make a request to /info
        if conjurrc_data.cert_file is None and conjurrc_data.conjur_url.startswith("https"):
            certificate_path = os.path.join(os.path.dirname(DEFAULT_CONFIG_FILE),
                                            "conjur-server.pem")
        else:
            certificate_path = conjurrc_data.cert_file

        logging.debug("Attempting to fetch the account from the Conjur server")
        try:
            invoke_endpoint(HttpVerb.GET,
                            ConjurEndpoint.INFO,
                            params,
                            ssl_verify=certificate_path)
        except:
            raise NotSupportedByServerException()
