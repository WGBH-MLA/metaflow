from metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider import (
    AwsSecretsManagerSecretsProvider,
)


def test_aws_secrets_manager_uses_global_session_vars_and_client_params(mocker):
    provider = AwsSecretsManagerSecretsProvider()
    mock_client = mocker.Mock()
    mock_client.get_secret_value.return_value = {
        "Name": "my-secret",
        "SecretString": '{"K":"V"}',
    }
    get_aws_client = mocker.patch(
        "metaflow.plugins.aws.aws_client.get_aws_client",
        return_value=mock_client,
    )
    mocker.patch(
        "metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider.AWS_SECRETS_MANAGER_DEFAULT_REGION",
        "us-west-2",
    )
    mocker.patch(
        "metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider.AWS_SECRETS_MANAGER_SESSION_VARS",
        {"global_session": "1"},
    )
    mocker.patch(
        "metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider.AWS_SECRETS_MANAGER_CLIENT_PARAMS",
        {"verify": False},
    )

    result = provider.get_secret_as_dict("my-secret", options={}, role=None)

    assert result == {"K": "V"}
    get_aws_client.assert_called_once_with(
        "secretsmanager",
        client_params={"verify": False, "region_name": "us-west-2"},
        role_arn=None,
        session_vars={"global_session": "1"},
    )


def test_aws_secrets_manager_options_override_global_session_vars_and_client_params(mocker):
    provider = AwsSecretsManagerSecretsProvider()
    mock_client = mocker.Mock()
    mock_client.get_secret_value.return_value = {
        "Name": "my-secret",
        "SecretString": '{"K":"V"}',
    }
    get_aws_client = mocker.patch(
        "metaflow.plugins.aws.aws_client.get_aws_client",
        return_value=mock_client,
    )
    mocker.patch(
        "metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider.AWS_SECRETS_MANAGER_DEFAULT_REGION",
        "us-west-2",
    )
    mocker.patch(
        "metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider.AWS_SECRETS_MANAGER_SESSION_VARS",
        {"shared": "global", "global_only": "yes"},
    )
    mocker.patch(
        "metaflow.plugins.aws.secrets_manager.aws_secrets_manager_secrets_provider.AWS_SECRETS_MANAGER_CLIENT_PARAMS",
        {"shared": "global", "verify": False},
    )

    options = {
        "region": "eu-west-1",
        "session_vars": {"shared": "option", "option_only": "yes"},
        "client_params": {"shared": "option", "read_timeout": 10},
    }
    result = provider.get_secret_as_dict("my-secret", options=options, role=None)

    assert result == {"K": "V"}
    get_aws_client.assert_called_once_with(
        "secretsmanager",
        client_params={
            "shared": "option",
            "verify": False,
            "read_timeout": 10,
            "region_name": "eu-west-1",
        },
        role_arn=None,
        session_vars={"shared": "option", "global_only": "yes", "option_only": "yes"},
    )
