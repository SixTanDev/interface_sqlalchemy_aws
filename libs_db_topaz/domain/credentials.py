# pylint: disable=C0114
from typing import Optional
import os
import boto3
from botocore.client import BaseClient
from dotenv import dotenv_values
from aws_lambda_powertools.utilities.parser.pydantic import BaseModel, Field
from ..custom_logger import custom_logger


class CredentialsAWS(BaseModel):
    """
        AWS Credentials information for authentication.
    """

    user: str = Field(default=..., description="Username for AWS authentication.")
    password: str = Field(default=..., description="Password for AWS authentication.")
    host: str = Field(default="localhost", description="Host address for the AWS service.")
    port: int = Field(default=1057, description="Port number to connect to the AWS service.")
    database: Optional[str] = Field(
        default=None,
        description="Database name for the AWS service."
    )
    driver: Optional[str] = Field(
        default="pymysql",
        description="Specific driver used to establish the connection with the database."
    )
    dialect: Optional[str] = Field(
        default="mysql",
        description="Dialect to establish the connection with the database."
    )

    @classmethod
    def _get_secret(cls, secret_name: str) -> dict[str:str]:
        """
            Retrieves the secret value from AWS Secrets Manager
            based on the provided secret name.
            Args:

            - secret_name: A string representing the name of
                           the secret in AWS Secrets Manager.

            Returns:
            - dict[str | str]: A dictionary containing the retrieved
                               secret information.

            Raises:
            - ValueError: If the specified secret does not exist
                          or if there is an error retrieving the secret.
        """

        client: BaseClient = boto3.client('secretsmanager')
        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)

            secret = (get_secret_value_response.get('SecretString')
                      or get_secret_value_response.get('SecretBinary'))

            custom_logger.info('The secret is successfully obtained from AWS')
            return eval(secret)

        except client.exceptions.ResourceNotFoundException as nfe:
            msg: str = "The specified secret does not exist."
            custom_logger.error(msg)
            raise ValueError(msg) from nfe
        except client.exceptions.ClientError as e:
            msg: str = f"Error retrieving the secret: {secret_name}"
            custom_logger.error(msg)
            raise ValueError(msg) from e

    @classmethod
    def credentials_lambda(cls):
        """
            Retrieves database credentials from AWS Secrets
            Manager based on the specified secret name
            stored in the environment variables and creates
            an instance of the class using these credentials.

            Returns:
            - Database: An instance of the class initialized
                        with the retrieved credentials.

            Raises:
            - ValueError: If there is an error retrieving the
                          secret or if the specified secret does not exist.
        """

        if not os.environ.get('SECRET_NAME'):
            msg: str = 'Did not find the SECRET_NAME environment variable.'
            custom_logger.error(msg)
            raise ValueError(msg)

        custom_logger.info('Get the SECRET_NAME from the environment in AWS Lambda')
        secret_dict = CredentialsAWS._get_secret(
                secret_name=os.environ.get('SECRET_NAME')
            )

        return cls(
            user=secret_dict.get('username'),
            password=secret_dict.get('password'),
            host=secret_dict.get('masterEndpoint'),
            port=secret_dict.get('masterPort'),
            database=secret_dict.get('database')
        )

    @classmethod
    def credentials_localhost(cls, path_env: str):
        """
           Create and return instances of credentials for connecting to the local database.

            Args:
                cls: The class to which the credentials instance will belong.
                path_env (str): The path to the `.env` file containing the environment variables.
           Return:
                An instance of the class with credentials for connecting to the local database.
        """
        env_vars = dotenv_values(path_env)

        db_host = env_vars.get("DB_HOST")
        db_user = env_vars.get("DB_USER")
        db_pass = env_vars.get("DB_PASS")

        custom_logger.info("Creating credentials for localhost")

        return cls(
            user=db_user,
            password=db_pass,
            database=db_host
        )

    def db_connection_string(self) -> str:
        """
            Creates a connection string based on the provided credentials.
        """
        # Construct the base URL
        base_url = (
            f"{self.dialect}+{self.driver}://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/"
        )

        # Add the database name if provided
        custom_logger.info('Create URL for database')
        return f"{base_url}{self.database}" if self.database else base_url
