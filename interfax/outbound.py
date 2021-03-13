from .files import File
from .response import Image, OutboundFax


class Outbound(object):

    def __init__(self, client):
        self.client = client
        self.headers = {} ##


    def deliver(self, fax_number, files, **kwargs):
        """Submit a fax to a single destination number."""
        valid_keys = ['fax_number', 'contact', 'postpone_time',
                      'retries_to_perform', 'csid', 'page_header', 'reference',
                      'reply_address', 'page_size', 'fit_to_page',
                      'page_orientation', 'resolution', 'rendering']

        kwargs['fax_number'] = fax_number

        data = None
        binaryfile = None

        for f in files: # checking if the file supplied is an URL or binary data
            if f.startswith('http://') or f.startswith('https://'):
                self.headers['Content-Location'] = f
                data = self._generate_files(files)
            else:
                binaryfile = self._generate_files(files)


        print('DELIVERING...')
        result = self.client.post('/outbound/faxes', kwargs, valid_keys, data=data, files=binaryfile,
                                  headers=self.headers)  ## PARAMS: 'data' for URI, 'files' for binary data, with either one supllied the other stays empty

        return OutboundFax(self.client, {'id': result.split('/')[-1]})

    def _generate_files(self, files):
        results = []

        for f in files:
            if not hasattr(f, 'file_tuple'):
                f = File(self.client, f)

            results.append((None, f.file_tuple()))

        return results

    def all(self, **kwargs):
        """Get a list of recent outbound faxes (which does not include batch
        faxes)."""
        valid_keys = ['limit', 'last_id', 'sort_order', 'user_id']

        faxes = self.client.get('/outbound/faxes', kwargs, valid_keys)

        return [OutboundFax(self.client, fax) for fax in faxes]

    def completed(self, *args):
        """Get details for a subset of completed faxes from a submitted list.

        (Submitted id's which have not completed are ignored).

        """
        valid_keys = ['ids']
        args_str = ""
        for idx, arg in enumerate(args):
            if idx == len(args) - 1:
                args_str += str(arg)
            else:
                args_str += str(arg) + ", "
        kwargs = {'ids': args}

        faxes = self.client.get('/outbound/faxes/completed', kwargs,
                                valid_keys)

        return [OutboundFax(self.client, fax) for fax in faxes]

    def find(self, message_id):
        """Retrieves information regarding a previously-submitted fax,
        including its current status."""
        fax = self.client.get('/outbound/faxes/{0}'.format(message_id))

        return OutboundFax(self.client, fax)

    def image(self, message_id):
        """Retrieve the fax image (TIFF file) of a submitted fax."""
        data = self.client.get('/outbound/faxes/{0}/image'.format(message_id))

        return Image(self.client, {'data': data})

    def cancel(self, message_id):
        """Cancel a fax in progress."""
        self.client.post('/outbound/faxes/{0}/cancel'.format(message_id))

    def search(self, **kwargs):
        """Search for outbound faxes."""
        valid_keys = ['ids', 'reference', 'date_from', 'date_to', 'status',
                      'user_id', 'fax_number', 'limit', 'offset']

        faxes = self.client.get('/outbound/search', kwargs, valid_keys)

        return [OutboundFax(self.client, fax) for fax in faxes]
