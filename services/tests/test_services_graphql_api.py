from string import Template

from open_city_profile.consts import SERVICE_CONNECTION_ALREADY_EXISTS_ERROR
from services.enums import ServiceType
from services.tests.factories import ProfileFactory, ServiceConnectionFactory


def test_normal_user_can_query_own_services(
    rf, user_gql_client, service, allowed_data_field_factory
):
    request = rf.post("/graphql")
    request.user = user_gql_client.user
    profile = ProfileFactory(user=user_gql_client.user)
    first_field = allowed_data_field_factory()
    second_field = allowed_data_field_factory()
    allowed_data_field_factory()
    service.allowed_data_fields.add(first_field)
    service.allowed_data_fields.add(second_field)
    ServiceConnectionFactory(profile=profile, service=service)

    query = """
        {
            myProfile {
                serviceConnections {
                    edges {
                        node {
                            service {
                                type
                                title
                                description
                                allowedDataFields {
                                    edges {
                                        node {
                                            fieldName
                                            label
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """
    expected_data = {
        "myProfile": {
            "serviceConnections": {
                "edges": [
                    {
                        "node": {
                            "service": {
                                "type": ServiceType.BERTH.name,
                                "title": service.title,
                                "description": service.description,
                                "allowedDataFields": {
                                    "edges": [
                                        {
                                            "node": {
                                                "fieldName": first_field.field_name,
                                                "label": first_field.label,
                                            }
                                        },
                                        {
                                            "node": {
                                                "fieldName": second_field.field_name,
                                                "label": second_field.label,
                                            }
                                        },
                                    ]
                                },
                            }
                        }
                    }
                ]
            }
        }
    }
    executed = user_gql_client.execute(query, context=request)
    assert dict(executed["data"]) == expected_data


def test_normal_user_can_add_service_mutation(rf, user_gql_client, service_factory):
    request = rf.post("/graphql")
    request.user = user_gql_client.user
    ProfileFactory(user=user_gql_client.user)
    service_factory()

    t = Template(
        """
        mutation {
            addServiceConnection(input: {
                serviceConnection: {
                    service: {
                        type: ${service_type}
                    }
                    enabled: false
                }
            }) {
                serviceConnection {
                    service {
                        type
                    }
                    enabled
                }
            }
        }
    """
    )
    query = t.substitute(service_type=ServiceType.BERTH.name)
    expected_data = {
        "addServiceConnection": {
            "serviceConnection": {
                "service": {"type": ServiceType.BERTH.name},
                "enabled": False,
            }
        }
    }
    executed = user_gql_client.execute(query, context=request)
    assert dict(executed["data"]) == expected_data


def test_normal_user_cannot_add_service_multiple_times_mutation(
    rf, user_gql_client, service_factory
):
    request = rf.post("/graphql")
    request.user = user_gql_client.user
    ProfileFactory(user=user_gql_client.user)
    service_factory()

    t = Template(
        """
        mutation {
            addServiceConnection(input: {
                serviceConnection: {
                    service: {
                        type: ${service_type}
                    }
                }
            }) {
                serviceConnection {
                    service {
                        type
                    }
                }
            }
        }
    """
    )
    query = t.substitute(service_type=ServiceType.BERTH.name)
    expected_data = {
        "addServiceConnection": {
            "serviceConnection": {"service": {"type": ServiceType.BERTH.name}}
        }
    }
    executed = user_gql_client.execute(query, context=request)
    assert dict(executed["data"]) == expected_data
    assert "errors" not in executed

    # do the mutation again
    executed = user_gql_client.execute(query, context=request)
    assert "errors" in executed
    assert "code" in executed["errors"][0]["extensions"]
    assert (
        executed["errors"][0]["extensions"]["code"]
        == SERVICE_CONNECTION_ALREADY_EXISTS_ERROR
    )


def test_normal_user_can_query_own_services_gdpr_api_scopes(
    rf, user_gql_client, service_factory,
):
    query_scope = "query_scope"
    delete_scope = "delete_scope"
    service = service_factory(
        gdpr_query_scope=query_scope, gdpr_delete_scope=delete_scope
    )
    request = rf.post("/graphql")
    request.user = user_gql_client.user
    profile = ProfileFactory(user=user_gql_client.user)

    ServiceConnectionFactory(profile=profile, service=service)

    query = """
        {
            myProfile {
                serviceConnections {
                    edges {
                        node {
                            service {
                                type
                                gdprQueryScope
                                gdprDeleteScope
                            }
                        }
                    }
                }
            }
        }
    """

    expected_data = {
        "myProfile": {
            "serviceConnections": {
                "edges": [
                    {
                        "node": {
                            "service": {
                                "type": service.service_type.name,
                                "gdprQueryScope": query_scope,
                                "gdprDeleteScope": delete_scope,
                            }
                        }
                    }
                ]
            }
        }
    }
    executed = user_gql_client.execute(query, context=request)

    assert dict(executed["data"]) == expected_data
