import dependency_injector.containers as containers
import dependency_injector.providers as providers

from application.command_bus import CommandBus
from application.command_handlers import AddItemCommandHandler
from application.query_bus import QueryBus
from application.query_handlers import GetItemsQueryHandler
from application.services import IdentityHashingService
from infrastructure.framework.falcon.controllers import (InfoController,
                                                         ItemsController)
from infrastructure.framework.flask.controllers import (InfoController as FlaskInfoController,
                                                        ItemsController as FlaskItemsController)
from infrastructure.repositories.auction_items_repository import AuctionItemsRepository
from infrastructure.repositories.users_repository import InMemoryUsersRepository
from infrastructure.framework.falcon.authentication import BasicAuthenticationService
from infrastructure.framework.flask.authentication import BasicAuthenticationService as FlaskBasicAuthenticationService


class ObjectiveCommandHandler():
    def __init__(self, logger):
        self.logger = logger

    def handle(self, command):
        print('objective handler is handling', command, self.logger)


def functional_handler(logger):
    def handle(command):
        print('functional handler is handling', command, logger)
    return handle



class BaseContainer(containers.DeclarativeContainer):
    hashing_service_factory = providers.Singleton(IdentityHashingService)
    falcon_authentication_service_factory = providers.Factory(BasicAuthenticationService,
                                                              users_repository=providers.Factory(InMemoryUsersRepository, hashing_service=hashing_service_factory)
                                                              )
    flask_authentication_service_factory = providers.Factory(FlaskBasicAuthenticationService,
                                                             users_repository=providers.Factory(
                                                                 InMemoryUsersRepository,
                                                                 hashing_service=hashing_service_factory)
                                                             )


class CommandBusContainer(containers.DeclarativeContainer):
    items_repository = providers.Singleton(AuctionItemsRepository)

    command_handler_factory = providers.FactoryAggregate(
        AddItemCommand=providers.Factory(AddItemCommandHandler,
                                         items_repository=items_repository
                                         )
    )

    command_bus_factory = providers.Factory(
        CommandBus,
        command_handler_factory=providers.DelegatedFactory(
            command_handler_factory)
    )


class QueryBusContainer(containers.DeclarativeContainer):
    items_repository = providers.Singleton(AuctionItemsRepository)

    query_handler_factory = providers.FactoryAggregate(
        GetItemsQuery=providers.Factory(
            GetItemsQueryHandler, items_repository=items_repository)
    )

    query_bus_factory = providers.Factory(
        QueryBus, query_handler_factory=providers.DelegatedFactory(query_handler_factory))


class FalconContainer(containers.DeclarativeContainer):
    items_controller_factory = providers.Factory(ItemsController,
                                                 command_bus=CommandBusContainer.command_bus_factory,
                                                 query_bus=QueryBusContainer.query_bus_factory,
                                                 authentication_service=BaseContainer.falcon_authentication_service_factory,
                                                 )
    info_controller_factory = providers.Factory(InfoController,
                                                authentication_service=BaseContainer.falcon_authentication_service_factory
                                                )


class FlaskContainer(containers.DeclarativeContainer):
    info_controller_factory = providers.Factory(FlaskInfoController,
                                                authentication_service=BaseContainer.flask_authentication_service_factory
                                                )
    items_controller_factory = providers.Factory(FlaskItemsController,
                                                 command_bus=CommandBusContainer.command_bus_factory,
                                                 query_bus=QueryBusContainer.query_bus_factory,
                                                 authentication_service=BaseContainer.flask_authentication_service_factory,
                                                 )