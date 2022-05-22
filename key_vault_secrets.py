import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = "tema4-keys"
KVUri = f"https://{keyVaultName}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)


def get_secret(secret_name):
    print(f"Retrieving your secret from {keyVaultName}.")

    retrieved_secret = client.get_secret(secret_name)
    # print(f"Your secret is '{retrieved_secret.value}'.")

    return retrieved_secret.value
