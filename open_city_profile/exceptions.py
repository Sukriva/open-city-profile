from graphql import GraphQLError


class ProfileGraphQLError(GraphQLError):
    """GraphQLError that is not sent to Sentry."""


class ServiceAlreadyExistsError(ProfileGraphQLError):
    """Service already connected for the user"""


class TokenExpiredError(ProfileGraphQLError):
    """Token has expired"""


class CannotDeleteProfileWhileServiceConnectedError(ProfileGraphQLError):
    """Profile cannot be deleted while service is still connected"""


class ProfileDoesNotExistError(ProfileGraphQLError):
    """Profile does not exist"""


class APINotImplementedError(ProfileGraphQLError):
    """The functionality is not yet implemented"""


class ProfileHasNoPrimaryEmailError(ProfileGraphQLError):
    """Profile does not have a primary email address"""


class CannotRenewYouthProfileError(ProfileGraphQLError):
    """Youth profile is already renewed or not yet in the next renew window"""


class CannotSetPhotoUsagePermissionIfUnder15YearsError(ProfileGraphQLError):
    """A youth cannot set photo usage permission by himself if he is under 15 years old"""


class ApproverEmailCannotBeEmptyForMinorsError(ProfileGraphQLError):
    """Approver email is required for youth under 18 years old"""
