import sys

if sys.version_info.major == 2:
    from httplib import BAD_REQUEST, SEE_OTHER, NOT_FOUND
    from urlparse import parse_qs
else:
    from http.client import BAD_REQUEST, SEE_OTHER, NOT_FOUND
    from urllib.parse import parse_qs