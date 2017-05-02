from .base import VMetadataObject


class VMetadataImage(VMetadataObject):

    def __init__(self, name=None, versions=None, description=None):
        """
        :param name: name of the image
        :type name: str
        :param versions: list of VMetadataVersion objects
        :type versions: collections.Iterable
        :param description: short description of the image
        :type description: str
        """

        self.name = name
        self.description = description
        if versions:
            self.versions = [v if isinstance(v, VMetadataVersion)
                             else VMetadataVersion().from_json(v)
                             for v in versions]
        else:
            self.versions = []


class VMetadataVersion(VMetadataObject):

    def __init__(self, version=None, providers=None):
        """
        :param version: short number of Version divided by dots
        :type version: str
        :param providers: list of VMetadataProvider objects
        :type providers: collection.Iterable
        """

        self.version = version
        if providers:
            self.providers = [p if isinstance(p, VMetadataProvider)
                              else VMetadataProvider().from_json(p)
                              for p in providers]
        else:
            self.providers = None


class VMetadataProvider(VMetadataObject):

    def __init__(self, url=None, name=None, checksum_type=None, checksum=None):
        """
        :param url: Public accessible URL of the image
        :type url: str
        :param name: short name of the image
        :type name: str
        :param checksum_type: type of checksum type
        :type checksum_type: str
        :param checksum: checksum hex digit string
        :type checksum str
        """

        self.url = url
        self.name = name
        self.checksum_type = checksum_type
        self.checksum = checksum
