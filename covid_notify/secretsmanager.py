import json
import logging
import boto3
from botocore.exceptions import ClientError

class SecretsManagerSecret:
    _logger = logging.getLogger(__name__)

    def __init__(self, secretsmanager_client, name):
        self.secretsmanager_client = secretsmanager_client
        self.name = name
        self._secret = None

    def _get_secret(self):
        if self.name is None:
            raise ValueError

        try:
            kwargs = { 'SecretId': self.name }
            response = self.secretsmanager_client.get_secret_value(**kwargs)
            if 'SecretString' in response:
                self._secret = json.loads(response.get('SecretString'))
            else:
                self._logger.exception(f'Missing SecretString in secret {self.name}')
                raise KeyError
        except Exception:
            self._logger.exception(f'Could not get secret value for {self.name}')
            raise

    def get_value(self, key):
        if self._secret is None:
            self._get_secret()
        
        if key not in self._secret:
            self._logger.exception(f'Could not find key {key} in secret {self.name}')
            raise KeyError
        return self._secret.get(key)